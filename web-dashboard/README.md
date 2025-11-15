# QueueCTL Web Dashboard

A minimal React-based web dashboard for monitoring QueueCTL job queue system.

## Features

- Real-time queue status monitoring
- Worker status and management
- Job listing with filtering by state
- Auto-refresh every 2-3 seconds
- Modern, responsive UI

## Setup

### Prerequisites

- Node.js (v14 or higher)
- Python 3.8+ with FastAPI
- Redis server running

### Installation

1. Install Python dependencies:
```bash
cd web-dashboard
pip install -r requirements.txt
```

2. Install Node.js dependencies:
```bash
cd web-dashboard
npm install
```

## Running

### Start the FastAPI backend:

```bash
cd web-dashboard
python app.py
```

Or using uvicorn directly:
```bash
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

The backend will run on `http://localhost:5000`

### Start the React frontend:

In a new terminal:
```bash
cd web-dashboard
npm start
```

The frontend will run on `http://localhost:3000` and automatically open in your browser.

## API Endpoints

- `GET /api/status` - Get queue status summary and workers
- `GET /api/jobs` - Get all jobs
- `GET /api/jobs/<state>` - Get jobs by state (pending, processing, completed, dead, delayed)
- `GET /api/workers` - Get list of active workers

## Development

The React app uses a proxy to connect to the Flask backend. Make sure both servers are running for full functionality.

