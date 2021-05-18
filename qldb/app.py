#!/usr/bin/env python3
import os
from aws_cdk import core

from qldb_ledger.qldb_stack import QldbStack

# Set the values to be used in the stack
PROJECT_CODE = 'ledger-support'
DEFAULT_REGION = 'us-east-1'
AWS_SERVICE_SUPPORTED_REGIONS = ['us-east-1', 'eu-west-1']

app = core.App()

account = os.environ.get("AWS_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"])
if not account:
    print('Account not specified via AWS_ACCOUNT or CDK_DEFAULT_ACCOUNT')
    exit()

region = os.environ.get("AWS_REGION", os.environ["CDK_DEFAULT_REGION"])
if not region:
    print('Account not specified via AWS_REGION or CDK_DEFAULT_REGION')
    exit()

if region not in AWS_SERVICE_SUPPORTED_REGIONS:
    print(f'Region {region} not currently supported; defaulting to {DEFAULT_REGION}')
    region = DEFAULT_REGION

stage_name = app.node.try_get_context("stage_name")

stack_name = f"{PROJECT_CODE}-{stage_name}-qldb"
QldbStack(app, stack_name,
          project_code=PROJECT_CODE,
          stage_name=stage_name,
          description='Stack template for creating a QLDB Ledger',
          env=core.Environment(
            account=account,
            region=region))

app.synth()
