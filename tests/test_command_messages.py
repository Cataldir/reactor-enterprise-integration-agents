"""Tests for Command Messages pattern."""

import pytest
import asyncio
from typing import Dict, Any

from patterns.command_messages import (
    CommandHandler,
    CommandInvoker,
    CommandBus
)
from shared.models import AgentConfig, CommandMessage


async def sample_command_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """Sample command handler for testing."""
    return {"processed": True, "input": params}


async def slow_command_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """Slow command handler for timeout testing."""
    await asyncio.sleep(5)
    return {"done": True}


@pytest.mark.asyncio
async def test_command_handler_executes_command():
    """Test that command handler executes registered command."""
    config = AgentConfig(name="TestHandler")
    handler = CommandHandler(
        config,
        command_handlers={"test_command": sample_command_handler}
    )
    
    command = CommandMessage(
        id="test-id",
        source="test",
        command_name="test_command",
        parameters={"key": "value"}
    )
    
    response = await handler.execute_command(command)
    assert response.status == "success"
    assert response.result["processed"] is True
    assert response.result["input"]["key"] == "value"


@pytest.mark.asyncio
async def test_command_handler_returns_error_for_unknown_command():
    """Test that handler returns error for unknown command."""
    config = AgentConfig(name="TestHandler")
    handler = CommandHandler(config, command_handlers={})
    
    command = CommandMessage(
        id="test-id",
        source="test",
        command_name="unknown_command",
        parameters={}
    )
    
    response = await handler.execute_command(command)
    assert response.status == "error"
    assert "Unknown command" in response.error


@pytest.mark.asyncio
async def test_command_handler_register_command():
    """Test dynamic command registration."""
    config = AgentConfig(name="TestHandler")
    handler = CommandHandler(config)
    
    handler.register_command("new_command", sample_command_handler)
    
    command = CommandMessage(
        id="test-id",
        source="test",
        command_name="new_command",
        parameters={"test": "data"}
    )
    
    response = await handler.execute_command(command)
    assert response.status == "success"


@pytest.mark.asyncio
async def test_command_invoker():
    """Test command invoker."""
    config = AgentConfig(name="TestHandler")
    handler = CommandHandler(
        config,
        command_handlers={"test_command": sample_command_handler}
    )
    
    invoker = CommandInvoker("TestInvoker")
    
    response = await invoker.invoke_command(
        handler,
        "test_command",
        {"key": "value"}
    )
    
    assert response.status == "success"
    assert response.result["processed"] is True


@pytest.mark.asyncio
async def test_command_invoker_timeout():
    """Test that invoker respects timeout."""
    config = AgentConfig(name="TestHandler")
    handler = CommandHandler(
        config,
        command_handlers={"slow_command": slow_command_handler}
    )
    
    invoker = CommandInvoker("TestInvoker")
    
    with pytest.raises(asyncio.TimeoutError):
        await invoker.invoke_command(
            handler,
            "slow_command",
            {},
            timeout=1  # Will timeout
        )


@pytest.mark.asyncio
async def test_command_bus():
    """Test command bus routing."""
    config1 = AgentConfig(name="Handler1")
    handler1 = CommandHandler(
        config1,
        command_handlers={"command1": sample_command_handler}
    )
    
    config2 = AgentConfig(name="Handler2")
    handler2 = CommandHandler(
        config2,
        command_handlers={"command2": sample_command_handler}
    )
    
    bus = CommandBus()
    bus.register_handler("command1", handler1)
    bus.register_handler("command2", handler2)
    
    # Test routing to handler1
    response1 = await bus.dispatch("command1", {"test": "data1"})
    assert response1.status == "success"
    assert response1.source == "Handler1"
    
    # Test routing to handler2
    response2 = await bus.dispatch("command2", {"test": "data2"})
    assert response2.status == "success"
    assert response2.source == "Handler2"


@pytest.mark.asyncio
async def test_command_bus_unknown_command():
    """Test command bus with unknown command."""
    bus = CommandBus()
    
    with pytest.raises(ValueError, match="Nenhum handler registrado"):
        await bus.dispatch("unknown", {})


@pytest.mark.asyncio
async def test_command_bus_list_commands():
    """Test listing registered commands."""
    config = AgentConfig(name="Handler")
    handler = CommandHandler(
        config,
        command_handlers={"cmd1": sample_command_handler}
    )
    
    bus = CommandBus()
    bus.register_handler("cmd1", handler)
    bus.register_handler("cmd2", handler)
    
    commands = bus.list_commands()
    assert "cmd1" in commands
    assert "cmd2" in commands
    assert len(commands) == 2
