

# 📄 File: backend/agents/mock_interview_evaluator.py

import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from llm_client import llm  # your configured Groq or Gemini model

# Prompt Template
EVALUATION_PROMPT = """
Evaluate the following mock interview response.
Your output MUST be a valid JSON object.

Question: {question}
Candidate Response: {response}

Evaluate on the following criteria:
1. **Tone**: Is it confident, enthusiastic, and professional?
2. **Confidence**: Does the candidate seem sure of their experience and delivery?
3. **Relevance**: Is the response aligned with the question?

Return your answer in JSON format with the following keys:
- question
- response
- tone (score out of 100)
- confidence (score out of 100)
- relevance (score out of 100)
- feedback (list of 2-3 actionable tips to improve)

No preamble. No conversational text. Just the JSON.
"""

# LangChain setup
evaluation_template = PromptTemplate.from_template(EVALUATION_PROMPT)
evaluation_chain = LLMChain(llm=llm, prompt=evaluation_template)

def evaluate_mock_response(question: str, response: str) -> dict:
    raw = evaluation_chain.run({
        "question": question,
        "response": response
    })
    try:
        # Strip whitespace and potential hidden characters before parsing
        return json.loads(raw.strip())
    except json.JSONDecodeError as e:
        # Provide more specific error for JSON parsing issues
        raise ValueError(f"Failed to parse LLM output as JSON: {e}\nRaw output: '{raw}'")
    except Exception as e:
        # Catch any other unexpected errors
        raise ValueError(f"An unexpected error occurred during LLM output parsing: {e}\nRaw output: '{raw}'")