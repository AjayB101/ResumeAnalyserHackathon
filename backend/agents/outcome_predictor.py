# 📄 File: backend/agents/predict_outcome.py

import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from llm_client import llm  # Your Gemini or Groq LLM

PREDICTOR_PROMPT = """
You are an AI interview coach.

Based on the candidate's scores:
- Resume average score: {resume_avg}
- Mock interview average: {mock_avg}
- Behavioral match score: {behavior_score}

Generate a one-sentence reason justifying a success prediction score (0–100). Focus on strengths and areas for improvement.

No preamble. Output only the justification sentence.
"""

template = PromptTemplate.from_template(PREDICTOR_PROMPT)
predictor_chain = LLMChain(llm=llm, prompt=template)

def predict_outcome(resume_scores: dict, mock_scores: dict, behavior_score: int) -> dict:
    # Safely compute averages
    def safe_avg(score_dict):
        values = [v for v in score_dict.values() if isinstance(v, (int, float))]
        return sum(values) / len(values) if values else 0

    resume_avg = safe_avg(resume_scores)
    mock_avg = safe_avg(mock_scores)

    final_score = round(0.4 * resume_avg + 0.4 * mock_avg + 0.2 * behavior_score)

    justification = predictor_chain.run({
        "resume_avg": resume_avg,
        "mock_avg": mock_avg,
        "behavior_score": behavior_score
    })

    return {
        "success_score": final_score,
        "reason": justification.strip()
    }
