"""
MCP (Model Context Protocol) integration layer for AI agents.

This module provides a standardized interface for communication between
Azure AI Foundry agents and enterprise integration services.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MCPMessage:
    """Standard message format for MCP communication."""
    
    def __init__(
        self,
        message_id: str,
        message_type: str,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.message_id = message_id
        self.message_type = message_type
        self.payload = payload
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type,
            "payload": self.payload,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPMessage":
        """Create message from dictionary."""
        return cls(
            message_id=data["message_id"],
            message_type=data["message_type"],
            payload=data["payload"],
            metadata=data.get("metadata", {}),
        )


class MCPAdapter(ABC):
    """Abstract base class for MCP adapters."""
    
    @abstractmethod
    async def send_message(self, message: MCPMessage) -> None:
        """Send a message through the MCP layer."""
        pass
    
    @abstractmethod
    async def receive_message(self) -> Optional[MCPMessage]:
        """Receive a message from the MCP layer."""
        pass
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the message broker."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the message broker."""
        pass


class MCPRouter:
    """Routes messages to appropriate handlers based on message type."""
    
    def __init__(self) -> None:
        self.handlers: Dict[str, Any] = {}
    
    def register_handler(self, message_type: str, handler: Any) -> None:
        """Register a handler for a specific message type."""
        self.handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")
    
    async def route_message(self, message: MCPMessage) -> Any:
        """Route message to the appropriate handler."""
        handler = self.handlers.get(message.message_type)
        if handler is None:
            logger.warning(f"No handler found for message type: {message.message_type}")
            return None
        
        logger.info(f"Routing message {message.message_id} to handler for {message.message_type}")
        return await handler(message)
