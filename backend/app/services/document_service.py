import shutil
from pathlib import Path
from typing import List
from fastapi import UploadFile
from app.core.config import get_settings

settings = get_settings()


class DocumentService:
    """Service for handling document storage operations."""
    
    def __init__(self):
        self.storage_path = Path(settings.storage_dir)
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def save_single_file(self, file: UploadFile, job_id: str) -> dict:
        """
        Save a single file using job_id as the filename.
        
        Args:
            file: The uploaded file
            job_id: Unique job identifier (UUID)
            
        Returns:
            Dict with job_id, original filename, and storage path
        """
        file_extension = Path(file.filename).suffix
        storage_filename = f"{job_id}{file_extension}"
        file_path = self.storage_path / storage_filename
        
        # Read file content and save
        content = await file.read()
        with file_path.open("wb") as buffer:
            buffer.write(content)
        
        # Reset file pointer for potential re-use
        await file.seek(0)
            
        return {
            "job_id": job_id,
            "filename": file.filename,
            "path": str(file_path.absolute())
        }

    async def save_upload_files(
        self, 
        files: List[UploadFile], 
        ledger_names: List[str] = None,
        financial_year: str = None
    ) -> List[dict]:
        """
        Save multiple files (legacy method for simple uploads).
        """
        base_path = self.storage_path
        base_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        for file in files:
            file_path = base_path / file.filename
            
            # Save the file
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            saved_files.append({
                "filename": file.filename,
                "ledger_names": ledger_names,
                "date": financial_year,
                "content_type": file.content_type,
                "path": str(file_path)
            })
        return saved_files


document_service = DocumentService()
