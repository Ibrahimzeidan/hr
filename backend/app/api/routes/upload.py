from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from app.ai.resume_parser import parse_resume
from app.api.dependencies.database import DbSession
from app.core.security import limiter, sanitize_text
from app.schemas.upload import JobDescriptionOut, UploadResponse
from app.services.candidate_service import create_candidate, create_job_description
from app.services.parsing_service import parse_upload
from app.storage.cloudinary_service import upload_resume
from app.utils.serializers import candidate_to_out

router = APIRouter(tags=["upload"])


@router.post("/upload-resumes", response_model=UploadResponse)
@limiter.limit("20/minute")
async def upload_resumes(request: Request, db: DbSession, files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="At least one resume is required")
    candidates = []
    for file in files:
        parsed = await parse_upload(file)
        profile = parse_resume(parsed.text)
        resume_url = upload_resume(parsed.filename, parsed.content)
        candidate = create_candidate(db, profile, resume_url, parsed.text)
        candidates.append(candidate_to_out(candidate))
    return UploadResponse(candidates=candidates)


@router.post("/upload-job-description", response_model=JobDescriptionOut)
@limiter.limit("30/minute")
async def upload_job_description(
    request: Request,
    db: DbSession,
    content: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
):
    jd_text = sanitize_text(content or "")
    if file:
        jd_text = (await parse_upload(file)).text
    if len(jd_text.split()) < 8:
        raise HTTPException(status_code=400, detail="Job description is too short")
    return create_job_description(db, jd_text)

