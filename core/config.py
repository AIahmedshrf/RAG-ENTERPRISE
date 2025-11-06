"""
Configuration Module - Final & Production Ready
All attributes match actual usage in codebase
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings


class RateLimitConfig:
    """Rate Limit Configuration"""
    def __init__(self, enabled: bool, per_minute: int, per_hour: int):
        self.enabled = enabled
        self.requests_per_minute = per_minute  # Match actual usage
        self.requests_per_hour = per_hour      # Match actual usage


class AzureOpenAIConfig:
    """Azure OpenAI Configuration"""
    def __init__(self, settings):
        self.api_key = settings.azure_openai_api_key
        self.endpoint = settings.azure_openai_endpoint
        self.deployment = settings.azure_openai_deployment
        self.api_version = settings.azure_openai_api_version
        self.embedding_deployment = settings.azure_embedding_deployment


class SecurityConfig:
    """Security Configuration"""
    def __init__(self, secret_key: str, algorithm: str):
        self.secret_key = secret_key
        self.algorithm = algorithm


class Settings(BaseSettings):
    """Application Settings - Complete"""
    
    # === Application ===
    app_name: str = "RAG-ENTERPRISE"
    app_version: str = "2.1.0"
    api_prefix: str = "/api/v1"
    debug: bool = True
    
    # === Security ===
    secret_key: str = "rag-enterprise-secret-key-change-in-production-min-32-chars"
    algorithm: str = "HS256"
    access_token_expire_days: int = 365
    refresh_token_expire_days: int = 730
    
    # === Database ===
    database_url: str = "sqlite:///./data/rag_enterprise.db"
    
    # === OpenAI ===
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2000
    
    # === Azure OpenAI ===
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_deployment: Optional[str] = None
    azure_openai_api_version: str = "2023-05-15"
    azure_embedding_deployment: Optional[str] = None
    
    # === Embeddings ===
    embedding_model: str = "text-embedding-ada-002"
    embedding_dimension: int = 1536
    embedding_deployment: Optional[str] = None
    
    # === Storage ===
    storage_path: str = "/tmp/rag-enterprise/storage"
    upload_path: str = "/tmp/rag-enterprise/uploads"
    data_path: str = "./data"
    max_upload_size: int = 10485760  # 10MB
    allowed_extensions: List[str] = [".pdf", ".txt", ".docx", ".doc", ".md"]
    
    # === Logging ===
    log_level: str = "INFO"
    log_file: str = "/tmp/rag-enterprise/logs/api.log"
    
    # === CORS ===
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # === Rate Limiting ===
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # === Properties ===
    @property
    def rate_limit(self) -> RateLimitConfig:
        """Rate limit configuration object"""
        return RateLimitConfig(
            enabled=self.rate_limit_enabled,
            per_minute=self.rate_limit_per_minute,
            per_hour=self.rate_limit_per_hour
        )
    
    @property
    def azure_openai(self) -> AzureOpenAIConfig:
        """Azure OpenAI configuration object"""
        return AzureOpenAIConfig(self)
    
    @property
    def security(self) -> SecurityConfig:
        """Security configuration object"""
        return SecurityConfig(
            secret_key=self.secret_key,
            algorithm=self.algorithm
        )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"


# Singleton instance
settings = Settings()
