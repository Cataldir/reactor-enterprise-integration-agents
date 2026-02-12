"""
FastAPI MCP Server for Pipes and Filters Pattern

Provides REST API endpoints for executing cognitive pipelines.
"""

import asyncio
import logging
from typing import Any, Dict, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
import uvicorn

from shared.utils import get_project_client, load_env_config
from shared.mcp.fastapi_mcp import FastAPIMCP
from main import (
    Pipeline,
    ParallelPipeline,
    CognitiveFilter,
    PipelineData,
    create_filter_agent,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FilterConfig(BaseModel):
    """Configuration for a pipeline filter."""
    name: str = Field(..., description="Filter name")
    instructions: str = Field(..., description="Filter instructions for AI agent")


class PipelineRequest(BaseModel):
    """Request to execute a pipeline."""
    input_data: str = Field(..., description="Input data to process")
    filters: List[FilterConfig] = Field(..., description="List of filters to apply")
    parallel: bool = Field(default=False, description="Execute filters in parallel")


class PipelineResponse(BaseModel):
    """Response from pipeline execution."""
    output_data: Any = Field(..., description="Transformed output data")
    transformations: List[str] = Field(..., description="Applied transformations")
    metadata: Dict[str, Any] = Field(..., description="Processing metadata")
    execution_time: float = Field(..., description="Execution time in seconds")


# Initialize FastAPI MCP
mcp_api = FastAPIMCP(
    title="Pipes and Filters Agent API",
    description="REST API for Cognitive Pipes and Filters Pattern",
)
app = mcp_api.get_app()

# Global state
project_client = None
model_name = None


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize services on startup."""
    global project_client, model_name
    
    try:
        config = load_env_config()
        project_client = get_project_client()
        model_name = config.get("model_deployment_name", "gpt-4")
        
        logger.info("Pipes and Filters API started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.post("/pipeline/execute", response_model=PipelineResponse)
async def execute_pipeline(request: PipelineRequest) -> PipelineResponse:
    """Execute a cognitive pipeline."""
    start_time = datetime.utcnow()
    
    try:
        # Create agents for each filter
        filter_agents = []
        for filter_config in request.filters:
            agent_id = await create_filter_agent(
                project_client,
                filter_config.name,
                filter_config.instructions,
                model=model_name,
            )
            
            cognitive_filter = CognitiveFilter(
                name=filter_config.name,
                project_client=project_client,
                agent_id=agent_id,
                instructions=filter_config.instructions,
            )
            filter_agents.append(cognitive_filter)
        
        # Create pipeline
        if request.parallel:
            pipeline = ParallelPipeline("API Pipeline")
        else:
            pipeline = Pipeline("API Pipeline")
        
        for filter_agent in filter_agents:
            pipeline.add_filter(filter_agent)
        
        # Execute pipeline
        input_data = PipelineData(content=request.input_data)
        
        if request.parallel:
            results = await pipeline.execute(input_data)
            # For parallel, return all results
            output_data = [r.content for r in results]
            transformations = [t for r in results for t in r.transformations]
            metadata = {"parallel_results": [r.metadata for r in results]}
        else:
            result = await pipeline.execute(input_data)
            output_data = result.content
            transformations = result.transformations
            metadata = result.metadata
        
        # Calculate execution time
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        
        return PipelineResponse(
            output_data=output_data,
            transformations=transformations,
            metadata=metadata,
            execution_time=execution_time,
        )
        
    except Exception as e:
        logger.error(f"Error executing pipeline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pipeline/preset/text-analysis", response_model=PipelineResponse)
async def execute_text_analysis_pipeline(input_text: str = Body(...)) -> PipelineResponse:
    """Execute a preset text analysis pipeline (sentiment, entities, summary)."""
    request = PipelineRequest(
        input_data=input_text,
        filters=[
            FilterConfig(
                name="Sentiment Analysis",
                instructions="""Analyze the sentiment of the input text. 
                Provide sentiment (positive/negative/neutral) and confidence score.""",
            ),
            FilterConfig(
                name="Entity Extraction",
                instructions="""Extract key entities: people, organizations, locations, dates.
                Return as a structured list.""",
            ),
            FilterConfig(
                name="Summarization",
                instructions="Create a concise summary under 100 words.",
            ),
        ],
        parallel=False,
    )
    
    return await execute_pipeline(request)


@app.post("/pipeline/preset/parallel-analysis", response_model=PipelineResponse)
async def execute_parallel_analysis(input_text: str = Body(...)) -> PipelineResponse:
    """Execute multiple analyses in parallel."""
    request = PipelineRequest(
        input_data=input_text,
        filters=[
            FilterConfig(
                name="Sentiment Analyzer",
                instructions="Analyze sentiment and emotional tone.",
            ),
            FilterConfig(
                name="Topic Classifier",
                instructions="Classify the main topics and categories.",
            ),
            FilterConfig(
                name="Language Detector",
                instructions="Detect language and assess formality level.",
            ),
        ],
        parallel=True,
    )
    
    return await execute_pipeline(request)


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
