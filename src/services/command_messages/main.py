"""
Pattern 4: Command Messages with Asynchronous Pipelines

This module implements the Command Message pattern where AI agents
process commands asynchronously in a pipeline architecture.

Key Features:
- Command-based messaging pattern
- Asynchronous pipeline execution
- AI agents as command processors
- Result tracking and status updates
"""

import asyncio
import logging
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid

from azure.eventhub import EventData
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import MessageRole

from shared.utils import get_project_client, load_env_config, EventHubAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommandType(str, Enum):
    """Available command types."""
    PROCESS_DATA = "process_data"
    ANALYZE_CONTENT = "analyze_content"
    GENERATE_REPORT = "generate_report"
    VALIDATE_INPUT = "validate_input"
    TRANSFORM_DATA = "transform_data"


class CommandStatus(str, Enum):
    """Command execution status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CommandMessage:
    """A command message with parameters and metadata."""
    command_id: str
    command_type: CommandType
    parameters: Dict[str, Any]
    status: CommandStatus = CommandStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "command_id": self.command_id,
            "command_type": self.command_type.value,
            "parameters": self.parameters,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommandMessage":
        """Create from dictionary."""
        return cls(
            command_id=data["command_id"],
            command_type=CommandType(data["command_type"]),
            parameters=data["parameters"],
            status=CommandStatus(data.get("status", "pending")),
            result=data.get("result"),
            error=data.get("error"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat()),
            metadata=data.get("metadata", {}),
        )
    
    def update_status(self, status: CommandStatus, error: Optional[str] = None) -> None:
        """Update command status."""
        self.status = status
        self.updated_at = datetime.utcnow().isoformat()
        if error:
            self.error = error


class CommandProcessor:
    """An AI agent that processes specific command types."""
    
    def __init__(
        self,
        name: str,
        project_client: AIProjectClient,
        agent_id: str,
        command_types: List[CommandType],
        processing_instructions: str,
    ):
        self.name = name
        self.project_client = project_client
        self.agent_id = agent_id
        self.command_types = command_types
        self.processing_instructions = processing_instructions
        self.thread_id = None
        self.processed_commands = 0
    
    def _initialize_thread(self) -> str:
        """Initialize conversation thread."""
        if not self.thread_id:
            thread = self.project_client.agents.create_thread()
            self.thread_id = thread.id
            logger.info(f"Processor '{self.name}' created thread: {self.thread_id}")
        return self.thread_id
    
    def can_process(self, command: CommandMessage) -> bool:
        """Check if this processor can handle the command."""
        return command.command_type in self.command_types
    
    async def process_command(self, command: CommandMessage) -> CommandMessage:
        """
        Process a command using the AI agent.
        
        Args:
            command: The command to process
            
        Returns:
            Updated command with results
        """
        if not self.can_process(command):
            command.update_status(
                CommandStatus.FAILED,
                f"Processor '{self.name}' cannot handle {command.command_type}"
            )
            return command
        
        logger.info(
            f"Processor '{self.name}' processing command {command.command_id} "
            f"({command.command_type})"
        )
        
        command.update_status(CommandStatus.PROCESSING)
        
        try:
            # Create prompt
            prompt = f"""
            {self.processing_instructions}
            
            Command Type: {command.command_type.value}
            Command ID: {command.command_id}
            
            Parameters:
            {json.dumps(command.parameters, indent=2)}
            
            Please execute this command and provide:
            1. The execution result
            2. Any relevant output data
            3. Status of execution (success/failure)
            4. Any warnings or recommendations
            
            Format your response as structured data that can be parsed.
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
                    
                    # Update command with results
                    command.result = {
                        "processor": self.name,
                        "response": response,
                        "execution_time": datetime.utcnow().isoformat(),
                    }
                    command.update_status(CommandStatus.COMPLETED)
                    self.processed_commands += 1
                    
                    logger.info(
                        f"Processor '{self.name}' completed command "
                        f"{command.command_id}"
                    )
                    return command
            
            # Handle failures
            command.update_status(
                CommandStatus.FAILED,
                f"Agent run status: {run.status}"
            )
            return command
            
        except Exception as e:
            logger.error(
                f"Error in processor '{self.name}' for command "
                f"{command.command_id}: {e}",
                exc_info=True
            )
            command.update_status(CommandStatus.FAILED, str(e))
            return command


class AsyncCommandPipeline:
    """Asynchronous pipeline for processing commands."""
    
    def __init__(
        self,
        name: str,
        eventhub_adapter: EventHubAdapter,
    ):
        self.name = name
        self.eventhub_adapter = eventhub_adapter
        self.processors: List[CommandProcessor] = []
        self.command_store: Dict[str, CommandMessage] = {}
    
    def register_processor(self, processor: CommandProcessor) -> None:
        """Register a command processor."""
        self.processors.append(processor)
        logger.info(
            f"Registered processor '{processor.name}' for commands: "
            f"{[ct.value for ct in processor.command_types]}"
        )
    
    async def submit_command(self, command: CommandMessage) -> str:
        """
        Submit a command to the pipeline.
        
        Args:
            command: The command to submit
            
        Returns:
            Command ID for tracking
        """
        logger.info(f"Submitting command: {command.command_id} ({command.command_type})")
        
        # Store command
        self.command_store[command.command_id] = command
        
        # Send to Event Hub
        await self.eventhub_adapter.send_event(command.to_dict())
        
        return command.command_id
    
    def get_command_status(self, command_id: str) -> Optional[CommandMessage]:
        """Get the status of a command."""
        return self.command_store.get(command_id)
    
    async def _process_event(self, event: EventData) -> None:
        """Process a command from Event Hub."""
        try:
            # Parse command
            command_data = json.loads(event.body_as_str())
            command = CommandMessage.from_dict(command_data)
            
            # Skip if already processing or completed
            if command.status in [CommandStatus.PROCESSING, CommandStatus.COMPLETED]:
                return
            
            logger.info(f"Processing command: {command.command_id}")
            
            # Find processor
            processor = next(
                (p for p in self.processors if p.can_process(command)),
                None
            )
            
            if not processor:
                logger.warning(
                    f"No processor available for command type: {command.command_type}"
                )
                command.update_status(
                    CommandStatus.FAILED,
                    "No processor available"
                )
            else:
                # Process command
                command = await processor.process_command(command)
            
            # Update command store
            self.command_store[command.command_id] = command
            
            # Send result back to Event Hub
            await self.eventhub_adapter.send_event(command.to_dict())
            
        except Exception as e:
            logger.error(f"Error processing event: {e}", exc_info=True)
    
    async def start_processing(self) -> None:
        """Start processing commands from Event Hub."""
        logger.info(f"Pipeline '{self.name}' starting command processing...")
        await self.eventhub_adapter.receive_events(self._process_event)


async def create_command_processor_agent(
    client: AIProjectClient,
    name: str,
    instructions: str,
    model: str = "gpt-4",
) -> str:
    """Create an AI agent for command processing."""
    agent = client.agents.create_agent(
        model=model,
        name=name,
        instructions=instructions,
    )
    logger.info(f"Created command processor agent: {name} (ID: {agent.id})")
    return agent.id


async def demo_command_pipeline() -> None:
    """Demonstrate the command pipeline with multiple processors."""
    config = load_env_config()
    client = get_project_client()
    model = config.get("model_deployment_name", "gpt-4")
    
    # Create Event Hub adapter
    eventhub_adapter = EventHubAdapter(
        connection_string=config["eventhub_connection_string"],
        eventhub_name=config["eventhub_name"],
    )
    
    # Create pipeline
    pipeline = AsyncCommandPipeline("Command Pipeline", eventhub_adapter)
    
    # Create specialized processors
    
    # 1. Data Processing Agent
    data_agent_id = await create_command_processor_agent(
        client,
        "Data Processor",
        """You are a data processing expert. When you receive PROCESS_DATA or 
        TRANSFORM_DATA commands, analyze the data and perform the requested 
        transformations. Provide clear results with any data quality issues noted.""",
        model=model,
    )
    
    data_processor = CommandProcessor(
        name="Data Processor",
        project_client=client,
        agent_id=data_agent_id,
        command_types=[CommandType.PROCESS_DATA, CommandType.TRANSFORM_DATA],
        processing_instructions="Process and transform data",
    )
    pipeline.register_processor(data_processor)
    
    # 2. Content Analysis Agent
    analysis_agent_id = await create_command_processor_agent(
        client,
        "Content Analyzer",
        """You are a content analysis expert. When you receive ANALYZE_CONTENT 
        commands, perform comprehensive analysis including sentiment, topics, 
        entities, and key insights.""",
        model=model,
    )
    
    analysis_processor = CommandProcessor(
        name="Content Analyzer",
        project_client=client,
        agent_id=analysis_agent_id,
        command_types=[CommandType.ANALYZE_CONTENT],
        processing_instructions="Analyze content comprehensively",
    )
    pipeline.register_processor(analysis_processor)
    
    # 3. Report Generation Agent
    report_agent_id = await create_command_processor_agent(
        client,
        "Report Generator",
        """You are a report generation expert. When you receive GENERATE_REPORT 
        commands, create well-structured, professional reports based on the 
        provided data.""",
        model=model,
    )
    
    report_processor = CommandProcessor(
        name="Report Generator",
        project_client=client,
        agent_id=report_agent_id,
        command_types=[CommandType.GENERATE_REPORT],
        processing_instructions="Generate professional reports",
    )
    pipeline.register_processor(report_processor)
    
    # Submit sample commands
    commands = [
        CommandMessage(
            command_id=str(uuid.uuid4()),
            command_type=CommandType.PROCESS_DATA,
            parameters={
                "data": [1, 2, 3, 4, 5],
                "operation": "calculate_statistics",
            },
        ),
        CommandMessage(
            command_id=str(uuid.uuid4()),
            command_type=CommandType.ANALYZE_CONTENT,
            parameters={
                "content": "This product is amazing! Best purchase ever!",
                "analysis_type": "sentiment",
            },
        ),
    ]
    
    # Submit commands
    for cmd in commands:
        await pipeline.submit_command(cmd)
        await asyncio.sleep(1)
    
    # Start processing
    try:
        await pipeline.start_processing()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await eventhub_adapter.close()


async def main() -> None:
    """Main entry point."""
    await demo_command_pipeline()


if __name__ == "__main__":
    asyncio.run(main())
