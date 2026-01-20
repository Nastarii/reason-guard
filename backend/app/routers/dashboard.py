from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.reasoning import (
    ReasoningTrace, PathAnalysis, LogicGraph, ConsistencyCheck
)
from app.routers.auth import get_current_user
from app.schemas.reasoning import DashboardStats, RecentActivity

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get dashboard KPIs and statistics."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Total decisions (reasoning traces)
    total_decisions = db.query(func.count(ReasoningTrace.id)).filter(
        ReasoningTrace.user_id == current_user.id
    ).scalar() or 0

    # Decisions today
    decisions_today = db.query(func.count(ReasoningTrace.id)).filter(
        ReasoningTrace.user_id == current_user.id,
        ReasoningTrace.created_at >= today
    ).scalar() or 0

    # Average consistency rate
    consistency_checks = db.query(ConsistencyCheck.convergence_rate).filter(
        ConsistencyCheck.user_id == current_user.id
    ).all()

    avg_consistency = 0.0
    if consistency_checks:
        rates = [c[0] for c in consistency_checks if c[0] is not None]
        if rates:
            avg_consistency = sum(rates) / len(rates)

    # Average validity score
    logic_graphs = db.query(LogicGraph.overall_validity_score).filter(
        LogicGraph.user_id == current_user.id
    ).all()

    avg_validity = 0.0
    if logic_graphs:
        scores = [g[0] for g in logic_graphs if g[0] is not None]
        if scores:
            avg_validity = sum(scores) / len(scores)

    # Count critical alerts (graphs with contradictions or low validity)
    critical_alerts = db.query(func.count(LogicGraph.id)).filter(
        LogicGraph.user_id == current_user.id,
        (LogicGraph.has_contradictions == True) |
        (LogicGraph.overall_validity_score < 0.5)
    ).scalar() or 0

    # Total contradictions found
    graphs_with_contradictions = db.query(LogicGraph).filter(
        LogicGraph.user_id == current_user.id,
        LogicGraph.has_contradictions == True
    ).all()

    total_contradictions = sum(
        len(g.contradictions) if g.contradictions else 0
        for g in graphs_with_contradictions
    )

    return DashboardStats(
        total_decisions=total_decisions,
        consistency_rate=round(avg_consistency * 100, 2),
        critical_alerts=critical_alerts,
        decisions_today=decisions_today,
        average_validity_score=round(avg_validity * 100, 2),
        total_contradictions=total_contradictions,
    )


@router.get("/recent-activity", response_model=List[RecentActivity])
async def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get recent activity for the dashboard."""
    activities = []

    # Get recent reasoning traces
    traces = db.query(ReasoningTrace).filter(
        ReasoningTrace.user_id == current_user.id
    ).order_by(ReasoningTrace.created_at.desc()).limit(limit).all()

    for trace in traces:
        activities.append(RecentActivity(
            id=trace.id,
            type="reasoning_trace",
            description=trace.original_prompt[:100] + "..." if len(trace.original_prompt) > 100 else trace.original_prompt,
            created_at=trace.created_at,
            status="completed",
        ))

    # Get recent path analyses
    analyses = db.query(PathAnalysis).filter(
        PathAnalysis.user_id == current_user.id
    ).order_by(PathAnalysis.created_at.desc()).limit(limit).all()

    for analysis in analyses:
        activities.append(RecentActivity(
            id=analysis.id,
            type="path_analysis",
            description=analysis.original_problem[:100] + "..." if len(analysis.original_problem) > 100 else analysis.original_problem,
            created_at=analysis.created_at,
            status="completed",
        ))

    # Get recent logic graphs
    graphs = db.query(LogicGraph).filter(
        LogicGraph.user_id == current_user.id
    ).order_by(LogicGraph.created_at.desc()).limit(limit).all()

    for graph in graphs:
        status = "alert" if graph.has_contradictions else "completed"
        activities.append(RecentActivity(
            id=graph.id,
            type="logic_graph",
            description=f"Validação lógica (Score: {round(graph.overall_validity_score * 100, 1) if graph.overall_validity_score else 'N/A'}%)",
            created_at=graph.created_at,
            status=status,
        ))

    # Get recent consistency checks
    checks = db.query(ConsistencyCheck).filter(
        ConsistencyCheck.user_id == current_user.id
    ).order_by(ConsistencyCheck.created_at.desc()).limit(limit).all()

    for check in checks:
        status = "completed" if check.confidence_score > 0.7 else "warning"
        activities.append(RecentActivity(
            id=check.id,
            type="consistency_check",
            description=f"Verificação de consistência ({check.total_runs} execuções)",
            created_at=check.created_at,
            status=status,
        ))

    # Sort by date and limit
    activities.sort(key=lambda x: x.created_at, reverse=True)
    return activities[:limit]


@router.get("/summary")
async def get_summary(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get summary data for charts."""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Daily decision counts
    daily_counts = []
    for i in range(days):
        day_start = start_date + timedelta(days=i)
        day_end = day_start + timedelta(days=1)

        count = db.query(func.count(ReasoningTrace.id)).filter(
            ReasoningTrace.user_id == current_user.id,
            ReasoningTrace.created_at >= day_start,
            ReasoningTrace.created_at < day_end
        ).scalar() or 0

        daily_counts.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "count": count,
        })

    # Issue breakdown
    logic_graphs = db.query(LogicGraph).filter(
        LogicGraph.user_id == current_user.id,
        LogicGraph.created_at >= start_date
    ).all()

    issue_counts = {
        "contradictions": 0,
        "logic_gaps": 0,
        "hidden_premises": 0,
        "circularity": 0,
    }

    for graph in logic_graphs:
        if graph.contradictions:
            issue_counts["contradictions"] += len(graph.contradictions)
        if graph.logic_gaps:
            issue_counts["logic_gaps"] += len(graph.logic_gaps)
        if graph.hidden_premises:
            issue_counts["hidden_premises"] += len(graph.hidden_premises)
        if graph.circular_references:
            issue_counts["circularity"] += len(graph.circular_references)

    # Consistency distribution
    checks = db.query(ConsistencyCheck.confidence_score).filter(
        ConsistencyCheck.user_id == current_user.id,
        ConsistencyCheck.created_at >= start_date
    ).all()

    consistency_distribution = {
        "high": 0,  # > 80%
        "medium": 0,  # 50-80%
        "low": 0,  # < 50%
    }

    for check in checks:
        if check[0] > 0.8:
            consistency_distribution["high"] += 1
        elif check[0] > 0.5:
            consistency_distribution["medium"] += 1
        else:
            consistency_distribution["low"] += 1

    return {
        "daily_decisions": daily_counts,
        "issue_breakdown": issue_counts,
        "consistency_distribution": consistency_distribution,
    }
