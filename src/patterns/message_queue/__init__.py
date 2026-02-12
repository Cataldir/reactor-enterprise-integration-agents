"""Implementação do padrão Message Queue usando Azure Service Bus."""

import asyncio
import json
import logging
from typing import Optional, Callable, Any

from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient, ServiceBusReceiver, ServiceBusSender

from agents.base_agent import BaseAgent
from shared.models import AgentConfig, AgentMessage, MessageType
from shared.azure_clients import get_async_service_bus_client, get_queue_name

logger = logging.getLogger(__name__)


class MessageQueueAgent(BaseAgent):
    """
    Agente que processa mensagens de uma fila do Azure Service Bus.
    
    Este agente implementa o padrão Message Queue, onde mensagens
    são processadas de forma assíncrona e confiável.
    """
    
    def __init__(
        self,
        config: AgentConfig,
        queue_name: Optional[str] = None,
        connection_string: Optional[str] = None,
        max_concurrent_calls: int = 5
    ):
        """
        Inicializa o agente de fila.
        
        Args:
            config: Configuração do agente
            queue_name: Nome da fila
            connection_string: String de conexão do Service Bus
            max_concurrent_calls: Número máximo de mensagens processadas simultaneamente
        """
        super().__init__(config)
        self.queue_name = queue_name or get_queue_name()
        self._client: Optional[ServiceBusClient] = None
        self._receiver: Optional[ServiceBusReceiver] = None
        self._sender: Optional[ServiceBusSender] = None
        self._connection_string = connection_string
        self._max_concurrent_calls = max_concurrent_calls
    
    async def on_start(self) -> None:
        """Inicializa conexões ao iniciar o agente."""
        self._client = get_async_service_bus_client(self._connection_string)
        self._receiver = self._client.get_queue_receiver(queue_name=self.queue_name)
        self._sender = self._client.get_queue_sender(queue_name=self.queue_name)
        self.logger.info(f"Conectado à fila '{self.queue_name}'")
    
    async def on_stop(self) -> None:
        """Fecha conexões ao parar o agente."""
        if self._receiver:
            await self._receiver.close()
        if self._sender:
            await self._sender.close()
        if self._client:
            await self._client.close()
        self.logger.info("Conexões fechadas")
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Processa uma mensagem da fila.
        
        Args:
            message: Mensagem a processar
        
        Returns:
            Mensagem de resposta (implementar lógica customizada)
        """
        self.logger.info(f"Processando mensagem: {message.id}")
        # Implementar lógica de processamento aqui
        # Este é um exemplo básico que apenas loga a mensagem
        self.logger.info(f"Payload: {message.payload}")
        return None
    
    async def send_message(self, message: AgentMessage) -> None:
        """
        Envia uma mensagem para a fila.
        
        Args:
            message: Mensagem a enviar
        """
        if not self._sender:
            raise RuntimeError("Agente não foi iniciado. Chame start() primeiro.")
        
        # Serializa a mensagem
        message_body = message.model_dump_json()
        service_bus_message = ServiceBusMessage(message_body)
        
        # Envia para a fila
        await self._sender.send_messages(service_bus_message)
        self.logger.info(f"Mensagem {message.id} enviada para a fila '{self.queue_name}'")
    
    async def start_processing(self) -> None:
        """
        Inicia o processamento contínuo de mensagens da fila.
        
        Este método fica em loop processando mensagens até que
        o agente seja parado.
        """
        if not self._receiver:
            await self.start()
        
        self.logger.info(f"Iniciando processamento da fila '{self.queue_name}'")
        
        try:
            async with self._receiver:
                while self.is_running():
                    # Recebe mensagens em lote
                    received_msgs = await self._receiver.receive_messages(
                        max_message_count=self._max_concurrent_calls,
                        max_wait_time=5
                    )
                    
                    if not received_msgs:
                        continue
                    
                    # Processa mensagens em paralelo
                    tasks = []
                    for msg in received_msgs:
                        task = self._process_service_bus_message(msg)
                        tasks.append(task)
                    
                    await asyncio.gather(*tasks, return_exceptions=True)
        
        except Exception as e:
            self.logger.error(f"Erro no processamento da fila: {str(e)}", exc_info=True)
            raise
    
    async def _process_service_bus_message(self, msg: Any) -> None:
        """
        Processa uma mensagem individual do Service Bus.
        
        Args:
            msg: Mensagem do Service Bus
        """
        try:
            # Deserializa a mensagem
            body = str(msg)
            message_data = json.loads(body)
            agent_message = AgentMessage(**message_data)
            
            # Processa a mensagem
            result = await self.process_message(agent_message)
            
            # Completa a mensagem (remove da fila)
            await self._receiver.complete_message(msg)
            self.logger.info(f"Mensagem {agent_message.id} processada e completada")
            
            # Se houver resposta, pode enviar para outra fila se necessário
            if result:
                await self.send_message(result)
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao deserializar mensagem: {str(e)}")
            # Marca como dead letter
            await self._receiver.dead_letter_message(msg, reason="Invalid JSON")
        
        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem: {str(e)}", exc_info=True)
            # Abandona a mensagem para que possa ser reprocessada
            await self._receiver.abandon_message(msg)


class MessageProducer:
    """
    Produtor de mensagens para filas do Service Bus.
    
    Facilita o envio de mensagens para filas sem precisar
    gerenciar um agente completo.
    """
    
    def __init__(
        self,
        queue_name: Optional[str] = None,
        connection_string: Optional[str] = None
    ):
        """
        Inicializa o produtor.
        
        Args:
            queue_name: Nome da fila
            connection_string: String de conexão
        """
        self.queue_name = queue_name or get_queue_name()
        self._connection_string = connection_string
        self._client: Optional[ServiceBusClient] = None
        self._sender: Optional[ServiceBusSender] = None
    
    async def __aenter__(self):
        """Context manager entry."""
        self._client = get_async_service_bus_client(self._connection_string)
        self._sender = self._client.get_queue_sender(queue_name=self.queue_name)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._sender:
            await self._sender.close()
        if self._client:
            await self._client.close()
    
    async def send(self, message: AgentMessage) -> None:
        """
        Envia uma mensagem para a fila.
        
        Args:
            message: Mensagem a enviar
        """
        if not self._sender:
            raise RuntimeError("Produtor não inicializado. Use como context manager.")
        
        message_body = message.model_dump_json()
        service_bus_message = ServiceBusMessage(message_body)
        await self._sender.send_messages(service_bus_message)
        logger.info(f"Mensagem {message.id} enviada para '{self.queue_name}'")
