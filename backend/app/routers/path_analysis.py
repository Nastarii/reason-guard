from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.reasoning import PathAnalysisCreate, PathAnalysisResponse
from app.modules.path_analyzer import PathAnalyzer

router = APIRouter(prefix="/path-analysis", tags=["Path Analyzer (ToT)"])


@router.post("/analyze", response_model=PathAnalysisResponse)
async def create_analysis(
    request: PathAnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new path analysis with Tree-of-Thought exploration."""
    analyzer = PathAnalyzer(db)

    try:
        analysis = await analyzer.analyze(
            user_id=current_user.id,
            problem=request.problem,
            provider=request.model_provider.value,
            model=request.model_name,
            max_depth=request.max_depth,
            breadth=request.breadth,
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyses", response_model=List[PathAnalysisResponse])
async def list_analyses(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all path analyses for the current user."""
    analyzer = PathAnalyzer(db)
    return analyzer.get_user_analyses(current_user.id, limit)


@router.get("/analyses/{analysis_id}", response_model=PathAnalysisResponse)
async def get_analysis(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific path analysis."""
    analyzer = PathAnalyzer(db)
    analysis = analyzer.get_analysis(analysis_id)

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if analysis.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return analysis


@router.get("/analyses/{analysis_id}/tree")
async def get_analysis_tree(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the exploration tree for visualization."""
    analyzer = PathAnalyzer(db)
    analysis = analyzer.get_analysis(analysis_id)

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if analysis.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Format tree for frontend visualization
    tree_data = {
        "name": analysis.decomposition.get("main_goal", "Problem"),
        "children": [],
    }

    for branch in analysis.exploration_tree.get("root", {}).get("branches", []):
        branch_node = {
            "name": branch["subproblem"][:50] + "..." if len(branch["subproblem"]) > 50 else branch["subproblem"],
            "fullName": branch["subproblem"],
            "children": [],
        }

        for hyp in branch.get("hypotheses", []):
            hyp_node = {
                "name": hyp["approach"][:40] + "..." if len(hyp["approach"]) > 40 else hyp["approach"],
                "fullName": hyp["approach"],
                "score": hyp.get("score", 0),
                "isPruned": hyp.get("is_pruned", False),
                "pruneReason": hyp.get("prune_reason"),
                "children": [
                    {
                        "name": child["approach"][:30] + "..." if len(child["approach"]) > 30 else child["approach"],
                        "fullName": child["approach"],
                        "score": child.get("score", 0),
                        "isPruned": child.get("is_pruned", False),
                    }
                    for child in hyp.get("children", [])
                ],
            }
            branch_node["children"].append(hyp_node)

        tree_data["children"].append(branch_node)

    return {
        "tree": tree_data,
        "selected_path": analysis.selected_path,
        "stats": {
            "total_nodes": analysis.total_nodes_explored,
            "pruned_nodes": analysis.total_paths_pruned,
        },
    }
