import json
import requests

def sendMessage(message,parameters):

    parameters = json.loads(parameters.replace("'",'"'))
    OK = []
    NOK = []
    chatids = parameters["chat-id"].split(",")
    for chatid in chatids:
        send_text = 'https://api.telegram.org/bot' + parameters["bot-key"] + '/sendMessage?chat_id=' + chatid + '&parse_mode=Markdown&text=' + str(message)
        response = requests.get(send_text)
        if response.status_code in range(199, 300):
            OK.append(chatid)
        else:
            NOK.append(chatid)
    if len(OK) == 0:
        return False, NOK
    else:
        if len(NOK) == 0:
            return True, OK
        else:
            return False, (OK, NOK)