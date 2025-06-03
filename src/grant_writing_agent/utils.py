import os
import asyncio
import requests

from src.grant_writing_agent.state import Section
from langsmith import traceable
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.runnables import RunnableConfig
from src.grant_writing_agent.configuration import Configuration


def deduplicate_and_format_sources(
    search_response, max_tokens_per_source, include_raw_content=True
):
    """
    Takes a list of search responses and formats them into a readable string.
    Limits the raw_content to approximately max_tokens_per_source.

    Args:
        search_responses: List of search response dicts, each containing:
            - query: str
            - results: List of dicts with fields:
                - title: str
                - url: str
                - content: str
                - score: float
                - raw_content: str|None
        max_tokens_per_source: int
        include_raw_content: bool

    Returns:
        str: Formatted string with deduplicated sources
    """
    # Collect all results
    sources_list = []
    for response in search_response:
        sources_list.extend(response["results"])

    # Deduplicate by URL
    unique_sources = {source["url"]: source for source in sources_list}

    # Format output
    formatted_text = "Sources:\n\n"
    for i, source in enumerate(unique_sources.values(), 1):
        formatted_text += f"Source {source['title']}:\n===\n"
        formatted_text += f"URL: {source['url']}\n===\n"
        formatted_text += (
            f"Most relevant content from source: {source['content']}\n===\n"
        )
        if include_raw_content:
            # Using rough estimate of 4 characters per token
            char_limit = max_tokens_per_source * 4
            # Handle None raw_content
            raw_content = source.get("raw_content", "")
            if raw_content is None:
                raw_content = ""
                print(f"Warning: No raw_content found for source {source['url']}")
            if len(raw_content) > char_limit:
                raw_content = raw_content[:char_limit] + "... [truncated]"
            formatted_text += f"Full source content limited to {max_tokens_per_source} tokens: {raw_content}\n\n"

    return formatted_text.strip()


def format_sections(sections: list[Section]) -> str:
    """Format a list of sections into a string"""
    formatted_str = ""
    for idx, section in enumerate(sections, 1):
        formatted_str += f"""
{'='*60}
Section {idx}: {section.name}
{'='*60}
Description:
{section.description}
Requires Research: 
{section.research}

Content:
{section.content if section.content else '[Not yet written]'}

"""
    return formatted_str


embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

MONGODB_URI = os.getenv("MONGODB_URI")

# initialize MongoDB python client
client = MongoClient(MONGODB_URI)

DB_NAME = "vector_store"
COLLECTION_NAME = "client_docs_vector_store"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "client_docs_vector_index"

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]

vector_store = MongoDBAtlasVectorSearch(
    collection=MONGODB_COLLECTION,
    embedding=embeddings,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    text_key="text",
    embedding_key="embedding",
    relevance_score_fn="cosine",
)


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# retriever = vector_store.as_retriever(search_kwargs={"k": 6, "lambda_mult": 0.25})

# # Create a MultiQueryRetriever that generates multiple queries
# multi_query_retriever = MultiQueryRetriever.from_llm(retriever=retriever, llm=llm)
