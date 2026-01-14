# src/agents/base.py
"""
Base agent implementation using LangChain.

Provides a simple, consistent interface for all korben agents.
Supports multiple LLM providers (OpenAI, Anthropic) via config.
"""

import os
import logging
from typing import Optional, Any, Union
from abc import ABC, abstractmethod

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


def get_llm_config() -> dict:
    """
    Get LLM configuration from core config.
    
    Returns:
        dict: LLM configuration with provider, model, temperature, max_tokens
    """
    from src.lib.core_utils import get_core_config
    
    config = get_core_config()
    llm_config = config.get('llm', {})
    
    # Defaults
    provider = llm_config.get('provider', 'openai')
    
    # Get provider-specific settings
    provider_config = llm_config.get(provider, {})
    
    # Default models per provider
    default_models = {
        'openai': 'gpt-4o',
        'anthropic': 'claude-sonnet-4-20250514',
    }
    
    return {
        'provider': provider,
        'model': provider_config.get('model', default_models.get(provider, 'gpt-4o')),
        'temperature': provider_config.get('temperature', 0.7),
        'max_tokens': provider_config.get('max_tokens', 4096),
    }


def get_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> BaseChatModel:
    """
    Get a configured LangChain LLM instance.
    
    Reads defaults from config/korben.yml, with optional overrides.
    
    Args:
        provider: LLM provider ("openai" or "anthropic"). Defaults to config.
        model: The model to use. Defaults to config.
        temperature: Sampling temperature (0-1). Defaults to config.
        max_tokens: Maximum tokens in response. Defaults to config.
    
    Returns:
        BaseChatModel: Configured LLM instance
    
    Environment Variables:
        - OPENAI_API_KEY: Required for OpenAI provider
        - ANTHROPIC_API_KEY: Required for Anthropic provider
    """
    # Get defaults from config
    config = get_llm_config()
    
    # Apply overrides
    provider = provider or config['provider']
    model = model or config['model']
    temperature = temperature if temperature is not None else config['temperature']
    max_tokens = max_tokens or config['max_tokens']
    
    logger.debug(f"Initializing LLM: provider={provider}, model={model}")
    
    if provider == 'openai':
        from langchain_openai import ChatOpenAI
        
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Please set it to use OpenAI features."
            )
        
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
        )
    
    elif provider == 'anthropic':
        from langchain_anthropic import ChatAnthropic
        
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Please set it to use Anthropic features."
            )
        
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
        )
    
    else:
        raise ValueError(f"Unknown LLM provider: {provider}. Use 'openai' or 'anthropic'.")


class BaseAgent(ABC):
    """
    Abstract base class for korben agents.
    
    Subclass this to create specialized agents with their own
    system prompts and behaviors.
    
    Example:
        class MyAgent(BaseAgent):
            name = "MyAgent"
            system_prompt = "You are a helpful assistant..."
            
            def build_prompt(self, **kwargs) -> str:
                return f"Do something with {kwargs['input']}"
        
        agent = MyAgent()
        result = agent.run(input="some data")
    """
    
    # Override these in subclasses
    name: str = "BaseAgent"
    system_prompt: str = "You are a helpful assistant."
    temperature: float = 0.7
    max_tokens: int = 4096
    
    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize the agent.
        
        Args:
            provider: LLM provider ("openai" or "anthropic"). Defaults to config.
            model: Override model from config
            temperature: Override default temperature
            max_tokens: Override default max tokens
        """
        self._provider = provider
        self._model = model
        self._temperature = temperature if temperature is not None else self.temperature
        self._max_tokens = max_tokens or self.max_tokens
        self._llm = None
        
        logger.info(f"Initialized agent: {self.name}")
    
    @property
    def llm(self) -> BaseChatModel:
        """Lazy-load the LLM instance."""
        if self._llm is None:
            self._llm = get_llm(
                provider=self._provider,
                model=self._model,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
        return self._llm
    
    @abstractmethod
    def build_prompt(self, **kwargs) -> str:
        """
        Build the user prompt from input arguments.
        
        Override this in subclasses to construct the specific prompt
        for your agent's task.
        
        Args:
            **kwargs: Task-specific arguments
        
        Returns:
            str: The constructed prompt
        """
        pass
    
    def run(self, **kwargs) -> str:
        """
        Run the agent with the given inputs.
        
        Args:
            **kwargs: Task-specific arguments passed to build_prompt()
        
        Returns:
            str: The agent's response
        """
        prompt = self.build_prompt(**kwargs)
        
        logger.info(f"Running {self.name}: {prompt[:80]}...")
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt),
        ]
        
        response = self.llm.invoke(messages)
        result = response.content
        
        logger.debug(f"{self.name} response: {result[:100]}...")
        
        return result


def run_agent(agent_class: type, **kwargs) -> str:
    """
    Convenience function to instantiate and run an agent.
    
    Args:
        agent_class: The agent class to instantiate
        **kwargs: Arguments passed to agent.run()
    
    Returns:
        str: The agent's response
    
    Example:
        result = run_agent(DailySummaryAgent, daily_note="...", backlog="...")
    """
    agent = agent_class()
    return agent.run(**kwargs)
