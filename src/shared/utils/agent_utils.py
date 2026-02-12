"""
Utility functions for agent configuration and management.
"""

import os
from typing import Optional
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import AgentStreamEvent
import logging

logger = logging.getLogger(__name__)


def get_project_client() -> AIProjectClient:
    """
    Create and return an Azure AI Project client.
    
    Requires environment variable:
    - AZURE_AI_PROJECT_ENDPOINT (e.g. https://<resource>.services.ai.azure.com/api/projects/<project>)
    """
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    
    if not endpoint:
        raise ValueError(
            "AZURE_AI_PROJECT_ENDPOINT must be set "
            "(e.g. https://<resource>.services.ai.azure.com/api/projects/<project>)"
        )
    
    return AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )


def load_env_config() -> dict:
    """Load configuration from environment variables."""
    from dotenv import load_dotenv
    load_dotenv()
    
    return {
        "azure_ai_project_endpoint": os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
        "eventhub_fully_qualified_namespace": os.getenv("EVENTHUB_FULLY_QUALIFIED_NAMESPACE"),
        "eventhub_connection_string": os.getenv("EVENTHUB_CONNECTION_STRING"),
        "eventhub_name": os.getenv("EVENTHUB_NAME"),
        "azure_openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "azure_openai_api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "model_deployment_name": os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4"),
    }


async def create_agent(
    client: AIProjectClient,
    name: str,
    instructions: str,
    model: str = "gpt-4",
    tools: Optional[list] = None,
) -> str:
    """
    Create an AI agent with the specified configuration.
    
    Args:
        client: Azure AI Project client
        name: Name of the agent
        instructions: System instructions for the agent
        model: Model deployment name
        tools: Optional list of tools for the agent
    
    Returns:
        Agent ID
    """
    agent = client.agents.create_agent(
        model=model,
        name=name,
        instructions=instructions,
        tools=tools or [],
    )
    logger.info(f"Created agent: {name} (ID: {agent.id})")
    return agent.id
