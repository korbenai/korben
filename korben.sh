#!/bin/bash
# korben launcher
# Modes:
#   --mode local  (default)  → run korben.py
#   --mode worker           → start Prefect worker (process) in default-pool

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Defaults
MODE="local"
POOL="default-pool"
ARGS=()
PASSTHROUGH=0

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode=*) MODE="${1#*=}"; shift ;;
    --mode)   MODE="${2:-local}"; shift 2 ;;
    --pool=*) POOL="${1#*=}"; shift ;;
    --pool)   POOL="${2:-default-pool}"; shift 2 ;;
    -h|--help)
      if [[ $PASSTHROUGH -eq 1 ]]; then
        ARGS+=("$1"); shift; continue
      fi
      cat <<EOF
Usage: korben.sh [--mode local|worker] [--pool POOL] [-- ...args]

Examples:
  # Run locally (default)
  ./korben.sh -- --flow mallory_trending_stories --limit 10

  # Start Prefect worker in default pool
  ./korben.sh --mode worker

  # Start worker in a different pool
  ./korben.sh --mode worker --pool my-pool
EOF
      exit 0
      ;;
    --) shift; ARGS+=("$@"); break ;;
    *)  PASSTHROUGH=1; ARGS+=("$1"); shift ;;
  esac
done

# Suppress noisy warnings by default
export PYTHONWARNINGS="ignore::UserWarning,ignore::Warning"

if [[ "$MODE" == "worker" ]]; then
  # Start Prefect worker using project environment
  # TIP: set PREFECT_LOGGING_LEVEL=DEBUG to increase verbosity
  exec pdm run prefect worker start --pool "$POOL"
else
  # Run korben CLI locally
  if (( ${#ARGS[@]:-0} > 0 )); then
    exec pdm run python3 "$SCRIPT_DIR/korben.py" "${ARGS[@]}"
  else
    exec pdm run python3 "$SCRIPT_DIR/korben.py"
  fi
fi

