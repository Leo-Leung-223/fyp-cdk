from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key

# Define what table to query base on lex intent
return_table = {
    'aboutBooth': 'TempBoothInfo2',
    'aboutEvent': 'EventInfo',
    'Software_Engineering_Booth': 'workshopList'
}
return_slot = {
    'aboutBooth': 'Booth',
    'aboutEvent': 'eventName',
    'aboutWorkshop': 'workshopName',
    'listWorkshop': 'workshopList'
}


def queryDB(intent_name,item_name):
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(return_table[intent_name])
        response = table.query(
            IndexName='Info-index',
            KeyConditionExpression=Key('Name').eq(item_name)
        )
        item_name = str(response['Items'][0]['Info'])
    except Exception as e:
        item_name += ' is not found. queryDB Debug: ' + str(e)
    return item_name

def main(event,context):
    try:
        intent_name = event['currentIntent']['name']
        item_name = event['currentIntent']['slotDetails'][return_slot[intent_name]]['resolutions'][0]['value']
    except Exception as e:
        output = 'Booth not found. Debug: ' + str(e)
    response ={
        "dialogAction": {
        "type": "Close",
        "fulfillmentState": "Fulfilled",
        "message": {
            "contentType": "CustomPayload",
            "content": "Here is what I found: " + output
            },
        }
    }
    return response


