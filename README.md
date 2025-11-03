# Korben

Hackable personal automation framework built on ControlFlow and Prefect. Batteries included, plugin-first.

## Capabilities

- Utilities: file I/O, markdown ↔ HTML, email, Slack
- Podcasts: download, transcribe (Whisper), extract wisdom, email
- Mallory: fetch and summarize cybersecurity stories
- Movies: discover popular movies by genre and filters (TMDB)
- Books: search ISBNdb, fetch details
- arXiv: search papers; email/Slack results
- GitHub: create gists (file or directory)
- Linear: tickets, status report
- Google Calendar: list events across accounts
- AWS S3: buckets and file operations
- Share File: quick public links via temporary S3 buckets

## Getting Started

```bash
# 1) Install dependencies
pdm install

# 2) List available tasks and flows
./korben.sh --list

# 3) Run an individual task
./korben.sh --task send_email --subject "Your subject here" --content "Your content here" --email user@mail.com

# 4) Run a mult-step flow locally,.. this will: 
#  i) fetch cybersecurity stories from mallory.ai, 
#  ii) analyze them with an ai agent, 
#  iii) and email / slack them to configured addresses
./korben.sh --flow mallory_trending_stories --limit 10
```

## Plugin Docs

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

## Cloud Deployments (Optional, powered by Prefect)

If you want to run with prefect cloud, you'll want to start a worker, you can use the korben.sh launcher to do this as well. 

See `deployments/README.md` for deploying, running workers, and using Prefect Cloud Quick run.

The worker keeps a worker online to run scheduled/Quick runs for cloud 

```bash
# Start a Prefect worker (so Prefect Cloud Quick run works immediately)
./korben.sh --mode worker            # uses default-pool
# Or choose a different work pool
./korben.sh --mode worker --pool my-pool
```
