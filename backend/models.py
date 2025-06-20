from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, field_validator
from langgraph.graph import add_messages
from typing_extensions import Annotated

class InterviewState(BaseModel):
    """State model for the interview evaluation workflow"""
    
    # Input fields
    resume_path: str
    job_description: str
    candidate_response: str
    
    # Output fields - these will be populated by the workflow nodes
    resume_scores: Optional[Union[Dict[str, Any], BaseModel]] = None
    behavioral_patterns: Optional[Union[Dict[str, Any], BaseModel]] = None
    mock_scores: Optional[Union[Dict[str, Any], BaseModel]] = None
    outcome: Optional[Union[Dict[str, Any], BaseModel]] = None
    improvement_plan: Optional[Union[Dict[str, Any], BaseModel]] = None
    
    @field_validator('resume_scores', 'behavioral_patterns', 'mock_scores', 'outcome', 'improvement_plan', mode='before')
    @classmethod
    def convert_models_to_dict(cls, v):
        """Convert Pydantic models to dictionaries"""
        if v is None:
            return v
        if hasattr(v, 'model_dump'):
            return v.model_dump()
        elif hasattr(v, 'dict'):
            return v.dict()
        return v
    
    class Config:
        arbitrary_types_allowed = True
        
    def model_dump(self, **kwargs):
        """Custom model_dump to exclude file paths and only return results"""
        result = super().model_dump(**kwargs)
        # Remove file path for security/privacy
        if 'resume_path' in result:
            del result['resume_path']
        return result