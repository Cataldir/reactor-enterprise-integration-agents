"""Clientes Azure reutilizáveis para Service Bus e outros serviços."""

import os
from typing import Optional
from azure.servicebus import ServiceBusClient
from azure.servicebus.aio import ServiceBusClient as AsyncServiceBusClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()


def get_service_bus_client(connection_string: Optional[str] = None) -> ServiceBusClient:
    """
    Obtém um cliente síncrono do Azure Service Bus.
    
    Args:
        connection_string: String de conexão. Se não fornecida, usa a variável de ambiente.
    
    Returns:
        ServiceBusClient configurado
    """
    conn_str = connection_string or os.getenv("AZURE_SERVICEBUS_CONNECTION_STRING")
    if not conn_str:
        raise ValueError(
            "Connection string não encontrada. "
            "Defina AZURE_SERVICEBUS_CONNECTION_STRING no .env"
        )
    return ServiceBusClient.from_connection_string(conn_str)


def get_async_service_bus_client(
    connection_string: Optional[str] = None
) -> AsyncServiceBusClient:
    """
    Obtém um cliente assíncrono do Azure Service Bus.
    
    Args:
        connection_string: String de conexão. Se não fornecida, usa a variável de ambiente.
    
    Returns:
        AsyncServiceBusClient configurado
    """
    conn_str = connection_string or os.getenv("AZURE_SERVICEBUS_CONNECTION_STRING")
    if not conn_str:
        raise ValueError(
            "Connection string não encontrada. "
            "Defina AZURE_SERVICEBUS_CONNECTION_STRING no .env"
        )
    return AsyncServiceBusClient.from_connection_string(conn_str)


def get_queue_name() -> str:
    """Obtém o nome da fila do Service Bus das variáveis de ambiente."""
    queue_name = os.getenv("AZURE_SERVICEBUS_QUEUE_NAME", "agent-queue")
    return queue_name


def get_topic_name() -> str:
    """Obtém o nome do tópico do Service Bus das variáveis de ambiente."""
    topic_name = os.getenv("AZURE_SERVICEBUS_TOPIC_NAME", "agent-topic")
    return topic_name


def get_subscription_name() -> str:
    """Obtém o nome da assinatura do Service Bus das variáveis de ambiente."""
    subscription_name = os.getenv("AZURE_SERVICEBUS_SUBSCRIPTION_NAME", "agent-subscription")
    return subscription_name


class AzureServiceBusConfig:
    """Configuração centralizada para Azure Service Bus."""
    
    def __init__(
        self,
        connection_string: Optional[str] = None,
        queue_name: Optional[str] = None,
        topic_name: Optional[str] = None,
        subscription_name: Optional[str] = None
    ):
        self.connection_string = connection_string or os.getenv("AZURE_SERVICEBUS_CONNECTION_STRING")
        self.queue_name = queue_name or get_queue_name()
        self.topic_name = topic_name or get_topic_name()
        self.subscription_name = subscription_name or get_subscription_name()
        
        if not self.connection_string:
            raise ValueError(
                "Connection string não encontrada. "
                "Defina AZURE_SERVICEBUS_CONNECTION_STRING no .env"
            )
    
    def get_client(self) -> ServiceBusClient:
        """Retorna um cliente síncrono do Service Bus."""
        return ServiceBusClient.from_connection_string(self.connection_string)
    
    def get_async_client(self) -> AsyncServiceBusClient:
        """Retorna um cliente assíncrono do Service Bus."""
        return AsyncServiceBusClient.from_connection_string(self.connection_string)
