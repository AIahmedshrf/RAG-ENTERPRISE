"""
Agents Module
Provides specialized agents for financial analysis and enterprise operations
"""

from agents.agent_factory import (
    get_agent_factory,
    reset_agent_factory,
    AgentFactory,
    BaseAgent,
    PortfolioAgent,
    RiskAgent,
    MarketAgent,
    ComplianceAgent,
    SummarizerAgent,
    ResearcherAgent,
    QAAgent
)

from agents.financial.specialized_agents import (
    FinancialPortfolioAgent,
    FinancialRiskAgent,
    FinancialMarketAgent,
    FinancialComplianceAgent,
    FinancialSummarizerAgent
)

from agents.workflow import (
    AgentWorkflow,
    WorkflowStep,
    WorkflowStatus,
    PipelineBuilder,
    WorkflowTemplates
)

__all__ = [
    # Factory
    "get_agent_factory",
    "reset_agent_factory",
    "AgentFactory",
    
    # Base Agent
    "BaseAgent",
    
    # Generic Agents
    "PortfolioAgent",
    "RiskAgent",
    "MarketAgent",
    "ComplianceAgent",
    "SummarizerAgent",
    "ResearcherAgent",
    "QAAgent",
    
    # Specialized Financial Agents
    "FinancialPortfolioAgent",
    "FinancialRiskAgent",
    "FinancialMarketAgent",
    "FinancialComplianceAgent",
    "FinancialSummarizerAgent",
    
    # Workflow
    "AgentWorkflow",
    "WorkflowStep",
    "WorkflowStatus",
    "PipelineBuilder",
    "WorkflowTemplates"
]
