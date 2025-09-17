"""
File handling service for attachments and uploads
"""
import os
import uuid
import shutil
from typing import Optional, List
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings
import magic
import logging

logger = logging.getLogger(__name__)


class FileService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_types = settings.ALLOWED_FILE_TYPES
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def save_file(self, file: UploadFile, subfolder: str = "") -> dict:
        """
        Save uploaded file and return file information
        """
        try:
            # Validate file
            self._validate_file(file)
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create subfolder if specified
            save_dir = os.path.join(self.upload_dir, subfolder)
            os.makedirs(save_dir, exist_ok=True)
            
            # Full file path
            file_path = os.path.join(save_dir, unique_filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Detect MIME type
            mime_type = magic.from_file(file_path, mime=True)
            
            return {
                "original_filename": file.filename,
                "saved_filename": unique_filename,
                "file_path": file_path,
                "relative_path": os.path.join(subfolder, unique_filename),
                "file_size": file_size,
                "mime_type": mime_type
            }
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save file"
            )
    
    def _validate_file(self, file: UploadFile):
        """
        Validate uploaded file
        """
        # Check file size
        if file.size > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {self.max_file_size} bytes"
            )
        
        # Check file type by reading first few bytes
        file.file.seek(0)
        file_header = file.file.read(1024)
        file.file.seek(0)
        
        # Use python-magic to detect MIME type
        mime_type = magic.from_buffer(file_header, mime=True)
        
        if mime_type not in self.allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {mime_type} is not allowed"
            )
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from the filesystem
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get information about a file
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            mime_type = magic.from_file(file_path, mime=True)
            
            return {
                "file_path": file_path,
                "file_size": stat.st_size,
                "mime_type": mime_type,
                "created_at": stat.st_ctime,
                "modified_at": stat.st_mtime
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return None
    
    def list_files(self, subfolder: str = "") -> List[dict]:
        """
        List files in a directory
        """
        try:
            directory = os.path.join(self.upload_dir, subfolder)
            if not os.path.exists(directory):
                return []
            
            files = []
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    file_info = self.get_file_info(file_path)
                    if file_info:
                        file_info["filename"] = filename
                        files.append(file_info)
            
            return files
        except Exception as e:
            logger.error(f"Error listing files in {subfolder}: {str(e)}")
            return []
    
    def get_file_url(self, relative_path: str) -> str:
        """
        Generate URL for accessing a file
        """
        # In production, this might return a CDN URL or signed URL
        return f"/files/{relative_path}"
    
    def cleanup_old_files(self, days: int = 30):
        """
        Clean up files older than specified days
        """
        try:
            import time
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            
            for root, dirs, files in os.walk(self.upload_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.getctime(file_path) < cutoff_time:
                        try:
                            os.remove(file_path)
                            logger.info(f"Deleted old file: {file_path}")
                        except Exception as e:
                            logger.error(f"Error deleting old file {file_path}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error during file cleanup: {str(e)}")
