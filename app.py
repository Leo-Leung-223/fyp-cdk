#!/usr/bin/env python3

from aws_cdk import core

from cdkdeploy.cdkdeploy_stack import CdkdeployStack


app = core.App()
CdkdeployStack(app, "cdkdeploy", env={'region': 'us-west-2'})

app.synth()
