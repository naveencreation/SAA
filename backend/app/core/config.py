from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "Smart Audit Agent"
    env: str = "development"
    log_level: str = "info"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/smart_audit"
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    
    # API
    api_v1_prefix: str = "/api/v1"
    
    # Storage - support both naming conventions
    storage_dir: str = "Storage"
    storage_path: Optional[str] = None  # Alias for storage_dir
    
    # RabbitMQ
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_queue: str = "file_processing_queue"
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    
    # Azure AI - support both naming conventions
    azure_api_key: str = ""
    azure_endpoint: str = ""
    azure_analyzer_id: str = "TDS_Recivable"
    analyzer_id: Optional[str] = None  # Alias for azure_analyzer_id
    
    @property
    def effective_storage_path(self) -> str:
        """Returns storage_path if set, otherwise storage_dir."""
        return self.storage_path or self.storage_dir
    
    @property
    def effective_analyzer_id(self) -> str:
        """Returns analyzer_id if set, otherwise azure_analyzer_id."""
        return self.analyzer_id or self.azure_analyzer_id

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env that aren't defined here


@lru_cache
def get_settings() -> Settings:
    return Settings()

