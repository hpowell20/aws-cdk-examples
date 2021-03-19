#!/usr/bin/env python3
import os
from aws_cdk import core

from static_website.static_website_stack import StaticWebsiteStack


# Set the values to be used in the stack
PROJECT_CODE = 'project-code'

app = core.App()

stage_name = app.node.try_get_context("stage_name")
stack_name = f"{PROJECT_CODE}-{stage_name}-ui"

new StaticWebsiteStack(app, stack_name,
    project_code=PROJECT_CODE,
    stage_name=stage_name,
    env: {
      account: process.env.AWS_ACCOUNT || process.env.CDK_DEFAULT_ACCOUNT,
      region: process.env.AWS_REGION || process.env.CDK_DEFAULT_REGION
    }
)

app.synth()
