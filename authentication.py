import os
import settings
def validate(chatID):
    '''
    Check whether a user is the admin.
    '''
    if not isinstance(chatID, str):
        chatID = str(chatID)

    with open(os.sep.join([settings.CWD, 'authorized']), 'r') as fin:
        validated = [i.replace('\n', '') for i in fin.readlines()]

    return chatID in validated

def add(chatID):
    if not isinstance(chatID, str):
        chatID = str(chatID)
    
    if validate(chatID):
        return True

    with open(os.sep.join([settings.CWD, 'authorized']), 'a') as fin:
        fin.write(chatID + '\n')
        return True
    return False
