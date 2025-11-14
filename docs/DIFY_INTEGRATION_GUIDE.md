# Dify Integration Guide - RAG-ENTERPRISE Phase 3

## Overview

This document describes the Dify integration for RAG-ENTERPRISE, enabling advanced AI-powered agent workflows for financial analysis and enterprise operations.

## Architecture

### 1. Core Components

#### `core/dify_config.py`
- **DifyConfig**: Centralized configuration manager
- **AgentConfig**: Individual agent configurations
- **DifyAPIConfig**: API connection settings
- **AgentType & ModelProvider**: Enums for agent types and LLM providers

#### `core/dify_service.py`
- **DifyClient**: Low-level API client for Dify
- **DifyServiceManager**: High-level service manager for agent operations

#### `agents/agent_factory.py`
- **AgentFactory**: Factory pattern for creating agent instances
- **BaseAgent & Specialized Agents**: Agent implementations
  - `PortfolioAgent`: Portfolio analysis
  - `RiskAgent`: Risk management
  - `MarketAgent`: Market analysis
  - `ComplianceAgent`: Compliance verification
  - `SummarizerAgent`: Document summarization
  - `ResearcherAgent`: Research operations
  - `QAAgent`: Question answering

#### `agents/financial/specialized_agents.py`
- **Enhanced agent implementations** with financial-specific logic
- Pre-processing and post-processing of financial data
- Integration with financial tools and calculations

#### `agents/workflow.py`
- **AgentWorkflow**: Orchestrates multi-agent workflows
- **WorkflowStep**: Individual workflow steps
- **WorkflowTemplates**: Predefined workflow templates
- **PipelineBuilder**: Builder pattern for custom workflows

### 2. Supported Agent Types

```
PORTFOLIO     - Portfolio Analysis Agent
RISK          - Risk Management Agent
MARKET        - Market Analysis Agent
COMPLIANCE    - Compliance Officer Agent
SUMMARIZER    - Content Summarizer Agent
RESEARCHER    - Research Agent
QA            - Question & Answer Agent
```

### 3. Available Workflow Templates

#### Portfolio Review
5-step workflow:
1. Portfolio Analysis
2. Risk Analysis
3. Market Analysis
4. Compliance Check
5. Summary Report

#### Compliance Review
3-step workflow:
1. Compliance Check
2. Risk Assessment
3. Summary Report

#### Market Analysis
2-step workflow:
1. Market Analysis
2. Summary Report

## Configuration

### Environment Variables

Set the following in `.env`:

```bash
# Dify API Configuration
DIFY_API_KEY=your-dify-api-key
DIFY_BASE_URL=http://localhost:8001/api
DIFY_ENV=development

# LLM Model Selection
PORTFOLIO_AGENT_MODEL=gpt-4
RISK_AGENT_MODEL=gpt-4
MARKET_AGENT_MODEL=gpt-4
COMPLIANCE_AGENT_MODEL=gpt-4
SUMMARIZER_AGENT_MODEL=gpt-3.5-turbo
RESEARCHER_AGENT_MODEL=gpt-4
QA_AGENT_MODEL=gpt-3.5-turbo

# Knowledge Base IDs
KB_FINANCE=<knowledge-base-id>
KB_RISK=<knowledge-base-id>
KB_MARKET=<knowledge-base-id>
KB_COMPLIANCE=<knowledge-base-id>
KB_RESEARCH=<knowledge-base-id>
KB_GENERAL=<knowledge-base-id>

# Agent Settings
AGENT_MEMORY_ENABLED=true
AGENT_MEMORY_TYPE=full
AGENT_MAX_TOKENS=2000
AGENT_TEMPERATURE=0.7
```

### Dify Configuration

1. **Install Dify** (Self-hosted or Cloud)
   ```bash
   docker-compose up -d
   ```

2. **Configure API Key**
   - Get from Dify Dashboard
   - Set `DIFY_API_KEY` environment variable

3. **Create Knowledge Bases**
   - Financial KB
   - Risk KB
   - Market KB
   - Compliance KB

4. **Set LLM Models**
   - Configure OpenAI, Azure, or other providers in Dify

## API Endpoints

### Agent Management

#### Create Agent
```bash
POST /agents
Headers: Authorization: Bearer <token>
Body: {
  "name": "Portfolio Analyst",
  "agent_type": "portfolio",
  "description": "Analyzes investment portfolios"
}
```

#### List Agents
```bash
GET /agents
```

#### Execute Agent
```bash
POST /agents/{agent_id}/execute
Body: {
  "inputs": {
    "portfolio_data": {...},
    "benchmark": "S&P 500"
  }
}
```

#### Execute Agent Async
```bash
POST /agents/{agent_id}/execute-async?webhook_url=<callback>
```

### Workflow Management

#### Create from Template
```bash
POST /workflows/from-template
Body: {
  "template_type": "portfolio_review"
}
```

#### Create Custom Workflow
```bash
POST /workflows/custom?workflow_name=My Workflow
```

#### Add Step to Workflow
```bash
POST /workflows/{workflow_id}/add-step
Body: {
  "name": "portfolio_analysis",
  "agent_type": "portfolio"
}
```

#### Execute Workflow
```bash
POST /workflows/{workflow_id}/execute
Body: {
  "workflow_id": "...",
  "context": {
    "portfolio": {...},
    "benchmark": "S&P 500"
  }
}
```

#### Get Available Templates
```bash
GET /workflows/templates/available
```

#### Preview Template
```bash
GET /workflows/templates/{template_type}/preview
```

## Usage Examples

### 1. Simple Agent Execution

```python
from agents import get_agent_factory
from core.dify_service import get_dify_client

# Get factory
factory = get_agent_factory()

# Create agent
agent = factory.create_agent("portfolio", "portfolio_1")

# Execute
result = await agent.execute({
    "portfolio_data": {
        "assets": [
            {"symbol": "AAPL", "weight": 0.4, "shares": 100},
            {"symbol": "MSFT", "weight": 0.6, "shares": 50}
        ]
    },
    "benchmark": "S&P 500"
})

print(result)
```

### 2. Workflow Execution

```python
from agents import WorkflowTemplates

# Get template
workflow = WorkflowTemplates.create_portfolio_review_workflow()

# Execute
results = await workflow.execute({
    "portfolio": {...},
    "market_data": {...},
    "benchmark": "S&P 500"
})

# Get report
report = workflow.get_execution_report()
print(report)
```

### 3. Custom Workflow

```python
from agents import PipelineBuilder

builder = PipelineBuilder()

def portfolio_inputs(ctx, results):
    return {"portfolio_data": ctx.get("portfolio")}

def risk_inputs(ctx, results):
    return {"asset_data": ctx.get("assets")}

workflow = (builder
    .create_workflow("custom_1", "Custom Analysis")
    .add_step("portfolio", "portfolio", portfolio_inputs)
    .add_step("risk", "risk", risk_inputs)
    .build())

results = await workflow.execute(context)
```

## Testing

Run integration tests:

```bash
pytest tests/integration/test_dify_agents.py -v
```

### Test Coverage

- DifyConfig initialization and agent configuration
- AgentFactory creation and management
- Agent execution with mock Dify
- Workflow orchestration
- Template-based workflows
- Pipeline builder

## Performance Considerations

### Agent Configuration

- **Portfolio Agent**: Higher temperature for creative analysis
- **Compliance Agent**: Lower temperature for strict checking
- **Summarizer**: Faster model (GPT-3.5) to reduce latency

### Workflow Optimization

1. **Parallel Execution**: Steps can run in parallel where independent
2. **Caching**: Cache agent results for repeated queries
3. **Timeout Management**: Set appropriate timeouts for Dify calls
4. **Retry Logic**: Exponential backoff for failed steps

### Memory Management

- **Full Memory**: For complex, multi-turn workflows
- **Summary Memory**: For long conversations
- **Short-term Memory**: For simple, single-turn operations

## Monitoring & Logging

### Available Logs

```python
# Import logger
from utilities.logger import get_logger

logger = get_logger(__name__)

# Automatic logging
# - Agent creation
# - Workflow execution
# - API calls
# - Errors and exceptions
```

### Analytics Endpoints

```bash
GET /agents/{agent_id}/analytics?start_date=2024-01-01&end_date=2024-12-31
GET /agents/{agent_id}/logs?limit=20&offset=0
```

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Ensure `DIFY_API_KEY` is set
   - Check `.env` file

2. **Connection Timeout**
   - Verify Dify is running
   - Check `DIFY_BASE_URL`
   - Increase timeout in config

3. **Agent Validation Fails**
   - Check input format matches agent requirements
   - Review agent config for required fields

4. **Workflow Execution Slow**
   - Check step dependencies
   - Consider parallel execution
   - Optimize model selection

## Best Practices

1. **Agent Reusability**: Create agents once, reuse instances
2. **Context Management**: Pass minimal necessary context
3. **Error Handling**: Implement retry logic for network failures
4. **Monitoring**: Log all agent executions for debugging
5. **Security**: Keep API keys in environment variables
6. **Testing**: Write tests for custom agents
7. **Documentation**: Document custom agent behaviors

## Next Steps

1. **Dify Dashboard**: Create and test workflows in Dify UI
2. **Knowledge Bases**: Upload domain-specific documents
3. **Custom Agents**: Implement specialized agents for your domain
4. **Frontend Integration**: Build UI for agent management
5. **Production Deployment**: Set up Dify in production environment

## References

- [Dify Documentation](https://docs.dify.ai)
- [RAG-ENTERPRISE Docs](../README.md)
- [Agent API Reference](./api-reference.md)

## Support

For issues or questions:
1. Check logs: `tail -f /tmp/rag-enterprise/logs/api.log`
2. Review Dify logs: `docker logs dify`
3. Test endpoints: Use Swagger `/docs`
4. Report issues: GitHub Issues

---

Last Updated: 2024-11-14
Phase: 3 (Dify Integration)
Status: Complete
