"""
Agent Workflow Orchestration
Manages complex workflows involving multiple agents
"""

from typing import Dict, List, Any, Optional, Callable
import asyncio
import logging
from datetime import datetime
from enum import Enum

from agents.agent_factory import get_agent_factory, BaseAgent

logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStep:
    """Single step in a workflow"""
    
    def __init__(
        self,
        name: str,
        agent_type: str,
        inputs_handler: Callable,
        on_success: Optional[Callable] = None,
        on_failure: Optional[Callable] = None,
        retries: int = 1
    ):
        """Initialize workflow step"""
        self.name = name
        self.agent_type = agent_type
        self.inputs_handler = inputs_handler
        self.on_success = on_success
        self.on_failure = on_failure
        self.retries = retries
        self.result = None
        self.status = WorkflowStatus.PENDING
        self.error = None


class AgentWorkflow:
    """
    Manages orchestration of multiple agents
    Supports sequential and parallel workflows
    """
    
    def __init__(self, workflow_id: str, name: str):
        """Initialize workflow"""
        self.workflow_id = workflow_id
        self.name = name
        self.steps: List[WorkflowStep] = []
        self.status = WorkflowStatus.PENDING
        self.results: Dict[str, Any] = {}
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def add_step(self, step: WorkflowStep) -> 'AgentWorkflow':
        """Add step to workflow"""
        self.steps.append(step)
        return self
    
    async def execute_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> bool:
        """
        Execute single workflow step
        
        Args:
            step: Workflow step to execute
            context: Execution context from previous steps
            
        Returns:
            True if successful, False otherwise
        """
        step.status = WorkflowStatus.RUNNING
        
        for attempt in range(step.retries):
            try:
                # Get agent factory
                factory = get_agent_factory()
                
                # Create agent
                agent = factory.create_agent(step.agent_type, f"{self.workflow_id}_{step.name}")
                if not agent:
                    raise Exception(f"Failed to create agent: {step.agent_type}")
                
                # Prepare inputs
                inputs = step.inputs_handler(context, self.results)
                
                # Execute agent
                self.logger.info(f"Executing step: {step.name}")
                step.result = await agent.execute(inputs)
                
                # Store result
                self.results[step.name] = step.result
                
                # Success callback
                if step.on_success:
                    await step.on_success(step.result, context)
                
                step.status = WorkflowStatus.COMPLETED
                return True
            
            except Exception as e:
                self.logger.error(f"Step {step.name} attempt {attempt + 1} failed: {e}")
                step.error = str(e)
                
                if attempt < step.retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    # All retries exhausted
                    if step.on_failure:
                        await step.on_failure(e, context)
                    step.status = WorkflowStatus.FAILED
                    return False
        
        return False
    
    async def execute(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute entire workflow
        
        Args:
            context: Initial context for workflow
            
        Returns:
            Workflow results
        """
        context = context or {}
        self.started_at = datetime.now()
        self.status = WorkflowStatus.RUNNING
        
        self.logger.info(f"Starting workflow: {self.name}")
        
        for step in self.steps:
            # Execute step
            success = await self.execute_step(step, context)
            
            if not success:
                self.status = WorkflowStatus.FAILED
                self.logger.error(f"Workflow {self.name} failed at step: {step.name}")
                return self.results
        
        self.completed_at = datetime.now()
        self.status = WorkflowStatus.COMPLETED
        
        self.logger.info(f"Workflow {self.name} completed successfully")
        
        return self.results
    
    def get_execution_report(self) -> Dict[str, Any]:
        """Get workflow execution report"""
        duration = None
        if self.started_at and self.completed_at:
            duration = (self.completed_at - self.started_at).total_seconds()
        
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": duration,
            "steps": [
                {
                    "name": step.name,
                    "agent_type": step.agent_type,
                    "status": step.status.value,
                    "error": step.error,
                    "result": step.result
                }
                for step in self.steps
            ],
            "results": self.results
        }


class PipelineBuilder:
    """Builder pattern for creating agent pipelines"""
    
    def __init__(self):
        """Initialize builder"""
        self.workflow_id = None
        self.workflow_name = None
        self.workflow: Optional[AgentWorkflow] = None
    
    def create_workflow(self, workflow_id: str, name: str) -> 'PipelineBuilder':
        """Create new workflow"""
        self.workflow_id = workflow_id
        self.workflow_name = name
        self.workflow = AgentWorkflow(workflow_id, name)
        return self
    
    def add_step(
        self,
        name: str,
        agent_type: str,
        inputs_handler: Callable
    ) -> 'PipelineBuilder':
        """Add step to workflow"""
        step = WorkflowStep(
            name=name,
            agent_type=agent_type,
            inputs_handler=inputs_handler
        )
        self.workflow.add_step(step)
        return self
    
    def build(self) -> AgentWorkflow:
        """Build and return workflow"""
        if not self.workflow:
            raise ValueError("No workflow created")
        return self.workflow


# Predefined Workflow Templates
class WorkflowTemplates:
    """Common workflow templates"""
    
    @staticmethod
    def create_portfolio_review_workflow() -> AgentWorkflow:
        """
        Create portfolio review workflow:
        1. Portfolio Analysis
        2. Risk Analysis
        3. Market Analysis
        4. Compliance Check
        5. Summary Report
        """
        workflow = AgentWorkflow("portfolio_review", "Portfolio Review")
        
        # Step 1: Portfolio Analysis
        def portfolio_inputs(ctx, results):
            return {
                "portfolio_data": ctx.get("portfolio"),
                "benchmark": ctx.get("benchmark", "S&P 500")
            }
        
        workflow.add_step(
            WorkflowStep(
                "portfolio_analysis",
                "portfolio",
                portfolio_inputs
            )
        )
        
        # Step 2: Risk Analysis
        def risk_inputs(ctx, results):
            return {
                "asset_data": ctx.get("portfolio", {}).get("assets", []),
                "time_horizon": ctx.get("time_horizon", "1y")
            }
        
        workflow.add_step(
            WorkflowStep(
                "risk_analysis",
                "risk",
                risk_inputs
            )
        )
        
        # Step 3: Market Analysis
        def market_inputs(ctx, results):
            return {
                "market_data": ctx.get("market_data", {}),
                "asset_type": "equity"
            }
        
        workflow.add_step(
            WorkflowStep(
                "market_analysis",
                "market",
                market_inputs
            )
        )
        
        # Step 4: Compliance Check
        def compliance_inputs(ctx, results):
            return {
                "transaction_data": ctx.get("portfolio", {}),
                "regulation_type": ctx.get("regulation", "general")
            }
        
        workflow.add_step(
            WorkflowStep(
                "compliance_check",
                "compliance",
                compliance_inputs
            )
        )
        
        # Step 5: Summarize
        def summary_inputs(ctx, results):
            summary_text = f"""
            Portfolio Analysis Summary:
            - Portfolio Analysis: {str(results.get('portfolio_analysis', 'N/A'))[:100]}
            - Risk Analysis: {str(results.get('risk_analysis', 'N/A'))[:100]}
            - Market Analysis: {str(results.get('market_analysis', 'N/A'))[:100]}
            - Compliance Status: {str(results.get('compliance_check', 'N/A'))[:100]}
            """
            return {"content": summary_text}
        
        workflow.add_step(
            WorkflowStep(
                "summary",
                "summarizer",
                summary_inputs
            )
        )
        
        return workflow
    
    @staticmethod
    def create_compliance_review_workflow() -> AgentWorkflow:
        """
        Create compliance review workflow:
        1. Compliance Check
        2. Risk Assessment
        3. Summary Report
        """
        workflow = AgentWorkflow("compliance_review", "Compliance Review")
        
        # Step 1: Compliance Check
        def compliance_inputs(ctx, results):
            return {
                "transaction_data": ctx.get("transaction", {}),
                "regulation_type": ctx.get("regulation", "general")
            }
        
        workflow.add_step(
            WorkflowStep(
                "compliance_check",
                "compliance",
                compliance_inputs
            )
        )
        
        # Step 2: Risk Assessment
        def risk_inputs(ctx, results):
            return {
                "asset_data": ctx.get("assets", []),
                "time_horizon": "1y"
            }
        
        workflow.add_step(
            WorkflowStep(
                "risk_assessment",
                "risk",
                risk_inputs
            )
        )
        
        # Step 3: Summary
        def summary_inputs(ctx, results):
            return {
                "content": f"Compliance Review: {str(results.get('compliance_check', 'N/A'))}"
            }
        
        workflow.add_step(
            WorkflowStep(
                "summary",
                "summarizer",
                summary_inputs
            )
        )
        
        return workflow
    
    @staticmethod
    def create_market_analysis_workflow() -> AgentWorkflow:
        """
        Create market analysis workflow:
        1. Market Analysis
        2. Summary Report
        """
        workflow = AgentWorkflow("market_analysis", "Market Analysis")
        
        # Step 1: Market Analysis
        def market_inputs(ctx, results):
            return {
                "market_data": ctx.get("market_data", {}),
                "asset_type": ctx.get("asset_type", "equity")
            }
        
        workflow.add_step(
            WorkflowStep(
                "market_analysis",
                "market",
                market_inputs
            )
        )
        
        # Step 2: Summary
        def summary_inputs(ctx, results):
            return {
                "content": f"Market Analysis: {str(results.get('market_analysis', 'N/A'))}"
            }
        
        workflow.add_step(
            WorkflowStep(
                "summary",
                "summarizer",
                summary_inputs
            )
        )
        
        return workflow
