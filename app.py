#!/usr/bin/env python3

from aws_cdk import core

from cdkdeploy.cdkdeploy_stack import CdkdeployStack


app = core.App()
CdkdeployStack(app, "CdkdeployStack", env={'region': 'us-east-1'})



app.synth()