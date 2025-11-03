# Deployments (Prefect 3)

Minimal guide to deploy, run, and monitor Korben flows with Prefect Cloud.

## Prerequisites

```bash
pdm install                   # installs dependencies into .venv
prefect cloud login           # authenticate to Prefect Cloud
prefect work-pool create default-pool --type process   # once per workspace
```

## Deploy

```bash
# Deploy all flows with default schedules (6am CT, weekly where noted)
.venv/bin/python deployments/cloud_all.py

# Deploy a single flow
.venv/bin/python deployments/cloud_all.py --flow mallory

# Override schedule
.venv/bin/python deployments/cloud_all.py --schedule "0 8 * * *" --timezone "America/Los_Angeles"

# No schedules (manual only)
.venv/bin/python deployments/cloud_all.py --no-schedule
```

Notes:
- Deployments set `working_dir` and `PYTHONPATH` so code loads correctly on the worker.
- Work pool: `default-pool`; work queue: `default`.

## Run

Start a worker on the machine that should execute flows:

```bash
# Recommended: verbose logs while testing
PREFECT_LOGGING_LEVEL=DEBUG .venv/bin/prefect worker start --pool default-pool
```

Trigger runs:

```bash
# From the Prefect UI: open the deployment → Quick run

# Or via CLI
.venv/bin/prefect deployment run 'mallory-trending-stories-workflow/default'
```

## Troubleshooting

- Run is Pending
  - Ensure a worker is online in `default-pool` and same workspace/profile
  - Use the scheduled deployment’s Quick run (creates a run at now)
  - Check worker logs: `/tmp/prefect-worker.log` or run with `PREFECT_LOGGING_LEVEL=DEBUG`

- Import/path errors
  - Redeploy; deployments set `job_variables.working_dir` and `env.PYTHONPATH`

- Env vars
  - The worker must inherit any required API keys (e.g., via your shell profile)

## Monitoring

Prefect Cloud: https://app.prefect.cloud — view deployments, runs, logs, and schedules.