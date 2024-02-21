import json
import os
import urllib.parse
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain import PromptTemplate


def main(event, context):
    # extracting s3 bucket and key information from SQS message
    # print(event)
    s3_info = json.loads(event['Records'][0]['body'])
    bucket_name = s3_info['Records'][0]['s3']['bucket']['name']
    object_key = urllib.parse.unquote_plus(s3_info['Records'][0]['s3']['object']['key'], encoding='utf-8')

    
    try:
        # the first approach to read the content of uploaded file. 
        # S3Reader = download_loader("S3Reader", custom_path='/tmp/llamahub_modules')
        # loader = S3Reader(bucket=bucket_name, key=object_key)
        # documents = loader.load_data()

        ## TODO change with Langchain + indexing pipeline

        ## TODO
        # ReIndex or Create New Index from document
        # Update or Insert into VectoDatabase
        # (Optional) Update or Insert into DocStorage DB
        # Update or Insert index to MongoDB
        # Can have Ingestion Pipeline with Redis Cache
        
        return {
            'statusCode': 200
        }
        
    except Exception as e:
        print(f"Error reading the file {object_key}: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error reading the file')
        }