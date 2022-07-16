from flask import Flask, request
import alert_sender
import gw_manager
import re
from multiprocessing import Process
app = Flask(__name__)
import sys,os
sys.path.append(os.path.abspath(os.path.pardir))
from db_structure import User, Channel, Message, session


def runapp(bind_address, port):
    app.secret_key = os.urandom(12)
    app.run(debug=False, host=bind_address, port=port, ssl_context="adhoc")

def createServer(bind_address, port):
    server = Process(target=runapp, args=(bind_address, port,))
    return server

def start(server):
    server.start()


def status(server):
    try:
        server.is_alive()
        return True
    except:
        return False


def stop(server):
    if server.is_alive():
        print("PASOAOSOASOASOASO")
        server.terminate()



def is_valid(key):
    if gw_manager.verify_apiKey(session, User, key):
        return True


def is_valid_ipv4(ip):
    """Validates IPv4 addresses.
    """
    pattern = re.compile(r"""
                ^
                (?:
                  # Dotted variants:
                  (?:
                    # Decimal 1-255 (no leading 0's)
                    [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
                  |
                    0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
                  |
                    0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
                  )
                  (?:                  # Repeat 0-3 times, separated by a dot
                    \.
                    (?:
                      [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
                    |
                      0x0*[0-9a-f]{1,2}
                    |
                      0+[1-3]?[0-7]{0,2}
                    )
                  ){0,3}
                |
                  0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
                |
                  0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
                |
                  # Decimal notation, 1-4294967295:
                  429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
                  42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
                  4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
                )
                $
            """, re.VERBOSE | re.IGNORECASE)
    return pattern.match(ip) is not None


def is_valid_ipv6(ip):
    """Validates IPv6 addresses.
    """
    pattern = re.compile(r"""
                ^
                \s*                         # Leading whitespace
                (?!.*::.*::)                # Only a single whildcard allowed
                (?:(?!:)|:(?=:))            # Colon iff it would be part of a wildcard
                (?:                         # Repeat 6 times:
                    [0-9a-f]{0,4}           #   A group of at most four hexadecimal digits
                    (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
                ){6}                        #
                (?:                         # Either
                    [0-9a-f]{0,4}           #   Another group
                    (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
                    [0-9a-f]{0,4}           #   Last group
                    (?: (?<=::)             #   Colon iff preceeded by exacly one colon
                     |  (?<!:)              #
                     |  (?<=:) (?<!::) :    #
                     )                      # OR
                 |                          #   A v4 address with NO leading zeros 
                    (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
                    (?: \.
                        (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
                    ){3}
                )
                \s*                         # Trailing whitespace
                $
            """, re.VERBOSE | re.IGNORECASE | re.DOTALL)
    return pattern.match(ip) is not None


@app.route('/sender/sendMessage2all/', methods=['POST'])
def sendMessage2all():
    if request.headers.get("key"):
        key = request.headers.get("key")
    else:
        return {"message": "Please provide an API key"}, 400
    if is_valid(key):
        t, nok = alert_sender.send2all(Message, User, Channel, session, key,
                                       request.form.get("message"))
        if t:
            return {"message": "Success"}, 200
        else:
            return {"message": nok}
    else:
        return {"message": "The provided API key is not valid"}, 400


@app.route('/sender/sendMessage/<channel>', methods=['POST'])
def sendMessage2channel(channel):
    if request.headers.get("key"):
        key = request.headers.get("key")
    else:
        return {"message": "Please provide an API key"}, 400
    if is_valid(key):
        t, nok = alert_sender.send2channel(Message, User, Channel, session, key,
                                           request.form.get("message"), channel)
        if t:
            return {"message": "Success"}, 200
        else:
            return {"message": nok}, 400
    else:
        return {"message": "The provided API key is not valid"}, 400