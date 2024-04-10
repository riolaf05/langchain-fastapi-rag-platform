#lambda to turn off ec2 instance
import boto3
import json
import os
import logging

table_name = "chatgpt-summary-users"

class DynamoDBManager:
    def __init__(self, region, table_name):
        self.region = region
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb',  region_name=region)
        self.table = self.dynamodb.Table(table_name)
    
    def write_item(self, item):
        try:
            response = self.table.put_item(Item=item)
            print("Item added successfully:", response)
        except Exception as e:
            print("Error writing item:", e)
    
    def update_item(self, key, update_expression, expression_values):
        try:
            response = self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            print("Item updated successfully:", response)
        except Exception as e:
            print("Error updating item:", e)
    def get_item(self, key):
        try:
            response = self.table.get_item(Key=key)
            print("Item retrieved successfully:", response)
            return response
        except Exception as e:
            print("Error retrieving item:", e)

dynamo_manager = DynamoDBManager(os.getenv('LAMBDA_AWS_REGION'), table_name)

logging.basicConfig(level=logging.INFO)
ec2 = boto3.client('ec2', region_name=os.environ['LAMBDA_AWS_REGION'])
instances = [os.environ['EC2_INSTANCE_ID']]

def lambda_handler(event, context):

    print('Received event: ' + json.dumps(event))
        
    new_key = {
        "username": event["userName"],
        "time_limit": 43200,
        "n_images": 0
    }
    try:
        dynamo_manager.write_item(new_key)
    except Exception as e:
        return None
    
    return event