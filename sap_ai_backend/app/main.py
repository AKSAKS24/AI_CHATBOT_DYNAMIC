from fastapi import FastAPI
from app.routers import odata_router
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

def create_app() -> FastAPI:
    """Create FastAPI app instance with all routes loaded."""
    app = FastAPI(title=settings.app_name)

    app.include_router(odata_router.router)

    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting {settings.app_name} in {settings.environment} mode.")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down API service cleanly...")

    return app

app = create_app()