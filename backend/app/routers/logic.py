from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.reasoning import LogicGraphCreate, LogicGraphResponse
from app.modules.logic_validator import LogicValidator

router = APIRouter(prefix="/logic", tags=["Logic Validator (GoT)"])


@router.post("/validate", response_model=LogicGraphResponse)
async def create_validation(
    request: LogicGraphCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new logic validation with Graph-of-Thought analysis."""
    if not request.reasoning_trace_id and not request.raw_text:
        raise HTTPException(
            status_code=400,
            detail="Either reasoning_trace_id or raw_text must be provided"
        )

    validator = LogicValidator(db)

    try:
        graph = await validator.validate(
            user_id=current_user.id,
            reasoning_trace_id=request.reasoning_trace_id,
            raw_text=request.raw_text,
        )
        return graph
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graphs", response_model=List[LogicGraphResponse])
async def list_graphs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all logic graphs for the current user."""
    validator = LogicValidator(db)
    return validator.get_user_graphs(current_user.id, limit)


@router.get("/graphs/{graph_id}", response_model=LogicGraphResponse)
async def get_graph(
    graph_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific logic graph."""
    validator = LogicValidator(db)
    graph = validator.get_graph(graph_id)

    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    if graph.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return graph


@router.get("/graphs/{graph_id}/visualization")
async def get_graph_visualization(
    graph_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the logic graph formatted for visualization."""
    validator = LogicValidator(db)
    graph = validator.get_graph(graph_id)

    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    if graph.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    viz_data = validator.get_graph_for_visualization(graph_id)
    return viz_data


@router.get("/graphs/{graph_id}/issues")
async def get_graph_issues(
    graph_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all issues found in a logic graph."""
    validator = LogicValidator(db)
    graph = validator.get_graph(graph_id)

    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    if graph.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    issues = {
        "total_issues": 0,
        "contradictions": [],
        "logic_gaps": [],
        "hidden_premises": [],
        "circular_references": [],
    }

    if graph.contradictions:
        issues["contradictions"] = graph.contradictions
        issues["total_issues"] += len(graph.contradictions)

    if graph.logic_gaps:
        issues["logic_gaps"] = graph.logic_gaps
        issues["total_issues"] += len(graph.logic_gaps)

    if graph.hidden_premises:
        issues["hidden_premises"] = graph.hidden_premises
        issues["total_issues"] += len(graph.hidden_premises)

    if graph.circular_references:
        issues["circular_references"] = graph.circular_references
        issues["total_issues"] += len(graph.circular_references)

    return issues
