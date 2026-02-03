"""
Job model for tracking asynchronous document processing tasks.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, JSON
from app.db.session import Base


class JobStatus(str, enum.Enum):
    """Status of a processing job."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Job(Base):
    """
    Represents a document processing job.
    
    Each uploaded file gets a Job record that tracks its processing status
    through the async pipeline (upload -> queue -> worker -> result).
    """
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    ledger_name = Column(String, nullable=True)
    financial_year = Column(String, nullable=True)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    result_data = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Job(job_id={self.job_id}, filename={self.original_filename}, status={self.status})>"
    
    def to_dict(self):
        """Convert job to dictionary for API responses."""
        return {
            "job_id": self.job_id,
            "filename": self.original_filename,
            "status": self.status.value,
            "ledger_name": self.ledger_name,
            "financial_year": self.financial_year,
            "result": self.result_data,
            "error": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
