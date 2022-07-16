import requests
import json
# Import smtplib for the actual sending function
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import ssl
# Import the email modules we'll need
from email.mime.text import MIMEText

def sendMessage(message,parameters):
    parameters = json.loads(parameters.replace("'",'"'))
    emails = parameters["emails"]

    try:
        subject = parameters["subject"]
    except:
        subject = None
    smtp_server = parameters["server"]
    smtp_server_port = parameters["port"]
    sent_from = parameters["from"]

    OK = []
    NOK = []
    for email in emails.split(","):
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = sent_from
        msg["To"] = email
        msg["Date"] = formatdate(localtime=True)
        try:
            server = smtplib.SMTP(smtp_server,smtp_server_port)
            server.starttls()
            if parameters["auth"].lower() == "yes":
                user = parameters["user"]
                password = parameters["password"]
                server.login(user,password)
            server.sendmail(sent_from, email, msg.as_string())
            server.close()
            OK.append(email)
        except Exception as e:
            print(e)
            NOK.append(email)
    if len(OK) == 0:
        return False, NOK
    else:
        if len(NOK)==0:
            return True, OK
        else:
            return False, (OK,NOK)