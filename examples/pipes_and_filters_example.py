"""Exemplo de uso do padrão Pipes and Filters."""

import asyncio
import uuid
from datetime import datetime

from patterns.pipes_and_filters import (
    Pipeline,
    ValidationFilter,
    TransformFilter,
    EnrichmentFilter,
    FilterAgent
)
from shared.models import AgentConfig, AgentMessage, MessageType


class DataNormalizationFilter(FilterAgent):
    """Filtro customizado que normaliza dados."""
    
    async def filter(self, message: AgentMessage) -> AgentMessage:
        """Normaliza campos de texto para maiúsculas."""
        normalized_message = message.model_copy()
        
        if "name" in normalized_message.payload:
            normalized_message.payload["name"] = (
                normalized_message.payload["name"].upper()
            )
        
        self.logger.info(f"Dados normalizados para mensagem {message.id}")
        return normalized_message


async def main():
    """Exemplo principal de uso do Pipes and Filters."""
    
    print("=" * 60)
    print("Exemplo: Pipes and Filters Pattern")
    print("=" * 60)
    
    # 1. Criar filtros do pipeline
    print("\n[1] Criando pipeline com 4 filtros...")
    
    validation_config = AgentConfig(name="ValidationFilter")
    validation_filter = ValidationFilter(
        validation_config,
        required_fields=["name", "email", "age"]
    )
    
    transform_config = AgentConfig(name="TransformFilter")
    transform_filter = TransformFilter(
        transform_config,
        transform_func=lambda payload: {
            **payload,
            "age_category": "adult" if payload.get("age", 0) >= 18 else "minor"
        }
    )
    
    enrichment_config = AgentConfig(name="EnrichmentFilter")
    enrichment_filter = EnrichmentFilter(
        enrichment_config,
        enrichment_data={
            "processed_at": datetime.utcnow().isoformat(),
            "processor": "DataPipeline-v1"
        }
    )
    
    normalization_config = AgentConfig(name="NormalizationFilter")
    normalization_filter = DataNormalizationFilter(normalization_config)
    
    # 2. Criar pipeline
    pipeline = Pipeline([
        validation_filter,
        transform_filter,
        enrichment_filter,
        normalization_filter
    ], name="DataProcessingPipeline")
    
    print(f"   ✓ Pipeline criado: {pipeline}")
    
    # 3. Criar mensagens de teste
    print("\n[2] Processando mensagens através do pipeline...\n")
    
    test_messages = [
        AgentMessage(
            id=str(uuid.uuid4()),
            type=MessageType.EVENT,
            source="API",
            payload={
                "name": "João Silva",
                "email": "joao@example.com",
                "age": 25
            }
        ),
        AgentMessage(
            id=str(uuid.uuid4()),
            type=MessageType.EVENT,
            source="API",
            payload={
                "name": "Maria Santos",
                "email": "maria@example.com",
                "age": 17
            }
        ),
        AgentMessage(
            id=str(uuid.uuid4()),
            type=MessageType.EVENT,
            source="API",
            payload={
                "name": "Pedro Costa",
                "email": "pedro@example.com"
                # Faltando 'age' - será rejeitado
            }
        ),
    ]
    
    # 4. Processar cada mensagem
    for i, message in enumerate(test_messages, 1):
        print(f"Mensagem {i}:")
        print(f"  Input:  {message.payload}")
        
        result = await pipeline.process(message)
        
        if result:
            print(f"  Output: {result.payload}")
            print(f"  Status: ✓ Aprovada")
        else:
            print(f"  Status: ✗ Rejeitada (validação falhou)")
        
        print()
    
    # 5. Processar lote em paralelo
    print("\n[3] Processando lote de mensagens em paralelo...")
    
    batch_messages = [
        AgentMessage(
            id=str(uuid.uuid4()),
            type=MessageType.EVENT,
            source="BatchAPI",
            payload={
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "age": 20 + i
            }
        )
        for i in range(10)
    ]
    
    processed = await pipeline.process_batch(batch_messages)
    
    print(f"   ✓ {len(processed)}/{len(batch_messages)} mensagens processadas com sucesso")
    
    # 6. Demonstrar pipeline dinâmico
    print("\n[4] Adicionando filtro dinamicamente...")
    
    class AuditFilter(FilterAgent):
        """Filtro de auditoria."""
        async def filter(self, message: AgentMessage) -> AgentMessage:
            self.logger.info(f"[AUDIT] Mensagem {message.id} processada")
            return message
    
    audit_config = AgentConfig(name="AuditFilter")
    audit_filter = AuditFilter(audit_config)
    pipeline.add_filter(audit_filter)
    
    print(f"   ✓ Pipeline atualizado: {len(pipeline.filters)} filtros")
    
    print("\n" + "=" * 60)
    print("Exemplo concluído!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
