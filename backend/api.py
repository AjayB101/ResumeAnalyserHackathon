from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os

from pydantic import BaseModel, HttpUrl # Import HttpUrl
from graph.workflow import build_graph
from models import InterviewState
# from pydantic.json import pydantic_encoder # We'll handle this more explicitly or let model_dump do its job
import json # Ensure json is imported

app = FastAPI(title="Interview Evaluation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for security in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global graph instance (compile once, reuse many times)
interview_graph = None

@app.on_event("startup")
async def startup_event():
    """Initialize the graph on startup"""
    global interview_graph
    try:
        interview_graph = build_graph()
        print("Interview evaluation graph initialized successfully")
    except Exception as e:
        print(f"Failed to initialize graph: {e}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Interview Evaluation API is running"}

@app.post("/run-interview-evaluation/")
async def run_pipeline(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    candidate_response: str = Form(...)
):
    """Run the complete interview evaluation pipeline"""
    temp_resume_path = None
    try:
        print(f"Processing request:")
        print(f"- Resume filename: {resume.filename}")
        print(f"- Job description length: {len(job_description)}")
        print(f"- Candidate response length: {len(candidate_response)}")

        # Validate inputs
        if not job_description.strip():
            return JSONResponse(
                content={"error": "Job description cannot be empty"},
                status_code=400
            )

        if not candidate_response.strip():
            return JSONResponse(
                content={"error": "Candidate response cannot be empty"},
                status_code=400
            )

        # Save resume file temporarily
        suffix = ".pdf"  # default
        if resume.filename:
            file_ext = os.path.splitext(resume.filename)[1].lower()
            if file_ext in ['.pdf', '.doc', '.docx', '.txt']:
                suffix = file_ext

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await resume.read()
            tmp.write(content)
            temp_resume_path = tmp.name

        print(f"Resume saved to: {temp_resume_path}")

        # Check if graph is initialized
        if interview_graph is None:
            return JSONResponse(
                content={"error": "Interview evaluation system not initialized"},
                status_code=500
            )

        # Create initial state
        state = InterviewState(
            resume_path=temp_resume_path,
            job_description=job_description,
            candidate_response=candidate_response
        )

        print("Starting interview evaluation workflow...")

        # Run the workflow
        result = interview_graph.invoke(state)

        print("Workflow completed successfully")

        # Convert AddableValuesDict to regular dict and exclude sensitive data
        response_data = dict(result)

        # Remove sensitive data
        if 'resume_path' in response_data:
            del response_data['resume_path']

        # Convert any remaining Pydantic models (including HttpUrl) to dicts/strings
        def recursive_model_dump_and_url_convert(obj):
            if isinstance(obj, BaseModel):
                return obj.model_dump(mode="json") # mode="json" handles HttpUrl automatically
            elif isinstance(obj, HttpUrl): # Explicitly convert HttpUrl to string
                return str(obj)
            elif isinstance(obj, dict):
                return {k: recursive_model_dump_and_url_convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [recursive_model_dump_and_url_convert(i) for i in obj]
            else:
                return obj

        response_json = recursive_model_dump_and_url_convert(response_data)
        return JSONResponse(content=response_json)

    except Exception as e:
        print(f"Error in pipeline: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"error": f"Internal server error: {str(e)}"},
            status_code=500
        )

    finally:
        # Clean up temporary file
        if temp_resume_path and os.path.exists(temp_resume_path):
            try:
                os.unlink(temp_resume_path)
                print(f"Cleaned up temporary file: {temp_resume_path}")
            except Exception as e:
                print(f"Failed to clean up temporary file: {e}")

# Keep your existing endpoints for individual components
@app.post("/analyze-resume/")
async def analyze_resume_endpoint(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """Individual resume analysis endpoint"""
    try:
        from agents.resume_analyzer import analyze_resume

        # Save uploaded file to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume.filename.split('.')[-1]}") as tmp:
            tmp.write(await resume.read())
            tmp_path = tmp.name

        result = analyze_resume(file_path=tmp_path, job_description=job_description)

        # Clean up
        os.unlink(tmp_path)

        # Ensure the result is properly serialized, especially if it contains Pydantic models
        if isinstance(result, BaseModel):
            return JSONResponse(content=result.model_dump(mode="json"))
        else:
            return JSONResponse(content=result)

    except Exception as e:
        print(f"Error in resume analysis: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/get-behavioral-patterns")
async def behavioral_patterns_endpoint(request: Request):
    """Individual behavioral patterns endpoint"""
    try:
        from agents.behavioral_retriever import get_behavioral_patterns

        body = await request.json()
        job_description = body.get("job_description")
        if not job_description:
            return JSONResponse(
                content={"error": "Missing job_description"},
                status_code=400
            )

        result = get_behavioral_patterns(job_description)
        # Ensure the result is properly serialized if it's a Pydantic model
        if isinstance(result, BaseModel):
            return JSONResponse(content=result.model_dump(mode="json"))
        else:
            return JSONResponse(content=result)

    except Exception as e:
        print(f"Error in behavioral patterns: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)