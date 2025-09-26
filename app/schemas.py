from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class DownloadRequest(BaseModel):
    url: str
    download_options: Dict[str, Any] = Field(default_factory=dict)
    cookie_string: Optional[str] = None

class DownloadResponse(BaseModel):
    task_id: str
    status: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None