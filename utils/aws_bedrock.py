import boto3
from dotenv import load_dotenv
load_dotenv(override=True)

bedrockClient = boto3.client('bedrock-agent-runtime', os.getenv('AWS_REGION'))

def getAWSBedrockAnswers(questions):
    knowledgeBaseResponse  = bedrockClient.retrieve_and_generate(
        input={'text': questions},
        retrieveAndGenerateConfiguration={
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': os.getenv('KNOWLEDGE_BASE_ID'),
                'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-instant-v1'
            },
            'type': 'KNOWLEDGE_BASE'
        })
    return knowledgeBaseResponse