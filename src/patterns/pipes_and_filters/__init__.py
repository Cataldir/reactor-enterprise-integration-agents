"""Implementação do padrão Pipes and Filters."""

import asyncio
import logging
from typing import List, Optional, Any, Dict
from abc import abstractmethod

from agents.base_agent import BaseAgent
from shared.models import AgentConfig, AgentMessage, MessageType

logger = logging.getLogger(__name__)


class FilterAgent(BaseAgent):
    """
    Agente que atua como um filtro em um pipeline.
    
    Processa uma mensagem e a passa adiante, potencialmente
    transformando ou filtrando o conteúdo.
    """
    
    def __init__(self, config: AgentConfig, pass_through: bool = True):
        """
        Inicializa o filtro.
        
        Args:
            config: Configuração do agente
            pass_through: Se True, passa a mensagem adiante mesmo se não modificada
        """
        super().__init__(config)
        self.pass_through = pass_through
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Processa e filtra a mensagem.
        
        Args:
            message: Mensagem a processar
        
        Returns:
            Mensagem processada ou None se filtrada
        """
        try:
            # Aplica o filtro
            filtered = await self.filter(message)
            
            if filtered:
                self.logger.info(f"Filtro '{self.name}' processou mensagem {message.id}")
                return filtered
            elif self.pass_through:
                self.logger.info(f"Filtro '{self.name}' passou mensagem {message.id}")
                return message
            else:
                self.logger.info(f"Filtro '{self.name}' bloqueou mensagem {message.id}")
                return None
        
        except Exception as e:
            await self.handle_error(e, message)
            return None if not self.pass_through else message
    
    @abstractmethod
    async def filter(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Implementa a lógica de filtragem.
        
        Args:
            message: Mensagem a filtrar
        
        Returns:
            Mensagem transformada ou None para bloquear
        """
        pass


class ValidationFilter(FilterAgent):
    """Filtro que valida mensagens baseado em regras."""
    
    def __init__(
        self,
        config: AgentConfig,
        required_fields: Optional[List[str]] = None
    ):
        """
        Inicializa o filtro de validação.
        
        Args:
            config: Configuração do agente
            required_fields: Campos obrigatórios no payload
        """
        super().__init__(config, pass_through=False)
        self.required_fields = required_fields or []
    
    async def filter(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Valida se a mensagem contém os campos obrigatórios."""
        for field in self.required_fields:
            if field not in message.payload:
                self.logger.warning(
                    f"Mensagem {message.id} rejeitada: campo '{field}' ausente"
                )
                return None
        
        return message


class TransformFilter(FilterAgent):
    """Filtro que transforma o payload da mensagem."""
    
    def __init__(
        self,
        config: AgentConfig,
        transform_func: Optional[callable] = None
    ):
        """
        Inicializa o filtro de transformação.
        
        Args:
            config: Configuração do agente
            transform_func: Função de transformação customizada
        """
        super().__init__(config)
        self._transform_func = transform_func
    
    async def filter(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Transforma o payload da mensagem."""
        if not self._transform_func:
            return message
        
        try:
            # Aplica a transformação
            transformed_payload = self._transform_func(message.payload)
            
            # Cria nova mensagem com payload transformado
            transformed_message = message.model_copy()
            transformed_message.payload = transformed_payload
            
            return transformed_message
        
        except Exception as e:
            self.logger.error(f"Erro na transformação: {str(e)}")
            return None


class EnrichmentFilter(FilterAgent):
    """Filtro que enriquece mensagens com dados adicionais."""
    
    def __init__(
        self,
        config: AgentConfig,
        enrichment_data: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa o filtro de enriquecimento.
        
        Args:
            config: Configuração do agente
            enrichment_data: Dados para adicionar às mensagens
        """
        super().__init__(config)
        self.enrichment_data = enrichment_data or {}
    
    async def filter(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Enriquece a mensagem com dados adicionais."""
        enriched_message = message.model_copy()
        enriched_message.payload.update(self.enrichment_data)
        
        self.logger.info(f"Mensagem {message.id} enriquecida com {len(self.enrichment_data)} campos")
        return enriched_message


class Pipeline:
    """
    Pipeline que conecta múltiplos filtros em sequência.
    
    Implementa o padrão Pipes and Filters, onde cada filtro
    processa a mensagem e a passa para o próximo na cadeia.
    """
    
    def __init__(self, filters: List[FilterAgent], name: str = "Pipeline"):
        """
        Inicializa o pipeline.
        
        Args:
            filters: Lista de filtros a aplicar em sequência
            name: Nome do pipeline
        """
        self.filters = filters
        self.name = name
        self.logger = logging.getLogger(f"Pipeline.{name}")
        self.logger.info(f"Pipeline '{name}' criado com {len(filters)} filtros")
    
    async def process(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Processa a mensagem através de todos os filtros.
        
        Args:
            message: Mensagem inicial
        
        Returns:
            Mensagem final após todos os filtros, ou None se filtrada
        """
        self.logger.info(f"Processando mensagem {message.id} através do pipeline")
        
        current_message = message
        
        for i, filter_agent in enumerate(self.filters):
            self.logger.debug(f"Aplicando filtro {i+1}/{len(self.filters)}: {filter_agent.name}")
            
            current_message = await filter_agent.process_message(current_message)
            
            if current_message is None:
                self.logger.info(
                    f"Mensagem {message.id} filtrada no estágio {i+1} "
                    f"por '{filter_agent.name}'"
                )
                return None
        
        self.logger.info(f"Mensagem {message.id} completou o pipeline com sucesso")
        return current_message
    
    async def process_batch(self, messages: List[AgentMessage]) -> List[AgentMessage]:
        """
        Processa um lote de mensagens em paralelo.
        
        Args:
            messages: Lista de mensagens
        
        Returns:
            Lista de mensagens processadas (não inclui as filtradas)
        """
        self.logger.info(f"Processando lote de {len(messages)} mensagens")
        
        tasks = [self.process(msg) for msg in messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtra None e exceções
        processed = [
            result for result in results
            if result is not None and not isinstance(result, Exception)
        ]
        
        self.logger.info(
            f"Lote processado: {len(processed)}/{len(messages)} "
            f"mensagens passaram pelo pipeline"
        )
        
        return processed
    
    def add_filter(self, filter_agent: FilterAgent) -> None:
        """Adiciona um novo filtro ao final do pipeline."""
        self.filters.append(filter_agent)
        self.logger.info(f"Filtro '{filter_agent.name}' adicionado ao pipeline")
    
    def __repr__(self) -> str:
        filter_names = [f.name for f in self.filters]
        return f"<Pipeline(name='{self.name}', filters={filter_names})>"
