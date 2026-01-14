# src/plugins/obsidian/agents.py
"""
Obsidian plugin agents - AI agents for wiki interaction.
"""

from src.agents.base import BaseAgent


class ObsidianDailySummaryAgent(BaseAgent):
    """
    Agent that summarizes daily notes and suggests tomorrow's priorities.
    
    Example:
        agent = ObsidianDailySummaryAgent()
        summary = agent.run(
            date="2026-01-14",
            daily_note_content="## Completed\n- Task 1\n- Task 2",
            backlog_content="## Next\n- Priority item"
        )
    """
    
    name = "ObsidianDailySummaryAgent"
    temperature = 0.5  # Slightly lower for more focused summaries
    
    system_prompt = """You are a productivity assistant helping summarize daily work and plan ahead.

Your role is to:
1. Identify completed work from daily notes
2. Surface high-priority items from the backlog
3. Notice patterns and provide actionable observations

Be concise but thorough. Focus on what matters most."""

    def build_prompt(
        self,
        date: str,
        daily_note_content: str,
        backlog_content: str,
        **kwargs
    ) -> str:
        """
        Build the summary prompt from wiki content.
        
        Args:
            date: The date being summarized (YYYY-MM-DD)
            daily_note_content: Content from the daily note file
            backlog_content: Content from the backlog file
        
        Returns:
            str: The constructed prompt
        """
        return f"""Please generate a daily summary for {date}.

## Daily Note Content
```markdown
{daily_note_content}
```

## Backlog Content  
```markdown
{backlog_content}
```

## Your Task
1. **Work Accomplished**: Summarize 3-5 key accomplishments from the "Completed" section of the daily note.
2. **Suggested Priorities for Tomorrow**: Identify 5-7 prioritized items from:
   - Remaining incomplete tasks from today
   - "Next (prioritized top to bottom)" section of backlog
   - "Needs Prioritization" section if relevant
3. **Observations**: Note any patterns (backlog growth, meeting load, recurring blockers, notable progress).

## Output Format
Respond with a clean markdown summary:

### Daily Summary - {date}

#### ✅ Work Accomplished
- [accomplishment 1]
- [accomplishment 2]
- [etc.]

#### 🎯 Suggested Priorities for Tomorrow
- [priority 1 - why it matters]
- [priority 2 - why it matters]
- [etc.]

#### 💡 Observations
- [observation about patterns, blockers, or progress]
"""
