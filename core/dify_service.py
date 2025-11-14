"""
Dify Service Layer
Handles integration with Dify workflow engine and agent management
"""

import requests
import json
import os
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DifyEnvironment(str, Enum):
    """Dify deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DifyConfig:
    """Dify configuration"""
    api_key: str
    base_url: str
    environment: DifyEnvironment = DifyEnvironment.DEVELOPMENT
    timeout: int = 30
    max_retries: int = 3


class DifyClient:
    """
    Dify API Client
    Provides methods to interact with Dify workflow engine
    """
    
    def __init__(self, config: DifyConfig):
        """Initialize Dify client with configuration"""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        })
        self.base_url = config.base_url.rstrip('/')
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Dify API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            
        Returns:
            Response JSON dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Dify API error: {e}")
            raise
    
    # ========================================================================
    # APP/WORKFLOW MANAGEMENT
    # ========================================================================
    
    def create_app(
        self,
        name: str,
        description: str = "",
        app_type: str = "agent",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create new app/workflow in Dify
        
        Args:
            name: App name
            description: App description
            app_type: Type of app (agent, chatbot, workflow)
            **kwargs: Additional app configuration
            
        Returns:
            Created app details with app_id
        """
        data = {
            "name": name,
            "description": description,
            "mode": app_type,
            **kwargs
        }
        return self._make_request("POST", "apps", data)
    
    def get_app(self, app_id: str) -> Dict[str, Any]:
        """Get app details by app_id"""
        return self._make_request("GET", f"apps/{app_id}")
    
    def list_apps(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """List all apps"""
        params = {"limit": limit, "offset": offset}
        return self._make_request("GET", "apps", params=params)
    
    def update_app(
        self,
        app_id: str,
        **update_data
    ) -> Dict[str, Any]:
        """Update app configuration"""
        return self._make_request("PUT", f"apps/{app_id}", update_data)
    
    def delete_app(self, app_id: str) -> Dict[str, Any]:
        """Delete app/workflow"""
        return self._make_request("DELETE", f"apps/{app_id}")
    
    # ========================================================================
    # WORKFLOW EXECUTION
    # ========================================================================
    
    def run_workflow(
        self,
        app_id: str,
        inputs: Dict[str, Any],
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Execute workflow and get results
        
        Args:
            app_id: Target app/workflow ID
            inputs: Input parameters for workflow
            user_id: User identifier for tracking
            
        Returns:
            Workflow execution result with output
        """
        data = {
            "inputs": inputs,
            "user": user_id
        }
        return self._make_request(
            "POST",
            f"apps/{app_id}/run",
            data
        )
    
    def run_workflow_async(
        self,
        app_id: str,
        inputs: Dict[str, Any],
        webhook_url: Optional[str] = None,
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Execute workflow asynchronously
        
        Args:
            app_id: Target app ID
            inputs: Input parameters
            webhook_url: Callback URL for results
            user_id: User identifier
            
        Returns:
            Task ID for tracking
        """
        data = {
            "inputs": inputs,
            "user": user_id
        }
        if webhook_url:
            data["webhook"] = webhook_url
        
        return self._make_request(
            "POST",
            f"apps/{app_id}/run-async",
            data
        )
    
    def get_execution_status(
        self,
        app_id: str,
        task_id: str
    ) -> Dict[str, Any]:
        """Get status of async execution"""
        return self._make_request(
            "GET",
            f"apps/{app_id}/tasks/{task_id}"
        )
    
    # ========================================================================
    # MODEL MANAGEMENT
    # ========================================================================
    
    def list_models(
        self,
        model_type: str = "llm"
    ) -> Dict[str, Any]:
        """
        List available models
        
        Args:
            model_type: Type of model (llm, embedding, etc.)
            
        Returns:
            List of available models
        """
        params = {"type": model_type}
        return self._make_request("GET", "models", params=params)
    
    def get_model(self, model_id: str) -> Dict[str, Any]:
        """Get model details"""
        return self._make_request("GET", f"models/{model_id}")
    
    # ========================================================================
    # TOOLS AND INTEGRATIONS
    # ========================================================================
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools for workflows"""
        return self._make_request("GET", "tools")
    
    def get_tool(self, tool_id: str) -> Dict[str, Any]:
        """Get tool details"""
        return self._make_request("GET", f"tools/{tool_id}")
    
    def add_tool_to_app(
        self,
        app_id: str,
        tool_id: str,
        config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Add tool to app workflow"""
        data = {"tool_id": tool_id}
        if config:
            data["config"] = config
        
        return self._make_request(
            "POST",
            f"apps/{app_id}/tools",
            data
        )
    
    # ========================================================================
    # KNOWLEDGE BASE
    # ========================================================================
    
    def create_knowledge_base(
        self,
        name: str,
        description: str = ""
    ) -> Dict[str, Any]:
        """Create knowledge base for RAG"""
        data = {
            "name": name,
            "description": description
        }
        return self._make_request("POST", "knowledge-bases", data)
    
    def upload_document(
        self,
        kb_id: str,
        file_path: str,
        doc_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload document to knowledge base
        
        Args:
            kb_id: Knowledge base ID
            file_path: Path to file
            doc_name: Document name
            
        Returns:
            Upload result with document ID
        """
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {}
            if doc_name:
                data['name'] = doc_name
            
            response = self.session.post(
                f"{self.base_url}/knowledge-bases/{kb_id}/documents",
                files=files,
                data=data,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json()
    
    # ========================================================================
    # LOGS AND ANALYTICS
    # ========================================================================
    
    def get_execution_logs(
        self,
        app_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get execution logs for app"""
        params = {"limit": limit, "offset": offset}
        return self._make_request(
            "GET",
            f"apps/{app_id}/logs",
            params=params
        )
    
    def get_app_analytics(
        self,
        app_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get app analytics/performance metrics
        
        Args:
            app_id: App ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Analytics data with performance metrics
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        return self._make_request(
            "GET",
            f"apps/{app_id}/analytics",
            params=params
        )


class DifyServiceManager:
    """
    High-level service manager for Dify operations
    Handles agent lifecycle and workflow management
    """
    
    def __init__(self, client: DifyClient):
        """Initialize with Dify client"""
        self.client = client
        self.logger = logging.getLogger(__name__)
    
    async def create_agent(
        self,
        name: str,
        agent_type: str,
        description: str = "",
        config: Optional[Dict] = None
    ) -> str:
        """
        Create new agent in Dify
        
        Args:
            name: Agent name
            agent_type: Type (portfolio, risk, market, compliance, summarizer)
            description: Agent description
            config: Agent-specific configuration
            
        Returns:
            Created app ID
        """
        app_config = config or {}
        result = self.client.create_app(
            name=name,
            description=description or f"{agent_type} Agent",
            app_type="agent",
            **app_config
        )
        
        self.logger.info(f"Agent created: {name} ({result.get('id')})")
        return result.get('id')
    
    async def execute_agent(
        self,
        app_id: str,
        inputs: Dict[str, Any],
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """Execute agent and return results"""
        result = self.client.run_workflow(
            app_id=app_id,
            inputs=inputs,
            user_id=user_id
        )
        return result
    
    async def get_agent_status(self, app_id: str) -> Dict[str, Any]:
        """Get agent status and configuration"""
        return self.client.get_app(app_id)
    
    async def list_agents(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List all agents"""
        result = self.client.list_apps(limit=limit, offset=offset)
        return result.get('items', [])
    
    async def delete_agent(self, app_id: str) -> bool:
        """Delete agent"""
        self.client.delete_app(app_id)
        return True


# Initialize Dify client from environment
def get_dify_client() -> DifyClient:
    """Get Dify client from environment configuration"""
    api_key = os.getenv('DIFY_API_KEY', '')
    base_url = os.getenv('DIFY_BASE_URL', 'http://localhost:8001/api')
    environment = os.getenv('DIFY_ENV', 'development')
    
    config = DifyConfig(
        api_key=api_key,
        base_url=base_url,
        environment=DifyEnvironment(environment)
    )
    
    return DifyClient(config)
