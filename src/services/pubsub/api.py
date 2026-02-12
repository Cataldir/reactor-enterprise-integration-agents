"""
FastAPI MCP Server for Pub/Sub Pattern

Provides REST API endpoints for publishing messages and managing subscribers.
"""

import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import uvicorn

from shared.utils import get_project_client, load_env_config, EventHubAdapter
from shared.mcp.fastapi_mcp import FastAPIMCP
from main import (
    PubSubBroker,
    AgentSubscriber,
    Message,
    TopicType,
    create_subscriber_agent,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PublishRequest(BaseModel):
    """Request to publish a message."""
    topic: TopicType = Field(..., description="Message topic")
    payload: Dict[str, Any] = Field(..., description="Message payload")


class SubscriberConfig(BaseModel):
    """Configuration for creating a subscriber."""
    name: str = Field(..., description="Subscriber name")
    topics: List[TopicType] = Field(..., description="Topics to subscribe to")
    instructions: str = Field(..., description="Processing instructions for the agent")


class PublishResponse(BaseModel):
    """Response from publishing a message."""
    message_id: str
    topic: str
    status: str
    timestamp: str


class SubscriberInfo(BaseModel):
    """Information about a subscriber."""
    name: str
    agent_id: str
    subscribed_topics: List[str]
    processed_count: int


# Initialize FastAPI MCP
mcp_api = FastAPIMCP(
    title="Pub/Sub Agent API",
    description="REST API for Publish/Subscribe Pattern with AI Agents",
)
app = mcp_api.get_app()

# Global state
broker: Optional[PubSubBroker] = None
project_client = None
model_name = None
consuming_task = None


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize services on startup."""
    global broker, project_client, model_name
    
    try:
        config = load_env_config()
        project_client = get_project_client()
        model_name = config.get("model_deployment_name", "gpt-4")
        
        # Create Event Hub adapter (SAS key auth)
        eventhub_adapter = EventHubAdapter(
            connection_string=config["eventhub_connection_string"],
            eventhub_name=config["eventhub_name"],
        )
        
        # Create broker
        broker = PubSubBroker(eventhub_adapter)
        
        logger.info("Pub/Sub API started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    global consuming_task
    
    if consuming_task:
        consuming_task.cancel()
    
    if broker and broker.eventhub_adapter:
        await broker.eventhub_adapter.close()
    
    logger.info("Pub/Sub API shut down")


@app.post("/publish", response_model=PublishResponse)
async def publish_message(request: PublishRequest) -> PublishResponse:
    """Publish a message to a topic."""
    try:
        message_id = str(uuid.uuid4())
        
        message = Message(
            topic=request.topic,
            payload=request.payload,
            message_id=message_id,
            timestamp=datetime.utcnow().isoformat(),
        )
        
        await broker.publish(message)
        
        return PublishResponse(
            message_id=message_id,
            topic=request.topic.value,
            status="published",
            timestamp=message.timestamp,
        )
    except Exception as e:
        logger.error(f"Error publishing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/subscribers/create", response_model=SubscriberInfo)
async def create_subscriber(config: SubscriberConfig) -> SubscriberInfo:
    """Create and register a new subscriber."""
    try:
        # Create agent
        agent_id = await create_subscriber_agent(
            project_client,
            config.name,
            config.instructions,
            model=model_name,
        )
        
        # Create subscriber
        subscriber = AgentSubscriber(
            name=config.name,
            project_client=project_client,
            agent_id=agent_id,
            subscribed_topics=config.topics,
            processing_instructions=config.instructions,
        )
        
        # Register with broker
        broker.register_subscriber(subscriber)
        
        return SubscriberInfo(
            name=subscriber.name,
            agent_id=subscriber.agent_id,
            subscribed_topics=[t.value for t in subscriber.subscribed_topics],
            processed_count=subscriber.processed_count,
        )
    except Exception as e:
        logger.error(f"Error creating subscriber: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/subscribers", response_model=List[SubscriberInfo])
async def list_subscribers() -> List[SubscriberInfo]:
    """List all registered subscribers."""
    return [
        SubscriberInfo(
            name=sub.name,
            agent_id=sub.agent_id,
            subscribed_topics=[t.value for t in sub.subscribed_topics],
            processed_count=sub.processed_count,
        )
        for sub in broker.subscribers
    ]


@app.post("/consumers/start")
async def start_consumers(background_tasks: BackgroundTasks) -> Dict[str, str]:
    """Start consuming messages in the background."""
    global consuming_task
    
    if consuming_task:
        return {"status": "already_running"}
    
    try:
        # Start consumption in background
        async def consume() -> None:
            await broker.start_consuming()
        
        background_tasks.add_task(consume)
        consuming_task = True
        
        return {"status": "started"}
    except Exception as e:
        logger.error(f"Error starting consumers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/topics", response_model=List[str])
async def list_topics() -> List[str]:
    """List available topics."""
    return [topic.value for topic in TopicType]


# Preset subscriber configurations
@app.post("/subscribers/preset/customer-service", response_model=SubscriberInfo)
async def create_customer_service_subscriber() -> SubscriberInfo:
    """Create a preset customer service subscriber."""
    config = SubscriberConfig(
        name="Customer Service Agent",
        topics=[TopicType.CUSTOMER_EVENTS],
        instructions="""You are a customer service expert. Analyze customer events,
        identify issues, and recommend service actions.""",
    )
    return await create_subscriber(config)


@app.post("/subscribers/preset/order-processor", response_model=SubscriberInfo)
async def create_order_processor_subscriber() -> SubscriberInfo:
    """Create a preset order processing subscriber."""
    config = SubscriberConfig(
        name="Order Processing Agent",
        topics=[TopicType.ORDER_EVENTS],
        instructions="""You are an order processing specialist. Validate orders,
        check for fraud, and optimize fulfillment.""",
    )
    return await create_subscriber(config)


@app.post("/subscribers/preset/analytics", response_model=SubscriberInfo)
async def create_analytics_subscriber() -> SubscriberInfo:
    """Create a preset analytics subscriber (subscribes to all topics)."""
    config = SubscriberConfig(
        name="Analytics Agent",
        topics=list(TopicType),
        instructions="""You are a data analytics expert. Extract metrics, identify
        trends, detect anomalies, and generate insights.""",
    )
    return await create_subscriber(config)


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info",
    )
