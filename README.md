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

cd backend
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

uvicorn api:app --reload

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
