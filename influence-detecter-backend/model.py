# models.py
from pydantic import BaseModel
from typing import List, Optional


class ChatInput(BaseModel):
    chat: str


class MessageAnalysis(BaseModel):
    speaker: str
    text: str
    label: str
    confidence: float
    explanation: Optional[str]


class ChatOutput(BaseModel):
    messages: List[MessageAnalysis]
    influence_score: float
