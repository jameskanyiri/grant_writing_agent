from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_community.document_loaders import WebBaseLoader
from typing import List, Annotated
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from src.grant_writing_agent.prompts import (
    grade_document_prompt,
    extract_project_idea_and_funding_requirements_prompt,
)
from src.grant_writing_agent.state import GradeDocuments, FundingRequirementsProjectIdea
from langchain_openai import ChatOpenAI
from src.grant_writing_agent.configuration import Configuration
from src.grant_writing_agent.utils import vector_store
from langchain.retrievers.multi_query import MultiQueryRetriever
from langgraph.prebuilt import InjectedState, InjectedStore


# Set writer model
writer_model = ChatOpenAI(model=Configuration.writer_model, temperature=0)


@tool
async def generate_sections(
    tool_call_id: Annotated[str, InjectedToolCallId],
    transfer_message: str,
    config: RunnableConfig,
    messages: Annotated[list, InjectedState("messages")],
) -> Command:
    """
    Transfer the control to the planning agent.

    Args:
        transfer_message: The message to transfer to the planning agent.
    """

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    user_name = configurable.user_name

    system_message = extract_project_idea_and_funding_requirements_prompt.format(
        conversation=messages, user_name=user_name
    )

    structured_llm = writer_model.with_structured_output(FundingRequirementsProjectIdea)

    project_idea_x_funding_requirements = structured_llm.invoke(system_message)

    funding_requirements = project_idea_x_funding_requirements.funding_requirements
    project_idea = project_idea_x_funding_requirements.project_idea

    return Command(
        update={
            "project_idea": project_idea,
            "funding_requirements": funding_requirements,
            "start_writing_sections": True,
            # update the message history
            "messages": [
                ToolMessage(
                    "Please respond the following message to the user: Processing your request... Now transferring to the section generator.",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )


# Tavily Search
@tool
def tavily_search(query: str, config: RunnableConfig) -> str:
    """Performs a web search using Tavily search engine.

    Args:
        query: The search query string.

    Returns:
        JSON string with search results including answer, results list, raw content, and images.
    """

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    max_web_results = configurable.max_web_results

    tavily_search = TavilySearchResults(
        max_results=max_web_results,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True,
        include_images=True,
    )

    # Use invoke for operation
    result = tavily_search.invoke({"query": query})
    return result


# Web Scraping
@tool
def scrape_webpages(urls: List[str]) -> str:
    """Use requests and bs4 to scrape the provided web pages for detailed information."""
    loader = WebBaseLoader(urls)
    docs = loader.aload()  # Use aload for operation
    return "\n\n".join(
        [
            f'<Document name="{doc.metadata.get("title", "")}">\n{doc.page_content}\n</Document>'
            for doc in docs
        ]
    )


@tool
def retrieve_client_info(query: str, config: RunnableConfig) -> str:
    """
    Retrieve information about the client from the vector database.

    Args:
        query: The query to retrieve information about the client.

    Returns:
        A string of the information retrieved from the vector database or "No documents found" message.
    """

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    document_ids = configurable.context_document_ids
    max_search_depth = configurable.max_search_depth
    max_vector_results = configurable.max_vector_results
    client_id = configurable.client_id

    for attempt in range(max_search_depth):
        # Retrieve documents from vector store
        if document_ids:
            docs = vector_store.similarity_search(
                query=query,
                k=max_vector_results,
                pre_filter={"document_id": {"$in": document_ids}},
            )
        else:
            docs = vector_store.similarity_search(
                query=query, k=max_vector_results, pre_filter={"client_id": client_id}
            )

        all_docs = []

        # Grade documents
        for doc in docs:
            doc_content = doc.page_content

            # Grade documents
            grade_prompt = grade_document_prompt.format(
                question=query, document=doc_content
            )

            structured_llm_grader = writer_model.with_structured_output(GradeDocuments)

            score = structured_llm_grader.invoke(grade_prompt)

            if score.binary_score == "yes":
                all_docs.extend(docs)
            else:
                continue

        # If documents were found, return them
        if all_docs:
            return "\n\n".join(doc.page_content for doc in all_docs)

        # If this was the last attempt and no documents were found
        if attempt == max_search_depth - 1:
            return "No relevant document is found to answer the question.Please provide a document that will help answer the question."
