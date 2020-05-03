from aws_cdk import (
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_codecommit as code_co,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    aws_sam as sam,
    aws_dynamodb as ddb,
    aws_lambda as _lambda,
    aws_kms as kms,
    aws_secretsmanager as sm,
    aws_amplify as amplify,
    core,
)


class SumerianStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)