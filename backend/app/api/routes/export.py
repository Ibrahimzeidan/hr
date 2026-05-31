from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.api.dependencies.database import DbSession
from app.core.security import limiter
from app.services.export_service import csv_bytes, excel_bytes

router = APIRouter(tags=["export"])


@router.get("/download/csv")
@limiter.limit("30/minute")
def download_csv(request: Request, db: DbSession):
    return StreamingResponse(
        iter([csv_bytes(db)]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=candidates.csv"},
    )


@router.get("/download/excel")
@limiter.limit("30/minute")
def download_excel(request: Request, db: DbSession):
    return StreamingResponse(
        iter([excel_bytes(db)]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=candidates.xlsx"},
    )

