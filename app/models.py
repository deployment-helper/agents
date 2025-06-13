from pydantic import BaseModel, Field
from typing import List

class MCQOption(BaseModel):
    text: str
    isCorrect: bool

class MCQQuestion(BaseModel):
    question: str
    questionDescription: str
    options: List[MCQOption] = Field(..., min_length=2, max_length=6, description="List of 2-6 multiple choice options")
    optionsDescription: str
    correctAnswer: str
    correctAnswerDescription: str
    explanation: str
    explanationDescription: str

class MCQList(BaseModel):
    count: int = Field(..., ge=20, le=30, description="Number of MCQ questions to generate")
    raw: List[MCQQuestion] = Field(..., min_length=20, max_length=30, description="List of 10-30 MCQ questions")
