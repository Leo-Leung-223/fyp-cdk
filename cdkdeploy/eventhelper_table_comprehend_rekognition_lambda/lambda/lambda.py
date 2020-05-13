import decimal,csv,json,boto3,logging

from boto3.dynamodb.conditions import Key, Attr
# import numpy as np
from datetime import datetime


def comprehend():
  client = boto3.resource('dynamodb')
  table = client.Table('eventhelper_comprehend')
  s3=boto3.client('s3')
  s3bucket='ryanlw123'
  bootname=''
  output=[]
  if bootname != '':
    response = table.scan(Select="ALL_ATTRIBUTES", FilterExpression=bootname)
  else:
    response = table.scan(Select="ALL_ATTRIBUTES")
  lst=response['Items']
  for data in lst:
    for key, value in data.items():
      if key == 'Time':
          data['Time']=datetime.fromtimestamp(value).strftime('%d/%m/%Y %H:%M:%S')

    output.append(data)
  try:
    with open('/tmp/comprehend.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile,fieldnames=['Boothname','Time','Result','Text','Username'])
        writer.writeheader()
        for row in output:
          writer.writerow(row)
    s3.upload_file('/tmp/comprehend.csv',s3bucket,'comprehend.csv')
  except IOError:
    print("I/O error")
    

def rekognition():
  client = boto3.resource('dynamodb')
  table = client.Table('eventhelper_rekognition')
  s3=boto3.client('s3')
  s3bucket='ryanlw123'
  bootname=''
  output=[]
  if bootname != '':
    response = table.scan(Select="ALL_ATTRIBUTES", FilterExpression=bootname)
  else:
    response = table.scan(Select="ALL_ATTRIBUTES")
  lst=response['Items']
  for data in lst:
    for key, value in data.items():
      if key == 'Time':
          data['Time']=datetime.fromtimestamp(value).strftime('%d/%m/%Y %H:%M:%S')
    output.append(data)
  try:
    with open('/tmp/rekognition.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile,fieldnames=['Username','Time','Emotion','Boothname','Ages'])
        writer.writeheader()
        for row in output:
          writer.writerow(row)
    s3.upload_file('/tmp/rekognition.csv',s3bucket,'rekognition.csv')
  except IOError:
    print("I/O error")
    
def lambda_handler(event, context):
    logging.info('event')
    rekognitionfunction=rekognition()
    comprehendfunction=comprehend()