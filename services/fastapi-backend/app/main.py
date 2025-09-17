"""
FastAPI application entry point
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
import time
import os
from app.core.config import settings
from app.core.database import init_db
from app.models.base import Base
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager

# Import API routers
from app.api import auth, users, tickets, chat, knowledge, analytics, transition

# Configure logging BEFORE any other imports that might use logging
def setup_logging():
    """Setup logging configuration"""
    # Get log level from settings or default to INFO
    log_level = getattr(settings, 'LOG_LEVEL', 'INFO').upper()
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),  # Console handler
        ]
    )
    
    # Set specific loggers
    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, log_level))
    
    # Set uvicorn loggers to the same level
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(getattr(logging, log_level))
    
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.setLevel(getattr(logging, log_level))
    
    # FastAPI logger
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(getattr(logging, log_level))
    
    return logger

# Setup logging first
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=== APPLICATION STARTUP ===")
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    
    if settings.ENVIRONMENT == "local":
        logger.info(f"Database URL: {settings.database_url_async}")
    else:
        logger.info(f"Database connection string: {settings.database_url_async}")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        
        # Health check
        from app.core.database import check_database_health, close_db
        logger.info("Checking database health...")
        if await check_database_health():
            logger.info("✓ Database connection verified")
        else:
            logger.error("✗ Database connection failed")
            raise Exception("Database connection failed")
        
        logger.info("✓ Initialization completed successfully")
        
    except Exception as e:
        logger.error(f"✗ Initialization failed: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("=== APPLICATION SHUTDOWN ===")
    logger.info("Shutting down application...")
    try:
        await close_db()
        logger.info("✓ Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)
    logger.info("✓ Shutdown completed")

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-Powered IT Operations Platform Backend API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url=f"/api/v1/openapi.json",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["intellica.com", "*.intellica.com"]
)
    
# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log request details
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    
    return response

# Mount static files only if directory exists
static_dir = "static"
if os.path.exists(static_dir) and os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"✓ Static files mounted from {static_dir}")
else:
    logger.warning(f"⚠ Static directory '{static_dir}' not found, skipping static files mounting")

# Log router inclusion
logger.info("Including API routers...")

# Include API routers
app.include_router(auth.router, prefix="/api/v1")
logger.info("✓ Auth router included")

app.include_router(users.router, prefix="/api/v1")
logger.info("✓ Users router included")

app.include_router(tickets.router, prefix="/api/v1")
logger.info("✓ Tickets router included")

app.include_router(chat.router, prefix="/api/v1")
logger.info("✓ Chat router included")

app.include_router(knowledge.router, prefix="/api/v1")
logger.info("✓ Knowledge router included")

app.include_router(analytics.router, prefix="/api/v1")
logger.info("✓ Analytics router included")

app.include_router(transition.router, prefix="/api/v1")
logger.info("✓ Transition router included")

logger.info("All routers included successfully")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AI Ops",
        version="1.0.0",
        description="API with OAuth2 authentication",
        routes=app.routes,
    )

    # Add OAuth2 security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/api/v1/auth/login",
                    "scopes": {}
                }
            }
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    logger.debug("Root endpoint requested")
    return {
        "message": "Welcome to Intellica API",
        "version": settings.VERSION,
        "docs_url": "/docs" if settings.DEBUG else None,
        "health_url": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Log startup info
    logger.info("Starting server with uvicorn...")
    logger.info(f"Host: 0.0.0.0, Port: 8000")
    logger.info(f"Reload: {settings.DEBUG}")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )