# Guia de Início Rápido

Este guia ajudará você a começar rapidamente com os padrões de integração empresarial.

## Primeiros Passos (5 minutos)

### 1. Clone o Repositório

```bash
git clone https://github.com/Cataldir/reactor-enterprise-integration-agents.git
cd reactor-enterprise-integration-agents
```

### 2. Configure o Ambiente Python

```bash
# Crie um ambiente virtual
python3 -m venv .venv

# Ative o ambiente virtual
# No Linux/macOS:
source .venv/bin/activate
# No Windows:
.venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

### 3. Execute Exemplos Locais (Sem Azure)

Comece com exemplos que **não** requerem Azure:

#### Exemplo 1: Pipes and Filters

```bash
python3 examples/pipes_and_filters_example.py
```

Este exemplo mostra como criar pipelines de processamento com filtros de validação, transformação e enriquecimento.

**Saída esperada:**
- Mensagens sendo validadas
- Transformações aplicadas
- Processamento em lote paralelo

#### Exemplo 2: Command Messages

```bash
python3 examples/command_messages_example.py
```

Este exemplo demonstra o padrão Command Messages com handlers, invokers e command bus.

**Saída esperada:**
- Execução de comandos
- Respostas estruturadas
- Tratamento de timeout e erros

#### Exemplo 3: Exemplo Completo

```bash
python3 examples/complete_example.py
```

Sistema completo de processamento de pedidos combinando múltiplos padrões!

**Saída esperada:**
- Pipeline de validação
- Execução de comandos
- Orquestração completa

## Próximos Passos: Azure Service Bus (Opcional)

Para usar os padrões **Message Queue** e **Pub/Sub**, você precisará do Azure Service Bus.

### 1. Crie uma Conta Azure

Se você ainda não tem:
1. Acesse [Azure Portal](https://portal.azure.com)
2. Crie uma conta gratuita (inclui créditos)

### 2. Configure o Azure Service Bus

#### Opção A: Via Azure Portal (Recomendado para iniciantes)

1. No Azure Portal, busque por "Service Bus"
2. Clique em "Create"
3. Preencha:
   - **Subscription**: Sua assinatura
   - **Resource group**: Crie um novo (ex: "rg-agents-demo")
   - **Namespace name**: Nome único (ex: "sb-agents-demo-123")
   - **Location**: Brasil Sul ou East US
   - **Pricing tier**: Basic (suficiente para testes)
4. Clique em "Review + create" → "Create"
5. Aguarde a criação (2-3 minutos)

#### Opção B: Via Azure CLI

```bash
# Login
az login

# Crie resource group
az group create --name rg-agents-demo --location brazilsouth

# Crie namespace do Service Bus
az servicebus namespace create \
  --name sb-agents-demo-123 \
  --resource-group rg-agents-demo \
  --location brazilsouth \
  --sku Basic

# Crie uma fila
az servicebus queue create \
  --name agent-queue \
  --namespace-name sb-agents-demo-123 \
  --resource-group rg-agents-demo

# Crie um tópico
az servicebus topic create \
  --name agent-topic \
  --namespace-name sb-agents-demo-123 \
  --resource-group rg-agents-demo

# Crie uma assinatura no tópico
az servicebus topic subscription create \
  --name agent-subscription \
  --topic-name agent-topic \
  --namespace-name sb-agents-demo-123 \
  --resource-group rg-agents-demo
```

### 3. Obtenha a Connection String

#### Via Portal:
1. Vá para seu namespace do Service Bus
2. Menu lateral: "Shared access policies"
3. Clique em "RootManageSharedAccessKey"
4. Copie "Primary Connection String"

#### Via CLI:
```bash
az servicebus namespace authorization-rule keys list \
  --resource-group rg-agents-demo \
  --namespace-name sb-agents-demo-123 \
  --name RootManageSharedAccessKey \
  --query primaryConnectionString \
  --output tsv
```

### 4. Configure o Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o .env e adicione sua connection string
nano .env  # ou use seu editor preferido
```

Conteúdo do `.env`:
```env
AZURE_SERVICEBUS_CONNECTION_STRING=Endpoint=sb://sb-agents-demo-123.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=sua_chave_aqui
AZURE_SERVICEBUS_QUEUE_NAME=agent-queue
AZURE_SERVICEBUS_TOPIC_NAME=agent-topic
AZURE_SERVICEBUS_SUBSCRIPTION_NAME=agent-subscription
```

### 5. Execute Exemplos com Azure

#### Message Queue

```bash
python3 examples/message_queue_example.py
```

#### Pub/Sub

```bash
python3 examples/pubsub_example.py
```

## Estrutura do Projeto

```
reactor-enterprise-integration-agents/
├── patterns/           # Implementações dos padrões
├── agents/            # Classes base de agentes
├── shared/            # Código compartilhado
├── examples/          # Exemplos prontos para uso
├── tests/             # Testes automatizados
└── docs/              # Documentação detalhada
```

## Testando Seu Setup

Execute os testes:

```bash
# Instale dependências de teste
pip install pytest pytest-asyncio

# Execute todos os testes
pytest tests/ -v

# Execute testes específicos
pytest tests/test_pipes_and_filters.py -v
```

**Resultado esperado:** Todos os testes passando ✅

## Exemplo: Criando Seu Primeiro Agente

```python
from patterns.pipes_and_filters import Pipeline, ValidationFilter
from shared.models import AgentConfig, AgentMessage
import asyncio

async def main():
    # Crie um filtro de validação
    config = AgentConfig(name="MyValidator")
    validator = ValidationFilter(
        config,
        required_fields=["name", "email"]
    )
    
    # Crie um pipeline
    pipeline = Pipeline([validator])
    
    # Crie uma mensagem
    message = AgentMessage(
        id="test-1",
        source="API",
        payload={
            "name": "João Silva",
            "email": "joao@example.com"
        }
    )
    
    # Processe
    result = await pipeline.process(message)
    print(f"Resultado: {result.payload if result else 'Rejeitado'}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Recursos de Aprendizado

### Documentação Completa

- [Guia de Padrões](docs/pt-br/integration-patterns.md) - Entenda cada padrão
- [Arquitetura de Agentes](docs/pt-br/agent-architecture.md) - Como tudo funciona
- [Melhores Práticas](docs/pt-br/best-practices.md) - Aprenda com exemplos
- [Troubleshooting](docs/pt-br/troubleshooting.md) - Resolva problemas

### Ordem de Estudo Recomendada

1. ✅ Execute `examples/pipes_and_filters_example.py`
2. ✅ Execute `examples/command_messages_example.py`
3. ✅ Execute `examples/complete_example.py`
4. 📖 Leia [Guia de Padrões](docs/pt-br/integration-patterns.md)
5. 🧪 Configure Azure Service Bus
6. ✅ Execute exemplos com Azure
7. 💻 Crie seu próprio agente
8. 📚 Explore [Melhores Práticas](docs/pt-br/best-practices.md)

## Dicas Rápidas

### Ativar Logs Detalhados

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Verificar Configuração

```python
from dotenv import load_dotenv
import os

load_dotenv()
print("Connection String:", os.getenv("AZURE_SERVICEBUS_CONNECTION_STRING")[:50] + "...")
```

### Executar com PYTHONPATH

```bash
PYTHONPATH=. python3 examples/pipes_and_filters_example.py
```

## Precisa de Ajuda?

- 📖 Consulte a [documentação completa](README.md)
- 🐛 [Troubleshooting Guide](docs/pt-br/troubleshooting.md)
- 💬 Abra uma [Issue no GitHub](https://github.com/Cataldir/reactor-enterprise-integration-agents/issues)

## Próximos Passos

Depois de dominar os exemplos básicos:

1. Combine múltiplos padrões
2. Integre com seus sistemas
3. Adicione monitoramento
4. Implemente em produção
5. Contribua com o projeto!

---

**Bora pro deep dive!** 🚀

Agora que você configurou tudo, explore os padrões e adapte-os para suas necessidades!
