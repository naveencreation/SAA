"""
Document routes for file upload and job management.
Supports both synchronous uploads and async processing via worker queue.
"""
import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.services.document_service import document_service
from app.db.session import get_db
from app.models.job import Job, JobStatus
from app.core.queue import rabbitmq_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_documents(
    files: List[UploadFile] = File(...),
    ledger_names: Optional[str] = Form(None),
    financial_year: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload documents and queue them for async AI processing.
    
    Returns job IDs immediately so the frontend can poll for status.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    # Validate file types
    allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".xlsx", ".xls", ".csv"}
    for file in files:
        extension = f".{file.filename.split('.')[-1].lower()}"
        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {extension} not allowed for file {file.filename}"
            )

    results = []

    for file in files:
        job_id = str(uuid.uuid4())
        
        try:
            # Save file with job_id as filename
            saved_file_info = await document_service.save_single_file(file, job_id)
            storage_path = saved_file_info["path"]

            # Create job record in database
            job = Job(
                job_id=job_id,
                original_filename=file.filename,
                storage_path=storage_path,
                ledger_name=ledger_names,
                financial_year=financial_year,
                status=JobStatus.PENDING
            )
            db.add(job)
            db.commit()
            db.refresh(job)

            # Publish to RabbitMQ queue
            queue_success = rabbitmq_manager.publish_job(
                job_id=job_id,
                storage_path=storage_path,
                ledger_name=ledger_names,
                financial_year=financial_year
            )
            
            if not queue_success:
                logger.warning(f"Job {job_id} saved but not queued - RabbitMQ may be unavailable")
            
            results.append({
                "job_id": job_id,
                "filename": file.filename,
                "status": job.status.value,
                "queued": queue_success
            })

        except Exception as e:
            db.rollback()
            logger.error(f"Error processing file {file.filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing file {file.filename}: {str(e)}"
            )

    return {
        "message": f"Successfully uploaded {len(results)} files",
        "jobs": results
    }


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get the status and result of a processing job.
    
    Frontend polls this endpoint to check if AI processing is complete.
    """
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job.to_dict()


@router.get("/jobs")
async def list_all_jobs(
    limit: int = 50,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all jobs, optionally filtered by status.
    """
    query = db.query(Job).order_by(Job.created_at.desc())
    
    if status_filter:
        try:
            status_enum = JobStatus(status_filter.upper())
            query = query.filter(Job.status == status_enum)
        except ValueError:
            pass  # Ignore invalid status filter
    
    jobs = query.limit(limit).all()
    return {
        "total": len(jobs),
        "jobs": [job.to_dict() for job in jobs]
    }


@router.get("/ledgers", response_model=List[str])
async def get_ledger_names():
    """
    Get a list of ledger names for the TDS agent.
    """
    # Mock data - in production this would come from database or Tally
    return ["State Bank of India", "HDFC Bank", "ICICI Bank", "Petty Cash", "Sales Account", "Purchase Account"]


@router.get("/financial-years", response_model=List[str])
async def get_financial_years():
    """
    Get a list of available financial years.
    """
    return ["2022-23", "2023-24", "2024-25", "2025-26"]
