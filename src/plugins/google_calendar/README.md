# Google Calendar Plugin

This plugin provides integration with Google Calendar API to retrieve calendar events using service account credentials.

## Features

- **Domain-based credential lookup**: Automatically finds credentials based on email domain
- **Flexible date queries**: Get events for today, specific dates, or date ranges
- **Service account authentication**: Uses Google service accounts for secure, delegated access
- **Rich event data**: Returns comprehensive event information including attendees, location, descriptions

## Setup

### 1. Google Cloud Configuration

1. Create a Google Cloud project at https://console.cloud.google.com
2. Enable the Google Calendar API for your project
3. Create a service account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Give it a name (e.g., "calendar-reader")
   - Grant it appropriate roles (no special roles needed)
4. Create and download a JSON key:
   - Click on your service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key" > "JSON"
   - Save the downloaded file

### 2. Credential Storage

Place your service account JSON key in one of these locations (searched in order):

1. **Domain-specific** (recommended for organizations):
   ```
   ~/.google/credentials/{domain}/credentials.json
   ```
   Example: `~/.google/credentials/example.com/credentials.json`

2. **Email-specific**:
   ```
   ~/.google/credentials/{email}/credentials.json
   ```
   Example: `~/.google/credentials/user@example.com/credentials.json`

3. **Default**:
   ```
   ~/.google/credentials/credentials.json
   ```

### 3. Grant Calendar Access

The service account needs permission to read the calendar:

1. Open Google Calendar (calendar.google.com)
2. Find the calendar you want to access (or use your primary calendar)
3. Click the three dots next to it > "Settings and sharing"
4. Scroll to "Share with specific people"
5. Click "Add people"
6. Add the service account email (found in your JSON key file, looks like: `service-account-name@project-id.iam.gserviceaccount.com`)
7. Give it "See all event details" permission

### 4. Plugin Configuration

Copy the example config and customize:

```bash
cp src/plugins/google_calendar/config.yml.example src/plugins/google_calendar/config.yml
```

Edit `config.yml` to set default values:

```yaml
variables:
  accounts:
    - "you@example.com"
    - "other@example.com"
  max_results: 100
```

## Tasks

### get_calendar_events

Retrieve calendar events for one or more accounts for a specific date or date range.

**Parameters:**

- `accounts`: Email address(es) to get calendar for (single email or comma-separated list)
  - If not provided, uses accounts from config file
- `date`: Specific date to query (YYYY-MM-DD, defaults to today)
- `start_date`: Start date for range query (YYYY-MM-DD)
- `end_date`: End date for range query (YYYY-MM-DD)
- `days`: Number of days from start_date/date (alternative to end_date)
- `max_results`: Maximum number of events to return per account (default: 100)

**Usage Examples:**

```bash
# Get today's events for all accounts in config
pdm run python3 ./korben.py --task get_calendar_events

# Get events for a single account
pdm run python3 ./korben.py --task get_calendar_events --accounts "user@example.com"

# Get events for multiple accounts
pdm run python3 ./korben.py --task get_calendar_events --accounts "user1@example.com,user2@example.com"

# Get events for a specific date
pdm run python3 ./korben.py --task get_calendar_events --date "2025-11-05"

# Get events for a date range
pdm run python3 ./korben.py --task get_calendar_events --start_date "2025-11-01" --end_date "2025-11-07"

# Get events for the next 7 days
pdm run python3 ./korben.py --task get_calendar_events --days 7

# With custom max results per account
pdm run python3 ./korben.py --task get_calendar_events --days 30 --max_results 50
```

**Output:**

Returns a JSON object with:
- `start_date`: Start of date range
- `end_date`: End of date range
- `accounts`: Array of account results, each containing:
  - `account`: The calendar email queried
  - `count`: Number of events found for this account
  - `events`: Array of event objects for this account
- `total_accounts`: Total number of accounts queried
- `successful_accounts`: Number of accounts successfully queried
- `total_events`: Total number of events across all accounts
- `errors`: (optional) Array of error objects for failed accounts

Each event object contains:
- `id`: Unique event ID
- `title`: Event title/summary
- `description`: Event description
- `location`: Event location
- `start`: Formatted start time
- `end`: Formatted end time
- `is_all_day`: Boolean indicating if event is all-day
- `attendees`: List of attendees
- `organizer`: Event organizer information
- `status`: Event status
- `html_link`: Link to event in Google Calendar

## Library Usage

You can also use the library directly in your flows:

```python
from src.plugins.google_calendar.lib import GoogleCalendarService
from datetime import datetime, timezone, timedelta

# Initialize service for an email account
calendar = GoogleCalendarService("user@example.com")

# Get today's events
events = calendar.get_events_by_date()

# Get events for a specific date range
start = datetime(2025, 11, 1, tzinfo=timezone.utc)
end = datetime(2025, 11, 7, tzinfo=timezone.utc)
events = calendar.get_events_by_date(start_date=start, end_date=end)

# Process events
for event in events:
    print(f"{event['start']}: {event['title']}")
    if event['description']:
        print(f"  {event['description']}")

# For multiple accounts, iterate:
accounts = ["user1@example.com", "user2@example.com"]
for account in accounts:
    calendar = GoogleCalendarService(account)
    events = calendar.get_events_by_date()
    print(f"\nEvents for {account}:")
    for event in events:
        print(f"  {event['start']}: {event['title']}")
```

## Troubleshooting

### "No credentials found" error

Make sure your credentials file is in one of the expected locations and has the correct filename (`credentials.json`).

### "403 Forbidden" error

The service account hasn't been granted access to the calendar. Follow step 3 in the setup to share the calendar with the service account.

### "404 Not Found" error

The calendar ID (email) doesn't exist or isn't accessible. Double-check the email address.

### Events not showing up

- Verify the date range is correct
- Check that events exist in that date range in Google Calendar
- Ensure the service account has "See all event details" permission

## API Reference

See the Google Calendar API documentation for more details:
- https://developers.google.com/calendar/api/guides/overview
- https://developers.google.com/calendar/api/v3/reference/events

