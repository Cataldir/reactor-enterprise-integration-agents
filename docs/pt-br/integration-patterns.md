# Guia de Padrões de Integração Empresarial

Este documento descreve os padrões de integração empresarial implementados neste repositório e como aplicá-los com agentes de AI.

## 1. Message Queue (Fila de Mensagens)

### Descrição
Padrão onde mensagens são enfileiradas para processamento assíncrono. Garante que nenhuma mensagem seja perdida e permite processamento desacoplado.

### Quando Usar
- Processamento assíncrono de tarefas
- Balanceamento de carga entre workers
- Garantia de entrega de mensagens
- Sistemas com picos de tráfego

### Vantagens
- ✅ Desacoplamento entre produtor e consumidor
- ✅ Escalabilidade horizontal (múltiplos consumers)
- ✅ Resiliência (mensagens persistidas)
- ✅ Controle de fluxo e backpressure

### Exemplo de Uso com Agentes

```python
from patterns.message_queue import MessageQueueAgent
from shared.models import AgentConfig

# Agente que processa pedidos
config = AgentConfig(name="OrderProcessor")
agent = MessageQueueAgent(config)

await agent.start()
await agent.start_processing()
```

### Casos de Uso Reais
- **E-commerce**: Processamento de pedidos
- **Analytics**: Processamento de eventos de usuários
- **IoT**: Processamento de dados de sensores
- **Notificações**: Envio de emails/SMS em lote

---

## 2. Pipes and Filters (Pipeline de Processamento)

### Descrição
Mensagens fluem através de uma série de filtros, cada um realizando uma transformação específica. Como uma linha de montagem onde cada estação adiciona ou modifica algo.

### Quando Usar
- Processamento de dados em etapas
- Transformações complexas decompostas em passos simples
- Validação e enriquecimento de dados
- ETL (Extract, Transform, Load)

### Vantagens
- ✅ Separação de responsabilidades
- ✅ Reutilização de filtros
- ✅ Fácil manutenção e teste
- ✅ Composição flexível

### Exemplo de Uso com Agentes

```python
from patterns.pipes_and_filters import Pipeline, ValidationFilter, TransformFilter

# Cria pipeline com 3 filtros
pipeline = Pipeline([
    ValidationFilter(config1, required_fields=["email", "name"]),
    TransformFilter(config2, transform_func=normalize_data),
    EnrichmentFilter(config3, enrichment_data={"version": "1.0"})
])

# Processa mensagem através do pipeline
result = await pipeline.process(message)
```

### Casos de Uso Reais
- **Data Processing**: ETL pipelines
- **Content Management**: Processamento de uploads
- **API Gateways**: Validação, transformação, roteamento
- **Machine Learning**: Feature engineering pipelines

---

## 3. Publish-Subscribe (Pub/Sub)

### Descrição
Publicadores enviam mensagens para um tópico, e múltiplos assinantes recebem cópias dessas mensagens. Permite comunicação de um-para-muitos.

### Quando Usar
- Broadcast de eventos para múltiplos sistemas
- Arquitetura orientada a eventos
- Notificações em tempo real
- Múltiplos consumidores para a mesma mensagem

### Vantagens
- ✅ Desacoplamento total entre publicador e assinantes
- ✅ Escalabilidade (adicionar assinantes sem modificar publicador)
- ✅ Múltiplos consumidores processam em paralelo
- ✅ Permite diferentes lógicas de processamento

### Exemplo de Uso com Agentes

```python
from patterns.pubsub import PublisherAgent, SubscriberAgent

# Publicador
publisher = PublisherAgent(config_pub)
await publisher.publish_event("user_registered", {"user_id": "123"})

# Múltiplos assinantes
analytics_agent = SubscriberAgent(config_sub1, handler=analytics_handler)
notification_agent = SubscriberAgent(config_sub2, handler=notification_handler)
audit_agent = SubscriberAgent(config_sub3, handler=audit_handler)

# Todos recebem o mesmo evento
await analytics_agent.start_listening()
await notification_agent.start_listening()
await audit_agent.start_listening()
```

### Casos de Uso Reais
- **Microserviços**: Comunicação entre serviços
- **Analytics**: Múltiplos sistemas processando eventos
- **Auditoria**: Logs centralizados
- **Real-time Updates**: Dashboards, notificações

---

## 4. Command Messages (Mensagens de Comando)

### Descrição
Padrão Request-Reply onde comandos são enviados explicitamente e respostas são aguardadas. Encapsula uma requisição como um objeto.

### Quando Usar
- Operações síncronas ou com resposta necessária
- RPC (Remote Procedure Call)
- Task orchestration
- APIs com feedback imediato

### Vantagens
- ✅ Comunicação bidirecional clara
- ✅ Suporte a timeout e retry
- ✅ Facilita logging e rastreamento
- ✅ Desacoplamento através do Command Bus

### Exemplo de Uso com Agentes

```python
from patterns.command_messages import CommandHandler, CommandInvoker

# Handler com comandos
handler = CommandHandler(config, {
    "process_data": process_func,
    "send_email": email_func
})

# Invocar comando e aguardar resposta
invoker = CommandInvoker("Client")
response = await invoker.invoke_command(
    handler,
    "process_data",
    {"data": "..."}
)

print(response.result)
```

### Casos de Uso Reais
- **APIs REST**: Endpoints que executam ações
- **Workflows**: Orquestração de tarefas
- **Batch Jobs**: Execução de tarefas agendadas
- **Admin Panels**: Operações administrativas

---

## Comparação dos Padrões

| Padrão | Comunicação | Resposta | Múltiplos Consumidores | Melhor Para |
|--------|-------------|----------|------------------------|-------------|
| **Message Queue** | Assíncrona | Não | Sim (competindo) | Tarefas assíncronas |
| **Pipes & Filters** | Síncrona | Sim | Não (sequencial) | Transformações |
| **Pub/Sub** | Assíncrona | Não | Sim (todos recebem) | Broadcasting |
| **Command Messages** | Síncrona/Async | Sim | Não (1-1) | RPC, operações |

---

## Combinando Padrões

Os padrões podem ser combinados para criar arquiteturas mais complexas:

### Exemplo 1: Command + Queue
```python
# Comando envia mensagem para fila
command_handler.register_command("process_order", 
    lambda params: queue_producer.send(params)
)
```

### Exemplo 2: Pub/Sub + Pipes
```python
# Assinante processa através de pipeline
subscriber = SubscriberAgent(config, 
    handler=lambda msg: pipeline.process(msg)
)
```

### Exemplo 3: Queue + Command
```python
# Mensagem da fila executa comando
queue_agent.process_message = lambda msg: 
    command_bus.dispatch(msg.command_name, msg.parameters)
```

---

## Melhores Práticas

### 1. **Escolha o Padrão Correto**
- Use **Message Queue** para tarefas assíncronas demoradas
- Use **Pipes & Filters** para transformações complexas
- Use **Pub/Sub** para broadcast de eventos
- Use **Command Messages** para operações síncronas

### 2. **Error Handling**
- Sempre implemente retry logic
- Use dead-letter queues para mensagens problemáticas
- Logging detalhado para debugging

### 3. **Monitoramento**
- Métricas de throughput
- Latência de processamento
- Taxa de erro
- Tamanho das filas

### 4. **Escalabilidade**
- Horizontal scaling com múltiplos workers
- Particionamento de filas/tópicos
- Load balancing automático

### 5. **Segurança**
- Autenticação com Azure AD
- Criptografia em trânsito e repouso
- Validação de mensagens
- Rate limiting

---

## Próximos Passos

1. ✅ Implemente os exemplos básicos
2. 📚 Estude os casos de uso reais
3. 🧪 Experimente combinações de padrões
4. 🚀 Adapte para seu caso de uso específico
5. 📊 Adicione monitoramento e observabilidade

Para mais exemplos, veja o diretório `/examples` no repositório.
