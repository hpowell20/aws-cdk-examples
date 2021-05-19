import boto3
import os
import urllib.parse
import uuid


def handler(event, context):
    """
    Create -> 'eventName': 'ObjectCreated:Put'(files and folders)
    Update -> 'eventName': 'ObjectCreated:Copy'
    :param event:
    :param context:
    :return:
    """
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    event_name = event['Records'][0]['eventName']
    print(f'Event Name: {event_name}')
    s3_time = event['Records'][0]['eventTime']

    # Create a new DynamoDB record for the result
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['FILE_UPLOAD_TABLE_NAME'])

    table.put_item(
        Item={
            'id': str(uuid.uuid4()),
            'key_name': key,
            'bucket_name': bucket,
            'created_at': s3_time
        }
    )

    return {
        'statusCode': 201,
        'body': event
    }
