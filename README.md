# 🚀 queuectl – Redis‑Backed Background Job Queue (CLI Tool)

`queuectl` is a lightweight, CLI‑based background job queue system inspired by BullMQ, RQ, and Celery — built entirely in Python with Redis for persistence.

It supports:

* Background job execution
* Multiple worker processes
* Automatic retries with exponential backoff
* Delayed jobs using Redis ZSET scheduling
* Dead Letter Queue (DLQ)
* Durable Redis‑based storage
* A clean CLI interface (`queuectl` command)

---

## 📦 Features

### ✔ Background Jobs

Enqueue shell commands as jobs via CLI.

### ✔ Multi‑Process Workers

Run one or more workers that process jobs concurrently.

### ✔ Redis Storage

All jobs, states, and metadata stored using Redis:

* LIST → pending queue
* ZSET → delayed jobs
* LIST → DLQ
* HASH → job details

### ✔ Automatic Retries

Failed jobs retry with exponential backoff:
`delay = backoff_base ** attempts`

### ✔ Delayed Jobs & Scheduler

Scheduler moves jobs from delayed queue → pending when `run_at` is reached.

### ✔ Dead Letter Queue

After `max_retries`, jobs move to DLQ.

### ✔ Configurable

* `max_retries`
* `backoff_base`
* Other settings stored in config.

---

## 📁 Project Structure

```
queuectl/
│
├── pyproject.toml
│
└── queuectl/
    ├── __init__.py
    ├── main.py                # CLI entrypoint
    ├── cli.py                 # Argument parsing and commands
    ├── storage.py             # Redis job storage & state management
    ├── worker.py              # Worker manager + worker processes
    ├── scheduler.py           # Delayed jobs scheduler
    ├── redisConnection.py     # Redis client wrapper
    ├── config.py              # Configuration handler
    ├── models.py              # Job dataclass
    ├── jobState.py            # State constants
    ├── dlq.py                 # Dead letter queue handling
    └── data/                  # Runtime data (optional)
```

---

## 🛠 Installation

### 1. Install Redis

Make sure Redis is running locally:

```
redis-server
```

### 2. Install queuectl in editable mode

Navigate to the project root:

```
pip install -e .
```

This adds the `queuectl` CLI globally.

---

## 🧪 Quickstart

### ▶ Enqueue a Job

```
queuectl enqueue --command 'echo hello'
```

### ▶ View Jobs

```
queuectl list
queuectl list --state PENDING
queuectl list --state COMPLETED
```

### ▶ Start Workers

```
queuectl worker start --count 3
```

### ▶ Stop Workers

```
queuectl worker stop
```

---

## 🔁 Retry Logic

Jobs retry automatically using exponential backoff:

| Attempt | Delay |
| ------- | ----- |
| 1       | 2s    |
| 2       | 4s    |
| 3       | 8s    |

Configurable via:

```
queuectl config set backoff_base 3
queuectl config set max_retries 5
```

---

## ⏳ Delayed & Scheduled Jobs

Failed jobs or jobs scheduled for later execution go into:

```
queuectl:queue:delayed
```

Scheduler periodically moves ready jobs → pending.

Start scheduler automatically with workers or run separately.

---

## 💀 Dead Letter Queue

Jobs exceeding retry limit move to DLQ.

### View DLQ

```
queuectl dlq list
```

### Retry a DLQ job

```
queuectl dlq retry <job_id>
```

---

## ⚙️ Configuration

```
queuectl config set max_retries 5
queuectl config set backoff_base 3
```

Stored typically in:

```
queuectl/data/config.json
```

---

## 🧩 Developer Guide

### Run Tests

Create your tests inside a `tests/` folder and run:

```
pytest
```

### Code Style

Use any formatter like Black or Ruff.

---

## 🤝 Contributing

Pull requests welcomed! You can contribute by:

* Fixing bugs
* Adding features (job timeouts, priority queues, dashboard)
* Improving documentation

---

## 📜 License

MIT License

---

## ⭐ Support

If you found this project useful, give it a ⭐ on GitHub!
