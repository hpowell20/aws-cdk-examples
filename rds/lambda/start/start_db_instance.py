import boto3
import os

from botocore.exceptions import ClientError


def handler(event, context):
    instance_name = os.environ['DB_INSTANCE_NAME']
    rds_client = boto3.client('rds')
    try:
        rds_client.start_db_instance(DBInstanceIdentifier=instance_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidDBInstanceState':
            print('Instance is not in the correct state to perform the start operation')
        else:
            print("Unexpected error: %s" % e)

    return event
