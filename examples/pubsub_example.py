"""Exemplo de uso do padrão Publish-Subscribe."""

import asyncio
import uuid
from datetime import datetime

from patterns.pubsub import PublisherAgent, SubscriberAgent, PubSubCoordinator
from shared.models import AgentConfig, EventMessage


async def analytics_handler(message):
    """Handler para agente de analytics."""
    print(f"  [Analytics] Evento recebido: {message.event_name}")
    print(f"              Dados: {message.event_data}")
    # Aqui você processaria dados para analytics
    await asyncio.sleep(0.5)


async def notification_handler(message):
    """Handler para agente de notificações."""
    print(f"  [Notification] Enviando notificação: {message.event_name}")
    # Aqui você enviaria notificações (email, SMS, etc)
    await asyncio.sleep(0.3)


async def audit_handler(message):
    """Handler para agente de auditoria."""
    print(f"  [Audit] Registrando evento: {message.event_name} às {message.timestamp}")
    # Aqui você salvaria logs de auditoria
    await asyncio.sleep(0.2)


async def main():
    """Exemplo principal de uso do Pub/Sub."""
    
    print("=" * 60)
    print("Exemplo: Publish-Subscribe Pattern com Azure Service Bus")
    print("=" * 60)
    
    # 1. Criar publicador
    print("\n[1] Configurando publicador...")
    
    publisher_config = AgentConfig(
        name="EventPublisher",
        description="Publica eventos do sistema"
    )
    publisher = PublisherAgent(publisher_config)
    
    print(f"   ✓ Publicador '{publisher.name}' criado")
    
    # 2. Criar assinantes
    print("\n[2] Configurando assinantes...")
    
    analytics_config = AgentConfig(name="AnalyticsAgent")
    analytics_subscriber = SubscriberAgent(
        analytics_config,
        message_handler=analytics_handler
    )
    
    notification_config = AgentConfig(name="NotificationAgent")
    notification_subscriber = SubscriberAgent(
        notification_config,
        message_handler=notification_handler
    )
    
    audit_config = AgentConfig(name="AuditAgent")
    audit_subscriber = SubscriberAgent(
        audit_config,
        message_handler=audit_handler
    )
    
    print(f"   ✓ 3 assinantes criados")
    
    # 3. Configurar coordenador
    print("\n[3] Configurando coordenador Pub/Sub...")
    
    coordinator = PubSubCoordinator()
    coordinator.add_publisher(publisher)
    coordinator.add_subscriber(analytics_subscriber)
    coordinator.add_subscriber(notification_subscriber)
    coordinator.add_subscriber(audit_subscriber)
    
    print(f"   ✓ Coordenador configurado com 1 publicador e 3 assinantes")
    
    # 4. Iniciar todos os agentes
    print("\n[4] Iniciando agentes...")
    await coordinator.start_all()
    print(f"   ✓ Todos os agentes iniciados")
    
    # 5. Publicar eventos
    print("\n[5] Publicando eventos...\n")
    
    events = [
        {
            "name": "user_registered",
            "data": {
                "user_id": "USR-001",
                "email": "novo@example.com",
                "timestamp": datetime.utcnow().isoformat()
            }
        },
        {
            "name": "order_placed",
            "data": {
                "order_id": "ORD-1001",
                "user_id": "USR-001",
                "amount": 250.00,
                "timestamp": datetime.utcnow().isoformat()
            }
        },
        {
            "name": "payment_processed",
            "data": {
                "payment_id": "PAY-5001",
                "order_id": "ORD-1001",
                "status": "approved",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    ]
    
    for i, event in enumerate(events, 1):
        print(f"Evento {i}: {event['name']}")
        await publisher.publish_event(event['name'], event['data'])
        print(f"   ✓ Publicado\n")
        await asyncio.sleep(1)
    
    # 6. Iniciar escuta (em background)
    print("\n[6] Iniciando escuta de eventos...")
    print("    (Os assinantes processarão as mensagens)")
    print("    (Pressione Ctrl+C para parar)\n")
    
    try:
        # Cria task para escuta em background
        listen_task = asyncio.create_task(coordinator.start_listening_all())
        
        # Aguarda um pouco para processar
        await asyncio.sleep(10)
        
        # Publica mais alguns eventos
        print("\n[7] Publicando eventos adicionais...\n")
        
        await publisher.publish_event(
            "system_alert",
            {"level": "warning", "message": "High CPU usage detected"}
        )
        
        await asyncio.sleep(5)
        
    except KeyboardInterrupt:
        print("\n\n[8] Parando todos os agentes...")
        listen_task.cancel()
        await coordinator.stop_all()
        print("    ✓ Todos os agentes parados!\n")
    
    print("=" * 60)
    print("Exemplo concluído!")
    print("=" * 60)


if __name__ == "__main__":
    # Nota: Este exemplo requer:
    # - Azure Service Bus configurado
    # - Variável AZURE_SERVICEBUS_CONNECTION_STRING no .env
    # - Tópico e assinaturas criados no Service Bus
    
    print("\n⚠️  Certifique-se de configurar o .env com suas credenciais Azure!")
    print("⚠️  Você também precisa criar tópico e assinaturas no Azure Portal\n")
    
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        print("\nVerifique se:")
        print("  1. O arquivo .env está configurado")
        print("  2. A connection string está correta")
        print("  3. O tópico e assinaturas existem no Azure Service Bus")
