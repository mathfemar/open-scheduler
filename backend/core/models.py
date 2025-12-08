"""SQLAlchemy models for Open Scheduler."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.core.database import Base


def generate_uuid():
    """Generate UUID as string."""
    return str(uuid.uuid4())


class TrackedDirectory(Base):
    """Directories tracked for file listing."""
    __tablename__ = "tracked_directories"

    id = Column(String, primary_key=True, default=generate_uuid)
    path = Column(String, nullable=False, unique=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TrackedDirectory(path='{self.path}')>"


class Job(Base):
    """Scheduled job/task."""
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    
    # File info
    file_path = Column(String, nullable=False)
    file_source = Column(String, default="project")  # 'project' | 'upload'
    
    # Schedule config
    schedule_type = Column(String, nullable=False)  # 'cron' | 'interval' | 'once'
    schedule_value = Column(String, nullable=False)  # cron expr or interval seconds or datetime
    timezone = Column(String, default="UTC")
    
    # Status
    status = Column(String, default="active")  # 'active' | 'paused' | 'disabled'
    
    # Execution config
    args = Column(String)  # CLI arguments
    env_vars = Column(JSON)  # Environment variables as JSON
    timeout = Column(Integer, default=300)  # seconds
    retry_max = Column(Integer, default=3)
    retry_delay = Column(Integer, default=60)  # seconds
    
    # Runtime info
    next_run = Column(DateTime)
    last_run = Column(DateTime)
    last_status = Column(String)  # 'success' | 'failed' | 'running' | 'timeout'
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    executions = relationship("Execution", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Job(name='{self.name}', status='{self.status}')>"


class Execution(Base):
    """Execution history of a job."""
    __tablename__ = "executions"

    id = Column(String, primary_key=True, default=generate_uuid)
    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    
    # Execution info
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    status = Column(String, default="running")  # 'running' | 'success' | 'failed' | 'timeout'
    
    # Output
    output = Column(Text)  # stdout + stderr (limited to 50KB)
    exit_code = Column(Integer)
    duration = Column(Float)  # seconds
    
    # Relationships
    job = relationship("Job", back_populates="executions")

    def __repr__(self):
        return f"<Execution(job_id='{self.job_id}', status='{self.status}')>"


class UploadedFile(Base):
    """Metadata for uploaded Python files."""
    __tablename__ = "uploaded_files"

    id = Column(String, primary_key=True, default=generate_uuid)
    original_name = Column(String, nullable=False)
    stored_path = Column(String, nullable=False, unique=True)
    file_hash = Column(String, nullable=False)  # SHA256 for deduplication
    size_bytes = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<UploadedFile(name='{self.original_name}')>"
