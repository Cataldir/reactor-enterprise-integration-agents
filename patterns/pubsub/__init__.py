"""Implementação do padrão Publish-Subscribe usando Azure Service Bus Topics."""

import asyncio
import json
import logging
from typing import Optional, List, Dict, Any, Callable

from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient, ServiceBusReceiver, ServiceBusSender

from agents.base_agent import BaseAgent
from shared.models import AgentConfig, AgentMessage, EventMessage
from shared.azure_clients import (
    get_async_service_bus_client,
    get_topic_name,
    get_subscription_name
)

logger = logging.getLogger(__name__)


class PublisherAgent(BaseAgent):
    """
    Agente que publica mensagens em um tópico do Azure Service Bus.
    
    Implementa o lado publicador do padrão Pub/Sub.
    """
    
    def __init__(
        self,
        config: AgentConfig,
        topic_name: Optional[str] = None,
        connection_string: Optional[str] = None
    ):
        """
        Inicializa o agente publicador.
        
        Args:
            config: Configuração do agente
            topic_name: Nome do tópico
            connection_string: String de conexão do Service Bus
        """
        super().__init__(config)
        self.topic_name = topic_name or get_topic_name()
        self._connection_string = connection_string
        self._client: Optional[ServiceBusClient] = None
        self._sender: Optional[ServiceBusSender] = None
    
    async def on_start(self) -> None:
        """Inicializa conexões ao iniciar."""
        self._client = get_async_service_bus_client(self._connection_string)
        self._sender = self._client.get_topic_sender(topic_name=self.topic_name)
        self.logger.info(f"Publicador conectado ao tópico '{self.topic_name}'")
    
    async def on_stop(self) -> None:
        """Fecha conexões ao parar."""
        if self._sender:
            await self._sender.close()
        if self._client:
            await self._client.close()
        self.logger.info("Conexões do publicador fechadas")
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Processa e publica uma mensagem.
        
        Args:
            message: Mensagem a publicar
        
        Returns:
            None (publicadores não retornam respostas)
        """
        await self.publish(message)
        return None
    
    async def publish(self, message: AgentMessage) -> None:
        """
        Publica uma mensagem no tópico.
        
        Args:
            message: Mensagem a publicar
        """
        if not self._sender:
            await self.start()
        
        # Serializa a mensagem
        message_body = message.model_dump_json()
        service_bus_message = ServiceBusMessage(message_body)
        
        # Adiciona propriedades para roteamento
        service_bus_message.application_properties = {
            "message_type": message.type,
            "source": message.source,
            "priority": str(message.priority) if hasattr(message, 'priority') else "normal"
        }
        
        # Publica no tópico
        await self._sender.send_messages(service_bus_message)
        self.logger.info(f"Mensagem {message.id} publicada no tópico '{self.topic_name}'")
    
    async def publish_event(
        self,
        event_name: str,
        event_data: Dict[str, Any]
    ) -> None:
        """
        Publica um evento no tópico.
        
        Args:
            event_name: Nome do evento
            event_data: Dados do evento
        """
        event_message = EventMessage(
            id=self._generate_id(),
            source=self.name,
            event_name=event_name,
            event_data=event_data,
            payload=event_data
        )
        
        await self.publish(event_message)
    
    def _generate_id(self) -> str:
        """Gera um ID único para mensagem."""
        import uuid
        return str(uuid.uuid4())


class SubscriberAgent(BaseAgent):
    """
    Agente que assina um tópico do Azure Service Bus.
    
    Implementa o lado assinante do padrão Pub/Sub.
    """
    
    def __init__(
        self,
        config: AgentConfig,
        topic_name: Optional[str] = None,
        subscription_name: Optional[str] = None,
        connection_string: Optional[str] = None,
        message_handler: Optional[Callable] = None
    ):
        """
        Inicializa o agente assinante.
        
        Args:
            config: Configuração do agente
            topic_name: Nome do tópico
            subscription_name: Nome da assinatura
            connection_string: String de conexão do Service Bus
            message_handler: Função para processar mensagens recebidas
        """
        super().__init__(config)
        self.topic_name = topic_name or get_topic_name()
        self.subscription_name = subscription_name or f"{config.name}-subscription"
        self._connection_string = connection_string
        self._message_handler = message_handler
        self._client: Optional[ServiceBusClient] = None
        self._receiver: Optional[ServiceBusReceiver] = None
    
    async def on_start(self) -> None:
        """Inicializa conexões ao iniciar."""
        self._client = get_async_service_bus_client(self._connection_string)
        self._receiver = self._client.get_subscription_receiver(
            topic_name=self.topic_name,
            subscription_name=self.subscription_name
        )
        self.logger.info(
            f"Assinante conectado ao tópico '{self.topic_name}' "
            f"via assinatura '{self.subscription_name}'"
        )
    
    async def on_stop(self) -> None:
        """Fecha conexões ao parar."""
        if self._receiver:
            await self._receiver.close()
        if self._client:
            await self._client.close()
        self.logger.info("Conexões do assinante fechadas")
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Processa uma mensagem recebida do tópico.
        
        Args:
            message: Mensagem recebida
        
        Returns:
            None (assinantes processam mas não retornam)
        """
        self.logger.info(f"Assinante '{self.name}' processando mensagem {message.id}")
        
        if self._message_handler:
            try:
                result = self._message_handler(message)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                await self.handle_error(e, message)
        else:
            # Implementação padrão - apenas loga
            self.logger.info(f"Mensagem recebida: {message.payload}")
        
        return None
    
    async def start_listening(self) -> None:
        """
        Inicia a escuta contínua de mensagens do tópico.
        
        Este método fica em loop processando mensagens até que
        o agente seja parado.
        """
        if not self._receiver:
            await self.start()
        
        self.logger.info(
            f"Iniciando escuta no tópico '{self.topic_name}' "
            f"(assinatura: '{self.subscription_name}')"
        )
        
        try:
            async with self._receiver:
                while self.is_running():
                    # Recebe mensagens
                    received_msgs = await self._receiver.receive_messages(
                        max_message_count=10,
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
            self.logger.error(f"Erro na escuta do tópico: {str(e)}", exc_info=True)
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
            await self.process_message(agent_message)
            
            # Completa a mensagem
            await self._receiver.complete_message(msg)
            self.logger.debug(f"Mensagem {agent_message.id} processada e completada")
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao deserializar mensagem: {str(e)}")
            await self._receiver.dead_letter_message(msg, reason="Invalid JSON")
        
        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem: {str(e)}", exc_info=True)
            await self._receiver.abandon_message(msg)


class PubSubCoordinator:
    """
    Coordenador para gerenciar múltiplos publicadores e assinantes.
    
    Facilita a criação e gerenciamento de sistemas Pub/Sub complexos.
    """
    
    def __init__(
        self,
        topic_name: Optional[str] = None,
        connection_string: Optional[str] = None
    ):
        """
        Inicializa o coordenador.
        
        Args:
            topic_name: Nome do tópico
            connection_string: String de conexão
        """
        self.topic_name = topic_name or get_topic_name()
        self._connection_string = connection_string
        self.publishers: List[PublisherAgent] = []
        self.subscribers: List[SubscriberAgent] = []
        self.logger = logging.getLogger("PubSubCoordinator")
    
    def add_publisher(self, publisher: PublisherAgent) -> None:
        """Adiciona um publicador ao coordenador."""
        self.publishers.append(publisher)
        self.logger.info(f"Publicador '{publisher.name}' adicionado")
    
    def add_subscriber(self, subscriber: SubscriberAgent) -> None:
        """Adiciona um assinante ao coordenador."""
        self.subscribers.append(subscriber)
        self.logger.info(f"Assinante '{subscriber.name}' adicionado")
    
    async def start_all(self) -> None:
        """Inicia todos os publicadores e assinantes."""
        self.logger.info("Iniciando todos os agentes Pub/Sub")
        
        # Inicia publicadores
        for publisher in self.publishers:
            await publisher.start()
        
        # Inicia assinantes
        for subscriber in self.subscribers:
            await subscriber.start()
        
        self.logger.info(
            f"{len(self.publishers)} publicadores e "
            f"{len(self.subscribers)} assinantes iniciados"
        )
    
    async def stop_all(self) -> None:
        """Para todos os publicadores e assinantes."""
        self.logger.info("Parando todos os agentes Pub/Sub")
        
        tasks = []
        for agent in self.publishers + self.subscribers:
            tasks.append(agent.stop())
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self.logger.info("Todos os agentes Pub/Sub parados")
    
    async def start_listening_all(self) -> None:
        """Inicia a escuta em todos os assinantes."""
        if not self.subscribers:
            self.logger.warning("Nenhum assinante configurado")
            return
        
        self.logger.info(f"Iniciando escuta em {len(self.subscribers)} assinantes")
        
        tasks = [sub.start_listening() for sub in self.subscribers]
        await asyncio.gather(*tasks, return_exceptions=True)
