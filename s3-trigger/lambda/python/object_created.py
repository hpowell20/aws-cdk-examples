import boto3
import os
import urllib.parse
import uuid


def handler(event, context):
    # print(f'Event: {event}')
    bucket = event['Records'][0]['s3']['bucket']['name']
    # print(f'Bucket: {bucket}')
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    # print(f'Key: {key}')
    # event_name = event['Records'][0]['eventName']
    # print(f'Event Name: {event_name}')
    s3_time = event['Records'][0]['eventTime']
    # print(f'S3 Time: {s3_time}')

    # Create a new DynamoDB record for the result
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['FILE_UPLOAD_TABLE_NAME'])

    table.put_item(
        Item={
            'id': str(uuid.uuid4()),
            'file_name': key,
            'bucket_name': bucket,
            'created_at': s3_time
        }
    )

    return {
        'statusCode': 201,
        'body': event
    }
