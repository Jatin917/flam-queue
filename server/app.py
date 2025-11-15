from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# Add parent directory to path to import queuectl
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from queuectl.storage import Storage
from queuectl.config import Config

app = FastAPI(title="QueueCTL API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_storage():
    """Get a Storage instance."""
    return Storage()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "QueueCTL API", "version": "1.0.0"}

@app.get("/api/status")
async def api_status():
    """Get queue status summary."""
    try:
        storage = get_storage()
        summary = storage.getSummary()
        
        # Get worker count
        workers = storage.list_workers()
        
        return {
            "success": True,
            "summary": summary,
            "worker_count": len(workers),
            "workers": workers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs")
async def api_jobs():
    """Get list of jobs."""
    try:
        storage = get_storage()
        jobs = storage.listJobs()
        
        return {
            "success": True,
            "jobs": jobs,
            "count": len(jobs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{state}")
async def api_jobs_by_state(state: str):
    """Get jobs by state."""
    try:
        storage = get_storage()
        jobS = storage.listJobs(state=state)
        jobL = storage.listJobs(state=state.upper())
        jobList = jobS + jobL
        
        
        return {
            "success": True,
            "jobs": jobList,
            "state": state,
            "count": len(jobList)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workers")
async def api_workers():
    """Get list of workers."""
    try:
        storage = get_storage()
        workers = storage.list_workers()
        
        return {
            "success": True,
            "workers": workers,
            "count": len(workers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
