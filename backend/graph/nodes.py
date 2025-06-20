from models import InterviewState
from agents.resume_analyzer import analyze_resume
from agents.behavioral_retriever import get_behavioral_patterns
from agents.mock_evaluator import evaluate_mock_response
from agents.outcome_predictor import predict_outcome
from agents.gap_fixer import generate_improvement_plan

# graph/nodes.py
def resume_analysis_node(state: InterviewState) -> InterviewState:
    """Analyze resume and update state"""
    try:
        resume_result = analyze_resume(state.resume_path, state.job_description)
        
        # Convert ResumeScore model to dictionary
        if hasattr(resume_result, 'model_dump'):
            state.resume_scores = resume_result.model_dump()
        elif hasattr(resume_result, 'dict'):
            state.resume_scores = resume_result.dict()
        else:
            # Fallback: assume it's already a dict or convert manually
            state.resume_scores = dict(resume_result) if hasattr(resume_result, '__dict__') else resume_result
            
        print(f"Resume analysis completed: {state.resume_scores}")
    except Exception as e:
        print(f"Error in resume analysis: {e}")
        # Set default scores if analysis fails
        state.resume_scores = {
            "clarity": 50,
            "relevance": 50,
            "structure": 50,
            "experience": 1,
            "feedback": ["Resume analysis failed - please check the file format"]
        }
    return state

def behavioral_analysis_node(state: InterviewState) -> InterviewState:
    """Generate behavioral patterns and update state"""
    try:
        state.behavioral_patterns = get_behavioral_patterns(state.job_description)
        print(f"Behavioral analysis completed: Found {len(state.behavioral_patterns.get('questions', []))} questions")
    except Exception as e:
        print(f"Error in behavioral analysis: {e}")
        # Set default behavioral patterns if analysis fails
        state.behavioral_patterns = {
            "questions": [
                {
                    "question": "Tell me about yourself and your experience.",
                    "sample_answer": "I am a professional with experience in various projects and roles that have helped me develop strong problem-solving and communication skills.",
                    "source": "default"
                }
            ]
        }
    return state

def mock_evaluation_node(state: InterviewState) -> InterviewState:
    """Evaluate mock interview response and update state"""
    try:
        # Extract question from behavioral patterns
        question = "Tell me about yourself."
        if state.behavioral_patterns and "questions" in state.behavioral_patterns:
            questions = state.behavioral_patterns["questions"]
            if questions and len(questions) > 0:
                if isinstance(questions[0], dict) and "question" in questions[0]:
                    question = questions[0]["question"]
                elif isinstance(questions[0], str):
                    question = questions[0]
        
        state.mock_scores = evaluate_mock_response(question, state.candidate_response)
        print(f"Mock evaluation completed: {state.mock_scores}")
    except Exception as e:
        print(f"Error in mock evaluation: {e}")
        # Set default scores if evaluation fails
        state.mock_scores = {
            "question": "Tell me about yourself.",
            "response": state.candidate_response,
            "tone": 60,
            "relevance": 60,
            "confidence": 60,
            "feedback": ["Mock evaluation failed - using default scores"]
        }
    return state

def outcome_prediction_node(state: InterviewState) -> InterviewState:
    """Predict interview outcome and update state"""
    try:
        state.outcome = predict_outcome(
            resume_scores=state.resume_scores,
            mock_scores=state.mock_scores,
            behavior_score=60  # Optional: can be dynamic later
        )
        print(f"Outcome prediction completed: {state.outcome}")
    except Exception as e:
        print(f"Error in outcome prediction: {e}")
        # Set default outcome if prediction fails
        state.outcome = {
            "success_score": 65,
            "reason": "Analysis completed with mixed results. Focus on improving specific areas identified in feedback."
        }
    return state

def improvement_planning_node(state: InterviewState) -> InterviewState:
    """Generate improvement plan and update state"""
    try:
        state.improvement_plan = generate_improvement_plan(
            resume_scores=state.resume_scores,
            mock_scores=state.mock_scores,
            outcome=state.outcome
        )
        print(f"Improvement planning completed: {state.improvement_plan}")
    except Exception as e:
        print(f"Error in improvement planning: {e}")
        # Set default improvement plan if generation fails
        state.improvement_plan = {
            "priority_areas": ["Resume formatting", "Interview preparation"],
            "action_items": [
                "Review and update resume format",
                "Practice behavioral interview questions",
                "Research the company and role"
            ],
            "timeline": "2-3 weeks"
        }
    return state