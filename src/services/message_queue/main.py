"""
Pattern 1: Message Queue Monitor and Executor with AI Agents

This module implements an enterprise integration pattern where AI agents
act as intelligent monitors and executors of message queues using Azure Event Hub.

Key Features:
- Monitors message queues for incoming tasks
- Uses Azure AI Foundry agents to process messages intelligently
- Executes actions based on agent responses
- Provides status updates and error handling
"""

import asyncio
import logging
import os
import json
from typing import Any, Dict
from datetime import datetime

from azure.eventhub import EventData
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import MessageRole

from shared.utils import get_project_client, load_env_config, EventHubAdapter
from shared.mcp import MCPMessage
from shared.mcp.fastapi_mcp import FastAPIMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageQueueAgent:
    """AI Agent that monitors and executes tasks from a message queue."""
    
    def __init__(
        self,
        project_client: AIProjectClient,
        agent_id: str,
        eventhub_adapter: EventHubAdapter,
    ):
        self.project_client = project_client
        self.agent_id = agent_id
        self.eventhub_adapter = eventhub_adapter
        self.thread_id = None
    
    def initialize_thread(self) -> str:
        """Create a conversation thread for the agent."""
        if not self.thread_id:
            thread = self.project_client.agents.create_thread()
            self.thread_id = thread.id
            logger.info(f"Created thread: {self.thread_id}")
        return self.thread_id
    
    async def process_message(self, event: EventData) -> Dict[str, Any]:
        """
        Process a message from the queue using the AI agent.
        
        Args:
            event: Event data from Event Hub
            
        Returns:
            Processing result with agent response
        """
        try:
            # Parse event data
            message_data = json.loads(event.body_as_str())
            logger.info(f"Processing message: {message_data}")
            
            # Prepare context for the agent
            task_description = message_data.get("task", "")
            task_data = message_data.get("data", {})
            
            # Create prompt for agent
            prompt = f"""
            Task: {task_description}
            
            Data: {json.dumps(task_data, indent=2)}
            
            Please analyze this task and provide:
            1. Your understanding of the task
            2. Recommended actions or processing steps
            3. Any potential issues or considerations
            4. Expected outcome
            """
            
            # Initialize thread if needed
            thread_id = self.initialize_thread()
            
            # Create message in thread
            message = self.project_client.agents.create_message(
                thread_id=thread_id,
                role=MessageRole.USER,
                content=prompt,
            )
            
            # Run the agent
            run = self.project_client.agents.create_and_process_run(
                thread_id=thread_id,
                assistant_id=self.agent_id,
            )
            
            # Get agent's response
            if run.status == "completed":
                messages = self.project_client.agents.list_messages(thread_id=thread_id)
                
                # Get the latest assistant message
                assistant_messages = [
                    msg for msg in messages.data 
                    if msg.role == MessageRole.ASSISTANT
                ]
                
                if assistant_messages:
                    response_content = assistant_messages[0].content[0].text.value
                    
                    result = {
                        "status": "success",
                        "message_id": message_data.get("id", "unknown"),
                        "agent_response": response_content,
                        "timestamp": datetime.utcnow().isoformat(),
                        "thread_id": thread_id,
                    }
                    
                    logger.info(f"Successfully processed message: {result['message_id']}")
                    return result
            
            # Handle non-completed runs
            return {
                "status": "error",
                "message_id": message_data.get("id", "unknown"),
                "error": f"Run status: {run.status}",
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    async def start_monitoring(self) -> None:
        """Start monitoring the message queue."""
        logger.info("Starting message queue monitoring...")
        
        async def on_event(event: EventData) -> None:
            """Callback for processing events."""
            result = await self.process_message(event)
            logger.info(f"Processing result: {result}")
        
        await self.eventhub_adapter.receive_events(on_event)


async def create_queue_agent(client: AIProjectClient, model: str = "gpt-4") -> str:
    """Create an agent specialized for queue processing."""
    instructions = """
    You are an intelligent message queue processor. Your role is to:
    1. Analyze incoming tasks from the message queue
    2. Understand the context and requirements
    3. Provide clear, actionable recommendations
    4. Identify potential issues or edge cases
    5. Suggest optimal processing strategies
    
    Be concise but thorough in your analysis. Focus on practical, 
    executable actions that can be automated.
    """
    
    agent = client.agents.create_agent(
        model=model,
        name="Queue Monitor Agent",
        instructions=instructions,
    )
    
    logger.info(f"Created queue agent: {agent.id}")
    return agent.id


async def main() -> None:
    """Main entry point for the message queue pattern."""
    # Load configuration
    config = load_env_config()
    
    # Initialize clients
    project_client = get_project_client()
    
    # Create EventHub adapter
    eventhub_adapter = EventHubAdapter(
        connection_string=config["eventhub_connection_string"],
        eventhub_name=config["eventhub_name"],
    )
    
    # Create agent
    agent_id = await create_queue_agent(
        project_client,
        model=config.get("model_deployment_name", "gpt-4"),
    )
    
    # Create message queue agent
    queue_agent = MessageQueueAgent(
        project_client=project_client,
        agent_id=agent_id,
        eventhub_adapter=eventhub_adapter,
    )
    
    # Start monitoring
    try:
        await queue_agent.start_monitoring()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await eventhub_adapter.close()


if __name__ == "__main__":
    asyncio.run(main())
