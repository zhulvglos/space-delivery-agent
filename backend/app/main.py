"""FastAPI application entrypoint."""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
