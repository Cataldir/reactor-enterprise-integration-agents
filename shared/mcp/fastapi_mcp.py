"""
FastAPI MCP integration layer.

Provides REST API endpoints for MCP message handling using FastAPI.
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
import logging
import uuid

from shared.mcp import MCPMessage, MCPRouter

logger = logging.getLogger(__name__)


class MessageRequest(BaseModel):
    """Request model for sending messages."""
    message_type: str = Field(..., description="Type of the message")
    payload: Dict[str, Any] = Field(..., description="Message payload")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class MessageResponse(BaseModel):
    """Response model for message operations."""
    message_id: str = Field(..., description="Unique message identifier")
    status: str = Field(..., description="Operation status")
    result: Optional[Any] = Field(None, description="Operation result")


class FastAPIMCP:
    """FastAPI application for MCP message handling."""
    
    def __init__(self, title: str = "MCP API", description: str = "Model Context Protocol API"):
        self.app = FastAPI(title=title, description=description)
        self.router = MCPRouter()
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """Setup FastAPI routes for MCP operations."""
        
        @self.app.post("/messages", response_model=MessageResponse)
        async def send_message(request: MessageRequest) -> MessageResponse:
            """Send a message through MCP."""
            message_id = str(uuid.uuid4())
            message = MCPMessage(
                message_id=message_id,
                message_type=request.message_type,
                payload=request.payload,
                metadata=request.metadata,
            )
            
            try:
                result = await self.router.route_message(message)
                return MessageResponse(
                    message_id=message_id,
                    status="success",
                    result=result,
                )
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error processing message: {str(e)}",
                )
        
        @self.app.get("/health")
        async def health_check() -> Dict[str, str]:
            """Health check endpoint."""
            return {"status": "healthy"}
    
    def register_handler(self, message_type: str, handler: Any) -> None:
        """Register a message handler."""
        self.router.register_handler(message_type, handler)
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        return self.app
