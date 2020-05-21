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
    aws_ssm as ssm,
    aws_s3  as s3,
    aws_amplify as amplify,
    aws_events_targets as targets,
    aws_events as events,
    core
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
        
        

        access_key_id=ssm.StringParameter(self,"access_key_id1",string_value="45646216",description="accesss_key_id")
        access_key_id=ssm.StringParameter(self,"secret_access_key1",string_value="4564621dwdw6",description="secret_access_key")
        
        #token=sm.Secret(self,"token_secert",
        #        description="this is github_token",
        #        secret_name=secret_name,
        #        generate_secret_string={'secret_string_template':'{"github":"token"}', 
        #        'generate_string_key':"f904a6e064208f43a92151fc2758ae63405cece8"}
        #        )    
        #        
        
        
    
                            
        amplify_build = codebuild.PipelineProject(self, "CdkBuild",
                        environment=dict(build_image=
                        codebuild.LinuxBuildImage.STANDARD_2_0),
                        build_spec=codebuild.BuildSpec.from_object(dict(
                            version="0.2",
                            phases=dict(
                                install=dict(
                                    commands=["npm install",
                                              "npm install -g @aws-amplify/cli",
                                              "bash ./amplify_init.sh",
                                              "npm install"]),
                                build=dict(commands=[
                                   "amplify publish -c --yes"]))
                             ))) 
        
        
        
        source_output = codepipeline.Artifact()
        amplify_build_output= codepipeline.Artifact('AmplifyBuildOutput')
        github_oauth_token=core.SecretValue.secrets_manager("/serverless-pipeline/secrets/github/token",json_field="github-token")
        
        
        codepipeline_role=iam.Role(self,'codepipeline_role',assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"))
        codepipeline_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],actions=["*"]))
        
            
        
        amplify_repo=codepipeline.Pipeline(
                self, "AmplifyPipeline",
                role=codepipeline_role,
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
            
        bcuket_name='eventhelper-vtc-bucket'
        my_bucke=s3.Bucket(self,bcuket_name)

        eventhelper_comprehend_table= ddb.Table(self,"eventhelper_comprehend",partition_key={   #create a user table
            'name':'Boothname', 'type': ddb.AttributeType.STRING},
            sort_key={'name':'Time','type':ddb.AttributeType.NUMBER}
        
        )
        
        eventhelper_rekognition_table= ddb.Table(self,"eventhelper_rekognition",partition_key={   #create a user table
            'name':'Boothname', 'type': ddb.AttributeType.STRING},
            sort_key={'name':'Time','type':ddb.AttributeType.NUMBER}
        
        )
        eventhelper_workshop_participant_table= ddb.Table(self,"eventhelper_workshop_participant",partition_key={   #create a user table
            'name':'Workshop', 'type': ddb.AttributeType.STRING},
            sort_key={'name':'Username','type':ddb.AttributeType.STRING}

        )
        workshopList_table= ddb.Table(self,"workshopList",partition_key={
            'name':'Workshop', 'type': ddb.AttributeType.STRING})
        

        eventhelper_lambda_role=iam.Role(self,'eventhelper_connect_role',assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))
        eventhelper_lambda_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],actions=['*']))
        
        eventhelper_connect_lambda=_lambda.Function(self,'eventhelper-connect',
            runtime=_lambda.Runtime.PYTHON_3_7,code=_lambda.Code.asset("./cdkdeploy/eventhelper_connect_lambda/lambda/"),
            handler="lambda.lambda_handler",
            timeout=core.Duration.seconds(300),
            environment=dict(
                    ContactFlowId= 'None',
                    InstanceId='None',
                    SourcePhoneNumber='None'
            ),role=eventhelper_lambda_role)
        
        eventhelper_rekognition_table.grant_read_write_data(eventhelper_connect_lambda)
            
            
        eventhelper_table_comprehend_rekognition_lambda=_lambda.Function(self,'eventhelper-table-comprehend-rekognition',
            runtime=_lambda.Runtime.PYTHON_3_7,code=_lambda.Code.asset("./cdkdeploy/eventhelper_table_comprehend_rekognition_lambda/lambda/"),
            handler="lambda.lambda_handler",
            timeout=core.Duration.seconds(300),
            environment=dict(
                    Bucket= my_bucke.bucket_name)
            ,role=eventhelper_lambda_role)
        
        eventhelper_comprehend_table.grant_read_write_data(eventhelper_table_comprehend_rekognition_lambda)
    
            
        eventhelper_dynamodb_update_lambda=_lambda.Function(self,'eventhelper_dynamodb_update_lambda',
            runtime=_lambda.Runtime.PYTHON_3_7,code=_lambda.Code.asset("./cdkdeploy/eventhelper_dynamodb_update/lambda"),
            handler="lambda.lambda_handler",
            timeout=core.Duration.seconds(300),
            role=eventhelper_lambda_role)
    
        eventhelper_workshop_participant_table.grant_read_write_data(eventhelper_dynamodb_update_lambda)
        workshopList_table.grant_read_write_data(eventhelper_dynamodb_update_lambda)
        
        eventhelper_callout_lambda=_lambda.Function(self,'eventhelper_callout_lambda',
            runtime=_lambda.Runtime.PYTHON_3_7,code=_lambda.Code.asset("./cdkdeploy/eventhelper_callout_lambda/lambda"),
            handler="lambda.lambda_handler",
            timeout=core.Duration.seconds(300),
            role=eventhelper_lambda_role)
            
        eventhelper_workshop_participant_table.grant_read_write_data(eventhelper_dynamodb_update_lambda)
        workshopList_table.grant_read_write_data(eventhelper_dynamodb_update_lambda)
        
        rule = events.Rule(
            self, "Rule",
            schedule=events.Schedule.cron(
                minute='1',
                hour='*',
                month='*',
                week_day='*',
                year='*'
                ),
        )
        rule.add_target(targets.LambdaFunction(eventhelper_callout_lambda)) 
