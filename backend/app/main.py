"""FastAPI application entrypoint."""
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle."""
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    await init_db()
    logger.info("Database initialized")

    if settings.ENABLE_RAG_INIT:
        try:
            from app.rag.knowledge_base import KnowledgeBase

            kb = KnowledgeBase()
            await kb.initialize_default_knowledge()
            logger.info("Knowledge base initialized")
        except Exception as exc:
            logger.warning("Knowledge base initialization failed: %s", exc)
    else:
        logger.info("RAG startup init skipped; demo uses LLM + rule guardrails.")

    yield
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="MoveRenovateAI Agent PoC",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.agent import router as agent_router

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(agent_router)


@app.get("/")
async def root():
    frontend_index = Path(__file__).resolve().parents[2] / "frontend_dist" / "index.html"
    if frontend_index.exists():
        return FileResponse(frontend_index)
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/v1/info")
async def api_info():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_provider": settings.LLM_PROVIDER,
    }


frontend_dist = Path(__file__).resolve().parents[2] / "frontend_dist"
if frontend_dist.exists():
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    index_file = frontend_dist / "index.html"

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        requested = frontend_dist / full_path
        if requested.is_file():
            return FileResponse(requested)
        return FileResponse(index_file)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
