import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from services.upload_service import upload_file

router = APIRouter()

logger = logging.getLogger(__name__)
logger.propagate = False
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s :%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


@router.post("/upload", operation_id="upload")
async def upload(file: UploadFile = File(...)):
    try:
        response = upload_file(file)
        return response

    except Exception as e:  # Catch exceptions from upload_service
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
