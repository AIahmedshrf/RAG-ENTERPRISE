"""
Quick API Testing Script
Tests Dify agents and workflows endpoints
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000/api"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer test-token"  # Replace with actual token
}

async def test_agent_endpoints():
    """Test agent management endpoints"""
    async with aiohttp.ClientSession() as session:
        print("\n" + "="*60)
        print("TESTING AGENT ENDPOINTS")
        print("="*60)

        # 1. List Agents
        print("\n1. GET /agents - List agents")
        try:
            async with session.get(f"{BASE_URL}/agents", headers=HEADERS) as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")

        # 2. Create Agent
        print("\n2. POST /agents - Create agent")
        try:
            payload = {
                "name": "Test Portfolio Agent",
                "agent_type": "portfolio",
                "description": "Test agent for portfolio analysis"
            }
            async with session.post(
                f"{BASE_URL}/agents",
                headers=HEADERS,
                json=payload
            ) as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                
                agent_id = data.get("data", {}).get("id")
                return agent_id
        except Exception as e:
            print(f"   Error: {e}")
            return None


async def test_workflow_endpoints():
    """Test workflow management endpoints"""
    async with aiohttp.ClientSession() as session:
        print("\n" + "="*60)
        print("TESTING WORKFLOW ENDPOINTS")
        print("="*60)

        # 1. Get Available Templates
        print("\n1. GET /workflows/templates/available - List templates")
        try:
            async with session.get(
                f"{BASE_URL}/workflows/templates/available",
                headers=HEADERS
            ) as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Templates: {list(data.get('data', {}).keys())}")
        except Exception as e:
            print(f"   Error: {e}")

        # 2. Preview Template
        print("\n2. GET /workflows/templates/portfolio_review/preview - Preview template")
        try:
            async with session.get(
                f"{BASE_URL}/workflows/templates/portfolio_review/preview",
                headers=HEADERS
            ) as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Steps: {data.get('data', {}).get('steps', [])}")
        except Exception as e:
            print(f"   Error: {e}")

        # 3. Create from Template
        print("\n3. POST /workflows/from-template - Create from template")
        try:
            payload = {
                "template_type": "portfolio_review"
            }
            async with session.post(
                f"{BASE_URL}/workflows/from-template",
                headers=HEADERS,
                json=payload
            ) as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Workflow ID: {data.get('data', {}).get('workflow_id')}")
                workflow_id = data.get('data', {}).get('workflow_id')
                return workflow_id
        except Exception as e:
            print(f"   Error: {e}")
            return None


async def test_agent_execution(agent_id: str):
    """Test agent execution"""
    async with aiohttp.ClientSession() as session:
        print("\n" + "="*60)
        print("TESTING AGENT EXECUTION")
        print("="*60)

        # 1. Execute Agent (Sync)
        print(f"\n1. POST /agents/{agent_id}/execute - Execute agent (sync)")
        try:
            payload = {
                "inputs": {
                    "portfolio_data": {
                        "assets": [
                            {"symbol": "AAPL", "weight": 0.4},
                            {"symbol": "MSFT", "weight": 0.6}
                        ]
                    },
                    "benchmark": "S&P 500"
                }
            }
            async with session.post(
                f"{BASE_URL}/agents/{agent_id}/execute",
                headers=HEADERS,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Execution ID: {data.get('execution_id')}")
                print(f"   Duration: {data.get('duration_ms')}ms")
        except asyncio.TimeoutError:
            print("   Timeout: Agent execution took too long")
        except Exception as e:
            print(f"   Error: {e}")

        # 2. Execute Agent (Async)
        print(f"\n2. POST /agents/{agent_id}/execute-async - Execute agent (async)")
        try:
            payload = {
                "inputs": {
                    "portfolio_data": {"assets": []},
                    "benchmark": "S&P 500"
                }
            }
            async with session.post(
                f"{BASE_URL}/agents/{agent_id}/execute-async",
                headers=HEADERS,
                json=payload
            ) as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Task ID: {data.get('task_id')}")
        except Exception as e:
            print(f"   Error: {e}")

        # 3. Get Agent Logs
        print(f"\n3. GET /agents/{agent_id}/logs - Get agent logs")
        try:
            async with session.get(
                f"{BASE_URL}/agents/{agent_id}/logs",
                headers=HEADERS
            ) as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Logs count: {len(data.get('data', []))}")
        except Exception as e:
            print(f"   Error: {e}")

        # 4. Get Agent Analytics
        print(f"\n4. GET /agents/{agent_id}/analytics - Get agent analytics")
        try:
            async with session.get(
                f"{BASE_URL}/agents/{agent_id}/analytics",
                headers=HEADERS
            ) as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Analytics keys: {list(data.get('data', {}).keys())}")
        except Exception as e:
            print(f"   Error: {e}")


async def test_workflow_execution(workflow_id: str):
    """Test workflow execution"""
    async with aiohttp.ClientSession() as session:
        print("\n" + "="*60)
        print("TESTING WORKFLOW EXECUTION")
        print("="*60)

        # 1. Execute Workflow
        print(f"\n1. POST /workflows/{workflow_id}/execute - Execute workflow")
        try:
            payload = {
                "workflow_id": workflow_id,
                "context": {
                    "portfolio": {
                        "assets": [
                            {"symbol": "AAPL", "weight": 0.4},
                        ]
                    },
                    "benchmark": "S&P 500"
                }
            }
            async with session.post(
                f"{BASE_URL}/workflows/{workflow_id}/execute",
                headers=HEADERS,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Workflow Status: {data.get('status')}")
                print(f"   Duration: {data.get('duration_ms')}ms")
        except asyncio.TimeoutError:
            print("   Timeout: Workflow execution took too long")
        except Exception as e:
            print(f"   Error: {e}")

        # 2. Get Workflow Status
        print(f"\n2. GET /workflows/{workflow_id}/status - Get workflow status")
        try:
            async with session.get(
                f"{BASE_URL}/workflows/{workflow_id}/status",
                headers=HEADERS
            ) as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Workflow Status: {data.get('data', {}).get('status')}")
        except Exception as e:
            print(f"   Error: {e}")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("RAG-ENTERPRISE DIFY INTEGRATION - API TESTING")
    print("="*60)

    # Test agent endpoints
    agent_id = await test_agent_endpoints()

    # Test workflow endpoints
    workflow_id = await test_workflow_endpoints()

    # Test agent execution
    if agent_id:
        await test_agent_execution(agent_id)

    # Test workflow execution
    if workflow_id:
        await test_workflow_execution(workflow_id)

    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
