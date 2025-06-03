import os
from enum import Enum
from dataclasses import dataclass, fields
from typing import Any, Optional
from typing import List

from langchain_core.runnables import RunnableConfig
from dataclasses import dataclass

DEFAULT_GRANT_PROPOSAL_STRUCTURE = """
# **Grant Proposal Template**

## **1. Cover Page**

### **Project Title:**  
Clear, concise, and reflective of the project's core purpose. Consider using keywords relevant to the funding agency's priorities.

### **Applicant Information:**  
- **Organization Name:** Legal name of the applying organization.  
- **Address:** Official mailing address.  
- **Contact Person:** Name, title, phone number, and email address of the primary contact for the proposal.  
- **Organizational EIN/Tax ID:** For non-profits.  
- **Website:** If applicable.  

### **Funding Agency & Grant Program:**  
- **Name of Funding Agency:** E.g., National Endowment for the Arts, Department of Education.  
- **Grant Program Name:** Specific program the proposal is being submitted to (e.g., "Our Town" grant).  
- **Program Announcement Number/RFA (Request for Applications):** If applicable.  

### **Date of Submission & Project Period:**  
- **Submission Date:** The date the proposal is officially submitted.  
- **Project Start and End Dates:** Proposed dates for the project's duration.  

---

## **2. Executive Summary (1 Page)**

### **Introduction & Mission:**  
- A brief overview of the organization's mission and history.  
- Highlight the organization's relevant expertise and experience.  

### **Project Summary & Need:**  
- Concise description of the project, its goals, and target population.  
- Clearly articulate the problem or need the project addresses.  
- Emphasize the urgency and significance of the issue.  

### **Funding Request & Expected Outcomes:**  
- State the specific amount of funding requested.  
- Summarize the key expected outcomes and impact of the project.  
- Explain how the project aligns with the funding agency's mission.  

---

## **3. Statement of Need**

### **Problem Definition & Urgency:**  
- Provide a detailed description of the problem being addressed.  
- Cite relevant data, statistics, and research to support the problem statement.  
- Clearly demonstrate the urgency and consequences of not addressing the problem.  
- Consider including personal stories or anecdotes to illustrate the problem's impact.  

### **Target Population & Supporting Data:**  
- Identify the specific population that will benefit from the project.  
- Provide demographic data and characteristics of the target population.  
- Present evidence that demonstrates the need within the target population.  
- Include community needs assessments, surveys, or other relevant data sources.  

### **Gaps in Existing Services:**  
- Explain why existing services are insufficient to address the identified problem.  
- Identify any gaps in service delivery or accessibility.  
- Show how the proposed project will fill those gaps.  

---

## **4. Project Description & Implementation Plan**

### **Project Goals & SMART Objectives:**  
- **Goals:** Broad statements of what the project aims to achieve.  
- **SMART Objectives:** Specific, Measurable, Achievable, Relevant, and Time-bound objectives that outline how the project will achieve its goals. Provide quantitative targets whenever possible.  

**Example:** "Increase the number of students participating in the after-school program by 20% within the first year."

### **Scope of Work & Timeline:**  
- Detailed description of the project activities and tasks.  
- Clear and logical sequence of project activities.  
- Realistic timeline with start and end dates for each activity. Consider using a Gantt chart or similar visual representation.  
- Identify key milestones and deliverables.  

### **Partnerships & Geographic Scope:**  
- Identify key partners and their roles in the project.  
- Explain the benefits of the partnerships and how they will contribute to the project's success.  
- Define the geographic area served by the project.  
- If applicable, explain how the project will address specific needs within that geographic area.  

### **Project Evaluation Plan:**  
- Describe how the project's progress and outcomes will be evaluated.  
- Identify the data collection methods that will be used.  
- Explain how the data will be analyzed and used to improve the project.  
- Specify who will be responsible for conducting the evaluation.  

---

## **5. Budget & Justification**

### **Total Cost & Breakdown:**  
- Provide a detailed budget that includes all project expenses.  
- Categorize expenses into clear and logical categories (e.g., personnel, supplies, travel, equipment).  
- Ensure that all expenses are reasonable and necessary for the project.  

### **Matching Funds/In-Kind Contributions:**  
- If required or applicable, describe any matching funds or in-kind contributions that will support the project.  
- Quantify the value of in-kind contributions (e.g., volunteer time, donated space).  
- Provide documentation to support the matching funds or in-kind contributions.  

### **Budget Narrative:**  
- Provide a detailed justification for each line item in the budget.  
- Explain how each expense will contribute to the project's success.  
- Clearly demonstrate that the budget is realistic and cost-effective.  
- Justify personnel costs with roles and responsibilities.  

---

## **6. Sustainability & Impact Measurement**

### **Long-Term Viability & Future Funding:**  
- Explain how the project will be sustained beyond the grant period.  
- Identify potential sources of future funding.  
- Describe the organization's plan for securing those funds.  
- Discuss how the project's activities will be integrated into the organization's ongoing operations.  

### **Key Performance Indicators (KPIs):**  
- Identify the key metrics that will be used to measure the project's impact.  
- Provide a baseline for each KPI, if available.  
- Set targets for each KPI that will be achieved by the end of the project.  
- Explain how the KPIs will be tracked and reported.  

### **Community & Stakeholder Engagement:**  
- Describe how the community and stakeholders will be involved in the project.  
- Explain how their feedback will be incorporated into the project's design and implementation.  
- Discuss how the project will benefit the community and stakeholders.  

### **Dissemination Plan:**  
- Explain how the project's findings and successes will be shared with the broader community and field.  
- Describe the methods for disseminating information (e.g., reports, presentations, publications).  

---

## **7. Appendices**

### **Key Personnel & Organizational Experience:**  
- Resumes or CVs of key personnel involved in the project.  
- Information on the organization's experience and capacity to carry out the project.  
- Organizational chart, if applicable.  

### **Letters of Support & Relevant Documents:**  
- Letters of support from partners, stakeholders, and community members.  
- Memoranda of Understanding (MOUs) with partner organizations.  
- Needs assessment reports.  
- Evaluation reports from previous projects.  
- Relevant data or statistics that support the project's need and impact.  

### **Evaluation Tools:**  
- Copies of surveys, interview questions, or other evaluation instruments.  
"""


ABOUT_THE_CLIENT = """
**Earth Mission** is a nonprofit organization dedicated to improving healthcare access in remote Karen areas, primarily in Myanmar. Its mission is to **train healthcare teams to empower local communities with health, hope, and knowledge**.

### Key Programs and Activities:
- **Physician Associate Program** – A 5-year program that trains Karen youth in essential medical and surgical skills, ensuring they provide healthcare in their home communities.
- **Engineering Technology Program** – A 3-year program teaching students critical skills in construction, electricity, and logistics to sustain healthcare infrastructure.
- **Surgical Training Program** – A postgraduate initiative that equips graduates with essential surgical skills to address the lack of trained surgeons.
- **Hospital & Campus Program** – Facilities like Rain Tree Clinic provide vital medical services, including emergency care, maternity care, and mobile surgical units.
- **Faith and Community Support** – Earth Mission integrates Christian values, offers educational opportunities, and fosters community resilience.

### Current Challenges & Strategic Focus:
- **Impact of Conflict** – Myanmar's ongoing conflict has made operations challenging, affecting access to medical care and resources.
- **Infrastructure & Sustainability** – The organization aims to develop **local leadership, self-sustaining income sources, and better infrastructure** to ensure long-term impact.
- **Expansion Goals** – By 2030, Earth Mission plans to train more medical professionals, improve healthcare accessibility, and establish self-sufficient local leadership.
"""


class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"


class PlannerProvider(Enum):
    OPENAI = "openai"
    GROQ = "groq"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"

class WriterProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"

class ScraperProvider(Enum):
    FIRECREW = "firecrew"


@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the grant ."""

    grant_proposal_structure: str = DEFAULT_GRANT_PROPOSAL_STRUCTURE
    search_api: SearchAPI = SearchAPI.TAVILY
    scraper_provider: ScraperProvider = ScraperProvider.FIRECREW
    planner_provider: PlannerProvider = PlannerProvider.OPENAI
    writer_provider: WriterProvider = WriterProvider.OPENAI
    
    number_of_queries: int = 10  # Number of search queries to generate per iteration
    max_search_depth: int = 2 # Maximum number of reflection + search iterations
    max_web_results: int = 10  # Maximum number of web results to return
    max_vector_results: int = 5  # Maximum number of vector results to return
    
    planner_model: str = "gpt-4o-mini"  # Defaults to OpenAI o3-mini as planner model
    writer_model: str = "gpt-4o-mini"  # Defaults to Anthropic as provider
    
    user_name: str = "James"  # Default to James
    user_id: str = "67af22c37095e8f74f3e586e"
    client_name: str = "Earth Mission"  # Default to Earth Mission
    client_id: str = "67af388e38b807fc0a2a7f75"
    about_client: str = ABOUT_THE_CLIENT
    context_document_ids: Optional[List[str]] = None

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})
