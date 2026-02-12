"""Modelos de dados compartilhados usando Pydantic."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum


class MessagePriority(str, Enum):
    """Prioridade de mensagens."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MessageType(str, Enum):
    """Tipos de mensagens."""
    COMMAND = "command"
    EVENT = "event"
    QUERY = "query"
    RESPONSE = "response"


class AgentMessage(BaseModel):
    """Modelo base para mensagens entre agentes."""
    
    id: str = Field(description="Identificador único da mensagem")
    type: MessageType = Field(default=MessageType.EVENT, description="Tipo da mensagem")
    source: str = Field(description="Agente ou sistema de origem")
    destination: Optional[str] = Field(default=None, description="Agente de destino")
    priority: MessagePriority = Field(default=MessagePriority.NORMAL, description="Prioridade")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp UTC")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Dados da mensagem")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais")
    correlation_id: Optional[str] = Field(default=None, description="ID de correlação")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class CommandMessage(AgentMessage):
    """Mensagem de comando para agentes."""
    
    type: MessageType = Field(default=MessageType.COMMAND, description="Tipo da mensagem")
    command_name: str = Field(description="Nome do comando a executar")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parâmetros do comando")
    reply_to: Optional[str] = Field(default=None, description="Endereço de resposta")


class EventMessage(AgentMessage):
    """Mensagem de evento para Pub/Sub."""
    
    type: MessageType = Field(default=MessageType.EVENT, description="Tipo da mensagem")
    event_name: str = Field(description="Nome do evento")
    event_data: Dict[str, Any] = Field(default_factory=dict, description="Dados do evento")


class QueryMessage(AgentMessage):
    """Mensagem de consulta (Request-Reply)."""
    
    type: MessageType = Field(default=MessageType.QUERY, description="Tipo da mensagem")
    query: str = Field(description="Consulta a ser executada")
    query_params: Dict[str, Any] = Field(default_factory=dict, description="Parâmetros da consulta")


class ResponseMessage(AgentMessage):
    """Mensagem de resposta."""
    
    type: MessageType = Field(default=MessageType.RESPONSE, description="Tipo da mensagem")
    status: str = Field(description="Status da resposta (success, error, etc)")
    result: Any = Field(default=None, description="Resultado da operação")
    error: Optional[str] = Field(default=None, description="Mensagem de erro, se houver")


class AgentConfig(BaseModel):
    """Configuração de um agente."""
    
    name: str = Field(description="Nome do agente")
    description: Optional[str] = Field(default=None, description="Descrição do agente")
    max_retries: int = Field(default=3, description="Número máximo de tentativas")
    timeout_seconds: int = Field(default=30, description="Timeout em segundos")
    enabled: bool = Field(default=True, description="Se o agente está habilitado")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados customizados")
