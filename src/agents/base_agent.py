"""Classe base para agentes de integração empresarial."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable
from datetime import datetime
import uuid

from shared.models import AgentConfig, AgentMessage, MessageType

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Classe base abstrata para todos os agentes.
    
    Fornece funcionalidades comuns como logging, configuração,
    e interfaces para processamento de mensagens.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Inicializa o agente base.
        
        Args:
            config: Configuração do agente
        """
        self.config = config
        self.name = config.name
        self.enabled = config.enabled
        self.logger = logging.getLogger(f"Agent.{self.name}")
        self.logger.info(f"Agente '{self.name}' inicializado")
        self._running = False
    
    @abstractmethod
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Processa uma mensagem recebida.
        
        Args:
            message: Mensagem a ser processada
        
        Returns:
            Mensagem de resposta, se aplicável
        """
        pass
    
    async def start(self) -> None:
        """Inicia o agente."""
        if not self.enabled:
            self.logger.warning(f"Agente '{self.name}' está desabilitado")
            return
        
        self._running = True
        self.logger.info(f"Agente '{self.name}' iniciado")
        await self.on_start()
    
    async def stop(self) -> None:
        """Para o agente."""
        self._running = False
        self.logger.info(f"Agente '{self.name}' parado")
        await self.on_stop()
    
    async def on_start(self) -> None:
        """Hook chamado quando o agente inicia. Pode ser sobrescrito."""
        pass
    
    async def on_stop(self) -> None:
        """Hook chamado quando o agente para. Pode ser sobrescrito."""
        pass
    
    def is_running(self) -> bool:
        """Verifica se o agente está em execução."""
        return self._running
    
    def create_message(
        self,
        message_type: MessageType,
        payload: Dict[str, Any],
        destination: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> AgentMessage:
        """
        Cria uma nova mensagem.
        
        Args:
            message_type: Tipo da mensagem
            payload: Dados da mensagem
            destination: Agente de destino (opcional)
            correlation_id: ID de correlação (opcional)
        
        Returns:
            Nova mensagem criada
        """
        return AgentMessage(
            id=str(uuid.uuid4()),
            type=message_type,
            source=self.name,
            destination=destination,
            timestamp=datetime.utcnow(),
            payload=payload,
            correlation_id=correlation_id
        )
    
    async def handle_error(self, error: Exception, message: Optional[AgentMessage] = None) -> None:
        """
        Trata erros que ocorrem durante o processamento.
        
        Args:
            error: Exceção ocorrida
            message: Mensagem sendo processada quando o erro ocorreu
        """
        self.logger.error(
            f"Erro no agente '{self.name}': {str(error)}",
            exc_info=True
        )
        if message:
            self.logger.error(f"Mensagem problemática: {message.model_dump_json()}")
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', enabled={self.enabled})>"


class ProcessingAgent(BaseAgent):
    """
    Agente que processa mensagens com lógica customizável.
    
    Útil para casos simples onde você só precisa definir
    a lógica de processamento.
    """
    
    def __init__(
        self,
        config: AgentConfig,
        process_func: Optional[Callable[[AgentMessage], Optional[AgentMessage]]] = None
    ):
        """
        Inicializa o agente de processamento.
        
        Args:
            config: Configuração do agente
            process_func: Função customizada de processamento
        """
        super().__init__(config)
        self._process_func = process_func
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Processa mensagem usando a função customizada.
        
        Args:
            message: Mensagem a processar
        
        Returns:
            Resultado do processamento
        """
        if not self._process_func:
            self.logger.warning("Nenhuma função de processamento definida")
            return None
        
        try:
            result = self._process_func(message)
            if asyncio.iscoroutine(result):
                result = await result
            return result
        except Exception as e:
            await self.handle_error(e, message)
            return None
