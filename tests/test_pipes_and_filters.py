"""Tests for Pipes and Filters pattern."""

import pytest
import uuid
from datetime import datetime

from patterns.pipes_and_filters import (
    Pipeline,
    ValidationFilter,
    TransformFilter,
    EnrichmentFilter,
    FilterAgent
)
from shared.models import AgentConfig, AgentMessage, MessageType


@pytest.mark.asyncio
async def test_validation_filter_accepts_valid_message():
    """Test that validation filter accepts messages with required fields."""
    config = AgentConfig(name="ValidationFilter")
    filter = ValidationFilter(config, required_fields=["name", "email"])
    
    message = AgentMessage(
        id=str(uuid.uuid4()),
        type=MessageType.EVENT,
        source="test",
        payload={"name": "Test User", "email": "test@example.com"}
    )
    
    result = await filter.process_message(message)
    assert result is not None
    assert result.payload == message.payload


@pytest.mark.asyncio
async def test_validation_filter_rejects_invalid_message():
    """Test that validation filter rejects messages without required fields."""
    config = AgentConfig(name="ValidationFilter")
    filter = ValidationFilter(config, required_fields=["name", "email"])
    
    message = AgentMessage(
        id=str(uuid.uuid4()),
        type=MessageType.EVENT,
        source="test",
        payload={"name": "Test User"}  # Missing 'email'
    )
    
    result = await filter.process_message(message)
    assert result is None


@pytest.mark.asyncio
async def test_transform_filter():
    """Test that transform filter applies transformation."""
    config = AgentConfig(name="TransformFilter")
    
    def uppercase_name(payload):
        return {**payload, "name": payload["name"].upper()}
    
    filter = TransformFilter(config, transform_func=uppercase_name)
    
    message = AgentMessage(
        id=str(uuid.uuid4()),
        type=MessageType.EVENT,
        source="test",
        payload={"name": "test user"}
    )
    
    result = await filter.process_message(message)
    assert result is not None
    assert result.payload["name"] == "TEST USER"


@pytest.mark.asyncio
async def test_enrichment_filter():
    """Test that enrichment filter adds data."""
    config = AgentConfig(name="EnrichmentFilter")
    enrichment_data = {"version": "1.0", "processor": "test"}
    filter = EnrichmentFilter(config, enrichment_data=enrichment_data)
    
    message = AgentMessage(
        id=str(uuid.uuid4()),
        type=MessageType.EVENT,
        source="test",
        payload={"name": "Test"}
    )
    
    result = await filter.process_message(message)
    assert result is not None
    assert result.payload["version"] == "1.0"
    assert result.payload["processor"] == "test"
    assert result.payload["name"] == "Test"


@pytest.mark.asyncio
async def test_pipeline_processes_through_all_filters():
    """Test that pipeline processes message through all filters."""
    validation_config = AgentConfig(name="ValidationFilter")
    validation_filter = ValidationFilter(
        validation_config,
        required_fields=["name"]
    )
    
    enrichment_config = AgentConfig(name="EnrichmentFilter")
    enrichment_filter = EnrichmentFilter(
        enrichment_config,
        enrichment_data={"enriched": True}
    )
    
    pipeline = Pipeline([validation_filter, enrichment_filter])
    
    message = AgentMessage(
        id=str(uuid.uuid4()),
        type=MessageType.EVENT,
        source="test",
        payload={"name": "Test"}
    )
    
    result = await pipeline.process(message)
    assert result is not None
    assert result.payload["name"] == "Test"
    assert result.payload["enriched"] is True


@pytest.mark.asyncio
async def test_pipeline_stops_on_validation_failure():
    """Test that pipeline stops when a filter blocks the message."""
    validation_config = AgentConfig(name="ValidationFilter")
    validation_filter = ValidationFilter(
        validation_config,
        required_fields=["required_field"]
    )
    
    enrichment_config = AgentConfig(name="EnrichmentFilter")
    enrichment_filter = EnrichmentFilter(
        enrichment_config,
        enrichment_data={"enriched": True}
    )
    
    pipeline = Pipeline([validation_filter, enrichment_filter])
    
    message = AgentMessage(
        id=str(uuid.uuid4()),
        type=MessageType.EVENT,
        source="test",
        payload={"name": "Test"}  # Missing 'required_field'
    )
    
    result = await pipeline.process(message)
    assert result is None


@pytest.mark.asyncio
async def test_pipeline_batch_processing():
    """Test that pipeline can process batch of messages."""
    validation_config = AgentConfig(name="ValidationFilter")
    validation_filter = ValidationFilter(
        validation_config,
        required_fields=["name"]
    )
    
    pipeline = Pipeline([validation_filter])
    
    messages = [
        AgentMessage(
            id=str(uuid.uuid4()),
            type=MessageType.EVENT,
            source="test",
            payload={"name": f"User {i}"}
        )
        for i in range(10)
    ]
    
    results = await pipeline.process_batch(messages)
    assert len(results) == 10


@pytest.mark.asyncio
async def test_custom_filter():
    """Test creating a custom filter."""
    
    class UppercaseFilter(FilterAgent):
        async def filter(self, message: AgentMessage):
            modified = message.model_copy()
            if "name" in modified.payload:
                modified.payload["name"] = modified.payload["name"].upper()
            return modified
    
    config = AgentConfig(name="UppercaseFilter")
    filter = UppercaseFilter(config)
    
    message = AgentMessage(
        id=str(uuid.uuid4()),
        type=MessageType.EVENT,
        source="test",
        payload={"name": "test"}
    )
    
    result = await filter.process_message(message)
    assert result is not None
    assert result.payload["name"] == "TEST"
