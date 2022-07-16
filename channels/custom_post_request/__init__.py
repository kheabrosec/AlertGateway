import requests
import json

def sendMessage(message,parameters):
    parameters = json.loads(str(parameters).replace("'", '"'))
    OK = []
    NOK = []
    datavar = parameters["datavar"]
    if "receivers" in parameters:
        url = parameters["url"]
        del parameters["url"]
        receivers = parameters["receivers"].split(",")
        del parameters["receivers"]
        for receiver in receivers:
            url = url.replace("receiver", receiver)
            for key, value in parameters.items():
                url = url.replace(key, value)
            data = {datavar: message}
            response = requests.post(url, json=data)
            if response.status_code in range(199,300):
                OK.append(url)
            else:
                NOK.append(url)
    else:
        if "urls" in parameters:
            urls = parameters["urls"]
            del parameters["url"]
            for url in urls:
                for key, value in parameters.items():
                    url = url.replace(key, value)
                data = {datavar: message}
                response = requests.post(url, json=data)
                if response.status_code in range(199, 300):
                    OK.append(url)
                else:
                    NOK.append(url)
        else:
            url = parameters["url"]
            del parameters["url"]
            for key, value in parameters.items():
                url = url.replace(key, value)
            data = {datavar: message}
            response = requests.post(url, json=data)
            if response.status_code in range(199, 300):
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

#Example {'url':'https://discord.com/api/webhooks/992135264778588252/SkzgihKCToHndrYvZpKbQegspmtB0sZlPa5-lcaclia38s23xxg01v9v7-l9jv82JSLQ','datavar': 'content'})
