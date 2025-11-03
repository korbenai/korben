# Plugins

Korben is plugin‑first: each capability lives in a self‑contained module under `src/plugins/`.

## Structure

```
src/plugins/<name>/
├── __init__.py              # plugin marker
├── tasks.py                 # public functions → tasks
├── flows.py                 # @cf.flow functions → flows
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

## Example: minimal plugin

```python
# src/plugins/weather/tasks.py

def get_forecast(**kwargs):
    location = kwargs.get("location", "San Francisco")
    return f"Weather for {location}: Sunny, 75°F"
```

```python
# src/plugins/weather/flows.py
import controlflow as cf
from src.plugins.weather import tasks as weather_tasks

@cf.flow
def daily_weather_workflow(**kwargs):
    return weather_tasks.get_forecast(**kwargs)
```

Registered names:
- Task: `get_forecast`
- Flow: `daily_weather`

## Per‑Plugin Docs

Each plugin includes its own `README.md` with usage, parameters, and examples:
- Podcasts: `src/plugins/podcasts/README.md`
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

