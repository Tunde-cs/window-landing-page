#!/usr/bin/env python3
import os
import aws_cdk as cdk
from cdk_windowgeniusai.cdk_windowgeniusai_stack import CdkWindowgeniusaiStack

app = cdk.App()

CdkWindowgeniusaiStack(
    app, 
    "CdkWindowgeniusaiStack",
    env=cdk.Environment(
        account="629965575535",   # ✅ explicitly set account
        region="us-east-1"        # ✅ your deployment region
    )
)

app.synth()

