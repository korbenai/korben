# Email Plugin

Send HTML or plain text emails via Postmark API.

## Structure

```
email/
├── __init__.py
├── tasks.py           # send_email
├── lib.py             # Postmark email client
├── config.yml.example # Configuration template
└── README.md          # This file
```

## Tasks

- **send_email** - Send emails via Postmark API

## Requirements

### Environment Variables

- **`POSTMARK_API_KEY`** (required) - Your Postmark server API token
  - Get from: https://postmarkapp.com/
- **`PERSONAL_EMAIL`** (optional) - Default sender and recipient

### Configuration File (Optional)

**Location:** `src/core/plugins/email/config.yml`

```bash
cp src/core/plugins/email/config.yml.example src/core/plugins/email/config.yml
```

```yaml
variables:
  recipient: "you@example.com"  # Default recipient
```

## Usage

```bash
# Send email with defaults
pdm run python3 ./korben.py --task send_email \
  --subject "Test" \
  --content "Hello from Korben!"

# Send HTML email
pdm run python3 ./korben.py --task send_email \
  --recipient "you@example.com" \
  --subject "Report" \
  --content "<h1>HTML Content</h1><p>Rich formatting</p>"

# Get help
pdm run python3 ./korben.py --task send_email --help
```

## Used By Other Plugins

All workflow plugins use this for email delivery:
- `movies` - Email movie recommendations
- `books` - Email book recommendations
- `mallory` - Email security stories
- `podcasts` - Email podcast wisdom

## Notes

- Supports HTML and plain text
- Postmark provides excellent deliverability
- Used as building block in workflows
- Auto-registered via plugin system

