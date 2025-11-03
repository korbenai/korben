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

## Simple CLI (recommended)

Use the korben.sh launcher as the primary entrypoint. It responds in `--mode local` by default, so no need to specify it. 

```bash
# List available tasks and flows
./korben.sh --list

# Run flows locally
./korben.sh --flow mallory_trending_stories --limit 10
./korben.sh --flow arxiv_search --query "cat:cs.AI" --max_results 5
./korben.sh --flow trending_movies --genres "sci-fi,action"
```

If you want to run with prefect cloud, you'll want to start a worker, you can use the korben.sh launcher to do this as well. 

```bash
# Start a Prefect worker (so Prefect Cloud Quick run works immediately)
./korben.sh --mode worker            # uses default-pool
# Or choose a different work pool
./korben.sh --mode worker --pool my-pool
```

Notes:
- `--` separates launcher flags from arguments passed to `korben.py`.
- The worker keeps a Prefect process worker online to run scheduled/Quick runs.

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

## Deployments (Prefect)

See `deployments/README.md` for deploying, running workers, and using Prefect Cloud Quick run.
