from pydantic import BaseModel
from typing import List

class AnswerResponse(BaseModel):
    """Pydantic model for the API response"""
    answer: str
    sources: List[str]
    confidence: float