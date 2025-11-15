# 🚀 queuectl – Redis‑Backed Background Job Queue (CLI Tool)

`queuectl` is a lightweight, CLI‑based background job queue system inspired by **BullMQ**, **RQ**, and **Celery** — built entirely in **Python** with **Redis** for persistence.

It provides a simple CLI workflow while supporting advanced background job processing features.

---

## 📦 Features

### ✔ Background Jobs

Enqueue and execute shell commands as jobs via a clean CLI.

### ✔ Multi‑Process Workers

Scale by running multiple workers in parallel.

### ✔ Redis Storage

All job metadata and queue state are stored in Redis:

* **LIST** → pending queue
* **ZSET** → delayed jobs
* **LIST** → DLQ (dead letter queue)
* **HASH** → job metadata

### ✔ Automatic Retries

Failed jobs retry using exponential backoff:

```
delay = backoff_base ** attempts
```

### ✔ Delayed Jobs & Scheduler

Delayed jobs are stored in a Redis ZSET and moved back to pending when `run_at` is reached.

### ✔ Dead Letter Queue

After exceeding `max_retries`, jobs move to DLQ.

### ✔ Configurable

Settings include:

* `max_retries`
* `backoff_base`
* And more via configuration API.

---

## 📁 Project Structure

The project is organized into three major components:

### **1. queuectl/** — Core Queue Engine (Python + Redis)

Contains everything related to the queueing system: workers, scheduler, storage, CLI, and Redis integration.

```
queuectl/
│
├── pyproject.toml
│
└── queuectl/
    ├── __init__.py
    ├── main.py                # CLI entrypoint (queuectl command)
    ├── cli.py                 # Command parsing & routing
    ├── storage.py             # Redis job storage & transitions
    ├── worker.py              # Worker processes & manager
    ├── scheduler.py           # Delayed job scheduler
    ├── redisConnection.py     # Redis connection wrapper
    ├── config.py              # Global configuration handler
    ├── models.py              # Job dataclass
    ├── jobState.py            # Job state constants
    ├── dlq.py                 # Dead Letter Queue operations
    └── data/                  # Runtime config + metadata
```

---

### **2. server/** — FastAPI Monitoring Backend

This module provides APIs for the dashboard and external integrations.
It reads data only from Redis (no direct connection to workers).

```
server/
│
└── app.py                    # FastAPI server
```

**Responsibilities:**

* Serve job lists (pending, processing, completed, dead)
* Serve metrics/summary (`/stats`)
* Track worker processes
* Provide DLQ operations
* Act as backend for the React dashboard

---

### **3. web-dashboard/** — React Dashboard (Queue Monitoring UI)

A modern dashboard for real‑time visibility into queue status.

```
web-dashboard/
│
├── src/
│   ├── components/
├── public/
└── package.json
```

**Dashboard provides:**

* Overview cards (Pending, Processing, Completed, Dead)
* Worker list with PID, start time, live status
* Job list with filters (state-wise)
* Auto-refresh and manual refresh
* Color-coded job states (PENDING, PROCESSING, COMPLETED, DEAD)

---

## 🛠 Installation

### 1. Install Redis

```
redis-server
```

### 2. Install queuectl in editable mode

Navigate to the project root:

```
pip install -e .
```

This installs the `queuectl` command globally.

---

## 🧪 Quickstart

### ▶ Enqueue a Job

```
queuectl enqueue --command "echo hello"
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

Jobs retry automatically using exponential backoff.

| Attempt | Delay |
| ------- | ----- |
| 1       | 2s    |
| 2       | 4s    |
| 3       | 8s    |

You can configure retry behavior:

```
queuectl config set backoff_base 3
queuectl config set max_retries 5
```

---

## ⏳ Delayed & Scheduled Jobs

Failed jobs or scheduled jobs are placed in:

```
queuectl:queue:delayed
```

The scheduler reads this ZSET and moves ready jobs into the pending queue.

Scheduler starts automatically with workers.

---

## 💀 Dead Letter Queue

Jobs that exhaust retries move to DLQ.

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

Config is stored under:

```
queuectl/data/config.json
```

---

### Code Style

Use any formatter (Black, Ruff, etc.).

---

## 🤝 Contributing

Contributions are welcome!

You can help by:

* Fixing bugs
* Adding features (timeouts, priority queues, metrics)
* Improving dashboard UI
* Enhancing documentation

---

## 📜 License

MIT License

---

## ⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub!
