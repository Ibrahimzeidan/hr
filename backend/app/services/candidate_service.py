from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database.models import Candidate, CandidateSkill, JobDescription, Skill
from app.utils.serializers import candidate_to_out


def get_or_create_skill(db: Session, name: str) -> Skill:
    clean = name.strip().lower()
    skill = db.query(Skill).filter(func.lower(Skill.name) == clean).first()
    if skill:
        return skill
    skill = Skill(name=name.strip())
    db.add(skill)
    db.flush()
    return skill


def create_candidate(db: Session, profile: dict, resume_url: str, text: str) -> Candidate:
    candidate = Candidate(
        full_name=profile.get("full_name") or "Unknown Candidate",
        email=profile.get("email"),
        phone=profile.get("phone"),
        resume_url=resume_url,
        extracted_text=text,
    )
    db.add(candidate)
    db.flush()
    for skill_name in profile.get("skills", []):
        candidate.skills.append(CandidateSkill(skill=get_or_create_skill(db, skill_name)))
    db.commit()
    db.refresh(candidate)
    return candidate


def create_job_description(db: Session, content: str) -> JobDescription:
    jd = JobDescription(content=content)
    db.add(jd)
    db.commit()
    db.refresh(jd)
    return jd


def get_latest_job_description(db: Session) -> JobDescription | None:
    return db.query(JobDescription).order_by(JobDescription.created_at.desc()).first()


def get_candidate(db: Session, candidate_id: int) -> Candidate | None:
    return (
        db.query(Candidate)
        .options(joinedload(Candidate.skills).joinedload(CandidateSkill.skill), joinedload(Candidate.analysis))
        .filter(Candidate.id == candidate_id)
        .first()
    )


def list_candidates(db: Session, search: str | None, min_score: float | None, sort: str, page: int, limit: int):
    query = db.query(Candidate).options(
        joinedload(Candidate.skills).joinedload(CandidateSkill.skill), joinedload(Candidate.analysis)
    )
    if search:
        query = query.filter(Candidate.full_name.ilike(f"%{search}%"))
    if min_score is not None:
        query = query.filter(Candidate.score >= min_score)
    order = Candidate.full_name.asc() if sort == "name" else Candidate.score.desc()
    if sort == "created":
        order = Candidate.created_at.desc()
    total = query.count()
    rows = query.order_by(order).offset((page - 1) * limit).limit(limit).all()
    return [candidate_to_out(row) for row in rows], total

