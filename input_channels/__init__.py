import gw_manager
from db_structure import *
import importlib


class InputChannels_servers():
    input_channels = {}
    def __init__(self):
        for channel in gw_manager.getAllInputChannels(session, InputChannel):
            if channel.input_channel_status == False:
                predict = {}
                predict["funct"] = "input_channels." + channel.input_channel_location.split("/")[
                    len(channel.input_channel_location.split("/")) - 1]
                ch = importlib.import_module(predict["funct"])

                server = ch.createServer(bind_address=channel.input_channel_address, port=channel.input_channel_port)
                self.input_channels[channel.input_channel_name] = server
    def getProcesses(self):
        return self.input_channels
    def shutdownall(self):
        for channel in gw_manager.getAllInputChannels(session, InputChannel):
            predict = {}
            predict["funct"] = "input_channels." + channel.input_channel_location.split("/")[
                len(channel.input_channel_location.split("/")) - 1]
            ch = importlib.import_module(predict["funct"])
            for key in self.input_channels:
                if ch.status(self.input_channels[key]):
                    print("PASO")
                    ch.stop(self.input_channels[key])