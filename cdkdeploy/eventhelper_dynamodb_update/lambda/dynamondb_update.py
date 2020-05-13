from __future__ import print_function  # Python 2/3 compatibility
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr
from datetime import date
from datetime import datetime


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

table = dynamodb.Table('workshopList')
update_table = dynamodb.Table('eventhelper_workshop_participant')

time = []
location = []
workshop = []


def lambda_handler(event, context):
    response = table.scan(FilterExpression=Key('workshop').eq(event[1]))
    for i in response['Items']:
        time.append(i['Time'])
        location.append(i['location'])
        workshop.append(i['workshop'])
        for w, t, l in zip(workshop, time, location):
            update = update_table.put_item(
                Item={
               'Username': event[0],
               'Workshop': event[1],
               'Time': t,
               'Location':l,
                'Registered_Time':datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                })




