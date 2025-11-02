# Linear Plugin

The Linear plugin allows Korben to fetch and manage Linear tickets/issues based on configuration.

## Features

- Fetch tickets assigned to specific users
- Filter by workflow status (Todo, In Progress, etc.)
- Save tickets as JSON for further processing
- List all available workflow states
- GraphQL API integration with Linear

## Setup

### 1. Get your Linear API Key

1. Go to https://linear.app/settings/api
2. Create a new Personal API Key
3. Copy the key

### 2. Configure the Plugin

```bash
# Copy the example config
cp src/plugins/linear/config.yml.example src/plugins/linear/config.yml

# Edit the config file
# Set your API key and username
```

### 3. Configuration Options

```yaml
# Your Linear API key (or set LINEAR_API_KEY env var)
api_key: "lin_api_xxxxxxxxxxxxx"

# Your username (displayName, name, or email prefix)
username: "jcran"

# Statuses to fetch (comma-separated)
statuses: "In Progress,Todo"
```

## Usage

### Fetch Tickets

Fetch tickets based on your configuration:

```bash
# Using the configured settings
korben.py --task get_linear_tickets

# Override username
korben.py --task get_linear_tickets --username "different_user"

# Override statuses
korben.py --task get_linear_tickets --statuses "Blocked,In Review"

# Save to custom location
korben.py --task get_linear_tickets --output_file "/path/to/tickets.json"
```

### List Available Statuses

See all available workflow states in your Linear workspace:

```bash
korben.py --task list_linear_states
```

## Output Format

Tickets are saved as JSON with the following structure:

```json
[
  {
    "id": "issue-id",
    "identifier": "ENG-123",
    "name": "Issue title",
    "description": "Issue description in markdown",
    "status": "In Progress",
    "url": "https://linear.app/...",
    "priority": 1,
    "labels": ["bug", "high-priority"],
    "team": "Engineering",
    "project": "Q4 Goals",
    "dueDate": "2025-11-15",
    "createdAt": "2025-10-01T10:00:00.000Z",
    "updatedAt": "2025-11-02T15:30:00.000Z"
  }
]
```

## Common Statuses

Common workflow states in Linear:
- **Todo** - Not started
- **In Progress** - Currently being worked on
- **In Review** - Under review
- **Done** - Completed
- **Canceled** - Canceled/won't do
- **Backlog** - Planned for later

Use `list_linear_states` to see your workspace's specific states.

## Integration with Flows

You can integrate Linear ticket fetching into Prefect flows:

```python
from src.plugins.linear.tasks import get_linear_tickets

@flow(name="daily-sync")
def daily_sync():
    # Fetch current tickets
    get_linear_tickets()
    
    # Do something with the tickets
    # ... your logic here ...
```

## Troubleshooting

### "LINEAR_API_KEY not found"
- Make sure you've set the API key in `config.yml` OR
- Set the `LINEAR_API_KEY` environment variable

### "User not found"
- Check that the username matches your Linear displayName, name, or email
- Try using your full email address instead

### "No matching workflow states"
- Run `list_linear_states` to see available states
- Check for typos in status names (case-sensitive)
- Some teams may have custom workflow states

## API Rate Limits

Linear's API has rate limits:
- 5,000 requests per hour per API key
- 50 requests per 10 seconds per API key

The plugin makes 3 API calls per execution:
1. Fetch users
2. Fetch workflow states  
3. Fetch issues

## Links

- [Linear API Documentation](https://developers.linear.app/docs)
- [Linear GraphQL API](https://developers.linear.app/docs/graphql/working-with-the-graphql-api)
- [Create API Keys](https://linear.app/settings/api)

