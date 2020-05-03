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


class CdkdeployStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        github_repo="FYP-repo"
        repo_owner="180133517"
        

        table= ddb.Table(self,"user_table",partition_key={   #create a user table
            'name':'id', 'type': ddb.AttributeType.STRING},
            sort_key={'name':'userName','type':ddb.AttributeType.STRING}
        
        )
        
        lambda_function = _lambda.Function(   #create a lambda function that log user data from registeration
            self, "User_To_Db",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset("cdkdeploy/lambda"),
            handler="userdb.my_handler",
            environment={
                'TableName': table.table_name,
            })
        
        table.grant_read_write_data(lambda_function)  #grant permission for lambda function to write to table
        
        #token=sm.Secret(self,"token_secert",
        #        description="this is github_token",
        #        secret_name=secret_name,
        #        generate_secret_string={'secret_string_template':'{"github":"token"}', 
        #        'generate_string_key':"f904a6e064208f43a92151fc2758ae63405cece8"}
        #        )    
        #        
        
        amplify_build = codebuild.PipelineProject(self, "Amplify_Build",
                        build_spec=codebuild.BuildSpec.from_object(dict(
                            version="0.2",
                            phases=dict(
                                install=dict(
                                    commands=["npm install -g @aws-amplify/cli",
                                              "sumerian=homepage.json",
                                              "bash ./amplify_push.sh",
                                              "npm install"
                                              ]
                                             ),
                                build=dict(commands=[
                                    "amplify publish -c --yes",]),
                                sumerian=codebuild.BuildEnvironmentVariable(type=codebuild.BuildEnvironmentVariableType.PLAINTEXT,value="test"),
                                environment=codebuild.LinuxBuildImage.STANDARD_2_0))
                            ))
            
        source_output = codepipeline.Artifact()
        amplify_build_output= codepipeline.Artifact('AmplifyBuildOutput')
        github_oauth_token=core.SecretValue.secrets_manager("/serverless-pipeline/secrets/github/token",json_field="github-token")
        
        
        amplify_repo=codepipeline.Pipeline(
                self, "AmplifyPipeline",
                stages=[
                    codepipeline.StageProps(stage_name="Source",
                        actions=[
                            codepipeline_actions.GitHubSourceAction(
                                action_name="GitHub_Source",
                                owner=repo_owner,
                                repo=github_repo,
                                oauth_token=github_oauth_token,
                                branch="master",
                                trigger=codepipeline_actions.GitHubTrigger.POLL,
                                output=source_output
                                )]),
                    codepipeline.StageProps(stage_name="Amplify_Build",
                        actions=[
                            codepipeline_actions.CodeBuildAction(
                                action_name="CdkBuild",
                                project=amplify_build,
                                input=source_output,
                                )])
                    ]
            )
