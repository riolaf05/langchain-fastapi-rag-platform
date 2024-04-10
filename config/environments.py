from os import path
# Get the parent directory path of the current script
# parent_dir = ../
parent_dir = path.dirname(path.dirname(path.abspath(__file__)))

# Construct the path to the .env file
env_path = path.join(parent_dir, "infrastructure/.env")

from dotenv import load_dotenv
load_dotenv(env_path)


from os import getenv

# For subscription
SUBS_ENDPOINT = "subscribe/receive-message"
SNS_TOPIC= getenv("SNS_TOPIC")
SNS_ENDPOINT_SUBSCRIBE= getenv("SNS_ENDPOINT_SUBSCRIBE")

# For OpenAI and AWS credentials
OPENAI_API_KEY= getenv("OPENAI_API_KEY")
AWS_ACCESS_KEY_ID= getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY= getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION= getenv("AWS_REGION")
AWS_S3_BUCKET_NAME = getenv("AWS_S3_BUCKET_NAME")

# For embedding
JOB_URI=getenv('JOB_URI')
COGNITO_USER_POOL=getenv('COGNITO_USER_POOL')
COGNITO_CLIENT_ID=getenv('COGNITO_CLIENT_ID')
QDRANT_URL=getenv('QDRANT_URL')
COLLECTION_NAME=getenv('COLLECTION_NAME')
SQS_URL = getenv('SQS_URL')