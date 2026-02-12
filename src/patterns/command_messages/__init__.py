"""Implementação do padrão Command Messages."""

import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from datetime import datetime
import uuid

from agents.base_agent import BaseAgent
from shared.models import (
    AgentConfig,
    AgentMessage,
    CommandMessage,
    ResponseMessage,
    MessageType
)

logger = logging.getLogger(__name__)


class CommandHandler(BaseAgent):
    """
    Agente que processa comandos e retorna respostas.
    
    Implementa o padrão Command Message onde comandos específicos
    são executados e respostas são retornadas.
    """
    
    def __init__(
        self,
        config: AgentConfig,
        command_handlers: Optional[Dict[str, Callable]] = None
    ):
        """
        Inicializa o handler de comandos.
        
        Args:
            config: Configuração do agente
            command_handlers: Dicionário mapeando nomes de comandos para funções
        """
        super().__init__(config)
        self._command_handlers = command_handlers or {}
        self.logger.info(f"Handler criado com {len(self._command_handlers)} comandos")
    
    def register_command(self, command_name: str, handler: Callable) -> None:
        """
        Registra um novo comando.
        
        Args:
            command_name: Nome do comando
            handler: Função que processa o comando
        """
        self._command_handlers[command_name] = handler
        self.logger.info(f"Comando '{command_name}' registrado")
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Processa uma mensagem de comando.
        
        Args:
            message: Mensagem recebida
        
        Returns:
            Mensagem de resposta
        """
        if not isinstance(message, CommandMessage):
            self.logger.warning(f"Mensagem {message.id} não é um comando")
            return self._create_error_response(
                message,
                "Message is not a CommandMessage"
            )
        
        return await self.execute_command(message)
    
    async def execute_command(self, command: CommandMessage) -> ResponseMessage:
        """
        Executa um comando específico.
        
        Args:
            command: Comando a executar
        
        Returns:
            Resposta da execução
        """
        command_name = command.command_name
        
        if command_name not in self._command_handlers:
            self.logger.error(f"Comando '{command_name}' não encontrado")
            return self._create_error_response(
                command,
                f"Unknown command: {command_name}"
            )
        
        try:
            self.logger.info(f"Executando comando '{command_name}' (msg: {command.id})")
            
            # Executa o handler
            handler = self._command_handlers[command_name]
            result = handler(command.parameters)
            
            # Se for coroutine, aguarda
            if asyncio.iscoroutine(result):
                result = await result
            
            # Cria resposta de sucesso
            return self._create_success_response(command, result)
        
        except Exception as e:
            self.logger.error(f"Erro ao executar comando '{command_name}': {str(e)}")
            return self._create_error_response(command, str(e))
    
    def _create_success_response(
        self,
        command: CommandMessage,
        result: Any
    ) -> ResponseMessage:
        """Cria uma resposta de sucesso."""
        return ResponseMessage(
            id=str(uuid.uuid4()),
            source=self.name,
            destination=command.source,
            correlation_id=command.id,
            status="success",
            result=result,
            payload={"result": result}
        )
    
    def _create_error_response(
        self,
        command: AgentMessage,
        error_message: str
    ) -> ResponseMessage:
        """Cria uma resposta de erro."""
        return ResponseMessage(
            id=str(uuid.uuid4()),
            source=self.name,
            destination=command.source,
            correlation_id=command.id,
            status="error",
            error=error_message,
            payload={"error": error_message}
        )


class CommandInvoker:
    """
    Cliente que invoca comandos e aguarda respostas.
    
    Implementa o padrão Request-Reply para comunicação com agentes.
    """
    
    def __init__(self, name: str = "CommandInvoker"):
        """
        Inicializa o invocador.
        
        Args:
            name: Nome do invocador
        """
        self.name = name
        self.logger = logging.getLogger(f"CommandInvoker.{name}")
        self._pending_requests: Dict[str, asyncio.Future] = {}
    
    async def invoke_command(
        self,
        handler: CommandHandler,
        command_name: str,
        parameters: Dict[str, Any],
        timeout: int = 30
    ) -> ResponseMessage:
        """
        Invoca um comando e aguarda a resposta.
        
        Args:
            handler: Handler que processará o comando
            command_name: Nome do comando
            parameters: Parâmetros do comando
            timeout: Timeout em segundos
        
        Returns:
            Resposta do comando
        
        Raises:
            asyncio.TimeoutError: Se o timeout for excedido
        """
        # Cria o comando
        command = CommandMessage(
            id=str(uuid.uuid4()),
            source=self.name,
            destination=handler.name,
            command_name=command_name,
            parameters=parameters
        )
        
        self.logger.info(f"Invocando comando '{command_name}' (id: {command.id})")
        
        try:
            # Executa o comando com timeout
            response = await asyncio.wait_for(
                handler.execute_command(command),
                timeout=timeout
            )
            
            self.logger.info(
                f"Comando '{command_name}' executado: {response.status}"
            )
            
            return response
        
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout ao executar comando '{command_name}'")
            raise
        
        except Exception as e:
            self.logger.error(f"Erro ao invocar comando: {str(e)}")
            raise
    
    async def invoke_async(
        self,
        handler: CommandHandler,
        command_name: str,
        parameters: Dict[str, Any]
    ) -> str:
        """
        Invoca um comando de forma assíncrona (fire-and-forget).
        
        Args:
            handler: Handler que processará o comando
            command_name: Nome do comando
            parameters: Parâmetros do comando
        
        Returns:
            ID do comando para correlação futura
        """
        command = CommandMessage(
            id=str(uuid.uuid4()),
            source=self.name,
            destination=handler.name,
            command_name=command_name,
            parameters=parameters
        )
        
        self.logger.info(f"Invocando comando assíncrono '{command_name}' (id: {command.id})")
        
        # Dispara o comando sem aguardar
        asyncio.create_task(handler.execute_command(command))
        
        return command.id


class CommandBus:
    """
    Barramento de comandos que roteia comandos para handlers apropriados.
    
    Facilita o desacoplamento entre invocadores e handlers.
    """
    
    def __init__(self):
        """Inicializa o barramento de comandos."""
        self._handlers: Dict[str, CommandHandler] = {}
        self.logger = logging.getLogger("CommandBus")
    
    def register_handler(self, command_name: str, handler: CommandHandler) -> None:
        """
        Registra um handler para um comando específico.
        
        Args:
            command_name: Nome do comando
            handler: Handler que processará o comando
        """
        self._handlers[command_name] = handler
        self.logger.info(f"Handler '{handler.name}' registrado para comando '{command_name}'")
    
    async def dispatch(
        self,
        command_name: str,
        parameters: Dict[str, Any],
        source: str = "CommandBus"
    ) -> ResponseMessage:
        """
        Despacha um comando para o handler apropriado.
        
        Args:
            command_name: Nome do comando
            parameters: Parâmetros do comando
            source: Origem do comando
        
        Returns:
            Resposta do comando
        
        Raises:
            ValueError: Se não houver handler para o comando
        """
        if command_name not in self._handlers:
            raise ValueError(f"Nenhum handler registrado para comando '{command_name}'")
        
        handler = self._handlers[command_name]
        
        command = CommandMessage(
            id=str(uuid.uuid4()),
            source=source,
            destination=handler.name,
            command_name=command_name,
            parameters=parameters
        )
        
        self.logger.info(f"Despachando comando '{command_name}' para '{handler.name}'")
        
        return await handler.execute_command(command)
    
    def list_commands(self) -> list[str]:
        """Retorna a lista de comandos registrados."""
        return list(self._handlers.keys())
    
    def __repr__(self) -> str:
        return f"<CommandBus(commands={self.list_commands()})>"


# Decorador para facilitar o registro de comandos
def command(command_name: str):
    """
    Decorador para registrar funções como handlers de comando.
    
    Args:
        command_name: Nome do comando
    
    Usage:
        @command("process_data")
        async def process_data_handler(params):
            return {"processed": params}
    """
    def decorator(func: Callable) -> Callable:
        func._command_name = command_name
        return func
    return decorator
