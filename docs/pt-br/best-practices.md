# Melhores Práticas

Este guia apresenta as melhores práticas para usar os padrões de integração empresarial com agentes de AI.

## Práticas Gerais

### 1. Configuração e Gerenciamento de Segredos

**❌ Nunca faça isso:**
```python
# Hardcoded credentials - NUNCA!
connection_string = "Endpoint=sb://..."
api_key = "my-secret-key"
```

**✅ Faça isso:**
```python
# Use variáveis de ambiente
from dotenv import load_dotenv
import os

load_dotenv()
connection_string = os.getenv("AZURE_SERVICEBUS_CONNECTION_STRING")

# Ou use Azure Key Vault para produção
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://myvault.vault.azure.net/", credential=credential)
secret = client.get_secret("ServiceBusConnectionString")
```

### 2. Logging Estruturado

**✅ Use logging apropriado:**
```python
import logging

# Configure no início da aplicação
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# No código
self.logger.info("Processando mensagem", extra={
    "message_id": message.id,
    "source": message.source,
    "priority": message.priority
})
```

### 3. Error Handling

**✅ Sempre capture e trate erros:**
```python
async def process_message(self, message: AgentMessage):
    try:
        result = await self._process_internal(message)
        return result
    except ValidationError as e:
        self.logger.error(f"Validação falhou: {e}")
        # Enviar para dead-letter queue
        raise
    except Exception as e:
        self.logger.error(f"Erro inesperado: {e}", exc_info=True)
        # Implementar retry logic
        await self._retry(message)
```

### 4. Resource Management

**✅ Use context managers:**
```python
# Para clients Azure
async with MessageProducer() as producer:
    await producer.send(message)

# Para agentes
async with agent:
    await agent.process_message(message)
```

## Práticas por Padrão

### Message Queue

#### 1. Idempotência

**Problema:** Mensagens podem ser processadas mais de uma vez.

**✅ Solução: Implementar idempotência**
```python
class IdempotentAgent(MessageQueueAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._processed_ids = set()  # Em produção, use Redis/DB
    
    async def process_message(self, message: AgentMessage):
        if message.id in self._processed_ids:
            self.logger.info(f"Mensagem {message.id} já processada, pulando")
            return None
        
        result = await self._do_processing(message)
        self._processed_ids.add(message.id)
        return result
```

#### 2. Dead Letter Queue

**✅ Configure DLQ para mensagens problemáticas:**
```python
async def _process_service_bus_message(self, msg):
    try:
        # ... processamento
        await self._receiver.complete_message(msg)
    except ValidationError as e:
        # Mensagem inválida -> dead letter
        await self._receiver.dead_letter_message(
            msg,
            reason="ValidationError",
            error_description=str(e)
        )
    except TemporaryError as e:
        # Erro temporário -> reprocessar
        await self._receiver.abandon_message(msg)
```

#### 3. Batch Processing

**✅ Processe em lotes para melhor performance:**
```python
# Configure lote apropriado
agent = MessageQueueAgent(
    config,
    max_concurrent_calls=10  # Ajuste baseado em recursos
)

# Processe múltiplas mensagens em paralelo
async def process_batch(self, messages):
    tasks = [self.process_message(msg) for msg in messages]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### Pipes and Filters

#### 1. Separação de Responsabilidades

**✅ Cada filtro deve ter uma única responsabilidade:**
```python
# ❌ Filtro fazendo múltiplas coisas
class ComplexFilter(FilterAgent):
    async def filter(self, message):
        # Valida
        if not self._validate(message):
            return None
        # Transforma
        message = self._transform(message)
        # Enriquece
        message = self._enrich(message)
        return message

# ✅ Filtros especializados
validation_filter = ValidationFilter(config1)
transform_filter = TransformFilter(config2)
enrichment_filter = EnrichmentFilter(config3)

pipeline = Pipeline([
    validation_filter,
    transform_filter,
    enrichment_filter
])
```

#### 2. Pipeline Imutável

**✅ Não modifique mensagens originais:**
```python
async def filter(self, message: AgentMessage):
    # ❌ Modifica o original
    # message.payload["new_field"] = "value"
    # return message
    
    # ✅ Cria cópia
    modified = message.model_copy()
    modified.payload["new_field"] = "value"
    return modified
```

#### 3. Pipeline Testing

**✅ Teste cada filtro individualmente:**
```python
@pytest.mark.asyncio
async def test_validation_filter():
    config = AgentConfig(name="TestFilter")
    filter = ValidationFilter(config, required_fields=["email"])
    
    # Teste caso válido
    valid_msg = AgentMessage(payload={"email": "test@example.com"})
    result = await filter.process_message(valid_msg)
    assert result is not None
    
    # Teste caso inválido
    invalid_msg = AgentMessage(payload={})
    result = await filter.process_message(invalid_msg)
    assert result is None
```

### Publish-Subscribe

#### 1. Naming Convention

**✅ Use nomes descritivos para tópicos e eventos:**
```python
# ❌ Nomes genéricos
await publisher.publish_event("event1", data)

# ✅ Nomes descritivos
await publisher.publish_event("user.registered", user_data)
await publisher.publish_event("order.placed", order_data)
await publisher.publish_event("payment.processed", payment_data)
```

#### 2. Event Schema

**✅ Use schemas consistentes:**
```python
from pydantic import BaseModel

class UserRegisteredEvent(BaseModel):
    event_type: str = "user.registered"
    user_id: str
    email: str
    timestamp: datetime
    metadata: dict = {}

# Publique com schema
event = UserRegisteredEvent(user_id="123", email="user@example.com")
await publisher.publish_event(
    event.event_type,
    event.model_dump()
)
```

#### 3. Subscriber Isolation

**✅ Assinantes devem ser independentes:**
```python
# Cada assinante deve ter sua própria assinatura
analytics_subscriber = SubscriberAgent(
    config1,
    subscription_name="analytics-subscription"  # Específico
)

notification_subscriber = SubscriberAgent(
    config2,
    subscription_name="notification-subscription"  # Específico
)

# Erros em um não afetam o outro
```

### Command Messages

#### 1. Command Naming

**✅ Use verbos no imperativo:**
```python
# ❌ Nomes ambíguos
"data", "process", "handle"

# ✅ Nomes claros
"process_order", "send_email", "generate_report"
"create_user", "update_profile", "delete_account"
```

#### 2. Response Handling

**✅ Sempre retorne respostas estruturadas:**
```python
async def execute_command(self, command: CommandMessage):
    try:
        result = await self._do_work(command.parameters)
        return ResponseMessage(
            id=str(uuid.uuid4()),
            source=self.name,
            correlation_id=command.id,
            status="success",
            result=result,
            payload={"result": result}
        )
    except Exception as e:
        return ResponseMessage(
            id=str(uuid.uuid4()),
            source=self.name,
            correlation_id=command.id,
            status="error",
            error=str(e),
            payload={"error": str(e)}
        )
```

#### 3. Timeout Configuration

**✅ Configure timeouts apropriados:**
```python
# Para operações rápidas
response = await invoker.invoke_command(
    handler, "quick_operation", params, timeout=5
)

# Para operações lentas
response = await invoker.invoke_command(
    handler, "slow_operation", params, timeout=300
)

# Para operações que não devem ter timeout
response = await invoker.invoke_command(
    handler, "long_running", params, timeout=None
)
```

## Performance

### 1. Processamento Paralelo

**✅ Use asyncio.gather para paralelismo:**
```python
# ❌ Sequencial
results = []
for message in messages:
    result = await process(message)
    results.append(result)

# ✅ Paralelo
tasks = [process(message) for message in messages]
results = await asyncio.gather(*tasks)
```

### 2. Connection Pooling

**✅ Reutilize conexões:**
```python
class MyService:
    def __init__(self):
        self._client = None
    
    async def get_client(self):
        if not self._client:
            self._client = get_async_service_bus_client()
        return self._client
    
    async def close(self):
        if self._client:
            await self._client.close()
```

### 3. Batch Operations

**✅ Processe em lotes quando possível:**
```python
# Para Service Bus
async def send_batch(self, messages: List[AgentMessage]):
    batch = await self._sender.create_message_batch()
    
    for message in messages:
        try:
            batch.add_message(ServiceBusMessage(message.model_dump_json()))
        except ValueError:
            # Lote cheio, envia e cria novo
            await self._sender.send_messages(batch)
            batch = await self._sender.create_message_batch()
            batch.add_message(ServiceBusMessage(message.model_dump_json()))
    
    if len(batch) > 0:
        await self._sender.send_messages(batch)
```

## Monitoramento e Observabilidade

### 1. Métricas

**✅ Colete métricas importantes:**
```python
import time
from dataclasses import dataclass

@dataclass
class Metrics:
    messages_processed: int = 0
    messages_failed: int = 0
    total_processing_time: float = 0.0
    
    @property
    def average_processing_time(self):
        if self.messages_processed == 0:
            return 0
        return self.total_processing_time / self.messages_processed

class MonitoredAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = Metrics()
    
    async def process_message(self, message: AgentMessage):
        start = time.time()
        try:
            result = await self._process(message)
            self.metrics.messages_processed += 1
            return result
        except Exception as e:
            self.metrics.messages_failed += 1
            raise
        finally:
            elapsed = time.time() - start
            self.metrics.total_processing_time += elapsed
```

### 2. Health Checks

**✅ Implemente health checks:**
```python
class HealthCheckAgent(BaseAgent):
    async def health_check(self) -> dict:
        return {
            "status": "healthy" if self.is_running() else "unhealthy",
            "name": self.name,
            "uptime": self._uptime(),
            "metrics": {
                "processed": self.metrics.messages_processed,
                "failed": self.metrics.messages_failed
            }
        }
```

### 3. Distributed Tracing

**✅ Use correlation IDs:**
```python
def create_message(self, payload, correlation_id=None):
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
    
    message = AgentMessage(
        id=str(uuid.uuid4()),
        source=self.name,
        payload=payload,
        correlation_id=correlation_id,
        metadata={
            "trace_id": correlation_id,
            "span_id": str(uuid.uuid4())
        }
    )
    return message
```

## Testes

### 1. Unit Tests

**✅ Teste lógica de negócio isoladamente:**
```python
@pytest.mark.asyncio
async def test_process_message():
    config = AgentConfig(name="TestAgent")
    agent = MyAgent(config)
    
    message = AgentMessage(
        id="test-id",
        source="test",
        payload={"key": "value"}
    )
    
    result = await agent.process_message(message)
    
    assert result is not None
    assert result.payload["processed"] is True
```

### 2. Integration Tests

**✅ Use mocks para Azure services:**
```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
@patch('shared.azure_clients.get_async_service_bus_client')
async def test_with_azure_mock(mock_client):
    mock_sender = AsyncMock()
    mock_client.return_value.get_queue_sender.return_value = mock_sender
    
    agent = MessageQueueAgent(config)
    await agent.start()
    await agent.send_message(message)
    
    mock_sender.send_messages.assert_called_once()
```

### 3. End-to-End Tests

**✅ Use Azure Service Bus Emulator ou namespace de teste:**
```python
@pytest.fixture
async def test_namespace():
    """Usa namespace de teste do Azure."""
    connection_string = os.getenv("TEST_SERVICEBUS_CONNECTION_STRING")
    yield connection_string

@pytest.mark.e2e
async def test_full_flow(test_namespace):
    # Teste completo com Azure Service Bus real
    pass
```

## Deployment

### 1. Containerização

**✅ Use Docker:**
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "patterns.message_queue"]
```

### 2. Configuration Management

**✅ Use diferentes configs por ambiente:**
```python
import os

ENV = os.getenv("ENVIRONMENT", "development")

if ENV == "production":
    LOG_LEVEL = "INFO"
    MAX_RETRIES = 5
elif ENV == "staging":
    LOG_LEVEL = "DEBUG"
    MAX_RETRIES = 3
else:
    LOG_LEVEL = "DEBUG"
    MAX_RETRIES = 1
```

### 3. Graceful Shutdown

**✅ Implemente shutdown gracioso:**
```python
import signal

class GracefulAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame):
        self.logger.info("Recebido sinal de shutdown, parando...")
        asyncio.create_task(self.stop())
```

## Resumo

As melhores práticas essenciais:

1. ✅ Use variáveis de ambiente para configuração
2. ✅ Implemente logging estruturado
3. ✅ Sempre trate erros apropriadamente
4. ✅ Use context managers para recursos
5. ✅ Implemente idempotência para Message Queue
6. ✅ Mantenha filtros com responsabilidade única
7. ✅ Use eventos e comandos bem nomeados
8. ✅ Configure timeouts apropriados
9. ✅ Colete métricas e implemente health checks
10. ✅ Teste em todos os níveis (unit, integration, e2e)

Seguindo estas práticas, você terá um sistema robusto, escalável e de fácil manutenção.
