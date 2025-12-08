"""Pydantic schemas for validation and serialization."""
from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field, field_validator


# TrackedDirectory schemas
class TrackedDirectoryBase(BaseModel):
    path: str


class TrackedDirectoryCreate(TrackedDirectoryBase):
    active: bool = True


class TrackedDirectoryResponse(TrackedDirectoryBase):
    id: str
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Job schemas
class JobBase(BaseModel):
    name: str
    description: Optional[str] = None
    file_path: str
    file_source: str = "project"
    schedule_type: str  # 'cron' | 'interval' | 'once'
    schedule_value: str
    timezone: str = "UTC"
    args: Optional[str] = None
    env_vars: Optional[Dict[str, str]] = None
    timeout: int = 300
    retry_max: int = 3
    retry_delay: int = 60


class JobCreate(JobBase):
    status: str = "active"


class JobUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    schedule_type: Optional[str] = None
    schedule_value: Optional[str] = None
    timezone: Optional[str] = None
    status: Optional[str] = None
    args: Optional[str] = None
    env_vars: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None
    retry_max: Optional[int] = None
    retry_delay: Optional[int] = None


class JobResponse(JobBase):
    id: str
    status: str
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    last_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Execution schemas
class ExecutionBase(BaseModel):
    job_id: str
    status: str = "running"


class ExecutionCreate(ExecutionBase):
    pass


class ExecutionResponse(ExecutionBase):
    id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    output: Optional[str] = None
    exit_code: Optional[int] = None
    duration: Optional[float] = None

    class Config:
        from_attributes = True


# UploadedFile schemas
class UploadedFileBase(BaseModel):
    original_name: str
    stored_path: str
    file_hash: str
    size_bytes: int


class UploadedFileCreate(UploadedFileBase):
    pass


class UploadedFileResponse(UploadedFileBase):
    id: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


# Other utility schemas
class FileInfo(BaseModel):
    """File information for file tree."""
    relpath: str
    abspath: str
    size_kb: int
    source: str = "project"  # 'project' | 'upload'


class TestRunRequest(BaseModel):
    """Request to test-run a file."""
    file_path: str
    args: Optional[str] = None
    env_vars: Optional[Dict[str, str]] = None
    timeout: int = 60


class TestRunResponse(BaseModel):
    """Response from test-run."""
    success: bool
    exit_code: int
    output: str
    duration: float
