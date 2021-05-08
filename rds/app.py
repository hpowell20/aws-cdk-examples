#!/usr/bin/env python3
import os
from aws_cdk import core

from rds_instance.db_triggers_stack import DbTriggersStack
from rds_instance.rds_stack import RdsStack
from vpc.vpc_stack import VpcStack

# Set the values to be used in the stack
# TODO: Change me
PROJECT_CODE = 'project-code'

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

vpc_stack_name = f"{PROJECT_CODE}-{stage_name}-vpc"
vpc_stack = VpcStack(app, vpc_stack_name,
                     stage_name=stage_name,
                     description='Stack template for the application custom VPC',
                     env=core.Environment(
                        account=account,
                        region=region))

rds_stack_name = f"{PROJECT_CODE}-{stage_name}-rds"
rds_stack = RdsStack(app, rds_stack_name,
                     project_code=PROJECT_CODE,
                     description='Stack template for the application database instance',
                     stage_name=stage_name,
                     vpc_ref=vpc_stack.vpc_ref,
                     env=core.Environment(
                        account=account,
                        region=region))

db_triggers_stack_name = f"{PROJECT_CODE}-{stage_name}-triggers"
DbTriggersStack(app, db_triggers_stack_name,
                project_code=PROJECT_CODE,
                description='Stack template for scheduled triggers for the database instance',
                stage_name=stage_name,
                instance_ref=rds_stack.instance_ref,
                env=core.Environment(
                    account=account,
                    region=region))

app.synth()
