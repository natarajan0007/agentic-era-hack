from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncio
import logging
from .config import settings
from sqlalchemy import text

# Cloud SQL imports - only imported when needed
try:
    from google.cloud.sql.connector import create_async_connector
    import asyncpg
    CLOUD_SQL_AVAILABLE = True
except ImportError:
    CLOUD_SQL_AVAILABLE = False
    logging.warning("Cloud SQL connector not available. Install google-cloud-sql-connector and asyncpg for Cloud SQL support.")

Base = declarative_base()

# Global variables for database components
async_engine = None
AsyncSessionLocal = None
connector = None

async def setup_local_database():
    """Setup local database connection"""
    global async_engine, AsyncSessionLocal
    
    async_engine = create_async_engine(
        settings.database_url_async,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        # echo=settings.debug
    )
    
    AsyncSessionLocal = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    logging.info("Local database connection setup completed")

async def setup_cloud_sql_database():
    """Setup Cloud SQL database connection"""
    global async_engine, AsyncSessionLocal, connector
    
    if not CLOUD_SQL_AVAILABLE:
        raise ImportError("Cloud SQL dependencies not available. Install google-cloud-sql-connector and asyncpg.")
    
    # Initialize async connector - await it since create_async_connector() returns a coroutine
    connector = await create_async_connector()
    
    # Create connection function for asyncpg
    async def getconn() -> asyncpg.Connection:
        return await connector.connect_async(
            settings.db_host, 
            "asyncpg",
            user=settings.db_user,
            password=settings.db_password,
            db=settings.db_name,
            port=settings.db_port,
            ip_type="PRIVATE"
        )
    
    # Create async engine with Cloud SQL connector
    async_engine = create_async_engine(
        "postgresql+asyncpg://",
        async_creator=getconn,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=settings.DEBUG
    )
    
    AsyncSessionLocal = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    logging.info("Cloud SQL database connection setup completed")

async def initialize_database():
    """Initialize database based on environment mode"""
    global async_engine, AsyncSessionLocal
    
    # Avoid double initialization
    if AsyncSessionLocal is not None:
        return
    
    db_mode = getattr(settings, 'db_mode', 'local').lower()
    
    if db_mode == 'cloud_sql':
        await setup_cloud_sql_database()
    else:
        await setup_local_database()
    
    logging.info(f"Database initialized in {db_mode} mode")

# Initialize database on module import
async def _init_on_import():
    """Initialize database when module is imported"""
    try:
        await initialize_database()
    except Exception as e:
        logging.error(f"Failed to initialize database on import: {e}")
        # Don't raise here, let it be handled when actually needed

# Create a task to initialize the database
import asyncio
try:
    # Try to get the current event loop
    loop = asyncio.get_running_loop()
    # If we have a running loop, schedule the initialization
    loop.create_task(_init_on_import())
except RuntimeError:
    # No running loop, initialization will happen on first use
    pass

async def get_db():
    """Dependency to get async database session"""
    if AsyncSessionLocal is None:
        await initialize_database()
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logging.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_db_session():
    """Get a database session directly (for use in background tasks)"""
    if AsyncSessionLocal is None:
        await initialize_database()
    
    return AsyncSessionLocal()

class DatabaseSession:
    """Async context manager for database sessions"""
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        if AsyncSessionLocal is None:
            await initialize_database()
        self.session = AsyncSessionLocal()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type:
                await self.session.rollback()
            await self.session.close()

def get_db_context():
    """Get a database session context manager (for use in background tasks)"""
    return DatabaseSession()

async def init_db():
    """Initialize database tables"""
    try:
        # Ensure database is initialized
        if async_engine is None:
            await initialize_database()
                
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logging.info(f"Database tables initialized successfully in {settings.ENVIRONMENT} mode")
        
        # Log appropriate connection info based on mode
        db_mode = getattr(settings, 'db_mode', 'local').lower()
        if db_mode == 'cloud_sql':
            logging.info(f"Connected to Cloud SQL instance: {settings.db_host}")
        else:
            logging.info(f"Database URL: {settings.database_url_async}")
        
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise

async def close_db():
    """Close database connections"""
    global async_engine, connector
    
    if async_engine:
        await async_engine.dispose()
    
    if connector:
        await connector.close_async()
    
    logging.info("Database connections closed")

async def check_database_health() -> bool:
    """Check if database is accessible (async)"""
    try:
        if AsyncSessionLocal is None:
            await initialize_database()
        
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logging.error(f"Database health check failed: {e}")
        return False

async def check_sync_database_health() -> bool:
    """Check if database is accessible (async version of sync health check)"""
    # This function maintains the same name for backward compatibility
    return await check_database_health()

# Additional utility functions for Cloud SQL
async def test_cloud_sql_connection():
    """Test Cloud SQL connection specifically"""
    if not CLOUD_SQL_AVAILABLE:
        return False, "Cloud SQL dependencies not available"
    
    try:
        test_connector = await create_async_connector()
        conn = await test_connector.connect_async(
            settings.db_host,  # Cloud SQL connection name
            "asyncpg",
            user=settings.db_user,
            password=settings.db_password,
            db=settings.db_name,
            ip_type=getattr(settings, 'cloud_sql_ip_type', 'public')
        )
        await conn.close()
        await test_connector.close_async()
        return True, "Cloud SQL connection successful"
    except Exception as e:
        return False, f"Cloud SQL connection failed: {e}"

async def get_connection_info():
    """Get current database connection information"""
    db_mode = getattr(settings, 'db_mode', 'local').lower()
    
    if db_mode == 'cloud_sql':
        return {
            'mode': 'cloud_sql',
            'instance': settings.db_host,  # Cloud SQL connection name
            'database': settings.db_name,
            'user': settings.db_user,
            'ip_type': getattr(settings, 'cloud_sql_ip_type', 'public')
        }
    else:
        return {
            'mode': 'local',
            'url': settings.database_url_async,
            'debug': settings.debug
        }