"""
Enhanced Configuration Management
"""
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import Optional, List
import os
from functools import lru_cache


class DatabaseSettings(BaseSettings):
    """Database configuration"""
    model_config = ConfigDict(extra='ignore')
    
    name: str = Field(default="rag_enterprise.db")
    echo: bool = Field(default=False)
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)


class AzureOpenAISettings(BaseSettings):
    """Azure OpenAI configuration"""
    model_config = ConfigDict(extra='ignore')
    
    api_key: str = Field(default="")
    api_base: str = Field(default="")
    api_version: str = Field(default="2024-02-15-preview")
    deployment_name: str = Field(default="gpt-4")
    embedding_deployment: str = Field(default="text-embedding-ada-002")
    
    # Model parameters
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=32000)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)


class AzureAISearchSettings(BaseSettings):
    """Azure AI Search configuration"""
    model_config = ConfigDict(extra='ignore')
    
    endpoint: str = Field(default="")
    api_key: str = Field(default="")
    index_name: str = Field(default="rag-enterprise-index")
    semantic_configuration: str = Field(default="default")
    use_semantic_search: bool = Field(default=True)


class RedisSettings(BaseSettings):
    """Redis configuration"""
    model_config = ConfigDict(extra='ignore')
    
    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    db: int = Field(default=0)
    password: Optional[str] = Field(default=None)
    max_connections: int = Field(default=50)
    cache_ttl: int = Field(default=3600)
    
    @property
    def url(self) -> str:
        """Get Redis URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class SecuritySettings(BaseSettings):
    """Security configuration"""
    model_config = ConfigDict(extra='ignore')
    
    secret_key: str = Field(default="dev-secret-key-change-in-production-please")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)
    bcrypt_rounds: int = Field(default=12)
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:8000"])


class RateLimitSettings(BaseSettings):
    """Rate limiting configuration"""
    model_config = ConfigDict(extra='ignore')
    
    enabled: bool = Field(default=True)
    requests_per_minute: int = Field(default=60)
    requests_per_hour: int = Field(default=1000)


class StorageSettings(BaseSettings):
    """Storage configuration"""
    model_config = ConfigDict(extra='ignore')
    
    provider: str = Field(default="local")
    local_path: str = Field(default="./storage")
    azure_connection_string: Optional[str] = Field(default=None)
    azure_container: str = Field(default="rag-enterprise")
    max_file_size_mb: int = Field(default=50)


class RAGSettings(BaseSettings):
    """RAG configuration"""
    model_config = ConfigDict(extra='ignore')
    
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    top_k: int = Field(default=5)
    similarity_threshold: float = Field(default=0.7)
    vector_weight: float = Field(default=0.7)
    keyword_weight: float = Field(default=0.3)
    use_reranking: bool = Field(default=True)
    rerank_top_k: int = Field(default=3)


class Settings(BaseSettings):
    """Main application settings"""
    model_config = ConfigDict(
        extra='ignore',
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )
    
    # App info
    app_name: str = "RAG-ENTERPRISE"
    app_version: str = "1.0.0"
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    
    # API
    api_prefix: str = "/api/v1"
    
    # Monitoring
    enable_metrics: bool = Field(default=True)
    enable_tracing: bool = Field(default=False)
    
    # Sub-settings initialized as properties
    @property
    def database(self) -> DatabaseSettings:
        return DatabaseSettings()
    
    @property
    def azure_openai(self) -> AzureOpenAISettings:
        return AzureOpenAISettings()
    
    @property
    def azure_search(self) -> AzureAISearchSettings:
        return AzureAISearchSettings()
    
    @property
    def redis(self) -> RedisSettings:
        return RedisSettings()
    
    @property
    def security(self) -> SecuritySettings:
        return SecuritySettings()
    
    @property
    def rate_limit(self) -> RateLimitSettings:
        return RateLimitSettings()
    
    @property
    def storage(self) -> StorageSettings:
        return StorageSettings()
    
    @property
    def rag(self) -> RAGSettings:
        return RAGSettings()


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
