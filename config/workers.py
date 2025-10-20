"""Worker configuration - maps tasks to workers (future expansion)."""

# Worker pool definitions (for future GPU/specialized workers)
WORKER_POOLS = {
    "default": {
        "type": "process",
        "description": "Default worker pool for all tasks",
        "concurrency": 4,
    },
    # Future expansion:
    # "gpu-workers": {
    #     "type": "process",
    #     "description": "GPU-enabled workers for transcription",
    #     "concurrency": 1,
    # },
}

# Task configurations (stub for now, all use default pool)
TASK_WORKER_CONFIG = {
    "download_podcasts": {
        "pool": "default",
        "tags": ["podcasts", "io"],
        "retries": 3,
    },
    "transcribe_podcasts": {
        "pool": "default",  # Future: "gpu-workers"
        "tags": ["podcasts", "whisper", "cpu-intensive"],
        "retries": 2,
        "timeout_seconds": 3600,
    },
    "extract_wisdom": {
        "pool": "default",
        "tags": ["ai", "controlflow"],
        "retries": 2,
    },
    "send_email": {
        "pool": "default",
        "tags": ["io", "network"],
        "retries": 3,
    },
    "read_file": {
        "pool": "default",
        "tags": ["io"],
    },
    "write_file": {
        "pool": "default",
        "tags": ["io"],
    },
    "cybernews": {
        "pool": "default",
        "tags": ["ai", "network"],
    },
}

# Flow configurations
FLOW_WORKER_CONFIG = {
    "podcasts": {
        "pool": "default",
        "tags": ["workflow", "podcasts"],
    },
}


def get_task_config(task_name):
    """Get worker configuration for a task."""
    return TASK_WORKER_CONFIG.get(task_name, {
        "pool": "default",
        "tags": [],
    })


def get_flow_config(flow_name):
    """Get worker configuration for a flow."""
    return FLOW_WORKER_CONFIG.get(flow_name, {
        "pool": "default",
        "tags": [],
    })

