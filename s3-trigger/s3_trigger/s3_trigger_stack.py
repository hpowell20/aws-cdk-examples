from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_s3_notifications as notifications
)

from aws_cdk.core import Construct, CfnOutput, RemovalPolicy, Stack


class S3TriggerStack(Stack):
    def __init__(self, scope: Construct, id: str, project_code: str, stage_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the S3 bucket for the uploaded files
        bucket_name = f"{project_code}-{stage_name}-file-upload"
        upload_bucket = s3.Bucket(self, "FileUploadBucket",
                                  bucket_name=bucket_name,
                                  block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                                  encryption=s3.BucketEncryption.S3_MANAGED,
                                  versioned=True,
                                  removal_policy=RemovalPolicy.DESTROY,
                                  auto_delete_objects=True,
                                  cors=[s3.CorsRule(
                                      allowed_headers=["*"],
                                      allowed_methods=[s3.HttpMethods.PUT],
                                      allowed_origins=["*"],
                                      max_age=3500)
                                  ])

        CfnOutput(self, "BucketArn", value=upload_bucket.bucket_arn)
        CfnOutput(self, "BucketName", value=upload_bucket.bucket_name)

        # Create a Dynamo table
        table_name = f"{project_code}-{stage_name}-file-upload"
        file_upload_table = dynamodb.Table(self, 'file-upload-table',
                                           table_name=table_name,
                                           partition_key=dynamodb.Attribute(
                                               name='id',
                                               type=dynamodb.AttributeType.STRING),
                                           removal_policy=RemovalPolicy.DESTROY,
                                           billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
                                           stream=dynamodb.StreamViewType.NEW_IMAGE,
                                           point_in_time_recovery=True,
                                           encryption=dynamodb.TableEncryption.AWS_MANAGED)

        # Add a GSI for the key name
        file_upload_table.add_global_secondary_index(index_name='key-index',
                                                     partition_key=dynamodb.Attribute(
                                                        name='key_name',
                                                        type=dynamodb.AttributeType.STRING),
                                                     projection_type=dynamodb.ProjectionType.KEYS_ONLY)

        CfnOutput(self, "FileUploadTableName", value=file_upload_table.table_name)

        # base = f'{project_code}-{stage_name}-s3'
        # s3_access_role = iam.Role(self, 'S3TriggerAccessRole',
        #                           role_name=f'{base}-{self.region}-lambdaRole',
        #                           assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'))

        # Add a Lambda trigger to write a record in the table upon object creation
        create_lambda_function = _lambda.Function(self, 'ObjectCreateTableFunction',
                                                  function_name=f'{project_code}-{stage_name}-s3-object-create',
                                                  runtime=_lambda.Runtime.PYTHON_3_8,
                                                  handler='object_created.handler',
                                                  code=_lambda.Code.asset('./lambda/python/create'),
                                                  environment={
                                                     'FILE_UPLOAD_TABLE_NAME': file_upload_table.table_name
                                                  })

        # Create a trigger for the create object Lambda function
        create_notification = notifications.LambdaDestination(create_lambda_function)
        create_notification.bind(self, upload_bucket)
        upload_bucket.add_object_created_notification(create_notification)

        # Grant permissions for Lambda to read/write to the DynamoDB table
        file_upload_table.grant_read_write_data(create_lambda_function)

        # Grant permissions for Lambda to read only from the S3 bucket
        upload_bucket.grant_read(create_lambda_function)

        # Add a Lambda trigger to remove a record from the table upon object removal
        remove_lambda_function = _lambda.Function(self, 'ObjectRemoveTableFunction',
                                                  function_name=f'{project_code}-{stage_name}-s3-object-remove',
                                                  runtime=_lambda.Runtime.PYTHON_3_8,
                                                  handler='object_removed.handler',
                                                  code=_lambda.Code.asset('./lambda/python/remove'),
                                                  environment={
                                                      'FILE_UPLOAD_TABLE_NAME': file_upload_table.table_name
                                                  })
        # Create a trigger for the remove object Lambda function
        remove_notification = notifications.LambdaDestination(remove_lambda_function)
        remove_notification.bind(self, upload_bucket)
        upload_bucket.add_object_removed_notification(remove_notification)

        # Grant permissions for Lambda to read/write to the DynamoDB table
        file_upload_table.grant_read_write_data(remove_lambda_function)

        # Grant permissions for Lambda to read only from the S3 bucket
        upload_bucket.grant_read(remove_lambda_function)
