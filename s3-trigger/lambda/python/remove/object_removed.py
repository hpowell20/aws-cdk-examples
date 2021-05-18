import boto3
import os
import urllib.parse
import uuid


def handler(event, context):
    """
    Delete -> 'eventName': 'ObjectRemoved:DeleteMarkerCreated'
    """
    event_name = event['Records'][0]['eventName']
    print(f'Event Name: {event_name}')

    # Create a new DynamoDB record for the result
    # dynamodb = boto3.resource('dynamodb')
    # table = dynamodb.Table(os.environ['FILE_UPLOAD_TABLE_NAME'])
    #
    # table.put_item(
    #     Item={
    #         'id': str(uuid.uuid4()),
    #         'file_name': key,
    #         'bucket_name': bucket,
    #         'created_at': s3_time
    #     }
    # )

    return {
        'statusCode': 204,
        'body': event
    }
