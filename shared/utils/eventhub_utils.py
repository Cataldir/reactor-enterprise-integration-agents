"""
Utility functions for Azure Event Hub integration.
"""

import asyncio
from typing import Any, Callable, Optional
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubConsumerClient, EventHubProducerClient
import logging
import json

logger = logging.getLogger(__name__)


class EventHubAdapter:
    """Adapter for Azure Event Hub integration."""
    
    def __init__(
        self,
        connection_string: str,
        eventhub_name: str,
        consumer_group: str = "$Default",
    ):
        self.connection_string = connection_string
        self.eventhub_name = eventhub_name
        self.consumer_group = consumer_group
        self.producer: Optional[EventHubProducerClient] = None
        self.consumer: Optional[EventHubConsumerClient] = None
    
    async def get_producer(self) -> EventHubProducerClient:
        """Get or create producer client."""
        if self.producer is None:
            self.producer = EventHubProducerClient.from_connection_string(
                self.connection_string,
                eventhub_name=self.eventhub_name,
            )
        return self.producer
    
    async def get_consumer(self) -> EventHubConsumerClient:
        """Get or create consumer client."""
        if self.consumer is None:
            self.consumer = EventHubConsumerClient.from_connection_string(
                self.connection_string,
                consumer_group=self.consumer_group,
                eventhub_name=self.eventhub_name,
            )
        return self.consumer
    
    async def send_event(self, data: Any) -> None:
        """Send an event to Event Hub."""
        producer = await self.get_producer()
        
        # Convert data to JSON string
        if not isinstance(data, str):
            data = json.dumps(data)
        
        event_data = EventData(data)
        event_data_batch = await producer.create_batch()
        event_data_batch.add(event_data)
        await producer.send_batch(event_data_batch)
        logger.info(f"Sent event to Event Hub: {self.eventhub_name}")
    
    async def receive_events(
        self,
        on_event: Callable[[EventData], Any],
        starting_position: str = "-1",  # -1 means from the beginning
    ) -> None:
        """
        Receive events from Event Hub.
        
        Args:
            on_event: Callback function to process each event
            starting_position: Starting position for reading events
        """
        consumer = await self.get_consumer()
        
        async def on_event_batch(partition_context: Any, events: list) -> None:
            for event in events:
                try:
                    await on_event(event)
                    await partition_context.update_checkpoint(event)
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
        
        async with consumer:
            await consumer.receive(
                on_event_batch=on_event_batch,
                starting_position=starting_position,
            )
    
    async def close(self) -> None:
        """Close producer and consumer clients."""
        if self.producer:
            await self.producer.close()
        if self.consumer:
            await self.consumer.close()
        logger.info("Event Hub adapter closed")
