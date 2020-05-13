import boto3
from time import sleep

lex = boto3.client('lex-models')

lambad_permission = boto3.client('lambda')
account_id = boto3.client("sts").get_caller_identity()["Account"]

lambad_permission.add_permission(
    FunctionName='lexResponseWithDBinPython',
    StatementId='lex',
    Action='lambda:invokeFunction',
    Principal='lex.amazonaws.com',
    SourceArn='arn:aws:lex:us-east-1:'+account_id+':*'
)


def put_slot_intent(slot_type_name, value: list, slot_name, sentence: list, intent_name, ask_back: list):
    value_list = []
    for name in value:
        Json = {
            'value': name,
            'synonyms': name.split()
        }
        value_list.append(Json)
    lex.put_slot_type(
        name=slot_type_name,
        enumerationValues=value_list,
        valueSelectionStrategy='ORIGINAL_VALUE',
        createVersion=True
    )

    askback_list = []
    for question in ask_back:
        Json = {
            'contentType': 'PlainText',
            'content': question
        }
        askback_list.append(Json)

    return lex.put_intent(
        name=intent_name,
        sampleUtterances=sentence,
        slots=[
            {
                'name': slot_name,
                'slotConstraint': 'Required',
                'slotType': slot_type_name,
                'slotTypeVersion': '$LATEST',
                'valueElicitationPrompt': {
                    'messages': askback_list,
                    'maxAttempts': 2,
                },
                'priority': 1,
                'sampleUtterances': [
                    'it calls {'+slot_name+'}'
                ],
            },
        ],
        fulfillmentActivity={
            'type': 'CodeHook',
            'codeHook': {
                'uri': 'arn:aws:lambda:us-east-1:467005446488:function:lexResponseWithDBinPython',
                'messageVersion': '1.0'
            }
        }
    )['name']


def put_intent(intent_name, sentence: list, ans):
    return lex.put_intent(
        name=intent_name,
        sampleUtterances=sentence,
        fulfillmentActivity={
            'type': 'ReturnIntent',
        },
        conclusionStatement={
            'messages': [
                {
                    'contentType': 'PlainText',
                    'content': ans,
                },
            ],
        },
    )['name']



def put_bot(bot_name, intent_list: list, fail_sent):
    int_list = []
    for intent in intent_list:
        Json = {
            'intentName': intent,
            'intentVersion': '$LATEST'
        }
        int_list.append(Json)
    fail = []
    for sent in fail_sent:
        Json = {
            'contentType': 'PlainText',
            'content': sent,
        }
        fail.append(Json)
    print(lex.put_bot(
        name=bot_name,
        intents=int_list,
        # if fail to understand
        clarificationPrompt={
            'messages': fail,
            'maxAttempts': 2,
        },
        abortStatement={
            'messages': [
                {
                    'contentType': 'PlainText',
                    'content': 'Sorry, I could not understand. Please try again at the beginning.',
                },
            ]
        },
        voiceId='Kendra',
        processBehavior='BUILD',
        childDirected=False,
        # set true to sent to Amazon Comprehend for sentiment analysis
        detectSentiment=False,
        locale='en-US'
    )['name'])
    sleep(3)
    response = lex.put_bot_alias(
        name='DEMO',
        botVersion='$LATEST',
        botName=bot_name
    )
    print(response['botName'] + ': ' + response['name'])
    return


# Demo
def cloud_booth(bot_name, action):
    intent_list = ['cyrus', 'subject']

    print('building ' + bot_name)
    print(put_intent('cyrus', ['who is cyrus wong', 'what is the background of cyrus wong', 'Cyrus Wong'],
                     'AWS hero and teacher experience in development'))

    print(put_intent('subject', ['What is this subject about', 'What can I learn', 'What is this course about'],
                     'This subject is about principle of using cloud, basic networing skill, SQL statement'))

    put_bot(bot_name, intent_list, action)
