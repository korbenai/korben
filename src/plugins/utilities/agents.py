# src/plugins/utilities/agents.py
"""
Utilities plugin agents - general-purpose AI agents.
"""

from src.agents.base import BaseAgent


class WisdomExtractorAgent(BaseAgent):
    """
    Agent that extracts key insights, quotes, and actionable wisdom from text.
    
    Example:
        agent = WisdomExtractorAgent()
        wisdom = agent.run(text="[podcast transcript or article content]")
    """
    
    name = "WisdomExtractorAgent"
    temperature = 0.6
    max_tokens = 8192  # Allow longer outputs for detailed extraction
    
    system_prompt = """You are a wisdom extraction specialist. Your role is to distill key insights, memorable quotes, and actionable advice from content.

Focus on:
- Core ideas and arguments
- Surprising or counterintuitive insights
- Memorable quotes worth saving
- Actionable advice or recommendations
- Connections to broader themes

Be thorough but avoid redundancy. Quality over quantity."""

    def build_prompt(self, text: str, **kwargs) -> str:
        """
        Build the extraction prompt.
        
        Args:
            text: The source text to extract wisdom from
        
        Returns:
            str: The constructed prompt
        """
        return f"""Extract wisdom and insights from this text.

## Source Text
```
{text}
```

## Your Task
Analyze the text and extract:

1. **Summary** (2-3 sentences): What is this about?
2. **Key Ideas** (5-10 bullets): The core concepts and arguments
3. **Memorable Quotes** (3-5): Direct quotes worth saving, with context
4. **Actionable Insights** (3-5): Things the reader could do or apply
5. **Connections**: How does this relate to broader themes or other ideas?

## Output Format
Respond in clean markdown:

### Summary
[2-3 sentence summary]

### Key Ideas
- [idea 1]
- [idea 2]
- [etc.]

### Memorable Quotes
> "[quote 1]"
> — Context/speaker

> "[quote 2]"  
> — Context/speaker

### Actionable Insights
- [ ] [action 1]
- [ ] [action 2]
- [etc.]

### Connections
[How this relates to broader themes, other works, or areas of knowledge]
"""
