#!/usr/bin/env python3
import os
from aws_cdk import core

from rds_instance.rds_stack import RdsStack
from rds_instance.vpc_stack import VpcStack

# Set the values to be used in the stack
# TODO: Change me
PROJECT_CODE = 'project-code'

app = core.App()

stage_name = app.node.try_get_context("stage_name")
vpc_stack_name = f"{PROJECT_CODE}-{stage_name}-vpc"
rds_stack_name = f"{PROJECT_CODE}-{stage_name}-rds"

props = {'namespace': 'RdsInstanceStack'}

vpc_stack = VpcStack(app, vpc_stack_name,
    stage_name=stage_name,
    props=props,
    description='Template for the application custom VPC',
    env=core.Environment(
        account=os.environ["AWS_ACCOUNT"],
        region=os.environ["AWS_REGION"])
)

RdsStack(app, rds_stack_name,
    project_code=PROJECT_CODE,
    stage_name=stage_name,
    props=vpc_stack.outputs,
    description='Template for the application database instance',
    env=core.Environment(
        account=os.environ["AWS_ACCOUNT"],
        region=os.environ["AWS_REGION"])
)

app.synth()
