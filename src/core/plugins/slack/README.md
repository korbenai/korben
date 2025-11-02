# Slack Plugin

Send notifications to Slack channels via incoming webhooks.

## Structure

```
slack/
├── __init__.py
├── tasks.py           # send_slack_hook
├── config.yml.example # Configuration template
└── README.md          # This file
```

## Tasks

- **send_slack_hook** - Send messages to Slack via webhook

## Requirements

### Environment Variables (Optional)

- **`SLACK_WEBHOOK_URL`** - Default Slack webhook URL
  - Create webhooks at: https://api.slack.com/messaging/webhooks

### Configuration File (Optional)

**Location:** `src/core/plugins/slack/config.yml`

```bash
cp src/core/plugins/slack/config.yml.example src/core/plugins/slack/config.yml
```

```yaml
variables:
  hook_name: "default"
  webhooks:
    default: "https://hooks.slack.com/services/YOUR/WEBHOOK"
    security: "https://hooks.slack.com/services/SECURITY/WEBHOOK"
    alerts: "https://hooks.slack.com/services/ALERTS/WEBHOOK"
```

## Usage

```bash
# Send to default webhook
pdm run python3 ./korben.py --task send_slack_hook \
  --message "Workflow completed!"

# Send to specific webhook
pdm run python3 ./korben.py --task send_slack_hook \
  --message "Security alert!" \
  --hook_name "security"

# Get help
pdm run python3 ./korben.py --task send_slack_hook --help
```

## Used By Other Plugins

- `mallory` - Optionally sends security stories to Slack

## Notes

- Supports multiple webhook configurations
- Simple text messages only
- Auto-registered via plugin system
- Config allows multiple named webhooks

