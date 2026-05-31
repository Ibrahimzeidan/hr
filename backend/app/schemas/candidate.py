from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class SkillOut(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class AnalysisResultOut(BaseModel):
    matching_skills: list[str]
    missing_skills: list[str]
    semantic_similarity: float
    keyword_score: float
    explanation: str
    # Gemini-enhanced insights
    candidate_summary: str = ""
    hiring_recommendation: str = "Consider"
    confidence_score: float = 0
    strengths: list[str] = []
    weaknesses: list[str] = []
    recommendations: list[str] = []
    ai_provider: str | None = None
    ai_model: str | None = None
    model_config = ConfigDict(from_attributes=True)


class CandidateOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr | None
    phone: str | None
    resume_url: str
    score: float
    rank: int | None
    created_at: datetime
    skills: list[str] = []
    analysis: AnalysisResultOut | None = None
    model_config = ConfigDict(from_attributes=True)


class CandidateList(BaseModel):
    items: list[CandidateOut]
    total: int
    page: int
    limit: int

