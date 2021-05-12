import boto3
import os
import uuid


def handler(event, context):
    file_upload_bucket_name = (os.environ['FILE_UPLOAD_BUCKET_NAME'])
    key = event['Records'][0]['s3']['object']['key']
    s3_time = event['Records'][0]['eventTime']

    # Create a new DynamoDB record for the result
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['FILE_UPLOAD_TABLE'])

    table.put_item(
        Item={
            'id': str(uuid.uuid4()),
            'file_name': key,
            'bucket_name': file_upload_bucket_name,
            'created_at': s3_time
        }
    )

    return {
        'statusCode': 201,
        'body': event
    }
