#!/usr/bin/env python3
import os
from aws_cdk import core

from s3_trigger.s3_trigger_stack import S3TriggerStack

# Set the values to be used in the stack
PROJECT_CODE = 's3-triggers'

app = core.App()

account = os.environ.get("AWS_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"])
if not account:
    print('Account not specified via AWS_ACCOUNT or CDK_DEFAULT_ACCOUNT')
    exit()

region = os.environ.get("AWS_REGION", os.environ["CDK_DEFAULT_REGION"])
if not region:
    print('Account not specified via AWS_REGION or CDK_DEFAULT_REGION')
    exit()

stage_name = app.node.try_get_context("stage_name")

stack_name = f"{PROJECT_CODE}-{stage_name}-s3-trigger"
S3TriggerStack(app, stack_name,
               project_code=PROJECT_CODE,
               stage_name=stage_name,
               description='Stack template for the S3 trigger sample app',
               env=core.Environment(
                    account=account,
                    region=region))

app.synth()
