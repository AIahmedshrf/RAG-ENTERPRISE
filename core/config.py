# core/config.py
"""
التكوين المركزي لنظام RAG-ENTERPRISE
يدمج تكوينات جميع المكونات من المستودعات الستة
"""

import os
from typing import List, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()


@dataclass
class AzureOpenAIConfig:
    """تكوين Azure OpenAI"""
    endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    api_key: str = os.getenv("AZURE_OPENAI_KEY", "")
    api_version: str = "2024-02-15-preview"
    chat_deployment: str = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4")
    embedding_deployment: str = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
    max_retries: int = 3
    timeout: int = 60


@dataclass
class AzureSearchConfig:
    """تكوين Azure AI Search (من aisearchmm)"""
    endpoint: str = os.getenv("AZURE_SEARCH_ENDPOINT", "")
    api_key: str = os.getenv("AZURE_SEARCH_KEY", "")
    api_version: str = "2023-11-01"
    
    # Indexes
    general_index: str = "general-documents"
    financial_index: str = "financial-documents"
    research_index: str = "research-documents"


@dataclass
class DocumentProcessingConfig:
    """تكوين معالجة المستندات (من aisearchmm)"""
    doc_intelligence_endpoint: str = os.getenv("AZURE_DOC_INTELLIGENCE_ENDPOINT", "")
    doc_intelligence_key: str = os.getenv("AZURE_DOC_INTELLIGENCE_KEY", "")
    
    # Chunking settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Supported formats
    supported_formats: List[str] = field(default_factory=lambda: [
        "pdf", "docx", "xlsx", "pptx", "txt", "md"
    ])


@dataclass
class FinancialConfig:
    """تكوين النظام المالي (من wealthops + investmentagent)"""
    # Market Data
    market_data_api_key: str = os.getenv("MARKET_DATA_API_KEY", "")
    news_api_key: str = os.getenv("NEWS_API_KEY", "")
    
    # Features
    enable_portfolio_tracking: bool = True
    enable_real_time_data: bool = True
    enable_investment_recommendations: bool = True
    
    # Risk Settings
    var_confidence_level: float = 0.95
    default_risk_tolerance: str = "moderate"  # conservative, moderate, aggressive


@dataclass
class AgentConfig:
    """تكوين الوكلاء (من agents + agentpatterns)"""
    max_iterations: int = 5
    timeout: int = 120
    temperature: float = 0.7
    max_tokens: int = 2000
    
    # Agent patterns
    default_pattern: str = "router"  # sequential, parallel, hierarchical, router, consensus
    enable_memory: bool = True
    memory_window: int = 10


@dataclass
class LanguageConfig:
    """تكوين اللغات"""
    supported_languages: List[str] = field(default_factory=lambda: ["ar", "en"])
    default_language: str = "ar"
    enable_translation: bool = False


@dataclass
class SystemConfig:
    """التكوين الرئيسي للنظام"""
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # API Settings
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = "logs/app.log"
    
    # Sub-configurations
    azure_openai: AzureOpenAIConfig = field(default_factory=AzureOpenAIConfig)
    azure_search: AzureSearchConfig = field(default_factory=AzureSearchConfig)
    document_processing: DocumentProcessingConfig = field(default_factory=DocumentProcessingConfig)
    financial: FinancialConfig = field(default_factory=FinancialConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    language: LanguageConfig = field(default_factory=LanguageConfig)
    
    def validate(self) -> bool:
        """التحقق من صحة التكوين"""
        errors = []
        
        # التحقق من Azure OpenAI
        if not self.azure_openai.endpoint:
            errors.append("AZURE_OPENAI_ENDPOINT is required")
        if not self.azure_openai.api_key:
            errors.append("AZURE_OPENAI_KEY is required")
        
        # التحقق من Azure Search
        if not self.azure_search.endpoint:
            errors.append("AZURE_SEARCH_ENDPOINT is required")
        if not self.azure_search.api_key:
            errors.append("AZURE_SEARCH_KEY is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
    
    def get_summary(self) -> dict:
        """الحصول على ملخص التكوين"""
        return {
            "environment": self.environment,
            "debug": self.debug,
            "api": f"{self.api_host}:{self.api_port}",
            "azure_openai_configured": bool(self.azure_openai.endpoint),
            "azure_search_configured": bool(self.azure_search.endpoint),
            "financial_features_enabled": self.financial.enable_portfolio_tracking,
            "supported_languages": self.language.supported_languages
        }


# Singleton instance
config = SystemConfig()
