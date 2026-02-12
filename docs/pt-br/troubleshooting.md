# Troubleshooting

Este guia ajuda a resolver problemas comuns ao usar o repositório.

## Problemas de Instalação

### Erro: ModuleNotFoundError

**Sintoma:**
```
ModuleNotFoundError: No module named 'pydantic'
```

**Solução:**
```bash
# Instale as dependências
pip install -r requirements.txt

# Ou instale o projeto em modo de desenvolvimento
pip install -e .
```

### Erro: Python version incompatível

**Sintoma:**
```
ERROR: This package requires Python >=3.13
```

**Solução:**
```bash
# Verifique sua versão do Python
python3 --version

# Se necessário, instale Python 3.13+
# Ubuntu/Debian
sudo apt update
sudo apt install python3.13

# macOS (via Homebrew)
brew install python@3.13
```

## Problemas com Azure Service Bus

### Erro: Connection String inválida

**Sintoma:**
```
ValueError: Connection string não encontrada
```

**Solução:**
1. Certifique-se de ter um arquivo `.env` na raiz do projeto
2. Copie `.env.example` para `.env`
3. Adicione sua connection string do Azure Service Bus

```bash
cp .env.example .env
# Edite o .env com suas credenciais
```

### Erro: Fila não encontrada

**Sintoma:**
```
ServiceRequestError: The messaging entity 'agent-queue' could not be found
```

**Solução:**
1. Acesse o Azure Portal
2. Navegue até seu namespace do Service Bus
3. Crie a fila/tópico necessário:
   - Para Message Queue: Crie uma fila com o nome especificado em `AZURE_SERVICEBUS_QUEUE_NAME`
   - Para Pub/Sub: Crie um tópico e pelo menos uma assinatura

### Erro: Unauthorized

**Sintoma:**
```
ServiceBusAuthorizationError: Unauthorized access
```

**Solução:**
1. Verifique se a connection string está correta
2. Certifique-se de que a política de acesso tem as permissões necessárias:
   - Send (para publicar)
   - Listen (para consumir)
   - Manage (para criar filas/tópicos)

## Problemas de Execução

### Erro: asyncio event loop is closed

**Sintoma:**
```
RuntimeError: Event loop is closed
```

**Solução:**
Use `asyncio.run()` para executar código assíncrono:

```python
# ❌ Errado
async def main():
    await agent.process()

main()  # Não funciona

# ✅ Correto
async def main():
    await agent.process()

asyncio.run(main())
```

### Erro: Mensagens não sendo processadas

**Sintoma:**
O agente inicia mas não processa mensagens.

**Checklist:**
1. Verifique se `await agent.start()` foi chamado
2. Verifique se `await agent.start_processing()` foi chamado (para MessageQueue)
3. Verifique se há mensagens na fila no Azure Portal
4. Verifique os logs para erros de deserialização
5. Certifique-se de que não há lock nas mensagens

**Debug:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Ative logs detalhados
```

### Erro: Timeout ao processar mensagens

**Sintoma:**
```
asyncio.TimeoutError
```

**Solução:**
Aumente o timeout:

```python
# Para comandos
response = await invoker.invoke_command(
    handler,
    "command_name",
    params,
    timeout=60  # Aumente o timeout
)

# Para agentes
config = AgentConfig(
    name="MyAgent",
    timeout_seconds=60  # Aumente o timeout
)
```

## Problemas com Filtros e Pipelines

### Erro: Mensagem sendo bloqueada

**Sintoma:**
Pipeline retorna `None` para mensagens válidas.

**Checklist:**
1. Verifique se todos os campos obrigatórios estão presentes
2. Verifique se `pass_through=True` nos filtros que não devem bloquear
3. Adicione logging nos filtros para debug:

```python
class MyFilter(FilterAgent):
    async def filter(self, message: AgentMessage):
        self.logger.info(f"Processando: {message.payload}")
        # ... lógica do filtro
```

### Erro: Transformação não aplicada

**Sintoma:**
Payload não está sendo transformado.

**Solução:**
Certifique-se de retornar a mensagem modificada:

```python
# ❌ Errado
async def filter(self, message):
    message.payload["new_field"] = "value"
    return message  # Modifica o original (não recomendado)

# ✅ Correto
async def filter(self, message):
    modified = message.model_copy()
    modified.payload["new_field"] = "value"
    return modified
```

## Problemas de Performance

### Lentidão no processamento

**Sintomas:**
- Processamento muito lento
- Mensagens acumulando na fila

**Soluções:**

1. **Aumente o número de workers:**
```python
agent = MessageQueueAgent(
    config,
    max_concurrent_calls=10  # Padrão é 5
)
```

2. **Use processamento em lote:**
```python
results = await pipeline.process_batch(messages)
```

3. **Otimize a lógica de processamento:**
```python
# ❌ Processamento sequencial
for item in items:
    await process(item)

# ✅ Processamento paralelo
tasks = [process(item) for item in items]
await asyncio.gather(*tasks)
```

### Alto uso de memória

**Solução:**
Processe mensagens em lotes menores:

```python
async def process_in_batches(messages, batch_size=100):
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i + batch_size]
        await pipeline.process_batch(batch)
```

## Problemas de Imports

### Erro: No module named 'patterns'

**Sintoma:**
```
ModuleNotFoundError: No module named 'patterns'
```

**Solução:**
Defina o PYTHONPATH:

```bash
# Opção 1: Variável de ambiente
export PYTHONPATH=/caminho/para/o/projeto:$PYTHONPATH

# Opção 2: Instale o projeto em modo de desenvolvimento
pip install -e .

# Opção 3: Use imports relativos (dentro do projeto)
from patterns.message_queue import MessageQueueAgent
```

## Problemas com Testes

### Testes falhando

**Checklist:**
1. Instale as dependências de desenvolvimento:
```bash
pip install -e ".[dev]"
```

2. Use pytest-asyncio para testes assíncronos:
```python
import pytest

@pytest.mark.asyncio
async def test_agent():
    agent = MyAgent(config)
    result = await agent.process_message(message)
    assert result is not None
```

3. Mock o Azure Service Bus para testes:
```python
from unittest.mock import AsyncMock, patch

@patch('shared.azure_clients.get_async_service_bus_client')
async def test_with_mock(mock_client):
    mock_client.return_value = AsyncMock()
    # ... seu teste
```

## Obtendo Ajuda

Se você ainda está tendo problemas:

1. **Verifique os logs:**
```bash
# Ative logging detalhado
export LOG_LEVEL=DEBUG
python3 seu_script.py
```

2. **Execute os exemplos:**
```bash
# Teste com exemplos que não requerem Azure
python3 examples/pipes_and_filters_example.py
python3 examples/command_messages_example.py
```

3. **Verifique a documentação:**
- [Guia de Padrões](integration-patterns.md)
- [Arquitetura de Agentes](agent-architecture.md)

4. **Issues no GitHub:**
Abra uma issue com:
- Descrição do problema
- Código que reproduz o erro
- Logs completos
- Versão do Python
- Sistema operacional

## Dicas de Debug

### Habilitar logs detalhados

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Inspecionar mensagens

```python
# Adicione prints para debug
async def process_message(self, message: AgentMessage):
    print(f"Mensagem recebida: {message.model_dump_json(indent=2)}")
    # ... processamento
```

### Usar breakpoints

```python
# Para debug interativo
import pdb

async def process_message(self, message: AgentMessage):
    pdb.set_trace()  # Pausa execução aqui
    # ... código
```

### Validar configuração

```python
# Verifique se todas as variáveis de ambiente estão definidas
from dotenv import load_dotenv
import os

load_dotenv()

required_vars = [
    'AZURE_SERVICEBUS_CONNECTION_STRING',
    'AZURE_SERVICEBUS_QUEUE_NAME',
]

for var in required_vars:
    value = os.getenv(var)
    print(f"{var}: {'✓' if value else '✗ Missing'}")
```

## Checklist de Diagnóstico

Antes de relatar um problema, execute este checklist:

- [ ] Python 3.13+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` configurado
- [ ] Azure Service Bus configurado (se necessário)
- [ ] Filas/tópicos criados no Azure Portal
- [ ] Exemplos básicos funcionando
- [ ] Logs habilitados
- [ ] Connection string válida
- [ ] Permissões corretas no Service Bus

---

Para mais informações, consulte a [documentação completa](../README.md).
