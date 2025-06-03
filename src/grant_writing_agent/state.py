from typing import Annotated, List, TypedDict, Literal
from pydantic import BaseModel, Field
import operator
from langgraph.graph import MessagesState
from langchain_core.documents import Document


class SearchQuery(BaseModel):
    search_query: str = Field(
        ...,
        description=(
            "A concise, direct search query of approximately 5 words optimized for vector search. "
            "Include organization name and 1-2 key focus areas. Avoid articles, conjunctions, "
            "and unnecessary words. Format as targeted keyword phrases rather than questions."
        ),
    )


class Section(BaseModel):
    name: str = Field(
        description="Name for this section of the report.",
    )
    description: str = Field(
        description="""Structured blueprint for this section that MUST include:
        - **Core components:** Key information elements required for completion
        - **Strategic alignment:** How this section supports grant application objectives
        - **Critical questions:** 3-5 specific, targeted questions to answer
        - **Evidence requirements:** Specific data points, metrics, or examples needed
        - **Structure guidelines:** Format specifications (bullet points, tables, length)
        
        🔹 **Vector Database Instructions:**
        - Create 2-3 highly focused queries (5 words each)
        - Target organization-specific information over general context
        - Include specific program names, initiatives, or unique identifiers
        - Focus on retrieving evidence that demonstrates impact and capabilities
        """
    )
    research: bool = Field(
        description="Always set to true. System field for research tracking."
    )
    content: str = Field(
        description="The compiled, formatted content for this section based on retrieved data."
    )
    is_written: bool = Field(
        description="Always set to false. System field tracking completion status."
    )
    is_active: bool = Field(
        description="Always set to false. System field tracking current focus."
    )

    search_queries: list[SearchQuery] = Field(
        description="List of search queries"
    )  # List of search queries
    documents: list[str] = Field(description="List of documents")  # List of documents
    source_str: str = Field(
        description="String of formatted source content from data retrieval"
    )


class Sections(BaseModel):
    sections: List[Section] = Field(
        description="Sections of the grant proposal.",
    )


class FundingRequirementsProjectIdea(BaseModel):
    project_idea: str = Field(
        description="""
        A well defined project idea that is concise and to the point.
        It should be a description of the project that the user wants to write a grant for.
        it should capture the key elements of the project and the user's motivation for the project.
        """,
    )
    funding_requirements: str = Field(
        description="""
        A well defined funding requirements that is concise and to the point.
        It should be a description of the funding that the user is looking for.
        it should capture the key elements such as amount, duration, eligibility criteria, etc.
        
        """,
    )


class Queries(BaseModel):
    queries: List[SearchQuery] = Field(
        description="List of search queries.",
    )


class Feedback(BaseModel):
    grade: Literal["pass", "fail"] = Field(
        description="Evaluation result indicating whether the response meets requirements ('pass') or needs revision ('fail')."
    )
    follow_up_queries: List[SearchQuery] = Field(
        description="List of follow-up search queries.",
    )


class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


class AgentStateInput(MessagesState):
    """State input for the report state."""


class AgentStateOutput(TypedDict):
    final_report: str  # Final report


class AgentState(MessagesState):
    topic: str  # Report topic
    project_idea: str = None  # Project idea
    funding_requirements: str = None  # Funding requirements
    sections: list[Section]  # List of report sections
    start_writing_sections: bool = False  # Whether to generate sections
    start_generating_queries: bool = False  # Whether to generate queries
    completed_sections: list[
        Section
    ]  # Changed to be consistent with SectionOutputState
    report_sections_from_research: (
        str  # String of any completed sections from research to write final sections
    )
    final_report: str  # Final report
    final_grant_proposal: str
    retrieval_retries: int  # Number of retrieval retries
    feedback_on_sections: str  # Feedback on the sections
    start_editing_sections: bool = False  # Whether to edit the sections
    search_iterations: int = 0  # Number of search iterations done


class SectionState(TypedDict):
    section: Section  # Report section
    search_iterations: int  # Number of search iterations done
    search_queries: list[SearchQuery]  # List of search queries
    source_str: str  # String of formatted source content from web search
    feedback_on_sections: str  # Feedback on the sections
    report_sections_from_research: (
        str  # String of any completed sections from research to write final sections
    )
    # Removed commented out completed_sections as it's handled in SectionOutputState


class SectionOutputState(TypedDict):
    completed_sections: list[
        Section
    ]  # Final key we duplicate in outer state for Send() API
