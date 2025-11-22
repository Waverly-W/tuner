import os
from fastapi import UploadFile, HTTPException

class FileValidator:
    MAX_SIZE_MB = 100
    ALLOWED_EXTENSIONS = {'.txt', '.md', '.epub', '.pdf', '.mobi', '.docx'}

    @classmethod
    async def validate(cls, file: UploadFile):
        # Check extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file extension: {ext}. Allowed: {cls.ALLOWED_EXTENSIONS}"
            )

        # Check size (approximate, as we might not read whole file yet)
        # For UploadFile, we can check spooled file size or read chunk
        # Here we assume the file is already uploaded or we check header if available
        # But standard UploadFile doesn't always have size.
        # We'll check after reading or if Content-Length header is passed in real app.
        # For now, we'll skip strict size check here or do it during read.
        return True

    @classmethod
    def validate_path(cls, file_path: str):
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > cls.MAX_SIZE_MB:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large: {size_mb:.2f}MB. Max: {cls.MAX_SIZE_MB}MB"
            )
            
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
             raise HTTPException(
                status_code=400,
                detail=f"Unsupported file extension: {ext}"
            )
        return True
