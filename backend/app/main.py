import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.core.config import get_settings
from app.db.session import engine, Base
from app.core.queue import rabbitmq_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    logger.info("Starting application...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Connect to RabbitMQ
    if rabbitmq_manager.connect():
        logger.info("RabbitMQ connected")
    else:
        logger.warning("RabbitMQ connection failed - jobs will not be queued")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    rabbitmq_manager.close()


app = FastAPI(
    title=settings.app_name,
    description="Smart Audit Agent Backend API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/config", include_in_schema=False)
async def config_summary() -> dict:
    return {
        "env": settings.env,
        "log_level": settings.log_level,
        "app_name": settings.app_name,
    }
