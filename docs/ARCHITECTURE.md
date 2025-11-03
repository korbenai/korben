# Architecture

Korben is a small, plugin‑first Python application with two runtime modes:

- Local CLI (default): run tasks and flows directly.
- Prefect worker: run scheduled or on‑demand runs orchestrated by Prefect Cloud.

## Project Structure (high‑level)

```
korben/
├── korben.py                  # CLI entrypoint (tasks/flows via registry)
├── korben.sh                  # Recommended launcher (local/worker modes)
├── deployments/               # Prefect deployment code & docs
│   ├── cloud_all.py           # Deploy all/single flows (schedules, env)
│   └── README.md              # How to deploy & run workers
├── config/                    # Core & plugin configs (local only)
├── src/
│   ├── registry.py            # Auto‑discovery of tasks/flows from plugins
│   ├── lib/                   # Shared core utilities (config, helpers)
│   └── plugins/               # Self‑contained plugin modules
│       ├── <plugin>/
│       │   ├── tasks.py       # Public functions → tasks
│       │   ├── flows.py       # @cf.flow functions → flows
│       │   ├── lib.py         # Plugin helpers
│       │   ├── config.yml(.example)
│       │   └── README.md
└── docs/
    ├── ARCHITECTURE.md        # This document
    └── PLUGINS.md             # Plugin system details & conventions
```

## Runtime Overview

1. korben.sh (local)
   - Launches `korben.py` (suppresses noisy warnings)
   - `--` separator passes all args to `korben.py`
2. korben.sh (worker)
   - Starts a Prefect process worker in a given work pool
   - Prefect Cloud “Quick run” / schedules submit flow runs to the worker

## Registry & Auto‑Discovery

- `src/registry.py` imports `tasks.py` and `flows.py` from each directory under `src/plugins/`.
- Public functions in `tasks.py` are registered as tasks.
- Public functions in `flows.py` are registered as flows.
- Flow names ending in `_workflow` have the suffix removed for a clean CLI name.
- Plugins can declare `__dependencies__` if they require other plugins; registry disables a plugin if dependencies are missing.

## Deployments (Prefect 3)

- `deployments/cloud_all.py` builds deployments from source using `flow.from_source(...).deploy(...)`.
- Deployments set:
  - work pool: `default-pool`
  - work queue: `default`
  - job variables: `working_dir` (project root) and `env.PYTHONPATH` (project root)
  - optional schedules per flow (cron + timezone)
- A local worker must be online for runs to execute.

See `deployments/README.md` for how to deploy and run a worker.

## Configuration & Secrets

- Local only; load env from your shell (e.g., `.zshrc`) and plugin `config.yml` files.
- Do not commit secrets.
- A small, optional allowlist can be forwarded via deployment `job_variables.env` if needed for the worker subprocess.

## Notes on Heavy Dependencies

- Some plugins (e.g., podcasts/Whisper) require `torch`. Use Python 3.13 for current arm64 wheels.
- Prefer lazy imports inside task bodies for heavy libs so plugin discovery doesn’t fail when the lib isn’t present.

