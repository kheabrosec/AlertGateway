import requests
import json

def sendMessage(message,parameters):

    parameters = json.loads(parameters.replace("'",'"'))
    urls = parameters["webhook"]
    OK = []
    NOK = []
    for url in urls.split(","):
        headers = {'Content-type': 'application/json'}
        data = {"text": message}
        response = requests.post(url, json=data, headers=headers)
        if response.status_code in range(199, 300):
            OK.append(url)
        else:
            NOK.append(url)
    if len(OK) == 0:
        return False, NOK
    else:
        if len(NOK) == 0:
            return True, OK
        else:
            return False, (OK, NOK)