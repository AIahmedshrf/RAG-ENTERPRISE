"""
Dify Configuration Module
Manages Dify environment settings, agent configurations, and API connections
"""

import os
from typing import Dict, Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from dataclasses import dataclass, field


class AgentType(str, Enum):
    """Supported agent types"""
    PORTFOLIO = "portfolio"
    RISK = "risk"
    MARKET = "market"
    COMPLIANCE = "compliance"
    SUMMARIZER = "summarizer"
    RESEARCHER = "researcher"
    QA = "qa"


class DifyEnvironment(str, Enum):
    """Dify deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ModelProvider(str, Enum):
    """LLM Model Providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    OLLAMA = "ollama"
    BAIDU = "baidu"


@dataclass
class DifyAPIConfig:
    """Dify API configuration from environment"""
    api_key: str = field(default_factory=lambda: os.getenv('DIFY_API_KEY', ''))
    base_url: str = field(default_factory=lambda: os.getenv('DIFY_BASE_URL', 'http://localhost:8001/api'))
    api_version: str = field(default='v1')
    timeout: int = field(default=30)
    max_retries: int = field(default=3)
    environment: DifyEnvironment = field(default=DifyEnvironment.DEVELOPMENT)
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.api_key and self.environment == DifyEnvironment.PRODUCTION:
            raise ValueError("DIFY_API_KEY is required for production environment")
        
        self.environment = DifyEnvironment(
            os.getenv('DIFY_ENV', 'development')
        )


@dataclass
class AgentConfig:
    """Configuration for a specific agent"""
    name: str
    agent_type: AgentType
    description: str
    model: str = field(default="gpt-4")
    model_provider: ModelProvider = field(default=ModelProvider.OPENAI)
    temperature: float = field(default=0.7)
    max_tokens: int = field(default=2000)
    tools: List[str] = field(default_factory=list)
    system_prompt: Optional[str] = None
    knowledge_bases: List[str] = field(default_factory=list)
    memory_enabled: bool = field(default=True)
    memory_type: str = field(default="full")  # full, summary, short_term
    max_memory_tokens: int = field(default=4000)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "type": self.agent_type.value,
            "description": self.description,
            "model": self.model,
            "model_provider": self.model_provider.value,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "tools": self.tools,
            "system_prompt": self.system_prompt,
            "knowledge_bases": self.knowledge_bases,
            "memory": {
                "enabled": self.memory_enabled,
                "type": self.memory_type,
                "max_tokens": self.max_memory_tokens
            }
        }


class DifyConfig:
    """
    Centralized Dify Configuration Manager
    Manages API settings, agent configurations, and deployment settings
    """
    
    def __init__(self):
        """Initialize Dify configuration"""
        self.api_config = DifyAPIConfig()
        self.agents: Dict[str, AgentConfig] = {}
        self._load_agent_configs()
    
    def _load_agent_configs(self):
        """Load default agent configurations"""
        # Portfolio Agent
        self.agents[AgentType.PORTFOLIO.value] = AgentConfig(
            name="Portfolio Analyst Agent",
            agent_type=AgentType.PORTFOLIO,
            description="Analyzes investment portfolios and provides recommendations",
            model=os.getenv("PORTFOLIO_AGENT_MODEL", "gpt-4"),
            model_provider=ModelProvider.OPENAI,
            temperature=0.3,
            max_tokens=3000,
            tools=["portfolio_analysis", "risk_calculator", "performance_metrics"],
            system_prompt="""You are an expert portfolio analyst. Your role is to:
1. Analyze investment portfolios
2. Calculate risk metrics and returns
3. Identify optimization opportunities
4. Provide actionable recommendations
Be precise, data-driven, and consider multiple scenarios.""",
            knowledge_bases=[os.getenv("KB_FINANCE", "")],
            memory_enabled=True,
            memory_type="full"
        )
        
        # Risk Management Agent
        self.agents[AgentType.RISK.value] = AgentConfig(
            name="Risk Management Agent",
            agent_type=AgentType.RISK,
            description="Identifies and mitigates risks in financial portfolios",
            model=os.getenv("RISK_AGENT_MODEL", "gpt-4"),
            model_provider=ModelProvider.OPENAI,
            temperature=0.2,
            max_tokens=2500,
            tools=["risk_analysis", "stress_testing", "scenario_analysis", "correlation_analysis"],
            system_prompt="""You are a risk management specialist. Your responsibilities:
1. Identify financial risks
2. Assess probability and impact
3. Recommend mitigation strategies
4. Perform stress tests and scenario analysis
Focus on comprehensive risk assessment and practical solutions.""",
            knowledge_bases=[os.getenv("KB_RISK", "")],
            memory_enabled=True
        )
        
        # Market Analysis Agent
        self.agents[AgentType.MARKET.value] = AgentConfig(
            name="Market Analysis Agent",
            agent_type=AgentType.MARKET,
            description="Provides market insights and trend analysis",
            model=os.getenv("MARKET_AGENT_MODEL", "gpt-4"),
            model_provider=ModelProvider.OPENAI,
            temperature=0.5,
            max_tokens=2000,
            tools=["market_data", "trend_analysis", "sentiment_analysis", "technical_analysis"],
            system_prompt="""You are a market analyst expert. Your role includes:
1. Analyze market trends and dynamics
2. Provide sentiment analysis
3. Identify emerging opportunities
4. Track macroeconomic indicators
Be objective and cite data sources.""",
            knowledge_bases=[os.getenv("KB_MARKET", "")],
            memory_enabled=True
        )
        
        # Compliance Agent
        self.agents[AgentType.COMPLIANCE.value] = AgentConfig(
            name="Compliance Officer Agent",
            agent_type=AgentType.COMPLIANCE,
            description="Ensures compliance with financial regulations and policies",
            model=os.getenv("COMPLIANCE_AGENT_MODEL", "gpt-4"),
            model_provider=ModelProvider.OPENAI,
            temperature=0.1,
            max_tokens=2000,
            tools=["compliance_check", "regulation_lookup", "audit_trail", "policy_validator"],
            system_prompt="""You are a compliance officer. Your duties:
1. Verify regulatory compliance
2. Check policy adherence
3. Flag violations and risks
4. Provide compliance recommendations
Be strict and thorough in all assessments.""",
            knowledge_bases=[os.getenv("KB_COMPLIANCE", "")],
            memory_enabled=True,
            memory_type="full"
        )
        
        # Summarizer Agent
        self.agents[AgentType.SUMMARIZER.value] = AgentConfig(
            name="Content Summarizer Agent",
            agent_type=AgentType.SUMMARIZER,
            description="Summarizes financial documents and reports",
            model=os.getenv("SUMMARIZER_AGENT_MODEL", "gpt-3.5-turbo"),
            model_provider=ModelProvider.OPENAI,
            temperature=0.3,
            max_tokens=1000,
            tools=["text_extraction", "summarization", "key_points"],
            system_prompt="""You are a content summarizer. Your tasks:
1. Extract key information
2. Create concise summaries
3. Identify important metrics
4. Preserve critical details
Be clear, concise, and accurate.""",
            memory_enabled=False
        )
        
        # Researcher Agent
        self.agents[AgentType.RESEARCHER.value] = AgentConfig(
            name="Research Agent",
            agent_type=AgentType.RESEARCHER,
            description="Conducts research and gathers information",
            model=os.getenv("RESEARCHER_AGENT_MODEL", "gpt-4"),
            model_provider=ModelProvider.OPENAI,
            temperature=0.6,
            max_tokens=3000,
            tools=["web_search", "document_retrieval", "data_aggregation"],
            system_prompt="""You are a research specialist. Your role:
1. Conduct thorough research
2. Gather relevant information
3. Synthesize findings
4. Provide citations and sources
Be comprehensive and accurate.""",
            knowledge_bases=[os.getenv("KB_RESEARCH", "")],
            memory_enabled=True
        )
        
        # QA Agent
        self.agents[AgentType.QA.value] = AgentConfig(
            name="Q&A Agent",
            agent_type=AgentType.QA,
            description="Answers questions based on knowledge base",
            model=os.getenv("QA_AGENT_MODEL", "gpt-3.5-turbo"),
            model_provider=ModelProvider.OPENAI,
            temperature=0.4,
            max_tokens=1500,
            tools=["knowledge_retrieval", "question_answering"],
            system_prompt="""You are a helpful Q&A assistant. Your role:
1. Answer questions accurately
2. Use provided knowledge base
3. Admit when uncertain
4. Provide clear explanations
Be friendly and informative.""",
            knowledge_bases=[os.getenv("KB_GENERAL", "")],
            memory_enabled=True,
            memory_type="short_term"
        )
    
    def get_agent_config(self, agent_type: str) -> Optional[AgentConfig]:
        """Get configuration for specific agent type"""
        return self.agents.get(agent_type)
    
    def get_all_agent_types(self) -> List[str]:
        """Get list of all available agent types"""
        return list(self.agents.keys())
    
    def get_api_headers(self) -> Dict[str, str]:
        """Get HTTP headers for Dify API"""
        return {
            "Authorization": f"Bearer {self.api_config.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "RAG-ENTERPRISE/2.1.0"
        }
    
    def get_full_api_url(self, endpoint: str) -> str:
        """Get full API URL for endpoint"""
        base = self.api_config.base_url.rstrip('/')
        endpoint = endpoint.lstrip('/')
        return f"{base}/{endpoint}"
    
    @property
    def is_configured(self) -> bool:
        """Check if Dify is properly configured"""
        return bool(self.api_config.api_key and self.api_config.base_url)
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary"""
        return {
            "api": {
                "base_url": self.api_config.base_url,
                "api_version": self.api_config.api_version,
                "environment": self.api_config.environment.value
            },
            "agents": {
                name: config.to_dict() 
                for name, config in self.agents.items()
            }
        }


# Global instance
_dify_config: Optional[DifyConfig] = None


def get_dify_config() -> DifyConfig:
    """Get or create global Dify config instance"""
    global _dify_config
    if _dify_config is None:
        _dify_config = DifyConfig()
    return _dify_config


def reset_dify_config():
    """Reset global Dify config (for testing)"""
    global _dify_config
    _dify_config = None
