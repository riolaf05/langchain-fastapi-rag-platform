from config.environments import AWS_S3_BUCKET_NAME, AWS_TEXT_S3_BUCKET_NAME
from config.constants import RAW_DOCUMENT_FOLDER
from utils.aws_services import AWSS3

s3_client = AWSS3(AWS_TEXT_S3_BUCKET_NAME)

def upload_file_to_s3(file_obj, file_name):
    s3_client.upload_file(
        fileobj=file_obj,
        key=f"{RAW_DOCUMENT_FOLDER}/{file_name}"
    )