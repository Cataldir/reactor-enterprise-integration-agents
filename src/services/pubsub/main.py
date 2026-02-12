"""
Pattern 3: Publish/Subscribe with AI Agents

This module implements the Pub/Sub integration pattern where AI agents
act as intelligent subscribers to different topics.

Key Features:
- Multiple agents subscribe to topics
- Topic-based message routing
- Parallel processing by multiple subscribers
- Event-driven architecture with cognitive processing
"""

import asyncio
import logging
import json
from typing import Any, Dict, List, Callable, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from azure.eventhub import EventData
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import MessageRole

from shared.utils import get_project_client, load_env_config, EventHubAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TopicType(str, Enum):
    """Available topic types."""
    CUSTOMER_EVENTS = "customer_events"
    ORDER_EVENTS = "order_events"
    SYSTEM_EVENTS = "system_events"
    ANALYTICS_EVENTS = "analytics_events"


@dataclass
class Message:
    """Message with topic and payload."""
    topic: TopicType
    payload: Dict[str, Any]
    message_id: str
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "topic": self.topic.value,
            "payload": self.payload,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create from dictionary."""
        return cls(
            topic=TopicType(data["topic"]),
            payload=data["payload"],
            message_id=data["message_id"],
            timestamp=data["timestamp"],
        )


class AgentSubscriber:
    """An AI agent that subscribes to specific topics."""
    
    def __init__(
        self,
        name: str,
        project_client: AIProjectClient,
        agent_id: str,
        subscribed_topics: List[TopicType],
        processing_instructions: str,
    ):
        self.name = name
        self.project_client = project_client
        self.agent_id = agent_id
        self.subscribed_topics = subscribed_topics
        self.processing_instructions = processing_instructions
        self.thread_id = None
        self.processed_count = 0
    
    def _initialize_thread(self) -> str:
        """Initialize conversation thread."""
        if not self.thread_id:
            thread = self.project_client.agents.create_thread()
            self.thread_id = thread.id
            logger.info(f"Subscriber '{self.name}' created thread: {self.thread_id}")
        return self.thread_id
    
    def is_subscribed_to(self, topic: TopicType) -> bool:
        """Check if subscriber is interested in this topic."""
        return topic in self.subscribed_topics
    
    async def handle_message(self, message: Message) -> Dict[str, Any]:
        """
        Handle a message using the AI agent.
        
        Args:
            message: The message to process
            
        Returns:
            Processing result
        """
        if not self.is_subscribed_to(message.topic):
            logger.debug(f"Subscriber '{self.name}' not interested in {message.topic}")
            return {"status": "skipped", "reason": "not_subscribed"}
        
        logger.info(f"Subscriber '{self.name}' processing message from {message.topic}")
        
        try:
            # Create prompt
            prompt = f"""
            {self.processing_instructions}
            
            Topic: {message.topic.value}
            Message ID: {message.message_id}
            Timestamp: {message.timestamp}
            
            Payload:
            {json.dumps(message.payload, indent=2)}
            
            Please process this message according to your role and provide:
            1. Your analysis of the event
            2. Actions you would take
            3. Any alerts or notifications needed
            4. Recommendations for follow-up
            """
            
            # Initialize thread
            thread_id = self._initialize_thread()
            
            # Send message
            self.project_client.agents.create_message(
                thread_id=thread_id,
                role=MessageRole.USER,
                content=prompt,
            )
            
            # Run agent
            run = self.project_client.agents.create_and_process_run(
                thread_id=thread_id,
                assistant_id=self.agent_id,
            )
            
            if run.status == "completed":
                messages = self.project_client.agents.list_messages(thread_id=thread_id)
                assistant_messages = [
                    msg for msg in messages.data 
                    if msg.role == MessageRole.ASSISTANT
                ]
                
                if assistant_messages:
                    response = assistant_messages[0].content[0].text.value
                    self.processed_count += 1
                    
                    result = {
                        "status": "success",
                        "subscriber": self.name,
                        "topic": message.topic.value,
                        "message_id": message.message_id,
                        "response": response,
                        "processed_count": self.processed_count,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    
                    logger.info(
                        f"Subscriber '{self.name}' processed message "
                        f"{message.message_id} successfully"
                    )
                    return result
            
            return {
                "status": "error",
                "subscriber": self.name,
                "error": f"Run status: {run.status}",
            }
            
        except Exception as e:
            logger.error(f"Error in subscriber '{self.name}': {e}", exc_info=True)
            return {
                "status": "error",
                "subscriber": self.name,
                "error": str(e),
            }


class PubSubBroker:
    """Message broker that manages publishers and subscribers."""
    
    def __init__(self, eventhub_adapter: EventHubAdapter):
        self.eventhub_adapter = eventhub_adapter
        self.subscribers: List[AgentSubscriber] = []
    
    def register_subscriber(self, subscriber: AgentSubscriber) -> None:
        """Register a new subscriber."""
        self.subscribers.append(subscriber)
        logger.info(
            f"Registered subscriber '{subscriber.name}' for topics: "
            f"{[t.value for t in subscriber.subscribed_topics]}"
        )
    
    async def publish(self, message: Message) -> None:
        """
        Publish a message to all interested subscribers.
        
        Args:
            message: The message to publish
        """
        logger.info(f"Publishing message to topic: {message.topic.value}")
        
        # Send to Event Hub
        await self.eventhub_adapter.send_event(message.to_dict())
        logger.info(f"Message {message.message_id} published to Event Hub")
    
    async def _process_event(self, event: EventData) -> None:
        """Process an event from Event Hub."""
        try:
            # Parse message
            message_data = json.loads(event.body_as_str())
            message = Message.from_dict(message_data)
            
            logger.info(f"Received message on topic: {message.topic.value}")
            
            # Find interested subscribers
            interested_subscribers = [
                sub for sub in self.subscribers 
                if sub.is_subscribed_to(message.topic)
            ]
            
            if not interested_subscribers:
                logger.warning(f"No subscribers for topic: {message.topic.value}")
                return
            
            logger.info(
                f"Found {len(interested_subscribers)} subscribers for "
                f"{message.topic.value}"
            )
            
            # Process in parallel by all interested subscribers
            tasks = [sub.handle_message(message) for sub in interested_subscribers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Subscriber error: {result}")
                else:
                    logger.info(f"Subscriber result: {result.get('status')}")
                    
        except Exception as e:
            logger.error(f"Error processing event: {e}", exc_info=True)
    
    async def start_consuming(self) -> None:
        """Start consuming messages from Event Hub."""
        logger.info("Starting message consumption...")
        await self.eventhub_adapter.receive_events(self._process_event)


async def create_subscriber_agent(
    client: AIProjectClient,
    name: str,
    instructions: str,
    model: str = "gpt-4",
) -> str:
    """Create an AI agent for a subscriber."""
    agent = client.agents.create_agent(
        model=model,
        name=name,
        instructions=instructions,
    )
    logger.info(f"Created subscriber agent: {name} (ID: {agent.id})")
    return agent.id


async def demo_pubsub_system() -> None:
    """Demonstrate the Pub/Sub system with multiple agents."""
    config = load_env_config()
    client = get_project_client()
    model = config.get("model_deployment_name", "gpt-4")
    
    # Create Event Hub adapter
    eventhub_adapter = EventHubAdapter(
        connection_string=config["eventhub_connection_string"],
        eventhub_name=config["eventhub_name"],
    )
    
    # Create broker
    broker = PubSubBroker(eventhub_adapter)
    
    # Create subscriber agents with different specializations
    
    # 1. Customer Service Agent - subscribes to customer events
    customer_agent_id = await create_subscriber_agent(
        client,
        "Customer Service Agent",
        """You are a customer service expert. When you receive customer events:
        - Analyze customer sentiment and satisfaction
        - Identify issues requiring immediate attention
        - Recommend proactive service actions
        - Suggest personalization opportunities""",
        model=model,
    )
    
    customer_subscriber = AgentSubscriber(
        name="Customer Service Agent",
        project_client=client,
        agent_id=customer_agent_id,
        subscribed_topics=[TopicType.CUSTOMER_EVENTS],
        processing_instructions="Process customer-related events",
    )
    broker.register_subscriber(customer_subscriber)
    
    # 2. Order Processing Agent - subscribes to order events
    order_agent_id = await create_subscriber_agent(
        client,
        "Order Processing Agent",
        """You are an order processing specialist. When you receive order events:
        - Validate order information
        - Check for fraud indicators
        - Optimize fulfillment routing
        - Identify upsell opportunities""",
        model=model,
    )
    
    order_subscriber = AgentSubscriber(
        name="Order Processing Agent",
        project_client=client,
        agent_id=order_agent_id,
        subscribed_topics=[TopicType.ORDER_EVENTS],
        processing_instructions="Process order-related events",
    )
    broker.register_subscriber(order_subscriber)
    
    # 3. Analytics Agent - subscribes to all event types
    analytics_agent_id = await create_subscriber_agent(
        client,
        "Analytics Agent",
        """You are a data analytics expert. For any event you receive:
        - Extract key metrics and KPIs
        - Identify trends and patterns
        - Detect anomalies
        - Generate insights for business intelligence""",
        model=model,
    )
    
    analytics_subscriber = AgentSubscriber(
        name="Analytics Agent",
        project_client=client,
        agent_id=analytics_agent_id,
        subscribed_topics=[
            TopicType.CUSTOMER_EVENTS,
            TopicType.ORDER_EVENTS,
            TopicType.SYSTEM_EVENTS,
            TopicType.ANALYTICS_EVENTS,
        ],
        processing_instructions="Analyze all types of events",
    )
    broker.register_subscriber(analytics_subscriber)
    
    # Publish some sample messages
    messages = [
        Message(
            topic=TopicType.CUSTOMER_EVENTS,
            payload={
                "event_type": "customer_feedback",
                "customer_id": "C12345",
                "feedback": "Great service, but delivery was slow",
                "rating": 4,
            },
            message_id="msg_001",
            timestamp=datetime.utcnow().isoformat(),
        ),
        Message(
            topic=TopicType.ORDER_EVENTS,
            payload={
                "event_type": "order_placed",
                "order_id": "ORD-789",
                "customer_id": "C12345",
                "total": 199.99,
                "items": ["laptop_stand", "wireless_mouse"],
            },
            message_id="msg_002",
            timestamp=datetime.utcnow().isoformat(),
        ),
    ]
    
    # Publish messages
    for msg in messages:
        await broker.publish(msg)
        await asyncio.sleep(1)  # Small delay between publishes
    
    # Start consuming (this will run indefinitely)
    try:
        await broker.start_consuming()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await eventhub_adapter.close()


async def main() -> None:
    """Main entry point."""
    await demo_pubsub_system()


if __name__ == "__main__":
    asyncio.run(main())
