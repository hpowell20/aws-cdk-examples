from datetime import timezone

import boto3
import datetime
import os

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'


def handler(event, context):
    file_upload_bucket_name = (os.environ['FILE_UPLOAD_BUCKET_NAME'])
    key = event['Records'][0]['s3']['object']['key']

    # Set the current date and time for the record
    dt = datetime.datetime.now()
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.strftime(DATE_FORMAT)

    # Create a new DynamoDB record for the result
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['FILE_UPLOAD_TABLE'])

    table.put_item(
        Item={
            'id': 'test',
            'file_name': key,
            'bucket_name': file_upload_bucket_name,
            'created_at': utc_timestamp
        }
    )

    return {
        'statusCode': 200,
        'body': event
    }
