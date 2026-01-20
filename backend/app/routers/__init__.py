from app.routers.proxy import router as proxy_router
from app.routers.reasoning import router as reasoning_router
from app.routers.path_analysis import router as path_analysis_router
from app.routers.logic import router as logic_router
from app.routers.consistency import router as consistency_router
from app.routers.audit import router as audit_router
from app.routers.dashboard import router as dashboard_router
from app.routers.auth import router as auth_router
from app.routers.api_tokens import router as api_tokens_router

__all__ = [
    "proxy_router",
    "reasoning_router",
    "path_analysis_router",
    "logic_router",
    "consistency_router",
    "audit_router",
    "dashboard_router",
    "auth_router",
    "api_tokens_router",
]
