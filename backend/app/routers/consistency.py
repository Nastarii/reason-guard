from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.reasoning import ConsistencyCheckCreate, ConsistencyCheckResponse
from app.modules.consistency_checker import ConsistencyChecker

router = APIRouter(prefix="/consistency", tags=["Consistency Checker"])


@router.post("/check", response_model=ConsistencyCheckResponse)
async def create_check(
    request: ConsistencyCheckCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new consistency check with multiple runs."""
    checker = ConsistencyChecker(db)

    try:
        check = await checker.check(
            user_id=current_user.id,
            query=request.query,
            provider=request.model_provider.value,
            model=request.model_name,
            num_runs=request.num_runs,
            include_variations=request.include_variations,
        )
        return check
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/checks", response_model=List[ConsistencyCheckResponse])
async def list_checks(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all consistency checks for the current user."""
    checker = ConsistencyChecker(db)
    return checker.get_user_checks(current_user.id, limit)


@router.get("/checks/{check_id}", response_model=ConsistencyCheckResponse)
async def get_check(
    check_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific consistency check."""
    checker = ConsistencyChecker(db)
    check = checker.get_check(check_id)

    if not check:
        raise HTTPException(status_code=404, detail="Check not found")

    if check.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return check


@router.get("/checks/{check_id}/summary")
async def get_check_summary(
    check_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a summary of a consistency check."""
    checker = ConsistencyChecker(db)
    check = checker.get_check(check_id)

    if not check:
        raise HTTPException(status_code=404, detail="Check not found")

    if check.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return checker.get_summary(check)


@router.get("/checks/{check_id}/responses")
async def get_check_responses(
    check_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all responses from a consistency check."""
    checker = ConsistencyChecker(db)
    check = checker.get_check(check_id)

    if not check:
        raise HTTPException(status_code=404, detail="Check not found")

    if check.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "total_runs": check.total_runs,
        "variations": check.query_variations,
        "responses": check.responses,
        "divergent_points": check.divergent_points,
    }
