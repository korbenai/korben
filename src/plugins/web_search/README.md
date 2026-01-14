# Search Plugin

Tavily-backed web search tasks.

## Setup

1) Install dependency:

```bash
pdm install
```

2) Provide your Tavily API key (preferred via env var):

```bash
export TAVILY_API_KEY="sk-..."
```

Or copy the example and edit:

```bash
cp src/plugins/web_search/config.yml.example src/plugins/web_search/config.yml
```

Note: If both config and the environment variable are set, the config value takes precedence.

## Task

- `web_search` — Search the web and return a Markdown summary with sources.

### Usage

```bash
pdm run python3 ./korben.py --task web_search --query "latest AI agent frameworks" --max_results 5
```

### Parameters

- `query` (str, required): Search query
- `max_results` (int, default 5)
- `search_depth` (str, default "basic"): "basic" or "advanced"
- `include_answer` (bool, default true)
- `include_raw_content` (bool, default false)


