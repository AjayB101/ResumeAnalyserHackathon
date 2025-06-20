# 🧠 Interview Outcome Predictor & Booster

A modular, agent-powered AI system that analyzes a candidate’s resume, evaluates mock interview responses, predicts interview success, and recommends personalized improvement suggestions with learning resources.

---

## 🚀 Features

- 📄 **Resume Analysis**: Scores resume on clarity, relevance, structure, and experience.
- 💬 **Behavioral Patterns Generator**: Provides job-specific behavioral questions with sample answers.
- 🎤 **Mock Interview Evaluator**: Evaluates candidate response on tone, relevance, and confidence.
- 📈 **Outcome Predictor**: Predicts interview success score based on combined metrics.
- 🧭 **Improvement Planner**: Suggests actionable improvements and curated learning resources.
- 🌐 **FastAPI Backend**: Robust API endpoints for full and individual pipeline steps.
- 🔗 **LangChain + LangGraph**: Modular agent graph for clean, explainable pipeline flow.

---

## 🛠️ Tech Stack

| Layer          | Tools & Libraries                                   |
| -------------- | --------------------------------------------------- |
| Language Model | [Groq LLaMA-3](https://groq.com), Gemini (optional) |
| LangChain      | `langchain`, `langgraph`, `langchain_groq`          |
| Backend        | `FastAPI`, `pydantic`, `pdfplumber`, `docx2txt`     |
| LLM Evaluation | Prompt engineering + structured JSON parsing        |
| Deployment     | Run locally or via containerized API                |

---

## 📦 Folder Structure

📦 Project Root
├── 🧩 frontend/ # UI (Streamlit or React)
│
├── 🛠️ backend/ # Core backend logic
│ ├── 🤖 agents/ # Modular AI agents
│ │ ├── resume_analyzer.py # Analyze resume strength
│ │ ├── behavioral_retriever.py # RAG-based behavioral Q&A retriever
│ │ ├── mock_evaluator.py # Evaluate mock interview answers
│ │ ├── outcome_predictor.py # Predict interview outcome
│ │ └── gap_fixer.py # Recommend improvements
│ │
│ ├── orchestrator.py # LangGraph orchestration of agents
│ ├── api.py # FastAPI endpoints
│ ├── prompts/ # Prompt templates used by agents
│ ├── database/ # DB models and setup scripts
│ └── tests/ # Unit & integration tests
| | requirements.txt
│
└── .env # Environment variables (excluded from git)

Project architecture

                                 +------------------------+
                                 |      Frontend (UI)     |
                                 |------------------------|
                                 | - Upload Resume (PDF)  |
                                 | - Enter Job Description|
                                 | - Record/Type Responses|
                                 | - Show Results & Plan  |
                                 +------------------------+
                                            |
                                            v
                        ┌──────────────────────────────────────┐
                        │       FastAPI Backend Server         │
                        └──────────────────────────────────────┘
                          |       |        |       |         |
        ┌─────────────────┘       |        |       |         └────────────┐
        v                         v        v       v                      v

+----------------+ +-------------------------+ +-----------------+ +-------------------+
| Resume Analyzer| | Behavioral Retriever | | Mock Evaluator | | Gap Fixer Agent |
| Agent (LLM) | | Agent (RAG + LLM) | | Agent (LLM/STT) | | Agent (LLM) |
+----------------+ +-------------------------+ +-----------------+ +-------------------+
| | | |
v v v v
+----------------+ +-----------------------+ +-----------------+ +-------------------------+
| Resume Scores | | Behavioral Q&A Vector | | Response Scores | | Personalized Suggestions |
| (clarity, etc) | | from ChromaDB | | (tone, etc) | | + Learning Resources |
+----------------+ +-----------------------+ +-----------------+ +-------------------------+
|
v
+-----------------------------+
| ChromaDB Vector Store |
| (Behavioral Q&A Dataset) |
+-----------------------------+

                                 |
                                 v
                      +------------------------------+
                      | Outcome Predictor Agent (LLM)|
                      +------------------------------+
                                 |
                                 v
                      +-----------------------------+
                      | Success Likelihood (Score)  |
                      +-----------------------------+

                                 |
                                 v
                      +-----------------------------+
                      |      |
                      | Stores all results & plans  |
                      +-----------------------------+

                                 |
                                 v
                      +-----------------------------+
                      | Frontend Dashboard Displays |
                      | Resume Score, Predictions,  |
                      | Improvement Plan, History   |
                      +-----------------------------+

For a live, interactive version of the architecture diagram, you can access it here:
[View Interactive Architecture Diagram](https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=architecture.drawio.png&dark=auto#R%3Cmxfile%3E%3Cdiagram%20name%3D%22Interview%20System%20Architecture%22%20id%3D%22uCbzH1xQIn7Y3R4AgFk3%22%3E7Zrdc5s4EMD%2FGmbuHjwDiM9H24Fc0%2BScq3vt9V48CshAA4iR5a%2F%2B9SeBsA3GDr1A4s74JZFXK5B%2Bu1qtJCQwTja3BGbhA%2FZRLKmyv5HAjaSqtimzv1ywLQSGqhWCgER%2BIVL2gmn0AwmhaBcsIx8tKooU45hGWVXo4TRFHq3IICF4XVWb47j61gwG6Egw9WB8LP0a%2BTQspJZq7uV%2FoCgIyzcrhl3UJLBUFiNZhNDH6wMRcCQwJhjTopRsxijm7EouRTv3RO2uYwSltE2D8fbh08eBO%2F12N5llRnbz%2BRv4ZyCesoLxUgxYcmXJdqWhKdmsUv57gYjEn%2Byyvy7BKUWpLwZEtyUlgpepj%2FiLFAmM1mFE0TSDHq9dM7dgspAmsag%2B7njZC0Qo2hyIxEBuEU4QJVumImo1WUAVXlUyXu9NpBhCFh6Yp5RB4RXB7sl7cKwg2P0ER%2FUURxtIQ87RhQs6fPzASiPoPecMDUkFzM3B6LfHyfRzAZks00HEGJNVhNYDxJ8HaYTT398dOQBV5Ip8zBzIDczNvpiDI%2Bb3MA3yMMTEXzF5nsdswh1wnlJIUaEAhkznQ0k6r3gl43kUx2McY5K3BY7i6q7TE3v7vdlrZ%2FzdYpXyJ7RYJogVhgEf994IMIXx9geaEaHQIXLXdW8csxvkai3AWO8dYfSTkVqTbIPHFRTCVYQJjHP8lERoxWP3jnyA6OxppzTLIGXeny669XrL1R27IxMYLWxgvaUNjFM2sBxuBlV%2BwN4z%2B%2BcUcRuTBv8XMR3NEqbLZ0GG00XH8wA4uqt3YwSjboSG0PO2RjDPhR4e1SdL6uE89jwS5Edesx2yom6GS%2B0uZ4Hsmu6wn1kAjGMDsHzoDQ1gnYxEpjRkL5VvGR6W8UQbkToaMMlyGHxVwEviobzIsCcsEarFqBQRPjuiJCN4hZgCnWUxTDteKJyR09HavGMv7KNpDfZpmiC9rc32mQmSR6m76eTP3EBpvlaw%2BZItabeAFdfqahkAtVxfBy2XYr0vwOXe9AAW8%2BMh322yX08xXwTODF1MgRc3ZRQStmS%2FvOlAfmULewySoJhtIlbVHW33VJR%2BqagtqYDLoqL2SwW0pKJ1TUU0fcQRX1bLyarU04X6KlR0VLSqsd114xW4wWXg1i%2FLCbXLoGJcFhW9Xyp6SyrmZVEx%2BqVi%2FJpUzH6paL8mFatfKmZLKtZlUbH7pWK1pGJfFJXyQO1wW7Lf9%2BX7RLlBcFbcovL%2FqHTzwO4Vr128dvHaxWsXr13suYtXld5t0XahPxDUciqKNrTfm%2B%2FK7ap0dL5ol1chr8mVvO9yqHuTL1vlL%2Bsu%2FaL%2Bq99%2FHDRs11kSNxU%2FMaEhDnAKY2cvHe2Pazmtvc49xplg8R1RuhWf2MAlxU2katniixlqY%2F%2FBKxPN5rMlrTzQLW9ClBr%2F7s6WTo%2BqksCOQ4ITyGT%2BE%2FPUmLvjE7%2FNCHhpnl87iQvXJS%2F7kMJjy8ZxlC3Qy54MF1nxgdM82nA7j074cYPJTn9HY1WR7i4lDly%2F6e7C%2BnnP5x%2B37L51Kkyy%2F2AMOP8B%3C%2Fdiagram%3E%3C%2Fmxfile%3E)

---

## 📌 Setup Instructions

Follow these steps to get the backend API server up and running:

1.  **Clone the Repository**

    ```bash
    git clone [https://github.com/your-org/interview-booster.git](https://github.com/your-org/interview-booster.git)
    cd interview-booster/backend
    ```

2.  **Create and Activate Virtual Environment**

    ```bash
    python -m venv venv
    # On macOS/Linux:
    source venv/bin/activate
    # On Windows:
    # venv\Scripts\activate
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a `.env` file in the `backend/` directory and populate it with your API keys:

    ```ini
    # .env
    GROQ_API_KEY=your_groq_api_key_here
    TAVILY_API_KEY=your_tavily_api_key_here
    HUGGINGFACEHUB_API_TOKEN=your_huggingface_api_token_here
    GOOGLE_API_KEY=your_google_api_key_here
    ```

    - **GROQ_API_KEY**: Get from [Groq Console](https://console.groq.com/keys)
    - **TAVILY_API_KEY**: Get from [Tavily API](https://tavily.com/dashboard/settings)
    - **HUGGINGFACEHUB_API_TOKEN**: Optional, for HuggingFace embeddings fallback. Get from [Hugging Face](https://huggingface.co/settings/tokens)
    - **GOOGLE_API_KEY**: Optional, for Google Generative AI embeddings. Get from [Google AI Studio](https://aistudio.google.com/app/apikey)

5.  **Run the FastAPI Server**
    ```bash
    uvicorn api:app --reload
    ```
    The API will be accessible typically at `http://127.0.0.1:8000`. You can test the endpoints using tools like Postman, Insomnia, or directly through your browser at `http://127.0.0.1:8000/docs` for the Swagger UI.

---

## 💡 Example JSON Output

This is an example of the comprehensive JSON output you would receive from the system after a full evaluation cycle:

```json
{
  "resume_scores": {
    "clarity": 85,
    "relevance": 78,
    "structure": 90,
    "experience": 2,
    "feedback": ["Quantify project outcomes", "Align skills to job"]
  },
  "mock_scores": {
    "tone": 72,
    "confidence": 64,
    "relevance": 75,
    "feedback": ["Be more concise", "Highlight results"]
  },
  "outcome": {
    "success_score": 69,
    "reason": "Good structure and tone, but lacks confident delivery and alignment."
  },
  "improvement_plan": {
    "suggestions": [
      {
        "title": "Improve confidence",
        "description": "Practice speaking clearly in mock interviews"
      },
      {
        "title": "Reframe achievements",
        "description": "Use STAR format to explain past work"
      }
    ],
    "resources": [
      {
        "title": "Mock Interview Practice",
        "link": "[https://interviewing.io/](https://interviewing.io/)"
      },
      {
        "title": "Resume Alignment Tips",
        "link": "[https://careersidekick.com/](https://careersidekick.com/)"
      }
    ]
  }
}
```
