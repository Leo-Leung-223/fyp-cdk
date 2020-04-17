import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('userdataTable')
client = boto3.client('dynamodb')



def my_handler(event, context):
    userName = '{}'.format(event['userName'])
    id = '{}'.format(event['request']['userAttributes']['sub'])
    phone_number = '{}'.format(event['request']['userAttributes']['phone_number'])
    email = '{}'.format(event['request']['userAttributes']['email'])
    position='{}'.format(event['request']['userAttributes']['custom:Position'])
    url='{}'.format(event['request']['userAttributes']['custom:Url'])
    company='{}'.format(event['request']['userAttributes']['custom:CompanyName'])

    
    table.put_item(
        TableName=os.environ['TableName'],
        Item={
            "userName": userName,
            "id": id,
            "email": email,
            "phone_number": phone_number,
            "position":position,
            "url":url,
            "company":company
            }
        
    )
    return event