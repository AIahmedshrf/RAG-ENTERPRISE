"""
Agent Factory Pattern
Creates and manages specialized agent instances
"""

from typing import Dict, Optional, Any
import logging
from abc import ABC, abstractmethod

from core.dify_config import (
    get_dify_config, AgentType, AgentConfig, DifyConfig
)
from core.dify_service import DifyClient, DifyServiceManager

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(
        self,
        agent_id: str,
        config: AgentConfig,
        dify_client: DifyClient,
        dify_manager: DifyServiceManager
    ):
        """Initialize agent"""
        self.agent_id = agent_id
        self.config = config
        self.dify_client = dify_client
        self.dify_manager = dify_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent with inputs"""
        pass
    
    @abstractmethod
    async def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.config.name,
            "type": self.config.agent_type.value,
            "model": self.config.model,
            "status": "ready"
        }


class PortfolioAgent(BaseAgent):
    """Portfolio Analysis Agent"""
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute portfolio analysis"""
        self.logger.info(f"Portfolio Agent executing: {inputs}")
        
        # Validate inputs
        if not await self.validate_inputs(inputs):
            return {"error": "Invalid portfolio data"}
        
        # Execute via Dify
        result = await self.dify_manager.execute_agent(
            app_id=self.agent_id,
            inputs=inputs
        )
        
        return {
            "type": "portfolio_analysis",
            "result": result,
            "agent": "portfolio"
        }
    
    async def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate portfolio inputs"""
        required = ["portfolio_data", "benchmark"]
        return all(key in inputs for key in required)


class RiskAgent(BaseAgent):
    """Risk Management Agent"""
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute risk analysis"""
        self.logger.info(f"Risk Agent executing: {inputs}")
        
        if not await self.validate_inputs(inputs):
            return {"error": "Invalid risk analysis data"}
        
        result = await self.dify_manager.execute_agent(
            app_id=self.agent_id,
            inputs=inputs
        )
        
        return {
            "type": "risk_analysis",
            "result": result,
            "agent": "risk"
        }
    
    async def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate risk inputs"""
        required = ["asset_data", "time_horizon"]
        return all(key in inputs for key in required)


class MarketAgent(BaseAgent):
    """Market Analysis Agent"""
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute market analysis"""
        self.logger.info(f"Market Agent executing: {inputs}")
        
        if not await self.validate_inputs(inputs):
            return {"error": "Invalid market data"}
        
        result = await self.dify_manager.execute_agent(
            app_id=self.agent_id,
            inputs=inputs
        )
        
        return {
            "type": "market_analysis",
            "result": result,
            "agent": "market"
        }
    
    async def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate market inputs"""
        required = ["market_data", "asset_type"]
        return all(key in inputs for key in required)


class ComplianceAgent(BaseAgent):
    """Compliance Officer Agent"""
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute compliance check"""
        self.logger.info(f"Compliance Agent executing: {inputs}")
        
        if not await self.validate_inputs(inputs):
            return {"error": "Invalid compliance data"}
        
        result = await self.dify_manager.execute_agent(
            app_id=self.agent_id,
            inputs=inputs
        )
        
        return {
            "type": "compliance_check",
            "result": result,
            "agent": "compliance"
        }
    
    async def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate compliance inputs"""
        required = ["transaction_data", "regulation_type"]
        return all(key in inputs for key in required)


class SummarizerAgent(BaseAgent):
    """Content Summarizer Agent"""
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute summarization"""
        self.logger.info(f"Summarizer Agent executing: {inputs}")
        
        if not await self.validate_inputs(inputs):
            return {"error": "Invalid content data"}
        
        result = await self.dify_manager.execute_agent(
            app_id=self.agent_id,
            inputs=inputs
        )
        
        return {
            "type": "summarization",
            "result": result,
            "agent": "summarizer"
        }
    
    async def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate summarizer inputs"""
        required = ["content"]
        return all(key in inputs for key in required)


class ResearcherAgent(BaseAgent):
    """Research Agent"""
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research"""
        self.logger.info(f"Researcher Agent executing: {inputs}")
        
        if not await self.validate_inputs(inputs):
            return {"error": "Invalid research query"}
        
        result = await self.dify_manager.execute_agent(
            app_id=self.agent_id,
            inputs=inputs
        )
        
        return {
            "type": "research",
            "result": result,
            "agent": "researcher"
        }
    
    async def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate research inputs"""
        required = ["query", "topic"]
        return all(key in inputs for key in required)


class QAAgent(BaseAgent):
    """Q&A Agent"""
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Q&A"""
        self.logger.info(f"QA Agent executing: {inputs}")
        
        if not await self.validate_inputs(inputs):
            return {"error": "Invalid question"}
        
        result = await self.dify_manager.execute_agent(
            app_id=self.agent_id,
            inputs=inputs
        )
        
        return {
            "type": "question_answer",
            "result": result,
            "agent": "qa"
        }
    
    async def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate QA inputs"""
        required = ["question"]
        return all(key in inputs for key in required)


class AgentFactory:
    """
    Factory for creating agent instances
    Manages agent lifecycle and instantiation
    """
    
    # Agent class mapping
    AGENT_CLASSES = {
        AgentType.PORTFOLIO.value: PortfolioAgent,
        AgentType.RISK.value: RiskAgent,
        AgentType.MARKET.value: MarketAgent,
        AgentType.COMPLIANCE.value: ComplianceAgent,
        AgentType.SUMMARIZER.value: SummarizerAgent,
        AgentType.RESEARCHER.value: ResearcherAgent,
        AgentType.QA.value: QAAgent,
    }
    
    def __init__(
        self,
        dify_client: DifyClient,
        dify_manager: DifyServiceManager
    ):
        """Initialize factory"""
        self.dify_client = dify_client
        self.dify_manager = dify_manager
        self.dify_config = get_dify_config()
        self.logger = logging.getLogger(__name__)
        self._agent_instances: Dict[str, BaseAgent] = {}
    
    def create_agent(
        self,
        agent_type: str,
        agent_id: str,
        custom_config: Optional[AgentConfig] = None
    ) -> Optional[BaseAgent]:
        """
        Create agent instance
        
        Args:
            agent_type: Type of agent to create
            agent_id: Unique ID for this agent instance
            custom_config: Optional custom configuration
            
        Returns:
            Agent instance or None if creation fails
        """
        try:
            # Get agent configuration
            config = custom_config or self.dify_config.get_agent_config(agent_type)
            if not config:
                self.logger.error(f"No config found for agent type: {agent_type}")
                return None
            
            # Get agent class
            agent_class = self.AGENT_CLASSES.get(agent_type)
            if not agent_class:
                self.logger.error(f"No class registered for agent type: {agent_type}")
                return None
            
            # Create agent instance
            agent = agent_class(
                agent_id=agent_id,
                config=config,
                dify_client=self.dify_client,
                dify_manager=self.dify_manager
            )
            
            self._agent_instances[agent_id] = agent
            self.logger.info(f"Agent created: {agent_type} ({agent_id})")
            
            return agent
        
        except Exception as e:
            self.logger.error(f"Error creating agent: {e}")
            return None
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent instance by ID"""
        return self._agent_instances.get(agent_id)
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove agent instance"""
        if agent_id in self._agent_instances:
            del self._agent_instances[agent_id]
            return True
        return False
    
    def list_agents(self) -> Dict[str, BaseAgent]:
        """List all agent instances"""
        return self._agent_instances.copy()
    
    def get_available_agent_types(self) -> list:
        """Get list of available agent types"""
        return list(self.AGENT_CLASSES.keys())


# Global factory instance
_factory_instance: Optional[AgentFactory] = None


def get_agent_factory(
    dify_client: Optional[DifyClient] = None,
    dify_manager: Optional[DifyServiceManager] = None
) -> AgentFactory:
    """Get or create global agent factory"""
    global _factory_instance
    
    if _factory_instance is None:
        if dify_client is None:
            from core.dify_service import get_dify_client
            dify_client = get_dify_client()
        
        if dify_manager is None:
            dify_manager = DifyServiceManager(dify_client)
        
        _factory_instance = AgentFactory(dify_client, dify_manager)
    
    return _factory_instance


def reset_agent_factory():
    """Reset global agent factory (for testing)"""
    global _factory_instance
    _factory_instance = None
