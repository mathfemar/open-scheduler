"""API endpoints for job management."""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.core import models, schemas


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, close in caller


# Jobs CRUD
def get_jobs(db: Session, status: Optional[str] = None) -> List[models.Job]:
    """Get all jobs, optionally filtered by status."""
    query = db.query(models.Job)
    if status:
        query = query.filter(models.Job.status == status)
    return query.all()


def get_job(db: Session, job_id: str) -> Optional[models.Job]:
    """Get job by ID."""
    return db.query(models.Job).filter(models.Job.id == job_id).first()


def create_job(db: Session, job: schemas.JobCreate) -> models.Job:
    """Create new job."""
    db_job = models.Job(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def update_job(db: Session, job_id: str, job_update: schemas.JobUpdate) -> Optional[models.Job]:
    """Update existing job."""
    db_job = get_job(db, job_id)
    if not db_job:
        return None
    
    update_data = job_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_job, key, value)
    
    db_job.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_job)
    return db_job


def delete_job(db: Session, job_id: str) -> bool:
    """Delete job."""
    db_job = get_job(db, job_id)
    if not db_job:
        return False
    
    db.delete(db_job)
    db.commit()
    return True


# Executions
def get_executions(
    db: Session, 
    job_id: Optional[str] = None, 
    status: Optional[str] = None,
    limit: int = 50
) -> List[models.Execution]:
    """Get execution history."""
    query = db.query(models.Execution)
    if job_id:
        query = query.filter(models.Execution.job_id == job_id)
    if status:
        query = query.filter(models.Execution.status == status)
    
    return query.order_by(models.Execution.started_at.desc()).limit(limit).all()


def create_execution(db: Session, execution: schemas.ExecutionCreate) -> models.Execution:
    """Create execution record."""
    db_execution = models.Execution(**execution.model_dump())
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)
    return db_execution


def update_execution(db: Session, execution_id: str, **kwargs) -> Optional[models.Execution]:
    """Update execution record."""
    db_execution = db.query(models.Execution).filter(models.Execution.id == execution_id).first()
    if not db_execution:
        return None
    
    for key, value in kwargs.items():
        setattr(db_execution, key, value)
    
    db.commit()
    db.refresh(db_execution)
    return db_execution


# Tracked Directories
def get_tracked_dirs(db: Session, active_only: bool = True) -> List[models.TrackedDirectory]:
    """Get tracked directories."""
    query = db.query(models.TrackedDirectory)
    if active_only:
        query = query.filter(models.TrackedDirectory.active == True)
    return query.all()


def add_tracked_dir(db: Session, path: str) -> models.TrackedDirectory:
    """Add tracked directory."""
    # Check if already exists
    existing = db.query(models.TrackedDirectory).filter(models.TrackedDirectory.path == path).first()
    if existing:
        existing.active = True
        db.commit()
        db.refresh(existing)
        return existing
    
    tracked_dir = models.TrackedDirectory(path=path, active=True)
    db.add(tracked_dir)
    db.commit()
    db.refresh(tracked_dir)
    return tracked_dir


def remove_tracked_dir(db: Session, dir_id: str) -> bool:
    """Remove tracked directory."""
    tracked_dir = db.query(models.TrackedDirectory).filter(models.TrackedDirectory.id == dir_id).first()
    if not tracked_dir:
        return False
    
    db.delete(tracked_dir)
    db.commit()
    return True


# Uploaded Files
def create_uploaded_file(db: Session, file_data: schemas.UploadedFileCreate) -> models.UploadedFile:
    """Create uploaded file record."""
    db_file = models.UploadedFile(**file_data.model_dump())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def get_uploaded_file_by_hash(db: Session, file_hash: str) -> Optional[models.UploadedFile]:
    """Get uploaded file by hash (for deduplication)."""
    return db.query(models.UploadedFile).filter(models.UploadedFile.file_hash == file_hash).first()


# Statistics
def get_stats(db: Session) -> dict:
    """Get dashboard statistics."""
    total_jobs = db.query(models.Job).count()
    active_jobs = db.query(models.Job).filter(models.Job.status == "active").count()
    paused_jobs = db.query(models.Job).filter(models.Job.status == "paused").count()
    
    # Success rate (last 100 executions)
    recent_executions = db.query(models.Execution).order_by(models.Execution.started_at.desc()).limit(100).all()
    if recent_executions:
        success_count = sum(1 for e in recent_executions if e.status == "success")
        success_rate = (success_count / len(recent_executions)) * 100
    else:
        success_rate = 0
    
    # Failed today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    failed_today = db.query(models.Execution).filter(
        models.Execution.status == "failed",
        models.Execution.started_at >= today_start
    ).count()
    
    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "paused_jobs": paused_jobs,
        "success_rate": round(success_rate, 1),
        "failed_today": failed_today,
    }
