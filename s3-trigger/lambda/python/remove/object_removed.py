import boto3
import os
import urllib.parse

from boto3.dynamodb.conditions import Key


def handler(event, context):
    """
    Delete -> 'eventName': 'ObjectRemoved:DeleteMarkerCreated'
    """
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    # Look up the record in the DynamoDB table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['FILE_UPLOAD_TABLE_NAME'])

    response = table.query(
        IndexName='key-index',
        KeyConditionExpression=Key('key_name').eq(key)
    )

    items = response.get('Items')
    record = items[0]

    table.delete_item(
        Key={
            'id': record['id'],
        },
    )

    return {
        'statusCode': 204,
        'body': ''
    }
