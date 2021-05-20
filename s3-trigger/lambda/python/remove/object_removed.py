import boto3
import os
import urllib.parse

from boto3.dynamodb.conditions import Key


def handler(event, context):
    """
    Delete -> 'eventName': 'ObjectRemoved:DeleteMarkerCreated'
    """
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    event_name = event['Records'][0]['eventName']
    print(f'Performing event {event_name} using key {key}')

    # Look up the record in the DynamoDB table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['FILE_UPLOAD_TABLE_NAME'])

    record = table.query(
        IndexName='key-index',
        KeyConditionExpression=Key('key_name').eq(key)
    )

    if 'Items' in record:
        items = record.get('Items')
        item = items[0]

        table.delete_item(
            Key={
                'id': item['id'],
            },
        )

    return {
        'statusCode': 204,
        'body': ''
    }
