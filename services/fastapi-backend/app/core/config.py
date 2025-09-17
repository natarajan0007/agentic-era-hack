"""
Application configuration settings
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Intellica API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="local", env="ENVIRONMENT")
    DEBUG: bool = True
    
    # Database configuration
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Local database settings (fallback)
    local_db_host: str = Field(default="localhost", env="LOCAL_DB_HOST")
    local_db_port: int = Field(default=5433, env="LOCAL_DB_PORT")
    local_db_name: str = Field(default="intellica", env="LOCAL_DB_NAME")
    local_db_user: str = Field(default="postgres", env="LOCAL_DB_USER")
    local_db_password: str = Field(default="password", env="LOCAL_DB_PASSWORD")
    
    # Development database settings
    db_host: str = Field(default="dev-db-host", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(default="pdf_processing_dev", env="DB_NAME")
    db_user: str = Field(default="dev_user", env="DB_USER")
    db_password: str = Field(default="dev_password", env="DB_PASSWORD")
    db_mode: str = Field(default="local", env="DB_MODE")
    
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = Field(default=[
        "http://127.0.0.1:3000",
        "https://cto-nse-maedel-dev.vmo2digital.co.uk",
        "https://maedel-service-920266728097.europe-west2.run.app"
    ], env="ALLOWED_ORIGINS")
    
    # AI Services
    GEMINI_API_KEY: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    GEMINI_MODEL: str = "gemini-pro"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif",
        "application/pdf", "text/plain",
        "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    # Email (for notifications)
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # This is the key part - configure Pydantic to load from .env file
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"  # Ignore extra fields in .env that aren't in the model
    }
    
    @property
    def use_cloud_sql(self) -> bool:
        """
        Determine if we should use Cloud SQL connector
        """
        return (
            self.ENVIRONMENT.lower() in ["dev", "prod", "staging"] and 
            self.db_host and 
            self.db_user and 
            self.db_name
        )
    
    @property
    def database_url_computed(self) -> str:
        """
        Compute the database URL based on environment and available settings
        """
        # If DATABASE_URL is explicitly set, use it
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        # For cloud environments, we'll use a placeholder URL
        # The actual connection will be handled by the Cloud SQL connector
        if self.use_cloud_sql:
            return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@/{self.db_name}"
        
        # Otherwise, construct based on environment
        if self.ENVIRONMENT.lower() == "dev" and not self.use_cloud_sql:
            print(f"Using development database settings:")
            print(f"  Host: {self.db_host}")
            print(f"  Port: {self.db_port}")
            print(f"  Name: {self.db_name}")
            print(f"  User: {self.db_user}")
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        else:  # local or any other environment
            return f"postgresql://{self.local_db_user}:{self.local_db_password}@{self.local_db_host}:{self.local_db_port}/{self.local_db_name}"
    
    @property
    def database_url_async(self) -> str:
        """
        Get async database URL (for asyncpg)
        """
        base_url = self.database_url_computed
        if not base_url.startswith("postgresql+asyncpg://"):
            base_url = base_url.replace("postgresql://", "postgresql+asyncpg://")
        return base_url
    
    @property
    def cors_origins(self) -> List[str]:
        """
        Get CORS origins based on environment
        """
        if self.is_local:
            return self.ALLOWED_ORIGINS  # More permissive for local development
        else:
            return self.ALLOWED_ORIGINS
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT.lower() == "dev"
    
    @property
    def is_local(self) -> bool:
        """Check if running in local mode"""
        return self.ENVIRONMENT.lower() == "local"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT.lower() == "prod"
    
    @property
    def log_level(self) -> str:
        """Get log level (fix property name to match usage)"""
        return self.LOG_LEVEL
    
    def get_log_config(self) -> dict:
        """Get logging configuration based on environment"""
        base_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default" if self.is_development else "detailed",
                    "level": self.log_level,
                },
            },
            "root": {
                "level": self.log_level,
                "handlers": ["console"],
            },
        }
        
        # Add file handler for development
        if self.is_development:
            base_config["handlers"]["file"] = {
                "class": "logging.FileHandler",
                "filename": "app.log",
                "formatter": "detailed",
                "level": "DEBUG",
            }
            base_config["root"]["handlers"].append("file")
        
        return base_config
    
    def debug_env_loading(self):
        """Debug method to show what values are being loaded"""
        print("=== ENVIRONMENT CONFIGURATION DEBUG ===")
        print(f"Environment: {self.ENVIRONMENT}")
        print(f"Debug: {self.DEBUG}")
        print(f"Log Level: {self.LOG_LEVEL}")
        print(f"Database URL: {self.DATABASE_URL}")
        print(f"DB Host: {self.db_host}")
        print(f"DB Name: {self.db_name}")
        print(f"DB User: {self.db_user}")
        print(f"Local DB Host: {self.local_db_host}")
        print(f"Local DB Name: {self.local_db_name}")
        print(f"Use Cloud SQL: {self.use_cloud_sql}")
        print(f"Computed Database URL: {self.database_url_computed}")
        print("=== END DEBUG ===")

@lru_cache()
def get_settings() -> Settings:
    """
    Get settings instance with caching
    """
    settings = Settings()
    # Uncomment the line below to debug env loading
    # settings.debug_env_loading()
    return settings

# Create settings instance for backward compatibility
settings = get_settings()

# Convenience function to get the current environment
def get_environment() -> str:
    """Get the current environment"""
    return get_settings().ENVIRONMENT  # Fixed: was using .environment instead of .ENVIRONMENT

# Convenience function to check if running in development
def is_development() -> bool:
    """Check if running in development mode"""
    return get_settings().is_development

# Convenience function to check if running locally
def is_local() -> bool:
    """Check if running in local mode"""
    return get_settings().is_local