from pydantic import BaseModel
from typing import List

class MCQOption(BaseModel):
    text: str
    isCorrect: bool

class MCQQuestion(BaseModel):
    question: str
    questionDescription: str
    options: List[MCQOption]
    optionsDescription: str
    correctAnswer: str
    correctAnswerDescription: str
    explanation: str
    explanationDescription: str

class MCQList(BaseModel):
    raw: List[MCQQuestion]
