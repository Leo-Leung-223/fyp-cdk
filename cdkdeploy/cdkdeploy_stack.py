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
    core,
)


class CdkdeployStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
    
        github_repo="https://github.com/180133517/FYP-repo.git"
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
        
        
        amplify_build=codebuild.PipelineProject(
            self, "AmplifyBuild",
            build_spec=codebuild.BuildSpec.from_object(dict(
                version="0.2",
                phase=dict(
                    install=dict(
                        commands=[
                            "sudo yum update -y",
                            "npm install",
                        ]),
                    pre_build=dict(commands=[
                            "pwd",
                            "ls",#enter the name for the env
                            #'y', "aws profile"
                            #'\n',"use default profile"
                        ]),
             
                        environment=dict(buildImage=
                                codebuild.LinuxBuildImage.STANDARD_2_0)
                    )
                    )
                )
            )
            
            
        source_output = codepipeline.Artifact()
        amplify_build_output= codepipeline.Artifact('AmplifyBuildOutput')
        
        amplify_repo=codepipeline.Pipeline(
                self, "AmplifyPipeline",
                stages=[
                    codepipeline.StageProps(stage_name="Source",
                        actions=[
                            codepipeline_actions.GitHubSourceAction(
                                action_name="GitHub_Source",
                                owner=repo_owner,
                                repo=github_repo,
                                oauth_token=core.SecretValue.secrets_manager("f904a6e064208f43a92151fc2758ae63405cece8"),
                                branch="master",
                                trigger=codepipeline_actions.GitHubTrigger.POLL,
                                output=source_output
                                )]),
                    codepipeline.StageProps(stage_name="Build",
                        actions=[
                            codepipeline_actions.CodeBuildAction(
                                action_name="AmplifyBuild",
                                project=amplify_build,
                                input=source_output,
                                )])
                    ]
            )