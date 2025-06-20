import json
from typing import List
from pydantic import BaseModel, Field, HttpUrl
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from llm_client import llm  # Gemini/Groq model

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

def generate_improvement_plan(resume_scores: dict, mock_scores: dict, outcome: dict) -> dict:
    input_vars = {
        "resume_scores": json.dumps(resume_scores),
        "mock_scores": json.dumps(mock_scores),
        "outcome_score": outcome["success_score"],
        "outcome_reason": outcome["reason"]
    }

    try:
        result = gap_fixer_chain.invoke(input_vars)
        return result.model_dump()  # ✅ Ensures plain dict with str links
    except Exception as e:
        raise ValueError(f"Failed to parse LLM output: {e}")


