# RAG-ENTERPRISE Phase 3: Dify Integration - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (optional, for Dify)
- Access to LLM API (OpenAI, Azure, etc.)

### Step 1: Environment Setup

```bash
# Clone and enter project
cd /workspaces/RAG-ENTERPRISE

# Copy and configure environment
cp .env.example .env

# Edit .env with your credentials:
# - DIFY_API_KEY: Your Dify API key
# - DIFY_BASE_URL: Dify instance URL
# - OpenAI/Azure credentials for LLM models
```

### Step 2: Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db_with_data.py

# Start API server
python -m uvicorn api.main:app --reload --port 8000
```

### Step 3: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Step 4: Access the Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:3000/admin

## 📚 Key Features Overview

### Agent Management (`/admin/agents`)
- ✅ Create agents (7 types: Portfolio, Risk, Market, Compliance, Summarizer, Researcher, QA)
- ✅ List all agents with status
- ✅ Execute agents with custom inputs
- ✅ View execution results and metrics
- ✅ Delete agents

### Workflow Management (`/admin/workflows`)
- ✅ 3 Predefined templates
  - **Portfolio Review**: 5-step comprehensive analysis
  - **Compliance Review**: 3-step verification workflow
  - **Market Analysis**: 2-step market analysis
- ✅ Create workflows from templates
- ✅ Execute workflows with context
- ✅ View workflow results

### Agent Execution (`/admin/agents/[id]`)
- ✅ Dynamic input parameters based on agent type
- ✅ Real-time execution with progress
- ✅ Formatted result display
- ✅ Execution metrics (duration, timestamp)

## 🧪 Testing API Endpoints

### Quick Test Script

```bash
# Run all API tests
python test_dify_api.py

# Or test with curl
curl -X GET "http://localhost:8000/api/agents" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Example Agent Execution

```bash
# Create a portfolio agent
curl -X POST "http://localhost:8000/api/agents" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "My Portfolio Agent",
    "agent_type": "portfolio",
    "description": "Analyzes my portfolio"
  }'

# Execute the agent
curl -X POST "http://localhost:8000/api/agents/{agent_id}/execute" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "inputs": {
      "portfolio_data": {
        "assets": [
          {"symbol": "AAPL", "weight": 0.4},
          {"symbol": "MSFT", "weight": 0.6}
        ]
      },
      "benchmark": "S&P 500"
    }
  }'
```

### Example Workflow Execution

```bash
# Create workflow from template
curl -X POST "http://localhost:8000/api/workflows/from-template" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "template_type": "portfolio_review"
  }'

# Execute workflow
curl -X POST "http://localhost:8000/api/workflows/{workflow_id}/execute" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "workflow_id": "{workflow_id}",
    "context": {
      "portfolio": {
        "assets": [...]
      },
      "benchmark": "S&P 500"
    }
  }'
```

## 🔧 Agent Types & Configuration

### Available Agents

| Agent | Purpose | Model | Temperature | Input |
|-------|---------|-------|-------------|-------|
| Portfolio | Portfolio analysis & optimization | gpt-4 | 0.3 | portfolio_data, benchmark |
| Risk | Risk assessment & stress testing | gpt-4 | 0.2 | asset_data, time_horizon |
| Market | Market analysis & trends | gpt-4 | 0.5 | market_data, asset_type |
| Compliance | Regulatory compliance checks | gpt-4 | 0.1 | transaction_data, regulation |
| Summarizer | Document summarization | gpt-3.5-turbo | 0.3 | content |
| Researcher | Research & information gathering | gpt-4 | 0.6 | query, topic |
| QA | Question answering | gpt-3.5-turbo | 0.4 | question |

### Customizing Agent Configuration

Edit `core/dify_config.py` to customize:
- LLM model selection
- Temperature & token limits
- Knowledge bases
- Memory settings
- System prompts

## 📊 Project Structure

```
RAG-ENTERPRISE/
├── api/                          # FastAPI backend
│   ├── main.py                  # Main app & route registration
│   ├── routes/
│   │   ├── agents.py            # Agent management endpoints
│   │   └── workflows.py         # Workflow management endpoints
│   ├── models/                  # Database models
│   └── database.py              # Database configuration
├── core/
│   ├── dify_config.py           # Dify configuration & agent configs
│   ├── dify_service.py          # Dify API client
│   └── auth.py                  # Authentication
├── agents/
│   ├── agent_factory.py         # Agent factory pattern
│   ├── workflow.py              # Workflow orchestration
│   └── financial/
│       └── specialized_agents.py # Financial agent implementations
├── frontend/
│   ├── app/(dashboard)/admin/
│   │   ├── agents/              # Agent management UI
│   │   │   ├── page.tsx         # Agent list & create
│   │   │   └── [id]/page.tsx    # Agent execution
│   │   └── workflows/
│   │       └── page.tsx         # Workflow management UI
│   └── lib/api-constants.ts     # API configuration
├── tests/
│   └── integration/
│       └── test_dify_agents.py  # Integration tests
└── test_dify_api.py             # Quick API testing script
```

## 🔐 Authentication

The system uses JWT token-based authentication:

```typescript
// Get token from login
const token = localStorage.getItem('access_token');

// Use in API calls
const response = await fetch('/api/agents', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## 📈 Monitoring & Logs

### Check Logs

```bash
# API logs
tail -f /tmp/rag-enterprise/logs/api.log

# Dify logs (if Docker)
docker logs dify
```

### Monitor Agents

```bash
# Get agent metrics
curl -X GET "http://localhost:8000/api/agents/{agent_id}/analytics" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get execution logs
curl -X GET "http://localhost:8000/api/agents/{agent_id}/logs" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🐛 Troubleshooting

### API Connection Issues
```bash
# Check if API is running
curl http://localhost:8000/health/health

# Test database connection
python -c "from api.database import check_database_health; print(check_database_health())"
```

### Dify Connection Issues
```bash
# Check Dify API availability
curl -X GET "http://localhost:8001/api/apps" \
  -H "Authorization: Bearer YOUR_DIFY_KEY"
```

### Frontend Issues
```bash
# Clear cache and reinstall
rm -rf frontend/node_modules frontend/.next
cd frontend && npm install && npm run dev
```

## 📚 Documentation Files

- **[DIFY_INTEGRATION_GUIDE.md](./docs/DIFY_INTEGRATION_GUIDE.md)** - Complete Dify integration documentation
- **[README.md](./README.md)** - Project overview
- **[PROJECT_STATUS.md](./docs/PROJECT_STATUS.md)** - Development status

## 🎯 Next Steps

### Immediate
1. ✅ Setup environment variables
2. ✅ Start backend & frontend
3. ✅ Test agent creation and execution
4. ✅ Run workflow templates

### Short Term
1. Configure knowledge bases with your data
2. Fine-tune agent parameters for your use case
3. Create custom agents if needed
4. Setup monitoring and alerts

### Long Term
1. Deploy to production environment
2. Integrate with external data sources
3. Build custom dashboards
4. Implement advanced analytics

## 📞 Support Resources

- 📖 [API Documentation](http://localhost:8000/docs)
- 🔧 [Dify Documentation](https://docs.dify.ai)
- 💬 [GitHub Issues](https://github.com/AIahmedshrf/RAG-ENTERPRISE/issues)
- 📧 Contact: Your support email

## ✅ Checklist Before Production

- [ ] Environment variables configured
- [ ] Database initialized
- [ ] LLM models configured in Dify
- [ ] Knowledge bases created
- [ ] API endpoints tested
- [ ] Frontend pages accessible
- [ ] Authentication working
- [ ] Agents can be created and executed
- [ ] Workflows execute successfully
- [ ] Logs are being recorded

## 📝 License

RAG-ENTERPRISE © 2024

---

**Version**: 2.1.0 | **Phase**: 3 - Dify Integration | **Status**: Production Ready
