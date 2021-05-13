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

        CfnOutput(self, "FileUploadTableName", value=file_upload_table.table_name)

        # Add a Lambda trigger to write a record in the table
        # base = f'{project_code}-{stage_name}-s3'
        # s3_access_role = iam.Role(self, 'S3TriggerAccessRole',
        #                           role_name=f'{base}-{self.region}-lambdaRole',
        #                           assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'))

        lambda_function = _lambda.Function(self, 'UpdateUploadTableFunction',
                                           function_name=f'{project_code}-{stage_name}-s3-dynamo-trigger',
                                           # runtime=_lambda.Runtime.NODEJS_14_X,
                                           # handler='process-file.handler',
                                           # code=_lambda.Code.asset('./lambda/typescript'),
                                           runtime=_lambda.Runtime.PYTHON_3_8,
                                           handler='process_file.handler',
                                           code=_lambda.Code.asset('./lambda/python'),
                                           # role=s3_access_role,
                                           environment={
                                               'FILE_UPLOAD_BUCKET_NAME': upload_bucket.bucket_name,
                                               'FILE_UPLOAD_TABLE_NAME': file_upload_table.table_name
                                           })

        # Create a trigger for the Lambda function
        notification = notifications.LambdaDestination(lambda_function)
        notification.bind(self, upload_bucket)
        upload_bucket.add_object_created_notification(notification)

        # Grant permissions for Lambda to read/write to the DynamoDB table and S3 bucket
        file_upload_table.grant_read_write_data(lambda_function)
        upload_bucket.grant_read_write(lambda_function)
