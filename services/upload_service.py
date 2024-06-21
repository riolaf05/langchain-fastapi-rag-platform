import logging
from uuid import uuid4
from filetype import guess_mime
from fastapi import UploadFile

# Constants
from utils.aws_services import AWSS3
from config.environments import AWS_S3_BUCKET_NAME
from config.constants import RAW_DOCUMENT_FOLDER
from config.constants import FILE_EXTENSIONS

EXTENSIONS_SET = set.union(*FILE_EXTENSIONS.values())
MAX_FILE_SIZE = 100 * 1024 * 1024

s3_client = AWSS3(AWS_S3_BUCKET_NAME)

# Setup the logger
logger = logging.getLogger(__name__)
logger.propagate = False
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s :%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def allowed_file_extension(filename: str) -> bool:
    return "." in filename and filename.split(".")[-1].lower() in EXTENSIONS_SET


def upload_file(file_obj: UploadFile):
    logger.info(f"Received request to upload file: {file_obj.filename}")

    if file_obj.size > MAX_FILE_SIZE:
        logger.error(
            f"File size {file_obj.size} exceeds maximum allowed size of {MAX_FILE_SIZE}"
        )
        raise ValueError("File size exceeds maximum allowed size.")

    if not allowed_file_extension(file_obj.filename):
        logger.error(f"File type '{file_obj.filename.split('.')[-1]}' is not allowed.")
        raise ValueError("File type not allowed.")

    content_type = file_obj.content_type
    with file_obj.file as f:
        detected_type = None
        file_extension = file_obj.filename.split(".")[-1]
        if file_extension == "txt":
            detected_type = "text/plain"
        else:
            # Read the first 1024 bytes to determine the file type
            detected_type = guess_mime(f.read(1024))

        if detected_type is None:
            logger.error("Unable to determine file type.")
            raise ValueError(f"Unable to determine file type.")

        elif detected_type != content_type:
            logger.error(
                f"File type '{detected_type}' does not match content type '{content_type}' for '{file_obj.filename}'"
            )
            raise ValueError(
                f"File type '{detected_type}' does not match content type '{content_type}'."
            )

        # Ensure the pointer returns to the beginning after checking
        file_obj.file.seek(0)

        file_name = f"{uuid4()}.{file_extension}"

        try:
            s3_client.upload_file(
                fileobj=file_obj.file, key=f"{RAW_DOCUMENT_FOLDER}/{file_name}"
            )
            logger.info(
                f"Successfully stored {file_name} to S3 bucket {AWS_S3_BUCKET_NAME}/{RAW_DOCUMENT_FOLDER} ."
            )

            return {
                "success": True,
                "message": f"Successfully stored {file_name} to S3 bucket {AWS_S3_BUCKET_NAME}/{RAW_DOCUMENT_FOLDER} .",
            }
        except Exception as e:
            logger.error(f"Error uploading file '{file_name}' to S3 {str(e)}")
            raise e  # Re-raise the exception for the router to handle
