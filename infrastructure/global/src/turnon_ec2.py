#lambda to turn off ec2 instance
import boto3
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
ec2 = boto3.client('ec2', region_name=os.environ['LAMBDA_AWS_REGION'])
instances = [os.environ['EC2_INSTANCE_IDs'].split(",")][0]

def lambda_handler(event, context):
    
    ec2.start_instances(InstanceIds=instances)
    logging.info('stopped your instances: ' + str(instances))
    
    return {
        'statusCode': 200,
        'body': json.dumps('EC2 instance started!')
    }