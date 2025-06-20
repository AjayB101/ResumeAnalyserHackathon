from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tempfile import NamedTemporaryFile
from agents.resume_analyzer import analyze_resume
from agents.behavioral_retriever import get_behavioral_patterns
from agents.mock_evaluator import evaluate_mock_response

app = FastAPI()

# CORS for React (adjust origin if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or your deployed frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze-resume/")
async def analyze_resume_endpoint(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    try:
        # Save uploaded file to a temp file
        with NamedTemporaryFile(delete=False, suffix=f".{resume.filename.split('.')[-1]}") as tmp:
            tmp.write(await resume.read())
            tmp_path = tmp.name

        result = analyze_resume(file_path=tmp_path, job_description=job_description)
        return JSONResponse(content=result.model_dump())

    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/get-behavioral-patterns")
async def behavioral_patterns_endpoint(request: Request):
    try:
        body = await request.json()
        job_description = body.get("job_description")
        if not job_description:
            return JSONResponse(content={"error": "Missing job_description"}, status_code=400)

        result = get_behavioral_patterns(job_description)
        return JSONResponse(content=result)

    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/evaluate-response/")
async def evaluate_response_endpoint(request: Request):
    try:
        body = await request.json()
        question = body.get("question")
        response = body.get("response")

        if not question or not response:
            return JSONResponse(content={"error": "Missing question or response"}, status_code=400)

        result = evaluate_mock_response(question=question, response=response)
        return JSONResponse(content=result)

    except Exception as e:
        print("Mock Evaluator Error:", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)