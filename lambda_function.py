import json
import boto3
import requests
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')

def update_preference(event, context):
    try:
        user_id = event['pathParameters']['user_id']
        preference = json.loads(event['body'])['preference']

        table = dynamodb.Table('user_preferences')
        response = table.put_item(
            Item={
                'user_id': user_id,
                'preference': preference
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps('Preference updated successfully')
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }

def invoke(event, context):
    try:
        user_id = event['pathParameters']['user_id']
        table = dynamodb.Table('user_preferences')
        response = table.get_item(Key={'user_id': user_id})
        preference = response['Item']['preference']

        arxiv_url = f'https://export.arxiv.org/api/query?search_query={preference}'
        papers_info = requests.get(arxiv_url).json() # Assuming arxiv responds with JSON

        paper_table = dynamodb.Table('paper_info')
        for paper in papers_info:
            paper_table.put_item(Item=paper)

        return {
            'statusCode': 200,
            'body': json.dumps('Papers retrieved and saved successfully')
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }

def lambda_handler(event, context):
    path = event['resource']
    http_method = event['httpMethod']

    if http_method == 'POST' and path == '/update_preference/{user_id}':
        return update_preference(event, context)
    elif http_method == 'POST' and path == '/invoke/{user_id}':
        return invoke(event, context)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid request')
        }