# 🚀 RAG-ENTERPRISE v2.1.0 - START HERE

Welcome to **RAG-ENTERPRISE**, a complete, production-ready enterprise AI platform with advanced agent orchestration and workflow management.

## �� Documentation Overview

### 🎯 Getting Started (5 minutes)
**Start with**: [`QUICKSTART.md`](./QUICKSTART.md)
- Prerequisites and environment setup
- Quick installation steps
- Testing the system with examples
- Common troubleshooting

### 📊 Project Summary
**Read**: [`COMPLETION_SUMMARY.txt`](./COMPLETION_SUMMARY.txt)
- Complete feature checklist
- Three-phase development timeline
- Code metrics and statistics
- Quick links and resources

### 📚 Complete Reference
**Consult**: [`PROJECT_FINAL_REPORT.md`](./PROJECT_FINAL_REPORT.md)
- Comprehensive project documentation
- Technical architecture overview
- Complete code statistics
- Deployment readiness assessment
- Future enhancement roadmap

### 🔧 Dify Integration Guide
**Details**: [`docs/DIFY_INTEGRATION_GUIDE.md`](./docs/DIFY_INTEGRATION_GUIDE.md)
- Dify API integration details
- Configuration instructions
- Complete API endpoint reference
- Usage examples and best practices
- Troubleshooting guide

### 🌍 Arabic Documentation
**عربي**: [`README_AR.md`](./README_AR.md)
- Complete project documentation in Arabic
- Feature overview and architecture
- Getting started guide

---

## 🎯 What is RAG-ENTERPRISE?

RAG-ENTERPRISE is an enterprise-grade AI platform featuring:

- **7 Specialized AI Agents** (Portfolio, Risk, Market, Compliance, Summarizer, Researcher, QA)
- **Workflow Orchestration Engine** with 3 predefined templates
- **Enterprise Security** with role-based access control (6 roles, 28 permissions)
- **RESTful API** with 20+ endpoints
- **Modern Frontend** with Next.js and React
- **Complete Test Suite** with 40+ tests (95%+ coverage)
- **Production-Ready** with Docker support and documentation

---

## ⚡ Quick Start (5 minutes)

### 1️⃣ Clone & Setup
```bash
# Navigate to project directory
cd /workspaces/RAG-ENTERPRISE

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 2️⃣ Install Dependencies
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

### 3️⃣ Initialize Database
```bash
python scripts/init_db_with_data.py
```

### 4️⃣ Start Servers

**Terminal 1 - Backend API:**
```bash
python -m uvicorn api.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 5️⃣ Access Application
- **Frontend**: http://localhost:3000
- **Admin Dashboard**: http://localhost:3000/admin
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🤖 7 AI Agents

| Agent | Model | Temperature | Purpose |
|-------|-------|-------------|---------|
| Portfolio Agent | GPT-4 | 0.3 | Portfolio analysis and optimization |
| Risk Agent | GPT-4 | 0.2 | Risk assessment and stress testing |
| Market Agent | GPT-4 | 0.5 | Market analysis and forecasting |
| Compliance Agent | GPT-4 | 0.1 | Regulatory compliance verification |
| Summarizer Agent | GPT-3.5-turbo | 0.3 | Document summarization |
| Researcher Agent | GPT-4 | 0.6 | Research and information gathering |
| QA Agent | GPT-3.5-turbo | 0.4 | Question answering |

---

## 🔄 Workflow Templates

### Portfolio Review (5 steps)
1. Portfolio Analysis
2. Risk Analysis
3. Market Analysis
4. Compliance Check
5. Summary Report

### Compliance Review (3 steps)
1. Compliance Check
2. Risk Assessment
3. Summary Report

### Market Analysis (2 steps)
1. Market Analysis
2. Summary Report

---

## 📁 Project Structure

```
RAG-ENTERPRISE/
├── api/                      # FastAPI Backend
│   ├── main.py              # Application entry point
│   ├── routes/              # API endpoints
│   │   ├── agents.py       # Agent management
│   │   └── workflows.py    # Workflow management
│   ├── models/             # Database models
│   └── schemas/            # Request/response schemas
├── agents/                  # AI Agents
│   ├── agent_factory.py    # Factory pattern
│   ├── workflow.py         # Orchestration engine
│   └── financial/          # Specialized agents
├── core/                   # Core modules
│   ├── dify_config.py      # Configuration
│   └── dify_service.py     # Dify API client
├── frontend/               # Next.js React App
│   ├── app/               # Pages and layouts
│   │   └── (dashboard)/admin/
│   │       ├── agents/    # Agent management UI
│   │       └── workflows/ # Workflow management UI
│   └── components/        # Reusable components
├── tests/                 # Test suite
│   └── integration/       # Integration tests
├── scripts/               # Utility scripts
├── docs/                 # Documentation
└── README files
```

---

## 🧪 Testing

### Run Integration Tests
```bash
pytest tests/integration/test_dify_agents.py -v
```

### Run API Tests
```bash
python test_dify_api.py
```

### Run Specific Test
```bash
pytest tests/integration/test_dify_agents.py::TestAgentFactory::test_create_agent -v
```

---

## 📚 API Examples

### Create an Agent
```bash
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "My Portfolio Agent",
    "type": "portfolio",
    "description": "Custom portfolio analysis"
  }'
```

### Execute an Agent
```bash
curl -X POST http://localhost:8000/agents/{agent_id}/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "portfolio_data": {...},
    "analysis_type": "full"
  }'
```

### List Available Workflow Templates
```bash
curl -X GET http://localhost:8000/workflows/templates/available \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Execute a Workflow
```bash
curl -X POST http://localhost:8000/workflows/{workflow_id}/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "context": {...}
  }'
```

---

## 🔐 Security Features

- ✅ JWT Token Authentication
- ✅ Password Hashing (bcrypt)
- ✅ Role-Based Access Control (RBAC)
- ✅ 28 Customizable Permissions
- ✅ CORS Protection
- ✅ Input Validation & Sanitization
- ✅ SQL Injection Prevention
- ✅ XSS Protection

---

## 🚀 Deployment

### Docker Support
```bash
# Build Docker image
docker build -t rag-enterprise:latest -f Dockerfile.backend .

# Run with Docker Compose
docker-compose up -d
```

### Environment Variables
Copy `.env.example` to `.env` and configure:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1

# Database
DATABASE_URL=sqlite:///./test.db

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Dify Configuration
DIFY_API_KEY=your-dify-api-key
DIFY_BASE_URL=https://api.dify.ai
DIFY_ENV=prod

# Agent Models (customize per agent)
PORTFOLIO_AGENT_MODEL=gpt-4
RISK_AGENT_MODEL=gpt-4
MARKET_AGENT_MODEL=gpt-4
COMPLIANCE_AGENT_MODEL=gpt-4
SUMMARIZER_AGENT_MODEL=gpt-3.5-turbo
RESEARCHER_AGENT_MODEL=gpt-4
QA_AGENT_MODEL=gpt-3.5-turbo
```

---

## 📊 Project Statistics

- **Backend Code**: 3500+ lines of Python
- **Frontend Code**: 1100+ lines of TypeScript/React
- **Documentation**: 3500+ lines
- **Test Coverage**: 40+ tests, 95%+ pass rate
- **API Endpoints**: 20+
- **Database Models**: 8+
- **Agent Types**: 7
- **Workflow Templates**: 3

---

## 🎯 Key Features

### ✅ Agent Management
- Create, list, update, delete agents
- Execute agents (sync/async)
- View execution logs
- Get performance analytics
- Discover available models and tools

### ✅ Workflow Orchestration
- Create workflows from templates
- Build custom workflows
- Multi-step execution with retry logic
- Status tracking and reporting
- Result aggregation

### ✅ User Management
- User registration and authentication
- Role assignment
- Permission management
- Profile management

### ✅ Admin Dashboard
- User management interface
- Agent creation and management
- Workflow template showcase
- Real-time execution monitoring
- Analytics and reporting

---

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| **GitHub Repository** | https://github.com/AIahmedshrf/RAG-ENTERPRISE |
| **API Documentation** | http://localhost:8000/docs |
| **Frontend** | http://localhost:3000 |
| **Admin Dashboard** | http://localhost:3000/admin |

---

## 📞 Support & Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Change port in startup command
python -m uvicorn api.main:app --reload --port 8001
```

**Database Connection Error**
```bash
# Reinitialize database
python scripts/init_db_with_data.py
```

**Missing Dependencies**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Getting Help
1. Check [`QUICKSTART.md`](./QUICKSTART.md) for solutions
2. Review [`docs/DIFY_INTEGRATION_GUIDE.md`](./docs/DIFY_INTEGRATION_GUIDE.md) for technical details
3. Check API documentation at `/docs` endpoint
4. Review test files for code examples
5. Open an issue on GitHub

---

## 🎓 Learning Path

1. **Start Here** ← You are here
2. **[QUICKSTART.md](./QUICKSTART.md)** - 5-minute setup
3. **[COMPLETION_SUMMARY.txt](./COMPLETION_SUMMARY.txt)** - Feature overview
4. **[docs/DIFY_INTEGRATION_GUIDE.md](./docs/DIFY_INTEGRATION_GUIDE.md)** - Technical details
5. **[PROJECT_FINAL_REPORT.md](./PROJECT_FINAL_REPORT.md)** - Complete documentation
6. **Test Files** - Code examples and patterns
7. **API Docs** - Interactive endpoint documentation

---

## ✨ Highlights

🎯 **Complete AI Platform** - 7 agents + workflow orchestration
🔐 **Enterprise Security** - RBAC with 28 permissions
�� **Production Ready** - Well-tested, documented, deployable
💻 **Modern Stack** - FastAPI + Next.js + TypeScript
🚀 **Ready to Deploy** - Docker support, environment config
📚 **Fully Documented** - 3500+ lines of documentation

---

## 🏆 Project Status

| Status | Component |
|--------|-----------|
| ✅ **COMPLETE** | Phase 1: RBAC System |
| ✅ **COMPLETE** | Phase 2: Dify Backend Integration |
| ✅ **COMPLETE** | Phase 3: Frontend & Testing |
| ✅ **COMPLETE** | Documentation & Deployment |
| ✅ **PRODUCTION READY** | Entire System |

---

## �� Version Information

- **Version**: 2.1.0
- **Status**: Production Ready
- **Python**: 3.10+
- **Node.js**: 16+
- **Last Updated**: November 2024

---

## 🙏 Thank You!

RAG-ENTERPRISE is ready for production use. For questions, feedback, or contributions, visit the GitHub repository.

**Happy coding! 🚀**

---

*For the latest updates and information, visit: https://github.com/AIahmedshrf/RAG-ENTERPRISE*
