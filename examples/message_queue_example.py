"""Exemplo de uso do padrão Message Queue."""

import asyncio
from datetime import datetime
import uuid

from patterns.message_queue import MessageQueueAgent, MessageProducer
from shared.models import AgentConfig, AgentMessage, MessageType


class CustomProcessingAgent(MessageQueueAgent):
    """Exemplo de agente customizado que processa mensagens."""
    
    async def process_message(self, message: AgentMessage) -> None:
        """
        Processa mensagens de forma customizada.
        
        Exemplo: processa dados de pedidos.
        """
        self.logger.info(f"[CustomAgent] Processando pedido: {message.payload.get('order_id')}")
        
        # Simula processamento
        await asyncio.sleep(1)
        
        # Aqui você pode:
        # - Validar dados
        # - Salvar em banco de dados
        # - Chamar APIs externas
        # - Enviar notificações
        
        self.logger.info(f"[CustomAgent] Pedido {message.payload.get('order_id')} processado!")


async def main():
    """Exemplo principal de uso do Message Queue."""
    
    print("=" * 60)
    print("Exemplo: Message Queue Pattern com Azure Service Bus")
    print("=" * 60)
    
    # 1. Criar configuração do agente
    config = AgentConfig(
        name="OrderProcessor",
        description="Processa pedidos da fila",
        max_retries=3,
        timeout_seconds=30
    )
    
    # 2. Criar agente consumidor
    agent = CustomProcessingAgent(config)
    
    # 3. Enviar algumas mensagens de teste
    print("\n[1] Enviando mensagens para a fila...")
    
    async with MessageProducer() as producer:
        for i in range(5):
            message = AgentMessage(
                id=str(uuid.uuid4()),
                type=MessageType.COMMAND,
                source="OrderAPI",
                payload={
                    "order_id": f"ORD-{1000 + i}",
                    "customer": f"Customer {i+1}",
                    "amount": 100.0 * (i + 1),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            await producer.send(message)
            print(f"   ✓ Mensagem {i+1}/5 enviada: {message.payload['order_id']}")
    
    print("\n[2] Iniciando processamento da fila...")
    print("    (Pressione Ctrl+C para parar)\n")
    
    # 4. Iniciar processamento
    try:
        await agent.start()
        await agent.start_processing()
    except KeyboardInterrupt:
        print("\n\n[3] Parando agente...")
        await agent.stop()
        print("    ✓ Agente parado com sucesso!\n")


if __name__ == "__main__":
    # Nota: Este exemplo requer:
    # - Azure Service Bus configurado
    # - Variável AZURE_SERVICEBUS_CONNECTION_STRING no .env
    # - Fila criada no Service Bus
    
    print("\n⚠️  Certifique-se de configurar o .env com suas credenciais Azure!\n")
    
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        print("\nVerifique se:")
        print("  1. O arquivo .env está configurado")
        print("  2. A connection string está correta")
        print("  3. A fila existe no Azure Service Bus")
