"""Exemplo de uso do padrão Command Messages."""

import asyncio
from typing import Dict, Any

from patterns.command_messages import (
    CommandHandler,
    CommandInvoker,
    CommandBus,
    command
)
from shared.models import AgentConfig


# Exemplo 1: Comandos simples com funções
async def process_order_command(params: Dict[str, Any]) -> Dict[str, Any]:
    """Processa um pedido."""
    order_id = params.get("order_id")
    print(f"  → Processando pedido {order_id}...")
    await asyncio.sleep(1)  # Simula processamento
    return {
        "order_id": order_id,
        "status": "processed",
        "confirmation": f"ORD-CONF-{order_id}"
    }


async def send_email_command(params: Dict[str, Any]) -> Dict[str, Any]:
    """Envia um email."""
    to = params.get("to")
    subject = params.get("subject")
    print(f"  → Enviando email para {to}: '{subject}'...")
    await asyncio.sleep(0.5)  # Simula envio
    return {
        "sent": True,
        "to": to,
        "message_id": "MSG-12345"
    }


def calculate_total_command(params: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula total de itens."""
    items = params.get("items", [])
    total = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
    print(f"  → Calculando total de {len(items)} itens...")
    return {
        "total": total,
        "items_count": len(items),
        "currency": "BRL"
    }


# Exemplo 2: Usando decorador
@command("generate_report")
async def generate_report_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """Gera um relatório."""
    report_type = params.get("type", "summary")
    print(f"  → Gerando relatório tipo '{report_type}'...")
    await asyncio.sleep(2)
    return {
        "report_id": "RPT-001",
        "type": report_type,
        "url": f"/reports/RPT-001.pdf"
    }


async def main():
    """Exemplo principal de uso do Command Messages."""
    
    print("=" * 60)
    print("Exemplo: Command Messages Pattern")
    print("=" * 60)
    
    # ==========================================
    # Parte 1: Command Handler Básico
    # ==========================================
    
    print("\n[Parte 1] Command Handler Básico\n")
    print("-" * 60)
    
    # 1. Criar handler com comandos registrados
    handler_config = AgentConfig(name="OrderCommandHandler")
    handler = CommandHandler(
        handler_config,
        command_handlers={
            "process_order": process_order_command,
            "send_email": send_email_command,
            "calculate_total": calculate_total_command
        }
    )
    
    print("✓ Handler criado com 3 comandos registrados\n")
    
    # 2. Criar invoker
    invoker = CommandInvoker("APIClient")
    
    # 3. Invocar comandos
    print("Invocando comando 'process_order':")
    response1 = await invoker.invoke_command(
        handler,
        "process_order",
        {"order_id": "ORD-1001"}
    )
    print(f"  ✓ Resposta: {response1.result}\n")
    
    print("Invocando comando 'calculate_total':")
    response2 = await invoker.invoke_command(
        handler,
        "calculate_total",
        {
            "items": [
                {"name": "Item A", "price": 50.0, "quantity": 2},
                {"name": "Item B", "price": 30.0, "quantity": 3}
            ]
        }
    )
    print(f"  ✓ Resposta: {response2.result}\n")
    
    print("Invocando comando 'send_email':")
    response3 = await invoker.invoke_command(
        handler,
        "send_email",
        {
            "to": "customer@example.com",
            "subject": "Pedido confirmado",
            "body": "Seu pedido foi confirmado!"
        }
    )
    print(f"  ✓ Resposta: {response3.result}\n")
    
    # ==========================================
    # Parte 2: Command Bus
    # ==========================================
    
    print("\n[Parte 2] Command Bus (Desacoplado)\n")
    print("-" * 60)
    
    # 1. Criar command bus
    bus = CommandBus()
    
    # 2. Criar múltiplos handlers especializados
    order_handler_config = AgentConfig(name="OrderHandler")
    order_handler = CommandHandler(
        order_handler_config,
        {"process_order": process_order_command}
    )
    
    email_handler_config = AgentConfig(name="EmailHandler")
    email_handler = CommandHandler(
        email_handler_config,
        {"send_email": send_email_command}
    )
    
    report_handler_config = AgentConfig(name="ReportHandler")
    report_handler = CommandHandler(
        report_handler_config,
        {"generate_report": generate_report_handler}
    )
    
    # 3. Registrar handlers no bus
    bus.register_handler("process_order", order_handler)
    bus.register_handler("send_email", email_handler)
    bus.register_handler("generate_report", report_handler)
    
    print(f"✓ Command Bus configurado com comandos: {bus.list_commands()}\n")
    
    # 4. Despachar comandos através do bus
    print("Despachando comando através do bus:")
    response4 = await bus.dispatch(
        "generate_report",
        {"type": "monthly", "month": "January"}
    )
    print(f"  ✓ Resposta: {response4.result}\n")
    
    # ==========================================
    # Parte 3: Comandos Assíncronos
    # ==========================================
    
    print("\n[Parte 3] Comandos Assíncronos (Fire-and-Forget)\n")
    print("-" * 60)
    
    # Invocar sem esperar resposta
    command_id = await invoker.invoke_async(
        handler,
        "send_email",
        {
            "to": "admin@example.com",
            "subject": "Notificação do sistema",
            "body": "Evento importante ocorreu"
        }
    )
    
    print(f"✓ Comando disparado assincronamente (ID: {command_id})")
    print("  (Não aguardamos resposta)\n")
    
    # ==========================================
    # Parte 4: Tratamento de Erros
    # ==========================================
    
    print("\n[Parte 4] Tratamento de Erros\n")
    print("-" * 60)
    
    # Comando inexistente
    print("Tentando comando inexistente:")
    try:
        await bus.dispatch("unknown_command", {})
    except ValueError as e:
        print(f"  ✗ Erro capturado: {str(e)}\n")
    
    # Timeout
    print("Testando timeout:")
    try:
        async def slow_command(params):
            await asyncio.sleep(10)  # Muito lento
            return {"done": True}
        
        slow_handler_config = AgentConfig(name="SlowHandler")
        slow_handler = CommandHandler(
            slow_handler_config,
            {"slow_task": slow_command}
        )
        
        await invoker.invoke_command(
            slow_handler,
            "slow_task",
            {},
            timeout=2  # Timeout de 2 segundos
        )
    except asyncio.TimeoutError:
        print(f"  ✗ Timeout excedido (esperado)\n")
    
    # ==========================================
    # Resumo
    # ==========================================
    
    print("\n" + "=" * 60)
    print("Resumo do Padrão Command Messages")
    print("=" * 60)
    print("""
Vantagens:
  ✓ Desacoplamento entre invocador e executor
  ✓ Facilita logging e auditoria
  ✓ Permite retry e timeout
  ✓ Suporta comandos síncronos e assíncronos
  ✓ Command Bus permite roteamento flexível

Casos de Uso:
  • APIs REST que executam operações complexas
  • Sistemas de workflow e orquestração
  • Microserviços com comunicação assíncrona
  • Task queues e job processing
    """)


if __name__ == "__main__":
    asyncio.run(main())
