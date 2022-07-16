import logging
import socketserver
from multiprocessing import Process
import alert_sender
import json
from db_structure import User, Channel, Message, session


class SyslogUDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = bytes.decode(self.request[0].strip())
        socket = self.request[1]
        alertgw = data.split("|ALERTGW|")[1]
        data = data.split("|ALERTGW|")[0]
        alertgw = json.loads(alertgw)
        if alertgw["channel"] == "*":
            alert_sender.send2all(Message,User,Channel,session,alertgw["token"],data)
        else:
            alert_sender.send2channel(Message,User,Channel,session,alertgw["token"],data,alertgw["channel"])
        print( "%s : " % self.client_address[0], str(data))
        logging.info(str(data))

def createServer(bind_address, port):
    server = Process(target=main, args=(bind_address, port,))
    return server

def start(server):
    server.start()


def stop(server):
    server.terminate()

def main(HOST,PORT):
    try:
        server = socketserver.UDPServer((HOST,PORT), SyslogUDPHandler)
        server.serve_forever(poll_interval=0.5)
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print ("Crtl+C Pressed. Shutting down.")