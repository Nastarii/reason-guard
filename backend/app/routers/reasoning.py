from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.reasoning import ReasoningTraceCreate, ReasoningTraceResponse
from app.modules.reasoning_tracer import ReasoningTracer

router = APIRouter(prefix="/reasoning", tags=["Reasoning Tracer (CoT)"])


@router.post("/trace", response_model=ReasoningTraceResponse)
async def create_trace(
    request: ReasoningTraceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new reasoning trace with Chain-of-Thought analysis."""
    tracer = ReasoningTracer(db)

    try:
        trace = await tracer.trace(
            user_id=current_user.id,
            prompt=request.original_prompt,
            provider=request.model_provider.value,
            model=request.model_name,
        )
        return trace
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traces", response_model=List[ReasoningTraceResponse])
async def list_traces(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all reasoning traces for the current user."""
    tracer = ReasoningTracer(db)
    return tracer.get_user_traces(current_user.id, limit)


@router.get("/traces/{trace_id}", response_model=ReasoningTraceResponse)
async def get_trace(
    trace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific reasoning trace."""
    tracer = ReasoningTracer(db)
    trace = tracer.get_trace(trace_id)

    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")

    if trace.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return trace


@router.get("/traces/{trace_id}/verify")
async def verify_trace_integrity(
    trace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verify the integrity of a reasoning trace."""
    tracer = ReasoningTracer(db)
    trace = tracer.get_trace(trace_id)

    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")

    if trace.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    is_valid = tracer.verify_integrity(trace)

    return {
        "trace_id": trace_id,
        "integrity_valid": is_valid,
        "stored_hash": trace.integrity_hash,
    }
