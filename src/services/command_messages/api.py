"""
FastAPI MCP Server for Command Messages Pattern

Provides REST API endpoints for submitting commands and tracking status.
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
    AsyncCommandPipeline,
    CommandProcessor,
    CommandMessage,
    CommandType,
    CommandStatus,
    create_command_processor_agent,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommandRequest(BaseModel):
    """Request to submit a command."""
    command_type: CommandType = Field(..., description="Type of command")
    parameters: Dict[str, Any] = Field(..., description="Command parameters")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class CommandResponse(BaseModel):
    """Response from command submission."""
    command_id: str
    command_type: str
    status: str
    created_at: str


class CommandStatusResponse(BaseModel):
    """Command status information."""
    command_id: str
    command_type: str
    status: str
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]


class ProcessorConfig(BaseModel):
    """Configuration for creating a processor."""
    name: str = Field(..., description="Processor name")
    command_types: List[CommandType] = Field(..., description="Command types to handle")
    instructions: str = Field(..., description="Processing instructions")


class ProcessorInfo(BaseModel):
    """Information about a processor."""
    name: str
    agent_id: str
    command_types: List[str]
    processed_count: int


# Initialize FastAPI MCP
mcp_api = FastAPIMCP(
    title="Command Messages Agent API",
    description="REST API for Command Message Pattern with Async Pipelines",
)
app = mcp_api.get_app()

# Global state
pipeline: Optional[AsyncCommandPipeline] = None
project_client = None
model_name = None
processing_task = None


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize services on startup."""
    global pipeline, project_client, model_name
    
    try:
        config = load_env_config()
        project_client = get_project_client()
        model_name = config.get("model_deployment_name", "gpt-4")
        
        # Create Event Hub adapter (SAS key auth)
        eventhub_adapter = EventHubAdapter(
            connection_string=config["eventhub_connection_string"],
            eventhub_name=config["eventhub_name"],
        )
        
        # Create pipeline
        pipeline = AsyncCommandPipeline("API Pipeline", eventhub_adapter)
        
        logger.info("Command Messages API started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    global processing_task
    
    if processing_task:
        processing_task.cancel()
    
    if pipeline and pipeline.eventhub_adapter:
        await pipeline.eventhub_adapter.close()
    
    logger.info("Command Messages API shut down")


@app.post("/commands/submit", response_model=CommandResponse)
async def submit_command(request: CommandRequest) -> CommandResponse:
    """Submit a command for processing."""
    try:
        command_id = str(uuid.uuid4())
        
        command = CommandMessage(
            command_id=command_id,
            command_type=request.command_type,
            parameters=request.parameters,
            metadata=request.metadata or {},
        )
        
        await pipeline.submit_command(command)
        
        return CommandResponse(
            command_id=command_id,
            command_type=request.command_type.value,
            status=CommandStatus.PENDING.value,
            created_at=command.created_at,
        )
    except Exception as e:
        logger.error(f"Error submitting command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/commands/{command_id}", response_model=CommandStatusResponse)
async def get_command_status(command_id: str) -> CommandStatusResponse:
    """Get the status of a submitted command."""
    command = pipeline.get_command_status(command_id)
    
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    
    return CommandStatusResponse(
        command_id=command.command_id,
        command_type=command.command_type.value,
        status=command.status.value,
        result=command.result,
        error=command.error,
        created_at=command.created_at,
        updated_at=command.updated_at,
        metadata=command.metadata,
    )


@app.post("/processors/create", response_model=ProcessorInfo)
async def create_processor(config: ProcessorConfig) -> ProcessorInfo:
    """Create and register a new command processor."""
    try:
        # Create agent
        agent_id = await create_command_processor_agent(
            project_client,
            config.name,
            config.instructions,
            model=model_name,
        )
        
        # Create processor
        processor = CommandProcessor(
            name=config.name,
            project_client=project_client,
            agent_id=agent_id,
            command_types=config.command_types,
            processing_instructions=config.instructions,
        )
        
        # Register with pipeline
        pipeline.register_processor(processor)
        
        return ProcessorInfo(
            name=processor.name,
            agent_id=processor.agent_id,
            command_types=[ct.value for ct in processor.command_types],
            processed_count=processor.processed_commands,
        )
    except Exception as e:
        logger.error(f"Error creating processor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/processors", response_model=List[ProcessorInfo])
async def list_processors() -> List[ProcessorInfo]:
    """List all registered processors."""
    return [
        ProcessorInfo(
            name=proc.name,
            agent_id=proc.agent_id,
            command_types=[ct.value for ct in proc.command_types],
            processed_count=proc.processed_commands,
        )
        for proc in pipeline.processors
    ]


@app.post("/pipeline/start")
async def start_pipeline(background_tasks: BackgroundTasks) -> Dict[str, str]:
    """Start the command processing pipeline."""
    global processing_task
    
    if processing_task:
        return {"status": "already_running"}
    
    try:
        async def process() -> None:
            await pipeline.start_processing()
        
        background_tasks.add_task(process)
        processing_task = True
        
        return {"status": "started"}
    except Exception as e:
        logger.error(f"Error starting pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/command-types", response_model=List[str])
async def list_command_types() -> List[str]:
    """List available command types."""
    return [ct.value for ct in CommandType]


# Preset processor configurations
@app.post("/processors/preset/data-processor", response_model=ProcessorInfo)
async def create_data_processor() -> ProcessorInfo:
    """Create a preset data processing processor."""
    config = ProcessorConfig(
        name="Data Processor",
        command_types=[CommandType.PROCESS_DATA, CommandType.TRANSFORM_DATA],
        instructions="""You are a data processing expert. Process and transform 
        data according to the command parameters. Provide clear results.""",
    )
    return await create_processor(config)


@app.post("/processors/preset/content-analyzer", response_model=ProcessorInfo)
async def create_content_analyzer() -> ProcessorInfo:
    """Create a preset content analysis processor."""
    config = ProcessorConfig(
        name="Content Analyzer",
        command_types=[CommandType.ANALYZE_CONTENT],
        instructions="""You are a content analysis expert. Analyze content for 
        sentiment, topics, entities, and insights.""",
    )
    return await create_processor(config)


@app.post("/processors/preset/report-generator", response_model=ProcessorInfo)
async def create_report_generator() -> ProcessorInfo:
    """Create a preset report generation processor."""
    config = ProcessorConfig(
        name="Report Generator",
        command_types=[CommandType.GENERATE_REPORT],
        instructions="""You are a report generation expert. Create well-structured, 
        professional reports from the provided data.""",
    )
    return await create_processor(config)


@app.post("/processors/preset/validator", response_model=ProcessorInfo)
async def create_validator() -> ProcessorInfo:
    """Create a preset validation processor."""
    config = ProcessorConfig(
        name="Input Validator",
        command_types=[CommandType.VALIDATE_INPUT],
        instructions="""You are a validation expert. Validate input data for 
        correctness, completeness, and compliance with requirements.""",
    )
    return await create_processor(config)


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info",
    )
