# Plugins

Korben is plugin‑first: each capability lives in a self‑contained module under `src/plugins/`.

## Structure

```
src/plugins/<name>/
├── __init__.py              # plugin marker
├── tasks.py                 # public functions → tasks
├── flows.py                 # workflow functions → flows
├── lib.py                   # helpers (optional)
├── config.yml(.example)     # plugin config (optional)
└── README.md                # plugin docs
```

## Auto‑Registration

The registry scans all subdirectories of `src/plugins/` and imports `tasks.py` and `flows.py`:

- All public functions in `tasks.py` are registered as tasks.
- All public functions in `flows.py` are registered as flows.
- Flow names ending with `_workflow` have the suffix removed (e.g., `process_podcasts_workflow` → `process_podcasts`).
- Functions prefixed with `_` are treated as private and not registered.
- Plugins may expose `__dependencies__` (list/tuple of plugin names). Missing dependencies disable the plugin (with a warning) to avoid runtime errors.

## Conventions

- Keep heavy imports (e.g., `torch`, `whisper`) lazy inside task bodies to avoid import errors during discovery.
- Keep plugin state and configuration in the plugin directory; configs should have an `.example` checked in and a local `.yml` ignored by VCS.
- Flows are composed from tasks; flows should be declarative and idempotent where possible.
- For AI-powered tasks, use centralized agents from `src/agents/` or the base LLM helper: `from src.agents.base import get_llm`

## Example: minimal plugin

```python
# src/plugins/weather/tasks.py

def get_forecast(**kwargs):
    location = kwargs.get("location", "San Francisco")
    return f"Weather for {location}: Sunny, 75°F"
```

```python
# src/plugins/weather/flows.py
from src.plugins.weather import tasks as weather_tasks

def daily_weather_workflow(**kwargs):
    return weather_tasks.get_forecast(**kwargs)
```

Registered names:
- Task: `get_forecast`
- Flow: `daily_weather`

## AI-Powered Tasks

For tasks that need AI capabilities, use centralized agents or the LangChain LLM helper:

### Using a Centralized Agent

```python
# src/plugins/obsidian/tasks.py
from src.agents.daily_summary import DailySummaryAgent

def generate_daily_summary(**kwargs):
    agent = DailySummaryAgent()
    return agent.run(
        date="2026-01-14",
        daily_note_content="...",
        backlog_content="..."
    )
```

### Using the LLM Directly

```python
# src/plugins/analyzer/tasks.py
from src.agents.base import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

def analyze_text(**kwargs):
    text = kwargs.get('text', '')
    
    llm = get_llm()
    messages = [
        SystemMessage(content="You are a helpful analyst."),
        HumanMessage(content=f"Analyze this text: {text}"),
    ]
    response = llm.invoke(messages)
    
    return response.content
```

## Agents Directory

Centralized agents live in `src/agents/`:

```
src/agents/
├── __init__.py
├── base.py               # BaseAgent class + get_llm() helper
├── daily_summary.py      # DailySummaryAgent
└── wisdom_extractor.py   # WisdomExtractorAgent
```

Create new agents by subclassing `BaseAgent`:

```python
from src.agents.base import BaseAgent

class MyAgent(BaseAgent):
    name = "MyAgent"
    system_prompt = "You are a helpful assistant..."
    
    def build_prompt(self, **kwargs) -> str:
        return f"Do something with {kwargs['input']}"
```

## Per‑Plugin Docs

Each plugin includes its own `README.md` with usage, parameters, and examples:
- Podcasts: `src/plugins/podcasts/README.md`
- Obsidian: `src/plugins/obsidian/README.md`
- Mallory: `src/plugins/mallory/README.md`
- Movies: `src/plugins/movies/README.md`
- Books: `src/plugins/books/README.md`
- arXiv: `src/plugins/arxiv/README.md`
- GitHub: `src/plugins/github/README.md`
- Linear: `src/plugins/linear/README.md`
- Google Calendar: `src/plugins/google_calendar/README.md`
- AWS S3: `src/plugins/aws_s3/README.md`
- Share File: `src/plugins/share_file/README.md`
- Email: `src/plugins/email/README.md`
- Slack: `src/plugins/slack/README.md`
- Utilities: `src/plugins/utilities/README.md`
- Eater: `src/plugins/eater/README.md`
