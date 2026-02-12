# 🚀 Guia de Referência Rápida

## Começando em 5 Minutos

### Passo 1: Clonar e Configurar (2 min)
```bash
git clone https://github.com/Cataldir/reactor-enterprise-integration-agents.git
cd reactor-enterprise-integration-agents
cp .env.example .env
# Edite o .env com suas credenciais Azure
```

### Passo 2: Iniciar Todos os Padrões (2 min)
```bash
./start.sh up
```

### Passo 3: Testar as APIs (1 min)
Acesse estas URLs no seu navegador:
- Padrão 1: http://localhost:8000/docs
- Padrão 2: http://localhost:8001/docs
- Padrão 3: http://localhost:8002/docs
- Padrão 4: http://localhost:8003/docs

---

## 📡 Referência Rápida da API

### Padrão 1: Fila de Mensagens (Porta 8000)

**Enviar Tarefa para a Fila:**
```bash
curl -X POST "http://localhost:8000/queue/send" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Processar pedido do cliente",
    "data": {"order_id": "12345"},
    "priority": 1
  }'
```

**Iniciar Monitor do Agente:**
```bash
curl -X POST "http://localhost:8000/agent/start"
```

### Padrão 2: Pipes e Filtros (Porta 8001)

**Executar Pipeline de Análise de Texto:**
```bash
curl -X POST "http://localhost:8001/pipeline/preset/text-analysis" \
  -H "Content-Type: application/json" \
  -d '"Seu texto para análise aqui"'
```

**Pipeline Personalizado:**
```bash
curl -X POST "http://localhost:8001/pipeline/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": "Seus dados",
    "filters": [
      {
        "name": "Filtro 1",
        "instructions": "Processar isto..."
      }
    ],
    "parallel": false
  }'
```

### Padrão 3: Pub/Sub (Porta 8002)

**Publicar Mensagem:**
```bash
curl -X POST "http://localhost:8002/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "customer_events",
    "payload": {
      "event_type": "feedback",
      "customer_id": "C123",
      "rating": 5
    }
  }'
```

**Criar Assinante:**
```bash
curl -X POST "http://localhost:8002/subscribers/preset/customer-service"
```

**Iniciar Consumidores:**
```bash
curl -X POST "http://localhost:8002/consumers/start"
```

### Padrão 4: Mensagens de Comando (Porta 8003)

**Enviar Comando:**
```bash
curl -X POST "http://localhost:8003/commands/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "command_type": "process_data",
    "parameters": {
      "data": [1, 2, 3, 4, 5],
      "operation": "calculate_statistics"
    }
  }'
```

**Verificar Status:**
```bash
curl "http://localhost:8003/commands/{command_id}"
```

**Criar Processador:**
```bash
curl -X POST "http://localhost:8003/processors/preset/data-processor"
```

**Iniciar Pipeline:**
```bash
curl -X POST "http://localhost:8003/pipeline/start"
```

---

## 🐳 Comandos Docker

### Todos os Padrões
```bash
./start.sh up       # Iniciar todos
./start.sh down     # Parar todos
./start.sh logs     # Visualizar logs
./start.sh status   # Verificar status
./start.sh restart  # Reiniciar todos
./start.sh clean    # Limpar tudo
```

### Padrão Individual
```bash
# Construir
docker build -t service-message-queue --target production -f src/services/message_queue/Dockerfile .

# Executar
docker run --env-file .env -p 8000:8000 service-message-queue

# Modo desenvolvimento
docker build -t service-message-queue-dev --target development -f src/services/message_queue/Dockerfile .
docker run --env-file .env -p 8000:8000 -v $(pwd)/src/services/message_queue:/app/src/services/message_queue service-message-queue-dev
```

---

## 🔧 Variáveis de Ambiente

Necessárias no `.env`:
```bash
# Azure AI Foundry
AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>

# Azure Event Hub
EVENTHUB_CONNECTION_STRING=sua_conexao_eventhub
EVENTHUB_NAME=nome_do_seu_hub

# Opcional
MODEL_DEPLOYMENT_NAME=gpt-4
LOG_LEVEL=INFO
```

---

## 📂 Estrutura do Projeto

```
reactor-enterprise-integration-agents/
├── src/                       # Código-fonte principal
│   ├── agents/               # Classes base de agentes
│   ├── shared/               # Utilitários compartilhados
│   │   ├── mcp/             # Camada de integração MCP
│   │   └── utils/           # Utilitários comuns
│   ├── patterns/             # Implementações dos padrões
│   └── services/             # Serviços FastAPI
│       ├── message_queue/   # Padrão de fila
│       ├── pipes_filters/   # Padrão de pipeline
│       ├── pubsub/          # Padrão Pub/Sub
│       └── command_messages/ # Padrão de comando
├── docker-compose.yml        # Orquestração de todos os padrões
├── start.sh                  # Script de inicialização
└── pyproject.toml            # Configuração e dependências
```

---

## 🎯 Seleção de Caso de Uso

**Escolha o Padrão 1 (Fila)** quando:
- Processamento de jobs em segundo plano
- Distribuição de tarefas
- Gerenciamento de filas de trabalho

**Escolha o Padrão 2 (Pipes e Filtros)** quando:
- Pipelines de transformação de dados
- Processamento em múltiplas etapas
- Operações ETL

**Escolha o Padrão 3 (Pub/Sub)** quando:
- Arquitetura orientada a eventos
- Múltiplos consumidores por evento
- Notificações em tempo real

**Escolha o Padrão 4 (Comandos)** quando:
- Operações de longa duração
- Necessidade de rastreamento de status
- Padrão requisição/resposta

---

## 🐛 Resolução de Problemas

### Problemas de Conexão
```bash
# Verificar credenciais do Azure
echo $AZURE_AI_PROJECT_ENDPOINT
echo $EVENTHUB_CONNECTION_STRING

# Testar conectividade do Event Hub
# (Use o Portal Azure para verificar se o hub existe)
```

### Problemas com Docker
```bash
# Limpar ambiente Docker
./start.sh clean

# Reconstruir do zero
docker-compose build --no-cache
./start.sh up
```

### Conflitos de Porta
```bash
# Verificar o que está usando as portas
lsof -i :8000
lsof -i :8001
lsof -i :8002
lsof -i :8003

# Altere as portas no docker-compose.yml se necessário
```

### Problemas com Agentes
```bash
# Verificar criação do agente
# Procure por "Created agent" nos logs
./start.sh logs | grep "Created agent"

# Verificar cotas do Azure AI Foundry
# Verifique os limites de implantação no Portal Azure
```

---

## 📚 Saiba Mais

- [README Principal](README.md) - Visão geral do projeto
- [Arquitetura](ARCHITECTURE.md) - Arquitetura detalhada
- [Resumo da Implementação](IMPLEMENTATION_SUMMARY.md) - Detalhes completos
- [Guia do Padrão 1](src/services/message_queue/README.md)
- [Guia do Padrão 2](src/services/pipes_filters/README.md)
- [Guia do Padrão 3](src/services/pubsub/README.md)
- [Guia do Padrão 4](src/services/command_messages/README.md)

---

## 💡 Dicas Rápidas

1. **Comece simples:** Experimente o Padrão 1 primeiro
2. **Verifique os logs:** Use `./start.sh logs` frequentemente
3. **Use o Swagger:** Acesse `/docs` em cada porta
4. **Monitore o Azure:** Observe as métricas do Event Hub no portal
5. **Escale:** Adicione réplicas no docker-compose.yml

---

## 🆘 Precisa de Ajuda?

1. Consulte a documentação no README de cada padrão
2. Revise os logs: `./start.sh logs`
3. Valide o ambiente: `cat .env`
4. Verifique a saúde dos serviços no portal Azure
5. Abra uma issue no GitHub

---

**Boas Integrações! 🚀**
