"""
Utility functions for agent configuration and management.
"""

import os
from typing import Optional
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AgentStreamEvent
import logging

logger = logging.getLogger(__name__)


def get_project_client() -> AIProjectClient:
    """
    Create and return an Azure AI Project client.
    
    Requires environment variables:
    - PROJECT_CONNECTION_STRING or
    - AZURE_AI_PROJECT_NAME, AZURE_RESOURCE_GROUP, AZURE_SUBSCRIPTION_ID
    """
    connection_string = os.getenv("PROJECT_CONNECTION_STRING")
    
    if connection_string:
        return AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=connection_string,
        )
    
    # Alternative: construct from individual components
    project_name = os.getenv("AZURE_AI_PROJECT_NAME")
    resource_group = os.getenv("AZURE_RESOURCE_GROUP")
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    
    if not all([project_name, resource_group, subscription_id]):
        raise ValueError(
            "Either PROJECT_CONNECTION_STRING or all of "
            "(AZURE_AI_PROJECT_NAME, AZURE_RESOURCE_GROUP, AZURE_SUBSCRIPTION_ID) "
            "must be set"
        )
    
    return AIProjectClient(
        credential=DefaultAzureCredential(),
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        project_name=project_name,
    )


def load_env_config() -> dict:
    """Load configuration from environment variables."""
    from dotenv import load_dotenv
    load_dotenv()
    
    return {
        "project_connection_string": os.getenv("PROJECT_CONNECTION_STRING"),
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
