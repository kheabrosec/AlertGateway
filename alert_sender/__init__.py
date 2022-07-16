import importlib
import gw_manager

def send2all(Message,User,Channel,session,key,message):
    channels = gw_manager.getChannels(session,Channel,key)
    not_received = 0
    inactive_channels = 0
    if channels:
        for channel in channels:
            response, param = send2channel(Message,User,Channel,session,key,message,channel.channel_name)
            if not response:
                try:
                    if param == "Channel disabled.":
                        inactive_channels += 1
                    else:
                        not_received += int(param.split(" ")[4])
                except:
                    inactive_channels += 1
        if not_received != 0:
            return False, "Message not sended to {} receivers, {} channels disabled.".format(str(not_received),str(inactive_channels))
        else:
            return True, ""
    else:
        return False, "Forbidden"

def send2channel(Message,User,Channel,session,key,message,channel):
    message = str(message)
    print("Sending message to: "+channel)
    channel_type,parameters = gw_manager.verify_channel(session,Channel,key,channel)
    if channel_type:
        ch = importlib.import_module("channels."+channel_type)
        try:
            response, receivers = ch.sendMessage(message, parameters)
        except:
            return False, parameters
        if response:
            for receiver in receivers:
                gw_manager.newMessage(session,Message,User,key,channel,message,receiver)
            return True, receivers
        else:
            for receiver in receivers[0]:
                gw_manager.newMessage(session, Message, User, key, channel, message, receiver)
            return False, "Message not sended to {} receivers.".format(str(len(receivers)))
    else:
        print("NO PASA",parameters)
        return False, parameters