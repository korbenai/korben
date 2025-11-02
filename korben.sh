#!/bin/bash
# Wrapper script to run korben.py with warnings suppressed
# Suppresses pydantic warnings from controlflow dependency

export PYTHONWARNINGS="ignore::UserWarning,ignore::Warning"

# Run korben.py with all passed arguments
pdm run python3 "$(dirname "$0")/korben.py" "$@"

