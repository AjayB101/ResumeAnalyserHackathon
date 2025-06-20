# Gap Fixer module
import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from llm_client import llm  # your configured Gemini or Groq model

GAP_FIXER_PROMPT = """
You are a career coach AI.

The candidate has these scores:
- Resume: {resume_scores}
- Mock Interview: {mock_scores}
- Outcome Prediction: {outcome_score} - "{outcome_reason}"

Based on this data, suggest:
- 3 actionable improvement suggestions
- 2 personalized learning resources (like courses or websites)

Respond in JSON with two keys:
- "suggestions": [list of 3 tips]
- "resources": [list of 2 links or course names]

No preamble.
"""

template = PromptTemplate.from_template(GAP_FIXER_PROMPT)
gap_fixer_chain = LLMChain(llm=llm, prompt=template)

def generate_improvement_plan(resume_scores: dict, mock_scores: dict, outcome: dict) -> dict:
    input_vars = {
        "resume_scores": json.dumps(resume_scores),
        "mock_scores": json.dumps(mock_scores),
        "outcome_score": outcome["success_score"],
        "outcome_reason": outcome["reason"]
    }

    raw = gap_fixer_chain.run(input_vars)

    try:
        return json.loads(raw)
    except Exception as e:
        raise ValueError(f"Failed to parse LLM output: {e}\nRaw output: {raw}")
