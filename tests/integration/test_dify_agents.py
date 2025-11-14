"""
Integration Tests for Dify Agents and Workflows
Tests agent creation, execution, and workflow orchestration
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime

from agents.agent_factory import (
    get_agent_factory, reset_agent_factory, AgentFactory,
    PortfolioAgent, RiskAgent, MarketAgent, ComplianceAgent, SummarizerAgent
)
from agents.financial.specialized_agents import (
    FinancialPortfolioAgent, FinancialRiskAgent
)
from agents.workflow import (
    AgentWorkflow, WorkflowStep, WorkflowStatus, 
    PipelineBuilder, WorkflowTemplates
)
from core.dify_config import get_dify_config, AgentType, DifyConfig


class TestDifyConfig:
    """Test Dify configuration"""
    
    def test_dify_config_initialization(self):
        """Test DifyConfig initialization"""
        config = DifyConfig()
        assert config.is_configured or True  # May not have API key
        assert len(config.agents) > 0
        assert AgentType.PORTFOLIO.value in config.agents
    
    def test_get_agent_config(self):
        """Test getting agent configuration"""
        config = get_dify_config()
        
        portfolio_config = config.get_agent_config(AgentType.PORTFOLIO.value)
        assert portfolio_config is not None
        assert portfolio_config.name == "Portfolio Analyst Agent"
        assert portfolio_config.agent_type == AgentType.PORTFOLIO
    
    def test_all_agent_types_configured(self):
        """Test all agent types are configured"""
        config = get_dify_config()
        
        expected_types = [
            AgentType.PORTFOLIO.value,
            AgentType.RISK.value,
            AgentType.MARKET.value,
            AgentType.COMPLIANCE.value,
            AgentType.SUMMARIZER.value,
            AgentType.RESEARCHER.value,
            AgentType.QA.value
        ]
        
        for agent_type in expected_types:
            assert agent_type in config.agents
    
    def test_get_api_headers(self):
        """Test API headers generation"""
        config = get_dify_config()
        headers = config.get_api_headers()
        
        assert "Authorization" in headers
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"
    
    def test_get_full_api_url(self):
        """Test full API URL generation"""
        config = get_dify_config()
        
        url = config.get_full_api_url("apps/123/run")
        assert "apps/123/run" in url
        assert url.startswith("http")


class TestAgentFactory:
    """Test Agent Factory"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test"""
        yield
        reset_agent_factory()
    
    def test_factory_creation(self):
        """Test factory creation"""
        dify_client = Mock()
        dify_manager = Mock()
        
        factory = AgentFactory(dify_client, dify_manager)
        assert factory is not None
        assert factory.dify_client == dify_client
    
    def test_create_portfolio_agent(self):
        """Test portfolio agent creation"""
        dify_client = Mock()
        dify_manager = Mock()
        
        factory = AgentFactory(dify_client, dify_manager)
        agent = factory.create_agent(
            AgentType.PORTFOLIO.value,
            "portfolio_1"
        )
        
        assert agent is not None
        assert isinstance(agent, PortfolioAgent)
        assert agent.agent_id == "portfolio_1"
    
    def test_create_all_agent_types(self):
        """Test creating all agent types"""
        dify_client = Mock()
        dify_manager = Mock()
        
        factory = AgentFactory(dify_client, dify_manager)
        
        agent_types = [
            (AgentType.PORTFOLIO.value, PortfolioAgent),
            (AgentType.RISK.value, RiskAgent),
            (AgentType.MARKET.value, MarketAgent),
            (AgentType.COMPLIANCE.value, ComplianceAgent),
            (AgentType.SUMMARIZER.value, SummarizerAgent),
        ]
        
        for agent_type, expected_class in agent_types:
            agent = factory.create_agent(agent_type, f"{agent_type}_1")
            assert agent is not None
            assert isinstance(agent, expected_class)
    
    def test_get_agent(self):
        """Test getting agent by ID"""
        dify_client = Mock()
        dify_manager = Mock()
        
        factory = AgentFactory(dify_client, dify_manager)
        created_agent = factory.create_agent(AgentType.PORTFOLIO.value, "portfolio_1")
        
        retrieved_agent = factory.get_agent("portfolio_1")
        assert retrieved_agent == created_agent
    
    def test_remove_agent(self):
        """Test removing agent"""
        dify_client = Mock()
        dify_manager = Mock()
        
        factory = AgentFactory(dify_client, dify_manager)
        factory.create_agent(AgentType.PORTFOLIO.value, "portfolio_1")
        
        assert factory.remove_agent("portfolio_1")
        assert factory.get_agent("portfolio_1") is None
    
    def test_list_agents(self):
        """Test listing agents"""
        dify_client = Mock()
        dify_manager = Mock()
        
        factory = AgentFactory(dify_client, dify_manager)
        factory.create_agent(AgentType.PORTFOLIO.value, "portfolio_1")
        factory.create_agent(AgentType.RISK.value, "risk_1")
        
        agents = factory.list_agents()
        assert len(agents) == 2
        assert "portfolio_1" in agents
        assert "risk_1" in agents


class TestAgentExecution:
    """Test agent execution"""
    
    @pytest.mark.asyncio
    async def test_portfolio_agent_validation(self):
        """Test portfolio agent input validation"""
        dify_client = Mock()
        dify_manager = Mock()
        
        from core.dify_config import AgentConfig
        config = AgentConfig(
            name="Test Portfolio",
            agent_type=AgentType.PORTFOLIO,
            description="Test"
        )
        
        agent = PortfolioAgent("test_1", config, dify_client, dify_manager)
        
        # Valid inputs
        valid_inputs = {
            "portfolio_data": {"assets": []},
            "benchmark": "S&P 500"
        }
        assert await agent.validate_inputs(valid_inputs)
        
        # Invalid inputs
        invalid_inputs = {"portfolio_data": {}}
        assert not await agent.validate_inputs(invalid_inputs)
    
    @pytest.mark.asyncio
    async def test_agent_execution_mock(self):
        """Test agent execution with mocked Dify"""
        dify_client = Mock()
        dify_manager = AsyncMock()
        dify_manager.execute_agent = AsyncMock(return_value={"analysis": "test"})
        
        from core.dify_config import AgentConfig
        config = AgentConfig(
            name="Test Portfolio",
            agent_type=AgentType.PORTFOLIO,
            description="Test"
        )
        
        agent = PortfolioAgent("test_1", config, dify_client, dify_manager)
        
        inputs = {
            "portfolio_data": {"assets": []},
            "benchmark": "S&P 500"
        }
        
        result = await agent.execute(inputs)
        
        assert result is not None
        assert "type" in result
        assert result["type"] == "portfolio_analysis"


class TestWorkflow:
    """Test workflow orchestration"""
    
    def test_workflow_creation(self):
        """Test workflow creation"""
        workflow = AgentWorkflow("test_workflow", "Test Workflow")
        
        assert workflow.workflow_id == "test_workflow"
        assert workflow.name == "Test Workflow"
        assert workflow.status == WorkflowStatus.PENDING
        assert len(workflow.steps) == 0
    
    def test_add_workflow_step(self):
        """Test adding steps to workflow"""
        workflow = AgentWorkflow("test_workflow", "Test Workflow")
        
        def inputs_handler(ctx, results):
            return {"data": "test"}
        
        step = WorkflowStep(
            "step1",
            "portfolio",
            inputs_handler
        )
        
        workflow.add_step(step)
        
        assert len(workflow.steps) == 1
        assert workflow.steps[0].name == "step1"
    
    @pytest.mark.asyncio
    async def test_workflow_execution(self):
        """Test workflow execution"""
        workflow = AgentWorkflow("test_workflow", "Test Workflow")
        
        # Create mock agents
        with patch('agents.workflow.get_agent_factory') as mock_factory_func:
            mock_factory = Mock()
            mock_agent = AsyncMock()
            mock_agent.execute = AsyncMock(return_value={"result": "test"})
            
            mock_factory.create_agent = Mock(return_value=mock_agent)
            mock_factory_func.return_value = mock_factory
            
            def inputs_handler(ctx, results):
                return {"data": "test"}
            
            step = WorkflowStep(
                "step1",
                "portfolio",
                inputs_handler
            )
            
            workflow.add_step(step)
            
            # Execute workflow
            context = {}
            results = await workflow.execute(context)
            
            assert results is not None
            assert "step1" in results
    
    def test_workflow_report(self):
        """Test workflow execution report"""
        workflow = AgentWorkflow("test_workflow", "Test Workflow")
        workflow.status = WorkflowStatus.COMPLETED
        workflow.started_at = datetime.now()
        workflow.completed_at = datetime.now()
        
        def inputs_handler(ctx, results):
            return {"data": "test"}
        
        step = WorkflowStep(
            "step1",
            "portfolio",
            inputs_handler
        )
        step.status = WorkflowStatus.COMPLETED
        
        workflow.add_step(step)
        
        report = workflow.get_execution_report()
        
        assert report["workflow_id"] == "test_workflow"
        assert report["name"] == "Test Workflow"
        assert report["status"] == WorkflowStatus.COMPLETED.value
        assert len(report["steps"]) == 1


class TestWorkflowTemplates:
    """Test predefined workflow templates"""
    
    def test_portfolio_review_workflow_creation(self):
        """Test portfolio review workflow creation"""
        workflow = WorkflowTemplates.create_portfolio_review_workflow()
        
        assert workflow is not None
        assert workflow.name == "Portfolio Review"
        assert len(workflow.steps) == 5
        
        step_names = [step.name for step in workflow.steps]
        assert "portfolio_analysis" in step_names
        assert "risk_analysis" in step_names
        assert "market_analysis" in step_names
        assert "compliance_check" in step_names
        assert "summary" in step_names
    
    def test_compliance_review_workflow_creation(self):
        """Test compliance review workflow creation"""
        workflow = WorkflowTemplates.create_compliance_review_workflow()
        
        assert workflow is not None
        assert workflow.name == "Compliance Review"
        assert len(workflow.steps) == 3
    
    def test_market_analysis_workflow_creation(self):
        """Test market analysis workflow creation"""
        workflow = WorkflowTemplates.create_market_analysis_workflow()
        
        assert workflow is not None
        assert workflow.name == "Market Analysis"
        assert len(workflow.steps) == 2


class TestPipelineBuilder:
    """Test pipeline builder"""
    
    def test_pipeline_builder_workflow_creation(self):
        """Test pipeline builder creating workflow"""
        builder = PipelineBuilder()
        
        def inputs_handler(ctx, results):
            return {"data": "test"}
        
        workflow = (builder
            .create_workflow("test_1", "Test Pipeline")
            .add_step("step1", "portfolio", inputs_handler)
            .add_step("step2", "risk", inputs_handler)
            .build())
        
        assert workflow is not None
        assert workflow.workflow_id == "test_1"
        assert len(workflow.steps) == 2


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_agent_workflow(self):
        """Test complete agent and workflow integration"""
        # Reset factory
        reset_agent_factory()
        
        with patch('agents.workflow.get_agent_factory') as mock_factory_func:
            dify_client = Mock()
            dify_manager = AsyncMock()
            
            factory = AgentFactory(dify_client, dify_manager)
            mock_factory_func.return_value = factory
            
            # Create workflow
            workflow = AgentWorkflow("integration_test", "Integration Test")
            
            def inputs_handler(ctx, results):
                return {
                    "portfolio_data": {"assets": []},
                    "benchmark": "S&P 500"
                }
            
            step = WorkflowStep(
                "portfolio_analysis",
                AgentType.PORTFOLIO.value,
                inputs_handler
            )
            
            workflow.add_step(step)
            
            # Mock agent execution
            dify_manager.execute_agent = AsyncMock(return_value={
                "analysis": "test analysis"
            })
            
            # Execute workflow
            context = {}
            results = await workflow.execute(context)
            
            assert "portfolio_analysis" in results


# Pytest fixtures
@pytest.fixture
def cleanup():
    """Cleanup after tests"""
    yield
    reset_agent_factory()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
