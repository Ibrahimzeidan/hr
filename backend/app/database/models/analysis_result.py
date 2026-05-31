from sqlalchemy import Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"), unique=True
    )
    matching_skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    missing_skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    semantic_similarity: Mapped[float] = mapped_column(Float, default=0)
    keyword_score: Mapped[float] = mapped_column(Float, default=0)
    explanation: Mapped[str] = mapped_column(Text, default="")

    # Gemini-enhanced insights fields
    candidate_summary: Mapped[str] = mapped_column(Text, default="")
    hiring_recommendation: Mapped[str] = mapped_column(String(50), default="Consider")
    confidence_score: Mapped[float] = mapped_column(Float, default=0)
    strengths: Mapped[list[str]] = mapped_column(JSON, default=list)
    weaknesses: Mapped[list[str]] = mapped_column(JSON, default=list)
    recommendations: Mapped[list[str]] = mapped_column(JSON, default=list)
    ai_provider: Mapped[str | None] = mapped_column(String(50), default=None)
    ai_model: Mapped[str | None] = mapped_column(String(100), default=None)

    candidate: Mapped["Candidate"] = relationship(back_populates="analysis")

