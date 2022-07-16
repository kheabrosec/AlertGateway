from multiprocessing import Process
from datetime import datetime
import asyncore
from smtpd import SMTPServer
from alert_sender import send2channel
from db_structure import Message,User,Channel,session

class EmlServer(SMTPServer):
    no = 0
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        filename = '%s-%d.eml' % (datetime.now().strftime('%Y%m%d%H%M%S'),
            self.no)
        for rcp in rcpttos:
            send2channel(Message, User, Channel, session, mailfrom.split("@")[0], data.decode(), rcp.split("@")[0])
        self.no += 1


def main(bind_address,port):
    foo = EmlServer((bind_address, port), None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass




def createServer(bind_address, port):
    server = Process(target=main, args=(bind_address, port,))
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
    server.terminate()
