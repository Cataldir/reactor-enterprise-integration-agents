"""
Exemplo Completo: Combinando Múltiplos Padrões

Este exemplo demonstra como combinar diferentes padrões de integração
em um sistema completo de processamento de pedidos (e-commerce).

Padrões usados:
1. Pipes and Filters - Para validação e transformação de pedidos
2. Command Messages - Para executar ações específicas
3. Message Queue - Para processar pedidos assincronamente (simulado)
4. Pub/Sub - Para notificar múltiplos sistemas (simulado)
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any

from patterns.pipes_and_filters import Pipeline, ValidationFilter, TransformFilter, FilterAgent
from patterns.command_messages import CommandHandler, CommandBus
from shared.models import AgentConfig, AgentMessage, MessageType, CommandMessage


# =============================================================================
# 1. PIPES AND FILTERS - Pipeline de Validação e Transformação
# =============================================================================

class OrderValidationFilter(ValidationFilter):
    """Valida campos obrigatórios do pedido."""
    
    def __init__(self, config: AgentConfig):
        super().__init__(
            config,
            required_fields=["order_id", "customer_id", "items", "total"]
        )


class PriceCalculationFilter(FilterAgent):
    """Calcula o preço total com base nos itens."""
    
    async def filter(self, message: AgentMessage):
        """Recalcula o total do pedido."""
        modified = message.model_copy()
        items = modified.payload.get("items", [])
        
        total = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
        modified.payload["calculated_total"] = total
        
        # Valida se o total informado está correto
        informed_total = modified.payload.get("total", 0)
        if abs(total - informed_total) > 0.01:
            self.logger.warning(
                f"Total informado ({informed_total}) difere do calculado ({total})"
            )
            modified.payload["total"] = total
        
        self.logger.info(f"Total calculado: R$ {total:.2f}")
        return modified


class DiscountFilter(FilterAgent):
    """Aplica descontos baseado em regras."""
    
    async def filter(self, message: AgentMessage):
        """Aplica desconto se aplicável."""
        modified = message.model_copy()
        total = modified.payload.get("total", 0)
        
        # Regra: desconto de 10% para pedidos acima de R$ 500
        if total > 500:
            discount = total * 0.10
            modified.payload["discount"] = discount
            modified.payload["total_with_discount"] = total - discount
            self.logger.info(f"Desconto aplicado: R$ {discount:.2f}")
        else:
            modified.payload["discount"] = 0
            modified.payload["total_with_discount"] = total
        
        return modified


class EnrichmentOrderFilter(FilterAgent):
    """Enriquece pedido com informações adicionais."""
    
    async def filter(self, message: AgentMessage):
        """Adiciona metadata ao pedido."""
        modified = message.model_copy()
        modified.payload["processed_at"] = datetime.utcnow().isoformat()
        modified.payload["status"] = "validated"
        modified.payload["processor_version"] = "1.0"
        
        return modified


# =============================================================================
# 2. COMMAND MESSAGES - Handlers de Ações
# =============================================================================

async def process_payment_command(params: Dict[str, Any]) -> Dict[str, Any]:
    """Processa pagamento do pedido."""
    order_id = params.get("order_id")
    amount = params.get("amount")
    
    print(f"  💳 Processando pagamento de R$ {amount:.2f} para pedido {order_id}")
    await asyncio.sleep(1)  # Simula processamento
    
    # Simula aprovação
    return {
        "payment_id": f"PAY-{uuid.uuid4().hex[:8].upper()}",
        "order_id": order_id,
        "amount": amount,
        "status": "approved",
        "approved_at": datetime.utcnow().isoformat()
    }


async def reserve_inventory_command(params: Dict[str, Any]) -> Dict[str, Any]:
    """Reserva itens no estoque."""
    order_id = params.get("order_id")
    items = params.get("items", [])
    
    print(f"  📦 Reservando {len(items)} itens no estoque para pedido {order_id}")
    await asyncio.sleep(0.5)
    
    return {
        "reservation_id": f"RES-{uuid.uuid4().hex[:8].upper()}",
        "order_id": order_id,
        "items": items,
        "status": "reserved"
    }


async def send_confirmation_email_command(params: Dict[str, Any]) -> Dict[str, Any]:
    """Envia email de confirmação."""
    order_id = params.get("order_id")
    customer_email = params.get("customer_email")
    
    print(f"  📧 Enviando email de confirmação para {customer_email}")
    await asyncio.sleep(0.3)
    
    return {
        "email_id": f"EMAIL-{uuid.uuid4().hex[:8].upper()}",
        "order_id": order_id,
        "sent_to": customer_email,
        "sent_at": datetime.utcnow().isoformat()
    }


async def create_shipment_command(params: Dict[str, Any]) -> Dict[str, Any]:
    """Cria envio para o pedido."""
    order_id = params.get("order_id")
    
    print(f"  🚚 Criando envio para pedido {order_id}")
    await asyncio.sleep(0.7)
    
    return {
        "shipment_id": f"SHIP-{uuid.uuid4().hex[:8].upper()}",
        "order_id": order_id,
        "status": "pending_dispatch",
        "estimated_delivery": "3-5 dias úteis"
    }


# =============================================================================
# 3. ORQUESTRAÇÃO - Combinando Tudo
# =============================================================================

class OrderProcessingOrchestrator:
    """Orquestra o processamento completo de pedidos."""
    
    def __init__(self):
        # Pipeline de validação e transformação
        self.pipeline = self._create_pipeline()
        
        # Command Bus para ações
        self.command_bus = self._create_command_bus()
    
    def _create_pipeline(self) -> Pipeline:
        """Cria o pipeline de processamento."""
        filters = [
            OrderValidationFilter(AgentConfig(name="OrderValidation")),
            PriceCalculationFilter(AgentConfig(name="PriceCalculation")),
            DiscountFilter(AgentConfig(name="DiscountFilter")),
            EnrichmentOrderFilter(AgentConfig(name="OrderEnrichment"))
        ]
        return Pipeline(filters, name="OrderProcessingPipeline")
    
    def _create_command_bus(self) -> CommandBus:
        """Cria o command bus com todos os handlers."""
        bus = CommandBus()
        
        # Registra handlers
        payment_handler = CommandHandler(
            AgentConfig(name="PaymentHandler"),
            {"process_payment": process_payment_command}
        )
        
        inventory_handler = CommandHandler(
            AgentConfig(name="InventoryHandler"),
            {"reserve_inventory": reserve_inventory_command}
        )
        
        notification_handler = CommandHandler(
            AgentConfig(name="NotificationHandler"),
            {"send_confirmation": send_confirmation_email_command}
        )
        
        shipment_handler = CommandHandler(
            AgentConfig(name="ShipmentHandler"),
            {"create_shipment": create_shipment_command}
        )
        
        bus.register_handler("process_payment", payment_handler)
        bus.register_handler("reserve_inventory", inventory_handler)
        bus.register_handler("send_confirmation", notification_handler)
        bus.register_handler("create_shipment", shipment_handler)
        
        return bus
    
    async def process_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa um pedido completo através de todos os padrões.
        
        Fluxo:
        1. Valida e transforma através do pipeline (Pipes & Filters)
        2. Executa ações através de comandos (Command Messages)
        3. Retorna resultado consolidado
        """
        print(f"\n{'='*60}")
        print(f"Processando Pedido: {order_data['order_id']}")
        print(f"{'='*60}\n")
        
        # ETAPA 1: Pipeline de Validação e Transformação
        print("[1] Pipeline de Validação e Transformação")
        print("-" * 60)
        
        message = AgentMessage(
            id=str(uuid.uuid4()),
            type=MessageType.EVENT,
            source="OrderAPI",
            payload=order_data
        )
        
        validated_message = await self.pipeline.process(message)
        
        if not validated_message:
            print("❌ Pedido rejeitado na validação!\n")
            return {"status": "rejected", "reason": "validation_failed"}
        
        validated_order = validated_message.payload
        print(f"✓ Pedido validado: Total com desconto R$ {validated_order['total_with_discount']:.2f}\n")
        
        # ETAPA 2: Execução de Comandos
        print("[2] Execução de Comandos")
        print("-" * 60)
        
        results = {}
        
        # 2.1. Reservar inventário
        print("Comando: reserve_inventory")
        inventory_response = await self.command_bus.dispatch(
            "reserve_inventory",
            {
                "order_id": validated_order["order_id"],
                "items": validated_order["items"]
            }
        )
        results["inventory"] = inventory_response.result
        
        # 2.2. Processar pagamento
        print("Comando: process_payment")
        payment_response = await self.command_bus.dispatch(
            "process_payment",
            {
                "order_id": validated_order["order_id"],
                "amount": validated_order["total_with_discount"]
            }
        )
        results["payment"] = payment_response.result
        
        # 2.3. Criar envio
        print("Comando: create_shipment")
        shipment_response = await self.command_bus.dispatch(
            "create_shipment",
            {"order_id": validated_order["order_id"]}
        )
        results["shipment"] = shipment_response.result
        
        # 2.4. Enviar confirmação
        print("Comando: send_confirmation")
        email_response = await self.command_bus.dispatch(
            "send_confirmation",
            {
                "order_id": validated_order["order_id"],
                "customer_email": f"customer{validated_order['customer_id']}@example.com"
            }
        )
        results["notification"] = email_response.result
        
        # ETAPA 3: Resultado Consolidado
        print("\n" + "=" * 60)
        print("✅ Pedido Processado com Sucesso!")
        print("=" * 60)
        
        return {
            "status": "completed",
            "order": validated_order,
            "results": results
        }


async def main():
    """Exemplo principal."""
    
    print("=" * 60)
    print("Exemplo Completo: Sistema de Processamento de Pedidos")
    print("=" * 60)
    print("\nCombinando:")
    print("  • Pipes and Filters (validação e transformação)")
    print("  • Command Messages (ações específicas)")
    print("  • Orquestração assíncrona")
    print()
    
    # Criar orquestrador
    orchestrator = OrderProcessingOrchestrator()
    
    # Processar múltiplos pedidos
    orders = [
        {
            "order_id": "ORD-1001",
            "customer_id": "CUST-001",
            "items": [
                {"name": "Produto A", "price": 150.00, "quantity": 2},
                {"name": "Produto B", "price": 80.00, "quantity": 1}
            ],
            "total": 380.00
        },
        {
            "order_id": "ORD-1002",
            "customer_id": "CUST-002",
            "items": [
                {"name": "Produto Premium", "price": 600.00, "quantity": 1}
            ],
            "total": 600.00  # Este terá desconto!
        },
        {
            "order_id": "ORD-1003",
            "customer_id": "CUST-003",
            "items": [
                {"name": "Item C", "price": 50.00, "quantity": 3}
            ],
            "total": 150.00
        }
    ]
    
    # Processar cada pedido
    for order in orders:
        result = await orchestrator.process_order(order)
        
        if result["status"] == "completed":
            print(f"\n📊 Resumo do Pedido {result['order']['order_id']}:")
            print(f"   • Pagamento: {result['results']['payment']['payment_id']}")
            print(f"   • Reserva: {result['results']['inventory']['reservation_id']}")
            print(f"   • Envio: {result['results']['shipment']['shipment_id']}")
            print(f"   • Email: {result['results']['notification']['email_id']}")
        
        print("\n" + "=" * 60 + "\n")
        
        # Pequena pausa entre pedidos
        await asyncio.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("Todos os Pedidos Processados!")
    print("=" * 60)
    print("\n✨ Este exemplo demonstra como os padrões trabalham juntos:")
    print("   1. Pipeline valida e transforma dados")
    print("   2. Commands executam ações específicas")
    print("   3. Orquestrador coordena todo o fluxo")
    print("\n💡 Em produção, isso poderia incluir:")
    print("   • Message Queue para processar pedidos assincronamente")
    print("   • Pub/Sub para notificar outros sistemas")
    print("   • Retry logic e circuit breakers")
    print("   • Distributed tracing e monitoring")
    print()


if __name__ == "__main__":
    asyncio.run(main())
