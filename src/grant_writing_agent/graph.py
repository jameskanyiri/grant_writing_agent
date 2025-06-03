from typing import Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph
from langgraph.types import interrupt, Command
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from src.grant_writing_agent.tools import (
    generate_sections,
    tavily_search,
    scrape_webpages,
    retrieve_client_info,
)
from src.grant_writing_agent.state import (
    AgentStateInput,
    AgentStateOutput,
    Sections,
    AgentState,
    SectionState,
    SectionOutputState,
    Queries,
    Feedback,
    GradeDocuments,
)
from src.grant_writing_agent.prompts import (
    report_planner_query_writer_instructions,
    report_planner_instructions,
    query_writer_instructions,
    section_writer_instructions,
    final_section_writer_instructions,
    section_grader_instructions,
    gather_prompt,
    grade_document_prompt,
)
from src.grant_writing_agent.configuration import Configuration
from src.grant_writing_agent.utils import (
    deduplicate_and_format_sources,
    format_sections,
    vector_store,
)

from langchain_core.documents import Document

# Set writer model
# writer_model = ChatOpenAI(model="o1", reasoning_effort="medium", temperature=0)
writer_model = ChatOpenAI(model=Configuration.writer_model, temperature=0)


# Chat with the user
tools = [generate_sections, tavily_search, scrape_webpages, retrieve_client_info]
tool_node = ToolNode(tools)


# Grant genie is the main node that gathers the project idea and funding requirements from the user.
async def gather_requirement(
    state: AgentState, config
) -> Command[Literal["tools", "generate_sections", END]]:
    """Grant genie is the main node that gathers the project idea and funding requirements from the user."""

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    user_name = configurable.user_name
    organization_name = configurable.client_name
    about_client = configurable.about_client

    # Format system message
    system_message = gather_prompt.format(
        user_name=user_name, client_name=organization_name, about_client=about_client
    )

    model = writer_model.bind_tools(tools)
    response = await model.ainvoke(
        [SystemMessage(content=system_message)] + state["messages"]
    )
    state["messages"] = [response]

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return Command(goto="tools", update={"messages": [response]})

    elif state.get("start_writing_sections"):
        return Command(goto="generate_sections", update={"messages": [response]})

    else:
        return Command(goto=END, update={"messages": [response]})


# Nodes
async def generate_sections(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["generate_queries"]]:
    """Generate the grant proposal sections"""

    # Get state
    project_idea = state["project_idea"]
    funding_requirements = state["funding_requirements"]
    feedback = state.get("feedback_on_sections", None)

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    user_name = configurable.user_name
    client_name = configurable.client_name
    grant_proposal_structure = configurable.grant_proposal_structure
    about_client = configurable.about_client
    number_of_queries = configurable.number_of_queries
    # Format system instructions
    system_instructions_sections = report_planner_instructions.format(
        project_idea=project_idea,
        funding_requirements=funding_requirements,
        grant_proposal_structure=grant_proposal_structure,
        about_client=about_client,
        user_name=user_name,
        client_name=client_name,
        feedback_from_review=feedback,
        number_of_queries=number_of_queries,
    )

    # Set the planner model
    planner_llm = ChatOpenAI(model=configurable.planner_model)

    # Generate sections
    structured_llm = planner_llm.with_structured_output(Sections)
    report_sections = await structured_llm.ainvoke(
        [SystemMessage(content=system_instructions_sections)]
        + [
            HumanMessage(
                content="Generate the sections of the grant proposal. Your response must include a 'sections' field containing a list of sections. Each section must have: name, description, plan, research, and content fields."
            )
        ]
    )

    # Get sections
    sections = report_sections.sections

    return Command(goto="generate_queries", update={"sections": sections})


def generate_queries(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["retrieve_context"]]:
    """Generate search queries for a report section"""

    sections = state["sections"]

    # Get the first unwritten section that needs research
    section = None
    for s in sections:
        if not s.is_written and s.research:
            section = s
            section.is_active = True
            break

    if section is None:
        return Command(
            goto="write_section",
            update={"messages": [AIMessage(content="No sections require research")]},
        )

    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    number_of_queries = configurable.number_of_queries
    client_name = configurable.client_name
    user_name = configurable.user_name

    # Generate queries
    structured_llm = writer_model.with_structured_output(Queries)

    # Format system instructions
    system_instructions = query_writer_instructions.format(
        section_description=section.description,
        number_of_queries=number_of_queries,
        user_name=user_name,
        client_name=client_name,
    )

    # Generate queries
    queries = structured_llm.invoke(
        [SystemMessage(content=system_instructions)]
        + [HumanMessage(content="Generate search queries on the provided topic.")]
    )

    section.search_queries = queries.queries

    return Command(goto="retrieve_context", update={"sections": sections})


async def retrieve_context(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["write_section"]]:
    """Search the web for each query, then return a list of raw sources and a formatted string of sources."""

    sections = state["sections"]

    # Get the active section (should be the first unwritten one)
    section = None
    for s in sections:
        if s.is_active:
            section = s
            break

    if section is None:
        return Command(
            goto="write_section",
            update={"messages": [AIMessage(content="No active section found")]},
        )

    # Get Configuration
    configurable = Configuration.from_runnable_config(config)
    document_ids = configurable.context_document_ids
    client_id = configurable.client_id
    max_vector_results = configurable.max_vector_results
    max_search_depth = configurable.max_search_depth

    search_queries = section.search_queries

    for attempt in range(max_search_depth):
        all_docs = []  # Moved outside the query loop to collect docs from all queries
        source_str = ""

        for query in search_queries:
            # Extract the search query string
            query_str = (
                query.search_query if hasattr(query, "search_query") else str(query)
            )

            if document_ids:
                docs = vector_store.similarity_search(
                    query=query_str,
                    k=max_vector_results,
                    pre_filter={"document_id": {"$in": document_ids}},
                )
            else:
                docs = vector_store.similarity_search(
                    query=query_str,
                    k=max_vector_results,
                    pre_filter={"client_id": client_id},
                )

            # Grade documents
            for doc in docs:
                doc_content = doc.page_content

                # Grade documents
                grade_prompt = grade_document_prompt.format(
                    question=query_str,
                    document=doc_content,
                )

                structured_llm_grader = writer_model.with_structured_output(
                    GradeDocuments
                )

                score = await structured_llm_grader.ainvoke(grade_prompt)

                if score.binary_score == "yes":
                    # Check if the document is already in the all_docs list
                    if doc not in all_docs:
                        all_docs.append(doc)
                        source_str += doc.page_content

        if all_docs:  # Moved outside query loop to check all collected docs
            section.documents = all_docs
            section.source_str = source_str
            return Command(goto="write_section", update={"sections": sections})

        if attempt == max_search_depth - 1:
            # Interrupt to request more documents
            return Command(
                goto="write_section",
                update={"messages": [HumanMessage(content="No documents found")]},
            )


async def write_section(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["generate_queries", "retrieve_context", "gather_requirement"]]:
    """Write a section of the report"""

    # Get all the sections
    sections = state["sections"]

    # Get funding requirements
    funding_requirements = state["funding_requirements"]

    # Get project idea
    project_idea = state["project_idea"]

    # Get final grant proposal
    final_grant_proposal = state.get("final_grant_proposal", "")

    # Initialize search_iterations if it doesn't exist
    iterations = state.get("search_iterations", 0)

    # Get the first unwritten section
    section = None
    for s in sections:
        # Get the section that is active (means we have gathered information for it)
        if s.is_active:
            # Assign the section to the section variable
            section = s
            break

    # If no section is active, we are done
    if section is None:
        # All sections are written
        # Route to grant genie set the start_writing_sections to False
        # This will enable section editing
        return Command(
            goto="gather_requirement",
            update={
                # Add a message to the messages list to indicate that we are done
                "messages": [
                    AIMessage(
                        content="Respond to user with the following message: Successfully generated a grant proposal draft. Let's start editing the draft"
                    )
                ],
                # Set the start_writing_sections to False
                "start_writing_sections": False,
            },
        )

    # Get configuration
    configurable = Configuration.from_runnable_config(config)

    # Get user name
    user_name = configurable.user_name

    # get client name
    client_name = configurable.client_name

    # Get proposal structure
    grant_proposal_structure = configurable.grant_proposal_structure

    # Format system instructions
    system_instructions = section_writer_instructions.format(
        section_title=section.name,
        section_description=section.description,
        context=section.source_str,
        section_content=section.content,
        user_name=user_name,
        client_name=client_name,
        section_name=section.name,
        grant_proposal_structure=grant_proposal_structure,
        funding_requirements=funding_requirements,
        project_idea=project_idea,
    )

    # Generate section
    section_content = await writer_model.ainvoke(
        [
            SystemMessage(
                content=system_instructions,
            )
        ]
        + [
            HumanMessage(
                content="Generate a report section based on the provided sources."
            )
        ]
    )

    # Write content to the section object
    section.content = section_content.content

    # Section grading prompt
    section_grader_instructions_formatted = section_grader_instructions.format(
        section_topic=section.description,
        section=section.content,
    )

    # Feedback
    structured_llm = writer_model.with_structured_output(Feedback)

    feedback = structured_llm.invoke(
        [
            SystemMessage(
                content=section_grader_instructions_formatted,
            )
        ]
        + [
            HumanMessage(
                content="Grade the report and consider follow-up questions for missing information:"
            )
        ]
    )

    if feedback.grade == "pass" or iterations >= configurable.max_search_depth:
        # Reset search_iterations for next section
        iterations = 0

        # mark section as written
        section.is_written = True

        # mark the section as inactive since we dont want to write it again
        section.is_active = False

        # Append the completed section to final_grant_proposal
        final_grant_proposal += f"\n\n{section.content}"

        # Check if there are more sections that require research
        has_unwritten_research_sections = any(s for s in sections if not s.is_written)

        if has_unwritten_research_sections:
            return Command(
                goto="generate_queries",
                update={
                    "sections": sections,
                    "final_grant_proposal": final_grant_proposal,
                    "search_iterations": iterations,
                },
            )
        else:
            return Command(
                goto="grant_genie",
                update={
                    "sections": sections,
                    "final_grant_proposal": final_grant_proposal,
                    "start_writing_sections": False,
                    "search_iterations": iterations,
                    "messages": [
                        AIMessage(
                            content="Successfully generated a grant proposal draft. Let's start editing the draft"
                        )
                    ],
                },
            )

    else:
        # update search queries
        section.search_queries = feedback.follow_up_queries

        # Update the existing section with new content and update search queries
        return Command(
            goto="retrieve_context",
            update={
                "sections": sections,
                "search_iterations": iterations
                + 1,  # Use iterations variable instead of accessing state directly
            },
        )


# Outer graph --
builder = StateGraph(
    AgentState,
    input=AgentStateInput,
    output=AgentStateOutput,
    config_schema=Configuration,
)
builder.add_node("gather_requirement", gather_requirement)
builder.add_node("tools", tool_node)
builder.add_node("generate_sections", generate_sections)
builder.add_node("generate_queries", generate_queries)
builder.add_node("write_section", write_section)
builder.add_node("retrieve_context", retrieve_context)

# Add edges
builder.add_edge(START, "gather_requirement")

builder.add_edge("tools", "gather_requirement")

graph = builder.compile()
