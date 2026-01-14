# src/agents/__init__.py
"""
Korben Agents - Base classes for AI agents.

Plugins should define their own agents in `plugins/<name>/agents.py`
by subclassing BaseAgent from this module.

Example:
    # src/plugins/myproject/agents.py
    from src.agents.base import BaseAgent
    
    class MyAgent(BaseAgent):
        name = "MyAgent"
        system_prompt = "You are a helpful assistant..."
        
        def build_prompt(self, **kwargs) -> str:
            return f"Do something with {kwargs['input']}"
"""

from src.agents.base import BaseAgent, get_llm, get_llm_config, run_agent

__all__ = [
    "BaseAgent",
    "get_llm",
    "get_llm_config",
    "run_agent",
]
