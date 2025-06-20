import os
import json
import pdfplumber
import docx2txt
from typing import List
from pydantic import BaseModel
from llm_client import llm
from langchain_core.prompts import PromptTemplate

from interiew_prompts.prompts import InterviewPrompts

# ----------------------------
# Output Schema
# ----------------------------

class ResumeScore(BaseModel):
    clarity: int
    relevance: int
    structure: int
    experience: int
    feedback: List[str]
    

# ----------------------------
# Resume Extraction
# ----------------------------

def extract_resume_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    elif ext == ".docx":
        return docx2txt.process(file_path)
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX are allowed.")

# ----------------------------
# LLM Chain Setup
# ----------------------------


prompt = PromptTemplate.from_template(InterviewPrompts.resume_analyzer)
chain = prompt | llm

# ----------------------------
# Resume Analyzer Agent
# ----------------------------

def analyze_resume(file_path: str, job_description: str) -> ResumeScore:
    resume_text = extract_resume_text(file_path)

    result = chain.invoke({
        "resume_text": resume_text,
        "job_description": job_description
    }).content

    try:
        parsed = ResumeScore(**json.loads(result))
        return parsed
    except Exception as e:
        raise ValueError(f"Failed to parse output: {e}\nRaw output:\n{result}")
