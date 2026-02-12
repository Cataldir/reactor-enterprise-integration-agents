"""
Pattern 2: Pipes and Filters with Cognitive Capabilities

This module implements the Pipes and Filters integration pattern where
AI agents act as intelligent filters in a data processing pipeline.

Key Features:
- Multiple specialized agents acting as filters
- Sequential or parallel processing pipelines
- Cognitive transformation at each stage
- Flexible pipeline configuration
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MessageRole

from shared.utils import get_project_client, load_env_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PipelineData:
    """Data flowing through the pipeline."""
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    transformations: List[str] = field(default_factory=list)
    
    def add_transformation(self, filter_name: str) -> None:
        """Record a transformation."""
        self.transformations.append(f"{filter_name} @ {datetime.utcnow().isoformat()}")


class CognitiveFilter:
    """A filter that uses AI agent for data transformation."""
    
    def __init__(
        self,
        name: str,
        project_client: AIProjectClient,
        agent_id: str,
        instructions: str,
    ):
        self.name = name
        self.project_client = project_client
        self.agent_id = agent_id
        self.instructions = instructions
        self.thread_id = None
    
    def _initialize_thread(self) -> str:
        """Initialize conversation thread."""
        if not self.thread_id:
            thread = self.project_client.agents.create_thread()
            self.thread_id = thread.id
            logger.info(f"Filter '{self.name}' created thread: {self.thread_id}")
        return self.thread_id
    
    async def process(self, data: PipelineData) -> PipelineData:
        """
        Process data through this filter using AI agent.
        
        Args:
            data: Pipeline data to process
            
        Returns:
            Transformed pipeline data
        """
        logger.info(f"Filter '{self.name}' processing data")
        
        try:
            # Create prompt with context
            prompt = f"""
            {self.instructions}
            
            Input Data:
            {data.content}
            
            Previous Transformations:
            {chr(10).join(data.transformations) if data.transformations else 'None'}
            
            Please process this data according to your instructions.
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
                    # Get transformed content
                    transformed_content = assistant_messages[0].content[0].text.value
                    
                    # Update pipeline data
                    data.content = transformed_content
                    data.add_transformation(self.name)
                    data.metadata[f"{self.name}_status"] = "success"
                    
                    logger.info(f"Filter '{self.name}' completed successfully")
                    return data
            
            # Handle failures
            data.metadata[f"{self.name}_status"] = f"failed: {run.status}"
            logger.warning(f"Filter '{self.name}' failed with status: {run.status}")
            return data
            
        except Exception as e:
            logger.error(f"Error in filter '{self.name}': {e}", exc_info=True)
            data.metadata[f"{self.name}_error"] = str(e)
            return data


class Pipeline:
    """Pipeline that orchestrates multiple cognitive filters."""
    
    def __init__(self, name: str):
        self.name = name
        self.filters: List[CognitiveFilter] = []
    
    def add_filter(self, filter: CognitiveFilter) -> "Pipeline":
        """Add a filter to the pipeline."""
        self.filters.append(filter)
        logger.info(f"Added filter '{filter.name}' to pipeline '{self.name}'")
        return self
    
    async def execute(self, data: PipelineData) -> PipelineData:
        """
        Execute the pipeline by passing data through all filters sequentially.
        
        Args:
            data: Initial pipeline data
            
        Returns:
            Final transformed data
        """
        logger.info(f"Starting pipeline '{self.name}' with {len(self.filters)} filters")
        
        for filter in self.filters:
            data = await filter.process(data)
            
            # Check if we should continue
            if data.metadata.get(f"{filter.name}_status") == "failed":
                logger.warning(f"Pipeline '{self.name}' stopped at filter '{filter.name}'")
                break
        
        logger.info(f"Pipeline '{self.name}' completed")
        return data


class ParallelPipeline(Pipeline):
    """Pipeline that executes filters in parallel."""
    
    async def execute(self, data: PipelineData) -> List[PipelineData]:
        """
        Execute filters in parallel, each receiving a copy of the input.
        
        Args:
            data: Initial pipeline data
            
        Returns:
            List of transformed data from each filter
        """
        logger.info(
            f"Starting parallel pipeline '{self.name}' with {len(self.filters)} filters"
        )
        
        # Create data copies for each filter
        tasks = []
        for filter in self.filters:
            # Create a copy of the data
            data_copy = PipelineData(
                content=data.content,
                metadata=data.metadata.copy(),
                transformations=data.transformations.copy(),
            )
            tasks.append(filter.process(data_copy))
        
        # Execute all filters concurrently
        results = await asyncio.gather(*tasks)
        
        logger.info(f"Parallel pipeline '{self.name}' completed")
        return results


async def create_filter_agent(
    client: AIProjectClient,
    name: str,
    filter_instructions: str,
    model: str = "gpt-4",
) -> str:
    """Create a specialized agent for a filter."""
    agent = client.agents.create_agent(
        model=model,
        name=name,
        instructions=filter_instructions,
    )
    logger.info(f"Created filter agent: {name} (ID: {agent.id})")
    return agent.id


async def demo_text_processing_pipeline() -> None:
    """
    Demonstrate a text processing pipeline with multiple cognitive filters:
    1. Sentiment Analysis
    2. Entity Extraction
    3. Summarization
    """
    config = load_env_config()
    client = get_project_client()
    model = config.get("model_deployment_name", "gpt-4")
    
    # Create specialized agents for each filter
    sentiment_agent_id = await create_filter_agent(
        client,
        "Sentiment Analyzer",
        """Analyze the sentiment of the input text. 
        Provide a sentiment score (positive/negative/neutral) and key emotional indicators.
        Return the analysis in a clear, structured format.""",
        model=model,
    )
    
    entity_agent_id = await create_filter_agent(
        client,
        "Entity Extractor",
        """Extract and identify key entities from the input text.
        Find: people, organizations, locations, dates, and key concepts.
        Return the entities in a structured list.""",
        model=model,
    )
    
    summary_agent_id = await create_filter_agent(
        client,
        "Summarizer",
        """Create a concise summary of the input text.
        Focus on the main points and key takeaways.
        Keep the summary under 100 words.""",
        model=model,
    )
    
    # Build the pipeline
    pipeline = Pipeline("Text Processing Pipeline")
    
    pipeline.add_filter(
        CognitiveFilter("Sentiment Analysis", client, sentiment_agent_id, "")
    ).add_filter(
        CognitiveFilter("Entity Extraction", client, entity_agent_id, "")
    ).add_filter(
        CognitiveFilter("Summarization", client, summary_agent_id, "")
    )
    
    # Sample input
    input_text = """
    Microsoft announced today the launch of Azure AI Foundry, a comprehensive platform
    for building intelligent applications. The CEO, Satya Nadella, emphasized the 
    importance of responsible AI development. The platform will be available globally
    starting next month, with special pricing for startups and educational institutions.
    """
    
    data = PipelineData(content=input_text)
    
    # Execute pipeline
    result = await pipeline.execute(data)
    
    print("\n" + "="*80)
    print("PIPELINE EXECUTION RESULTS")
    print("="*80)
    print(f"\nOriginal Input:\n{input_text}")
    print(f"\nTransformations Applied:")
    for transformation in result.transformations:
        print(f"  - {transformation}")
    print(f"\nFinal Output:\n{result.content}")
    print(f"\nMetadata: {result.metadata}")
    print("="*80)


async def main() -> None:
    """Main entry point."""
    await demo_text_processing_pipeline()


if __name__ == "__main__":
    asyncio.run(main())
