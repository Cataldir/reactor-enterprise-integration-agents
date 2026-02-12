"""
FastAPI MCP Server for Message Queue Pattern

Provides REST API endpoints for sending messages to the queue
and monitoring agent activity.
"""

import asyncio
import logging
import json
from typing import Any, Dict
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import uvicorn

from shared.utils import get_project_client, load_env_config, EventHubAdapter
from shared.mcp.fastapi_mcp import FastAPIMCP, MessageRequest, MessageResponse
from main import create_queue_agent, MessageQueueAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueueTaskRequest(BaseModel):
    """Request model for queue tasks."""
    task: str = Field(..., description="Task description")
    data: Dict[str, Any] = Field(default_factory=dict, description="Task data")
    priority: int = Field(default=1, description="Task priority (1-5)")


class QueueTaskResponse(BaseModel):
    """Response model for queue tasks."""
    message_id: str
    status: str
    timestamp: str


# Initialize FastAPI MCP
mcp_api = FastAPIMCP(
    title="Message Queue Agent API",
    description="REST API for Message Queue monitoring with AI Agents",
)
app = mcp_api.get_app()

# Global state
eventhub_adapter = None
agent_monitor = None


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize services on startup."""
    global eventhub_adapter, agent_monitor
    
    try:
        config = load_env_config()
        
        # Initialize EventHub adapter
        eventhub_adapter = EventHubAdapter(
            connection_string=config["eventhub_connection_string"],
            eventhub_name=config["eventhub_name"],
        )
        
        logger.info("Message Queue API started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    if eventhub_adapter:
        await eventhub_adapter.close()
    logger.info("Message Queue API shut down")


@app.post("/queue/send", response_model=QueueTaskResponse)
async def send_to_queue(request: QueueTaskRequest) -> QueueTaskResponse:
    """Send a task to the message queue."""
    try:
        message_id = f"msg_{datetime.utcnow().timestamp()}"
        
        message_data = {
            "id": message_id,
            "task": request.task,
            "data": request.data,
            "priority": request.priority,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Send to Event Hub
        await eventhub_adapter.send_event(message_data)
        
        logger.info(f"Sent message to queue: {message_id}")
        
        return QueueTaskResponse(
            message_id=message_id,
            status="queued",
            timestamp=message_data["timestamp"],
        )
    except Exception as e:
        logger.error(f"Error sending to queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/start")
async def start_agent_monitor(background_tasks: BackgroundTasks) -> Dict[str, str]:
    """Start the agent monitor in the background."""
    global agent_monitor
    
    if agent_monitor:
        return {"status": "already_running"}
    
    try:
        config = load_env_config()
        project_client = get_project_client()
        
        # Create agent
        agent_id = await create_queue_agent(
            project_client,
            model=config.get("model_deployment_name", "gpt-4"),
        )
        
        # Create monitor
        agent_monitor = MessageQueueAgent(
            project_client=project_client,
            agent_id=agent_id,
            eventhub_adapter=eventhub_adapter,
        )
        
        # Start monitoring in background
        background_tasks.add_task(agent_monitor.start_monitoring)
        
        return {
            "status": "started",
            "agent_id": agent_id,
        }
    except Exception as e:
        logger.error(f"Error starting agent monitor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/status")
async def get_agent_status() -> Dict[str, Any]:
    """Get the status of the agent monitor."""
    if not agent_monitor:
        return {"status": "not_running"}
    
    return {
        "status": "running",
        "agent_id": agent_monitor.agent_id,
        "thread_id": agent_monitor.thread_id,
    }


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
