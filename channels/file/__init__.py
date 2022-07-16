import json
import os

def sendMessage(message,parameters):
    print("PARAMETERS",parameters)
    parameters = json.loads(parameters.replace("'",'"'))
    files = parameters["file"]
    OK = []
    NOK = []
    for file in files.split(","):
        try:
            f = open(file, "a+")
            f.write(str(message) + "\n")
            f.close()
            OK.append(file)
        except Exception as e:
            NOK.append(file)
    if len(OK) == 0:
        return False, NOK
    else:
        if len(NOK)==0:
            return True, OK
        else:
            return False, (OK,NOK)