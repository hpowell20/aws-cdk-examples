#!/usr/bin/env python3
import os
from aws_cdk import core

from es_domain.elasticsearch_stack import ElasticsearchDomainStack

# Set the values to be used in the stack
# TODO: Change me
PROJECT_CODE = 'project-code'

app = core.App()

stage_name = app.node.try_get_context("stage_name")
vpc_id = app.node.try_get_context("vpc_id")

es_stack_name = f"{PROJECT_CODE}-{stage_name}-es"
ElasticsearchDomainStack(app, es_stack_name,
    project_code=PROJECT_CODE,
    description='Template for the ElasticSearch cluster instance',
    stage_name=stage_name,
    vpc_id=vpc_id,
    env=core.Environment(
        account=os.environ["AWS_ACCOUNT"],
        region=os.environ["AWS_REGION"])
)

app.synth()
