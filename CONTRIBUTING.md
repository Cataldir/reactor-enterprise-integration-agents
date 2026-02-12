# Contribuindo

Obrigado por considerar contribuir com este projeto! 🎉

## Como Contribuir

### Reportando Bugs

Se você encontrou um bug:

1. Verifique se já não existe uma [issue](https://github.com/Cataldir/reactor-enterprise-integration-agents/issues) sobre o problema
2. Crie uma nova issue incluindo:
   - Descrição clara do problema
   - Passos para reproduzir
   - Comportamento esperado vs. comportamento atual
   - Versão do Python e sistema operacional
   - Logs relevantes

### Sugerindo Melhorias

Para sugerir novas funcionalidades ou melhorias:

1. Abra uma issue com a tag "enhancement"
2. Descreva claramente:
   - O problema que você quer resolver
   - Sua solução proposta
   - Exemplos de uso
   - Impacto em código existente

### Pull Requests

#### Antes de Começar

1. Faça fork do repositório
2. Clone seu fork localmente
3. Crie uma branch para sua feature/fix:
   ```bash
   git checkout -b feature/minha-feature
   # ou
   git checkout -b fix/meu-bug-fix
   ```

#### Desenvolvimento

1. **Instale dependências de desenvolvimento:**
   ```bash
   uv sync
   ```

2. **Mantenha o código consistente:**
   - Siga as convenções de código Python (PEP 8)
   - Use type hints
   - Adicione docstrings para classes e funções públicas

3. **Adicione testes:**
   ```bash
   # Execute testes existentes
   pytest tests/ -v
   
   # Adicione novos testes para sua funcionalidade
   # em tests/test_sua_funcionalidade.py
   ```

4. **Mantenha a documentação atualizada:**
   - Atualize o README.md se necessário
   - Adicione/atualize docstrings
   - Atualize docs/ se for uma feature maior

#### Enviando o PR

1. Commit suas mudanças:
   ```bash
   git add .
   git commit -m "feat: descrição clara da mudança"
   ```

   Use prefixos convencionais:
   - `feat:` - Nova funcionalidade
   - `fix:` - Correção de bug
   - `docs:` - Mudanças na documentação
   - `test:` - Adicionar/modificar testes
   - `refactor:` - Refatoração de código
   - `style:` - Formatação, ponto e vírgula, etc
   - `chore:` - Manutenção, dependências, etc

2. Push para seu fork:
   ```bash
   git push origin feature/minha-feature
   ```

3. Abra um Pull Request:
   - Descreva as mudanças claramente
   - Referencie issues relacionadas
   - Adicione screenshots se aplicável
   - Aguarde review

## Padrões de Código

### Style Guide

Este projeto segue:
- [PEP 8](https://peps.python.org/pep-0008/) - Style Guide for Python Code
- [PEP 257](https://peps.python.org/pep-0257/) - Docstring Conventions

### Formatação

Usamos Black para formatação:

```bash
black patterns/ agents/ shared/ tests/ examples/
```

### Linting

Usamos Ruff para linting:

```bash
ruff check patterns/ agents/ shared/ tests/ examples/
```

### Type Checking

Usamos mypy para type checking:

```bash
mypy patterns/ agents/ shared/
```

## Estrutura de Testes

### Organização

```
tests/
├── test_message_queue.py       # Testes de Message Queue
├── test_pipes_and_filters.py   # Testes de Pipes & Filters
├── test_pubsub.py              # Testes de Pub/Sub
├── test_command_messages.py    # Testes de Command Messages
└── conftest.py                 # Fixtures compartilhados
```

### Escrevendo Testes

```python
import pytest
from patterns.your_pattern import YourClass

@pytest.mark.asyncio
async def test_your_feature():
    """Test description."""
    # Arrange
    obj = YourClass()
    
    # Act
    result = await obj.method()
    
    # Assert
    assert result is not None
```

### Executando Testes

```bash
# Todos os testes
pytest tests/

# Com cobertura
pytest --cov=patterns --cov=agents tests/

# Testes específicos
pytest tests/test_pipes_and_filters.py::test_validation_filter

# Com output verbose
pytest tests/ -v -s
```

## Documentação

### Docstrings

Use Google-style docstrings:

```python
def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
    """
    Processa uma mensagem recebida.
    
    Args:
        message: Mensagem a ser processada
    
    Returns:
        Mensagem processada ou None se rejeitada
    
    Raises:
        ValueError: Se a mensagem for inválida
    
    Example:
        >>> agent = MyAgent(config)
        >>> result = await agent.process_message(message)
    """
    pass
```

### Documentação em Markdown

- Português brasileiro para docs/pt-br/
- Use exemplos práticos
- Adicione diagramas quando apropriado
- Mantenha código de exemplo atualizado

## Diretrizes Específicas

### Novos Padrões

Ao adicionar um novo padrão de integração:

1. Crie diretório em `patterns/novo_padrao/`
2. Implemente classe base herdando de `BaseAgent`
3. Adicione exemplo em `examples/novo_padrao_example.py`
4. Adicione testes em `tests/test_novo_padrao.py`
5. Documente em `docs/pt-br/integration-patterns.md`

### Novos Filtros

Para adicionar um filtro ao Pipes & Filters:

1. Herde de `FilterAgent`
2. Implemente método `filter()`
3. Adicione testes
4. Adicione exemplo de uso

### Novos Comandos

Para adicionar comandos:

1. Crie função handler
2. Registre no `CommandHandler` ou `CommandBus`
3. Adicione testes
4. Documente uso

## Revisão de Código

### O que Procuramos

✅ **Bom:**
- Código claro e legível
- Testes abrangentes
- Documentação atualizada
- Type hints
- Error handling apropriado
- Exemplos práticos

❌ **Evitar:**
- Código complexo sem necessidade
- Falta de testes
- Documentação desatualizada
- Magic numbers/strings
- Commits não descritivos

### Processo de Review

1. Automated checks (pytest, ruff, mypy)
2. Code review por mantenedores
3. Sugestões e discussão
4. Aprovação e merge

## Comunidade

### Código de Conduta

- Seja respeitoso e construtivo
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade
- Demonstre empatia com outros membros

### Comunicação

- Issues: Para bugs e features
- Discussions: Para ideias e perguntas
- Pull Requests: Para código

## Reconhecimento

Contribuidores serão:
- Listados no README.md
- Mencionados nos release notes
- Creditados nos commits

## Dúvidas?

- 📖 Leia a [documentação](README.md)
- 💬 Abra uma Discussion
- 📧 Entre em contato com mantenedores

---

**Obrigado por contribuir!** 🚀

Juntos podemos fazer este projeto ainda melhor para a comunidade de desenvolvedores.
