from uuid import uuid4
from fastapi import APIRouter, File, UploadFile, HTTPException
from services.upload_service import upload_file_to_s3
from filetype import guess_mime

router = APIRouter()

# Constants
from config.environments import AWS_S3_BUCKET_NAME
from config.constants import RAW_DOCUMENT_FOLDER
ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif", "mp4", "mp3", "mov", "avi", "webm"]
MAX_FILE_SIZE = 100 * 1024 * 1024

# Check file type
def allowed_file_extension(filename: str) -> bool:
    return "." in filename and filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS

@router.post("/upload", operation_id="upload")
async def upload(file: UploadFile = File(...)):
    
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds maximum allowed size.")
    
    if not allowed_file_extension(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed.")
    # Added to check the file content type. (o-a-s) 6/4/2024
    content_type = file.content_type
    with file.file as f:
        detected_type = guess_mime(f.read(1024))
        if detected_type is None:
            raise HTTPException(status_code=400, detail="Unable to determine file type.")
        elif detected_type != content_type:
            raise HTTPException(status_code=400, detail="File type does not match content type.")
    
        # Extract file extenison and generate a unique filename based on UUID
        file_extension = file.filename.split(".")[-1]
        file_name = f"{uuid4()}.{file_extension}"
        
        # Upload the file to the S3 bucket
        try:
            upload_file_to_s3(file.file, file_name)

        # If upload fails, return a 500 error
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Return success message
    return {"success": True, 
            "message": f"Successfully stored {file_name} to S3 bucket {AWS_S3_BUCKET_NAME}/{RAW_DOCUMENT_FOLDER} ."}
