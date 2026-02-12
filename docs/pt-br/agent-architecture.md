# Arquitetura de Agentes

## Visão Geral

Este documento descreve a arquitetura dos agentes implementados neste repositório e como eles se integram com os padrões de integração empresarial.

## Hierarquia de Classes

```
BaseAgent (Abstrato)
├── ProcessingAgent
├── MessageQueueAgent
├── FilterAgent
│   ├── ValidationFilter
│   ├── TransformFilter
│   └── EnrichmentFilter
├── PublisherAgent
├── SubscriberAgent
└── CommandHandler
```

## BaseAgent

Classe abstrata que fornece funcionalidades comuns:

- **Configuração**: Gerenciamento de configuração via `AgentConfig`
- **Logging**: Sistema de logging integrado
- **Lifecycle**: Métodos `start()`, `stop()`, `is_running()`
- **Error Handling**: Tratamento centralizado de erros
- **Message Creation**: Criação padronizada de mensagens

### Interface Principal

```python
class BaseAgent(ABC):
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Processa uma mensagem (deve ser implementado)"""
        pass
    
    async def start(self) -> None:
        """Inicia o agente"""
        pass
    
    async def stop(self) -> None:
        """Para o agente"""
        pass
```

## Modelos de Dados

Todos os modelos usam **Pydantic** para validação e serialização:

### AgentMessage
Mensagem base para comunicação entre agentes.

```python
class AgentMessage(BaseModel):
    id: str
    type: MessageType
    source: str
    destination: Optional[str]
    priority: MessagePriority
    timestamp: datetime
    payload: Dict[str, Any]
    metadata: Dict[str, Any]
    correlation_id: Optional[str]
```

### Tipos Especializados

- **CommandMessage**: Para comandos
- **EventMessage**: Para eventos (Pub/Sub)
- **QueryMessage**: Para consultas
- **ResponseMessage**: Para respostas

## Componentes por Padrão

### 1. Message Queue

**Componentes:**
- `MessageQueueAgent`: Consumidor de fila
- `MessageProducer`: Produtor simplificado

**Fluxo:**
```
Producer → Azure Service Bus Queue → Consumer Agent → Processing
```

**Features:**
- Processamento em lote
- Auto-complete de mensagens
- Dead-letter queue
- Retry automático

### 2. Pipes and Filters

**Componentes:**
- `FilterAgent`: Filtro base (abstrato)
- `ValidationFilter`: Validação de campos
- `TransformFilter`: Transformação de dados
- `EnrichmentFilter`: Enriquecimento
- `Pipeline`: Orquestrador de filtros

**Fluxo:**
```
Input → Filter 1 → Filter 2 → ... → Filter N → Output
```

**Features:**
- Processamento sequencial
- Processamento em lote paralelo
- Adição dinâmica de filtros
- Pass-through configurável

### 3. Publish-Subscribe

**Componentes:**
- `PublisherAgent`: Publicador de eventos
- `SubscriberAgent`: Assinante de tópicos
- `PubSubCoordinator`: Gerenciador central

**Fluxo:**
```
Publisher → Azure Service Bus Topic → Multiple Subscribers
```

**Features:**
- Múltiplos assinantes independentes
- Filtering por propriedades
- Gerenciamento de assinaturas
- Coordenação centralizada

### 4. Command Messages

**Componentes:**
- `CommandHandler`: Executor de comandos
- `CommandInvoker`: Cliente para invocar comandos
- `CommandBus`: Roteador de comandos

**Fluxo:**
```
Invoker → Command → Handler → Response → Invoker
```

**Features:**
- Registro dinâmico de comandos
- Timeout configurável
- Fire-and-forget (async)
- Command routing via Bus

## Integração com Azure

### Azure Service Bus

Todos os padrões baseados em mensageria usam Azure Service Bus:

- **Queues**: Para Message Queue pattern
- **Topics/Subscriptions**: Para Pub/Sub pattern

### Configuração

```python
from shared.azure_clients import AzureServiceBusConfig

config = AzureServiceBusConfig(
    connection_string="...",
    queue_name="my-queue",
    topic_name="my-topic"
)

client = config.get_async_client()
```

## Padrões de Uso

### Padrão 1: Agente Simples

```python
config = AgentConfig(name="MyAgent")
agent = ProcessingAgent(
    config,
    process_func=my_processing_function
)

await agent.start()
result = await agent.process_message(message)
```

### Padrão 2: Agente Customizado

```python
class MyCustomAgent(BaseAgent):
    async def process_message(self, message: AgentMessage):
        # Lógica customizada
        result = self.do_something(message.payload)
        return self.create_message(
            MessageType.RESPONSE,
            {"result": result}
        )
```

### Padrão 3: Pipeline Complexo

```python
pipeline = Pipeline([
    ValidationFilter(config1),
    CustomFilter(config2),
    EnrichmentFilter(config3),
])

results = await pipeline.process_batch(messages)
```

## Boas Práticas

### 1. Configuração

- Use `AgentConfig` para toda configuração
- Centralize configurações no `.env`
- Valide configuração no startup

### 2. Error Handling

```python
try:
    result = await agent.process_message(message)
except Exception as e:
    await agent.handle_error(e, message)
```

### 3. Logging

```python
# Logging automático via self.logger
self.logger.info("Processando mensagem")
self.logger.error("Erro ao processar", exc_info=True)
```

### 4. Lifecycle

```python
agent = MyAgent(config)

try:
    await agent.start()
    # Use o agente
finally:
    await agent.stop()
```

### 5. Context Managers

```python
async with MessageProducer() as producer:
    await producer.send(message)
```

## Extensibilidade

### Adicionando Novos Filtros

```python
class MyCustomFilter(FilterAgent):
    async def filter(self, message: AgentMessage):
        # Sua lógica aqui
        return modified_message
```

### Adicionando Novos Comandos

```python
handler = CommandHandler(config)
handler.register_command("my_command", my_handler_func)
```

### Adicionando Novos Padrões

1. Herdar de `BaseAgent`
2. Implementar `process_message()`
3. Adicionar lógica específica do padrão
4. Documentar uso

## Monitoramento e Observabilidade

### Logging

Todos os agentes usam logging estruturado:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Métricas Recomendadas

- **Throughput**: Mensagens processadas/segundo
- **Latência**: Tempo de processamento
- **Erros**: Taxa de erro
- **Queue Depth**: Tamanho das filas

### Health Checks

```python
if agent.is_running():
    print("Agent is healthy")
```

## Testes

### Unit Tests

```python
@pytest.mark.asyncio
async def test_agent_processes_message():
    config = AgentConfig(name="TestAgent")
    agent = MyAgent(config)
    
    message = AgentMessage(...)
    result = await agent.process_message(message)
    
    assert result is not None
```

### Integration Tests

Requer Azure Service Bus real ou emulador.

## Referências

- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/)
- [Azure Service Bus Documentation](https://docs.microsoft.com/azure/service-bus-messaging/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
