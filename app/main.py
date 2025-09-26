from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # <-- 1. Import middleware
from starlette.responses import FileResponse
from celery.result import AsyncResult
from .schemas import DownloadRequest, DownloadResponse, TaskStatusResponse
from worker.tasks import download_video_task
import os

app = FastAPI(title="SaveClips API v2", version="2.0.0")

# --------------------------------------------------------------------------
# 2. ADD THIS ENTIRE CORS CONFIGURATION BLOCK
# --------------------------------------------------------------------------
origins = [
    "https://saveclips.download",
    "https://www.saveclips.download",
    # You might want to add localhost for local development & testing
    "http://127.0.0.1",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)
# --------------------------------------------------------------------------


@app.post("/download", response_model=DownloadResponse, status_code=202)
def submit_download(request: DownloadRequest):
    options = request.download_options
    if request.cookie_string:
        options['cookie_string'] = request.cookie_string
    
    task = download_video_task.delay(request.url, options)
    return DownloadResponse(task_id=task.id, status="Task accepted")

@app.get("/status/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)
    return TaskStatusResponse(
        task_id=task_id,
        status=task_result.status,
        result=task_result.result if task_result.ready() else None
    )

@app.get("/download_file/{filename}")
def download_file(filename: str):
    file_path = os.path.join("/downloads", filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=filename)
    raise HTTPException(status_code=404, detail="File not found or has expired.")

@app.get("/")
def root():
    return {"message": "SaveClips API v2 is running."}
