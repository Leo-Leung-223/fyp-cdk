import boto3

slotName = 'BoothName'              # slot name
botName = 'TempGuide'               # bot name
client = boto3.client('lex-models')
ses = boto3.client('ses')

# build bot at the end


def update_bot():
    try:
        bot = client.get_bot(
            name=botName,
            versionOrAlias='$LATEST'
        )
        for intent in bot['intents']:
            intent['intentVersion'] = '$LATEST'
        output = client.put_bot(
            name=botName,
            intents=bot['intents'],
            locale=bot['locale'],
            childDirected=bot['childDirected'],
            checksum=bot['checksum'],
            abortStatement=bot['abortStatement']
        )
    except Exception as e:
        print(e)
    return


def update_intent():
    try:
        intent = client.get_intent(
            name='aboutBooth',
            version='$LATEST'
        )
        intent['slots'][0]['slotTypeVersion'] = '$LATEST'
        response = client.put_intent(
            name='aboutBooth',
            checksum=intent['checksum'],
            slots=intent['slots'],
            sampleUtterances=intent['sampleUtterances'],
            fulfillmentActivity=intent['fulfillmentActivity']
        )
    except Exception as e:
        print(e)
    else:
        update_bot()
    return


def update_slot(name_list):
    try:
        getSlot = client.get_slot_type(
            name=slotName,
            version='$LATEST'
        )
        if name_list['INSERT']:
            for name in name_list['INSERT']:
                newRecordInJson = {
                    'value': name,
                    'synonyms': name.split()
                }
                getSlot['enumerationValues'].append(newRecordInJson)
        elif name_list['MODIFY']:
            for name in name_list['MODIFY']:
                # Found name location from list of dict.
                location = [dic['value']
                            for dic in getSlot['enumerationValues']].index(name[1])
                getSlot['enumerationValues'][location]['value'] = name[0]
                getSlot['enumerationValues'][location]['synonyms'] = name[0].split()
        elif name_list['REMOVE']:
            for name in name_list['REMOVE']:
                # Found name location from list of dict.
                location = [dic['value']
                            for dic in getSlot['enumerationValues']].index(name)
                del getSlot['enumerationValues'][location]
        response = client.put_slot_type(
            name=slotName,
            enumerationValues=getSlot['enumerationValues'],
            checksum=getSlot['checksum']
        )
    except Exception as e:
        print(e)
        return
    else:
        update_intent()
    return


def db_stream(event, context):
    name_list = {
        'INSERT': [],
        'MODIFY': [],
        'REMOVE': []
    }
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            name_list['INSERT'].append(
                record['dynamodb']['NewImage']['Name']['S'])
        elif record['eventName'] == 'MODIFY':
            name_list['MODIFY'].append(
                [record['dynamodb']['NewImage']['Name']['S'], record['dynamodb']['OldImage']['Name']['S']])
        elif record['eventName'] == 'REMOVE':
            name_list['REMOVE'].append(
                record['dynamodb']['OldImage']['Name']['S'])
    try:
        update_slot(name_list)
    except Exception as e:
        print(e)
    return
