import json
from typing import List
from pydantic import BaseModel, Field, HttpUrl
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from llm_client import llm  # Gemini/Groq model
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import tool
# ---- Step 1: Define Pydantic schema ----

class Suggestion(BaseModel):
    title: str
    description: str

class Resource(BaseModel):
    title: str
    link: HttpUrl

class ImprovementPlan(BaseModel):
    suggestions: List[Suggestion]
    resources: List[Resource]

class ImprovementResponse(BaseModel):
    improvement_plan: ImprovementPlan

# ---- Step 2: Prompt ----

GAP_FIXER_PROMPT = """
You are a career coach AI.

The candidate has these scores:
- Resume: {resume_scores}
- Mock Interview: {mock_scores}
- Outcome Prediction: {outcome_score} - "{outcome_reason}"

Based on this data, suggest:
- 3 actionable improvement suggestions
- 2 personalized learning resources (like courses or websites)

Respond in strict JSON format matching this Pydantic schema:
{format_instructions}
"""

# ---- Step 3: Prepare prompt + parser ----

parser = PydanticOutputParser(pydantic_object=ImprovementResponse)

prompt = PromptTemplate.from_template(GAP_FIXER_PROMPT).partial(
    format_instructions=parser.get_format_instructions()
)

# ---- Step 4: Chain with LLM ----

gap_fixer_chain = prompt | llm | parser

# ---- Step 5: Wrapper function ----
from fastapi.responses import JSONResponse
# Set up Tavily tool (requires TAVILY_API_KEY in env)
search_tool = TavilySearchResults(k=1)

def get_learning_resource_urls(query: str) -> str:
    results = search_tool.invoke({"query": query})
    if isinstance(results, list) and len(results) > 0:
        return results[0]["url"]
    return "https://www.google.com/search?q=" + query.replace(" ", "+")
def generate_improvement_plan(resume_scores: dict, mock_scores: dict, outcome: dict) -> dict:
    input_vars = {
        "resume_scores": json.dumps(resume_scores),
        "mock_scores": json.dumps(mock_scores),
        "outcome_score": outcome["success_score"],
        "outcome_reason": outcome["reason"]
    }

    try:
        result = gap_fixer_chain.invoke(input_vars)
        plan = result.improvement_plan

        # Fetch real URLs for resources using Tavily
        enriched_resources = []
        for r in plan.resources:
            search_url = get_learning_resource_urls(r.title)
            enriched_resources.append(Resource(title=r.title, link=search_url))

        # Replace with enriched resources
        final_response = ImprovementResponse(
            improvement_plan=ImprovementPlan(
                suggestions=plan.suggestions,
                resources=enriched_resources
            )
        )

        return final_response.model_dump()
    except Exception as e:
        raise ValueError(f"Failed to parse or enrich LLM output: {e}")



