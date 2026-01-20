from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.reasoning import AuditReportCreate, AuditReportResponse
from app.modules.audit_generator import AuditGenerator

router = APIRouter(prefix="/audit", tags=["Audit Trail Generator"])


@router.post("/reports", response_model=AuditReportResponse)
async def create_report(
    request: AuditReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a new audit report."""
    generator = AuditGenerator(db)

    try:
        report = await generator.generate(
            user_id=current_user.id,
            report_type=request.report_type.value,
            format=request.format.value,
            reasoning_trace_ids=request.reasoning_trace_ids,
            path_analysis_ids=request.path_analysis_ids,
            logic_graph_ids=request.logic_graph_ids,
            consistency_check_ids=request.consistency_check_ids,
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports", response_model=List[AuditReportResponse])
async def list_reports(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all audit reports for the current user."""
    generator = AuditGenerator(db)
    return generator.get_user_reports(current_user.id, limit)


@router.get("/reports/{report_id}", response_model=AuditReportResponse)
async def get_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific audit report."""
    generator = AuditGenerator(db)
    report = generator.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return report


@router.get("/reports/{report_id}/download")
async def download_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download the audit report file."""
    generator = AuditGenerator(db)
    report = generator.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    content = generator.get_report_file(report)

    if not content:
        raise HTTPException(status_code=500, detail="Failed to generate report file")

    # Determine content type and filename
    content_type_map = {
        "pdf": "application/pdf",
        "json": "application/json",
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    extension_map = {
        "pdf": "pdf",
        "json": "json",
        "excel": "xlsx",
    }

    content_type = content_type_map.get(report.format, "application/octet-stream")
    extension = extension_map.get(report.format, "bin")
    filename = f"audit_report_{report.report_type}_{report.id}.{extension}"

    return Response(
        content=content,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
    )
