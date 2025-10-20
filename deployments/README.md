# Prefect Cloud Deployments

Scripts for deploying workflows to Prefect Cloud.

## Setup

### 1. Install Prefect

```bash
pdm install  # Installs prefect dependency
```

### 2. Login to Prefect Cloud

```bash
prefect cloud login
```

Follow the prompts to authenticate with your Prefect Cloud account (free tier available).

### 3. Create Work Pool

```bash
prefect work-pool create default-pool --type process
```

## Deploy Workflow

### Deploy to Prefect Cloud

```bash
python deployments/prefect_cloud.py
```

This pushes the podcast workflow metadata to Prefect Cloud with:
- Daily schedule (6:00 AM PST)
- Tags for organization
- Work pool assignment

### Start Worker

On the machine where you want to run the workflow:

```bash
prefect worker start --pool default-pool
```

The worker:
- Connects to Prefect Cloud
- Pulls scheduled runs
- Executes using your local code
- Reports status back to cloud

### Trigger Manual Run

```bash
# Via CLI
prefect deployment run 'podcasts-workflow/daily-podcasts'

# Or use Prefect Cloud UI
# Visit https://app.prefect.cloud
```

## Run Locally (Without Prefect)

If you want to run without Prefect orchestration:

```bash
# Option 1: Using run.py
pdm run python3 ./run.py --flow podcasts

# Option 2: Direct execution
python deployments/run_local.py
```

## Configuration

Worker configuration is defined in `config/workers.py`:
- Work pool definitions
- Task-to-worker mappings
- Tags for routing
- Retry policies

Currently all tasks use the `default` pool. In the future, you can:
- Add GPU worker pool for transcription
- Add specialized workers for different tasks
- Update `config/workers.py` to route tasks accordingly

## Monitoring

View workflow runs in Prefect Cloud:
1. Visit https://app.prefect.cloud
2. Navigate to Flows → podcasts-workflow
3. View run history, logs, and schedules

## Troubleshooting

### Worker not picking up runs
- Ensure worker is started: `prefect worker start --pool default-pool`
- Check worker is connected in Prefect Cloud UI
- Verify work pool name matches deployment

### Runs failing
- Check logs in Prefect Cloud UI
- Verify environment variables are set (`PERSONAL_EMAIL`, `POSTMARK_API_KEY`)
- Ensure `config/podcasts.yml` exists

### No runs scheduled
- Check deployment schedule in Prefect Cloud UI
- Verify timezone is correct
- Manually trigger a test run first

