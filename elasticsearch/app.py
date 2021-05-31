#!/usr/bin/env python3
import os
from aws_cdk import core

from es_domain.elasticsearch_stack import ElasticsearchDomainStack

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
if not stage_name:
    print('Please supply an environment stage name')
    exit()

vpc_id = app.node.try_get_context("vpc_id")
if not vpc_id:
    print('Please supply a VPC ID name')
    exit()

es_stack_name = f"{PROJECT_CODE}-{stage_name}-es"
ElasticsearchDomainStack(app, es_stack_name,
                         description='Template for the ElasticSearch cluster instance',
                         project_code=PROJECT_CODE,
                         stage_name=stage_name,
                         vpc_id=vpc_id,
                         env=core.Environment(
                             account=account,
                             region=region))

app.synth()
