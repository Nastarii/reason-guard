from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import (
    proxy_router,
    reasoning_router,
    path_analysis_router,
    logic_router,
    consistency_router,
    audit_router,
    dashboard_router,
    auth_router,
    api_tokens_router,
)

settings = get_settings()

app = FastAPI(
    title="ReasonGuard API",
    description="Plataforma de Auditoria de Raciocínio de IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(api_tokens_router)
app.include_router(proxy_router)
app.include_router(reasoning_router)
app.include_router(path_analysis_router)
app.include_router(logic_router)
app.include_router(consistency_router)
app.include_router(audit_router)
app.include_router(dashboard_router)


@app.get("/")
async def root():
    return {
        "name": "ReasonGuard API",
        "version": "1.0.0",
        "description": "Plataforma de Auditoria de Raciocínio de IA",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
