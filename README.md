# Reactor Enterprise Integration Agents

> Integração de Agentes do Azure AI Foundry com Padrões de Integração Empresarial

Um repositório que documenta e demonstra, em Python 3.13 e usando serviços da Azure, como integrar agentes do Azure AI Foundry em padrões clássicos de integração empresarial.

## 🎯 Objetivo

Fala se não é curioso saber como os agentes encaixam em um **Message Queue** ou um **Pipes and Filters**?

Ou qual a forma mais produtiva de entregar Agentes que trabalham em **Pub/Sub** e **Command Messages**?

Este repositório oferece um deep dive em integrações empresariais para aplicações de AI, com exemplos práticos e código pronto para uso.

## 🏗️ Padrões de Integração Implementados

### 1. Message Queue (Fila de Mensagens)
- Agentes como consumidores e produtores de mensagens
- Integração com Azure Service Bus Queues
- Processamento assíncrono e resiliente
- Exemplos: `/patterns/message_queue/`

### 2. Pipes and Filters (Pipeline de Processamento)
- Cadeia de agentes com filtros sequenciais
- Processamento em pipeline com transformações
- Composição de agentes especializados
- Exemplos: `/patterns/pipes_and_filters/`

### 3. Publish-Subscribe (Pub/Sub)
- Múltiplos agentes assinando tópicos
- Integração com Azure Service Bus Topics
- Comunicação desacoplada e escalável
- Exemplos: `/patterns/pubsub/`

### 4. Command Messages (Mensagens de Comando)
- Comunicação baseada em comandos
- Padrão Request-Reply com agentes
- Orquestração de tarefas complexas
- Exemplos: `/patterns/command_messages/`

## 📋 Pré-requisitos

- Python 3.13+
- Conta Azure com acesso ao Azure Service Bus
- Azure AI Foundry configurado (opcional para alguns exemplos)

## 🚀 Instalação

```bash
# Clone o repositório
git clone https://github.com/Cataldir/reactor-enterprise-integration-agents.git
cd reactor-enterprise-integration-agents

# Crie um ambiente virtual
python3.13 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instale as dependências
pip install -e .

# Para desenvolvimento
pip install -e ".[dev]"
```

## ⚙️ Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
# Azure Service Bus
AZURE_SERVICEBUS_CONNECTION_STRING=your_connection_string_here
AZURE_SERVICEBUS_QUEUE_NAME=agent-queue
AZURE_SERVICEBUS_TOPIC_NAME=agent-topic
AZURE_SERVICEBUS_SUBSCRIPTION_NAME=agent-subscription

# Azure AI Foundry (opcional)
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
```

## 📖 Estrutura do Projeto

```
reactor-enterprise-integration-agents/
├── patterns/                      # Implementações dos padrões
│   ├── message_queue/            # Padrão Message Queue
│   ├── pipes_and_filters/        # Padrão Pipes and Filters
│   ├── pubsub/                   # Padrão Publish-Subscribe
│   └── command_messages/         # Padrão Command Messages
├── agents/                       # Implementações de agentes
│   ├── base_agent.py            # Classe base para agentes
│   └── examples/                # Exemplos de agentes específicos
├── shared/                       # Código compartilhado
│   ├── models.py                # Modelos de dados (Pydantic)
│   └── azure_clients.py         # Clientes Azure reutilizáveis
├── docs/                        # Documentação detalhada
│   ├── pt-br/                   # Documentação em Português
│   └── architecture/            # Diagramas de arquitetura
├── examples/                    # Exemplos de uso completos
└── tests/                       # Testes unitários e de integração
```

## 🎓 Como Usar

### Exemplo 1: Agent em Message Queue

```python
from patterns.message_queue import MessageQueueAgent
from shared.azure_clients import get_service_bus_client

# Cria um agente consumidor de fila
agent = MessageQueueAgent(
    name="ProcessingAgent",
    queue_name="tasks-queue"
)

# Inicia o processamento
await agent.start_processing()
```

### Exemplo 2: Pipeline com Pipes and Filters

```python
from patterns.pipes_and_filters import Pipeline, FilterAgent

# Cria um pipeline de processamento
pipeline = Pipeline([
    FilterAgent("DataValidator"),
    FilterAgent("DataTransformer"),
    FilterAgent("DataEnricher"),
])

# Processa dados através do pipeline
result = await pipeline.process(input_data)
```

### Exemplo 3: Pub/Sub com Múltiplos Agentes

```python
from patterns.pubsub import SubscriberAgent, PublisherAgent

# Cria agentes assinantes
subscriber1 = SubscriberAgent("AnalyticsAgent", topic="events")
subscriber2 = SubscriberAgent("NotificationAgent", topic="events")

# Cria agente publicador
publisher = PublisherAgent(topic="events")

# Publica evento
await publisher.publish({"event": "user_action", "data": {...}})
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=patterns --cov=agents

# Executar testes específicos
pytest tests/test_message_queue.py
```

## 📚 Documentação Adicional

- [Guia de Padrões de Integração](docs/pt-br/integration-patterns.md)
- [Arquitetura de Agentes](docs/pt-br/agent-architecture.md)
- [Melhores Práticas](docs/pt-br/best-practices.md)
- [Troubleshooting](docs/pt-br/troubleshooting.md)

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

Este projeto foi desenvolvido para demonstrar a integração de agentes de AI com padrões empresariais consolidados, facilitando a adoção de AI em ambientes corporativos.

---

**Bora pro deep dive em integrações empresariais para aplicações de AI!** 🚀
