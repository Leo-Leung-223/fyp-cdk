import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import logging
import datetime;





def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    user_table = dynamodb.Table('userdataTable')
    eventtime_table = dynamodb.Table('eventhelper_workshop_participant')
    
    response = eventtime_table.scan()
    user_workshop={}
    connectclient = boto3.client('connect')
    for i in response['Items']:
        if i['Attend'] != 'yes':
            client_data_response = user_table.scan(FilterExpression=Key('userName').eq(i['Username']))['Items']
            for q in client_data_response:
                client_phonenumber=q['phone_number']
            user_workshop[i['Username']]={
                'Username':i['Username'],
                "Workshop":i['Workshop'],
                'Time':i['Time'],
                'Attend':['Attend'],
                'phone_nember':client_phonenumber
            }


    for k,v in user_workshop.items():
        event_within=int(v['Time'])-datetime.datetime.now().timestamp()
        diff_eventtime=round(event_within/60)

        if diff_eventtime <=15:
            try: 
              #Making the outbound phone alert...
                OutboundResponse = connectclient.start_outbound_voice_contact(
                              DestinationPhoneNumber=v['phone_nember'],
                              ContactFlowId='ac57640e-663d-480a-b8cf-38df090204af',
                              InstanceId='925f9a90-bbf8-40ac-aa3b-280e12e10cd9',
                              SourcePhoneNumber='+18336465321' ,
                              Attributes={'Message': 'This is the event alert: {}  start in 15 minute'.format(v['Workshop'])
                                          }
                              )
                
                update = eventtime_table.update_item(
                    Key={
                    'Workshop': v['Workshop'],
                    'Username': k,
                },
                UpdateExpression="set Attend = :r",
                ExpressionAttributeValues={
                    ':r': 'yes'
                },ReturnValues="UPDATED_NEW"
            )
            except ClientError as e:
                print(e)
