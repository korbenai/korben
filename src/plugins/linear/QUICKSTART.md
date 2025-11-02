# Linear Plugin - Quick Start Guide

Get up and running with the Linear plugin in 5 minutes.

## Prerequisites

- Linear account with API access
- Python environment with required dependencies

## Setup Steps

### 1. Get Your Linear API Key

```bash
# Open Linear API settings
open https://linear.app/settings/api
```

Create a new Personal API Key and copy it.

### 2. Configure the Plugin

```bash
# Navigate to the plugin directory
cd src/plugins/linear

# Copy the example config
cp config.yml.example config.yml

# Edit the config file (use your preferred editor)
nano config.yml
```

Set your configuration:

```yaml
# Paste your API key
api_key: "lin_api_YOUR_KEY_HERE"

# Set your username (your Linear display name, username, or email)
username: "jcran"

# Set which statuses to fetch
statuses: "In Progress,Todo"
```

### 3. Test the Plugin

```bash
# Return to the korben root directory
cd ../../..

# List available Linear workflow states
pdm run python3 ./korben.py --task list_linear_states

# Fetch your tickets
pdm run python3 ./korben.py --task get_linear_tickets
```

### 4. View Your Tickets

The tickets are saved as JSON in your data directory:

```bash
# View the tickets file
cat data/linear/tickets.json | python3 -m json.tool

# Or use jq for pretty output
cat data/linear/tickets.json | jq '.[] | {identifier, name, status}'
```

## Common Commands

### Fetch Tickets (Default Config)

```bash
pdm run python3 ./korben.py --task get_linear_tickets
```

### Fetch for Different User

```bash
pdm run python3 ./korben.py --task get_linear_tickets --username "other_user"
```

### Fetch Different Statuses

```bash
pdm run python3 ./korben.py --task get_linear_tickets --statuses "Blocked,In Review"
```

### Use the Sync Workflow

```bash
# Run the complete sync workflow
pdm run python3 ./korben.py --flow linear_sync

# Run daily report workflow  
pdm run python3 ./korben.py --flow linear_daily_report
```

### Schedule Daily Sync

You can schedule the Linear sync to run daily using Prefect. See the main Korben documentation for scheduling instructions.

## Troubleshooting

### "LINEAR_API_KEY not found"

Make sure you've:
1. Created `config.yml` from `config.yml.example`
2. Added your API key to the config file
3. Or set the `LINEAR_API_KEY` environment variable

### "User not found"

Try using:
- Your Linear display name (what shows in the UI)
- Your Linear username (from your profile URL)
- Your email address

### "No matching workflow states"

Run `list_linear_states` to see all available states in your workspace. Note that state names are case-sensitive.

## Next Steps

- Integrate with email plugin to send daily ticket reports
- Integrate with Slack plugin to post updates
- Create custom workflows combining Linear with other plugins
- Schedule automated ticket syncs with Prefect

## Examples

### Daily Morning Ticket Report

Create a flow that fetches your tickets and emails you a summary:

```bash
pdm run python3 ./korben.py --flow linear_daily_report --send_email true
```

### Combine with Other Plugins

The Linear plugin can be combined with other Korben plugins:

```python
# In your custom flow
@cf.flow
def my_workflow():
    # Fetch Linear tickets
    linear_tasks.get_linear_tickets()
    
    # Load and process tickets
    # ... your logic ...
    
    # Send via email
    email_tasks.send_email(subject="...", content="...")
```

## Support

- See [README.md](README.md) for full documentation
- Check Linear API docs: https://developers.linear.app/docs
- Review example flows in `flows.py`

