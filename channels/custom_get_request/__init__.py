import requests
import json


def sendMessage(message,parameters):
    parameters = json.loads(str(parameters).replace("'",'"'))
    url = parameters["url"]
    del parameters["url"]
    OK = []
    NOK = []
    receivers = parameters["receivers"].split(",")
    del parameters["receivers"]
    for receiver in receivers:
        url = url.replace("receiver",receiver)
        url = url.replace("message",message)
        for key,value in parameters.items():
            url = url.replace(key,value)
        print(url)
        response = requests.get(url)
        if response.status_code in range(199,300):
            OK.append(url)
        else:
            NOK.append(url)
        if len(OK) == 0:
            return False, NOK
        else:
            if len(NOK)==0:
                return True, OK
            else:
                return False, (OK,NOK)


#Example {'url':'https://api.telegram.org/botbot_key/sendMessage?chat_id=receiver&parse_mode=Markdown&text=message','receivers':'receiviwiowneroiwner','bot_key':'keyuansoidufaosdnf'})
