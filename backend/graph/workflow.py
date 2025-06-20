# graph/workflow.py
from langgraph.graph import StateGraph, END
from models import InterviewState
from graph.nodes import (
    resume_analysis_node,
    behavioral_analysis_node,
    mock_evaluation_node,
    outcome_prediction_node,
    improvement_planning_node
)

def build_graph():
    """Build and compile the interview evaluation workflow graph"""
    try:
        graph = StateGraph(InterviewState)
        
        # Add nodes with unique names (not conflicting with state attributes)
        graph.add_node("resume_analysis", resume_analysis_node)
        graph.add_node("behavioral_analysis", behavioral_analysis_node)
        graph.add_node("mock_evaluation", mock_evaluation_node)
        graph.add_node("outcome_prediction", outcome_prediction_node)
        graph.add_node("improvement_planning", improvement_planning_node)
        
        # Set entry point
        graph.set_entry_point("resume_analysis")
        
        # Add edges to define the workflow
        graph.add_edge("resume_analysis", "behavioral_analysis")
        graph.add_edge("behavioral_analysis", "mock_evaluation")
        graph.add_edge("mock_evaluation", "outcome_prediction")
        graph.add_edge("outcome_prediction", "improvement_planning")
        graph.add_edge("improvement_planning", END)
        
        return graph.compile()
    
    except Exception as e:
        print(f"Error building graph: {e}")
        raise e