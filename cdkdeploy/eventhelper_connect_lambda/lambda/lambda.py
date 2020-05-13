import json
import boto3
import logging
import os
import botocore.session
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

session = botocore.session.get_session()
logging.basicConfig(level=logging.DEBUG)
logger=logging.getLogger(__name__)

def lambda_handler(event, context):
    logger.setLevel(logging.DEBUG)
    logger.debug("Event is --- %s" %event)
       
    ContactFlowId = os.environ['ContactFlowId']              #Getting the Amazon Connect ContactFlowID passed in by the environment variables.
    InstanceId = os.environ['InstanceId']                    #Getting the Amazon Connect InstanceId passed in by the environment variables.
    SourcePhoneNumber = os.environ['SourcePhoneNumber']      #Getting the Source Phone Number passed in by the environment variables. This phone number is your Amazon Connect phone number.
    uuid=event[0]
    boothname=event[2].replace("_", " ")
    DestPhoneNumber='+852{}'.format(event[1])# Getting the destination phone number passed in by the environment variables.
    user_info=querdb(uuid)[0]
    user_company=user_info['company']
    user_postion=user_info['position']
    user_full_name=user_info['fullName']

    logger.debug("DestPhoneNumber is-- %s" %DestPhoneNumber)

    client = boto3.client('iam')
    connectclient = boto3.client('connect')
    response = client.list_account_aliases()
    logger.debug("List account alias response --- %s" %response)
    
    try:
      if not response['AccountAliases']:
          accntAliase = (boto3.client('sts').get_caller_identity()['Account'])
          logger.info("Account alias is not defined. Account ID is %s" %accntAliase)
      else:
          accntAliase = response['AccountAliases'][0]
          logger.info("Account alias is : %s" %accntAliase)
    
    except ClientError as e:
      logger.error("Client error occurred")
    
    try: 
      #Making the outbound phone alert...
      OutboundResponse = connectclient.start_outbound_voice_contact(
                      DestinationPhoneNumber=DestPhoneNumber,
                      ContactFlowId=ContactFlowId,
                      InstanceId=InstanceId,
                      SourcePhoneNumber=SourcePhoneNumber ,
                      Attributes={'Message': 'This is the user alert: {} {} {} calling from the {}'.format(user_company,user_postion,user_full_name,boothname)
                                  }
                      )
    
      logger.debug("outbound Call response is-- %s" %OutboundResponse)
    except ClientError as e:
      logger.error("An error occurred: %s" %e)
      
      
def querdb(username):
  client = boto3.resource('dynamodb')
  table = client.Table('userdataTable')
  fe = Key('userName').eq(username)

  response = table.scan(
      FilterExpression=fe,
      )


  result=response['Items']
  return result