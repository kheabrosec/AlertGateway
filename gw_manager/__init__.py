import bcrypt
import os
from PyInquirer import style_from_dict, Token, prompt
import re
import configparser
import getpass
from input_channels import InputChannels_servers

style = style_from_dict({
    Token.QuestionMark: '#E91E63 bold',
    Token.Selected: '#673AB7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#2196f3 bold',
    Token.Question: '',
})

class CustomChannel():
    def __init__(self, method, name, params, dataVar):
        self.method = type
        self.name = name
        self.params = params
        self.dataVar = dataVar

def selectOption(options,message="Choose an option"):
    questions = [
        {
            'type': 'list',
            'name': 'action',
            'message': message,
            'choices': options,
            'filter': lambda val: val.lower()
        }
    ]
    answers = prompt(questions, style=style)
    return answers["action"]


def createNewCustomChannel(Channel):
    pass
def listChannels(session,Channel):
    consulta = session.query(Channel).all()
    print("{:<30} {:<10} {:<15} {:<35} {:<10}".format("NAME", "ENABLED", "TYPE", "KEY","PARAMETERS"))
    for channel in consulta:
        print("{:<30} {:<10} {:<15} {:<35} {:<10}".format(channel.channel_name,channel.channel_enable, channel.channel_type, channel.channel_key, channel.channel_parameters))

def listInputChannels(session,InputChannel):
    consulta = session.query(InputChannel).all()
    print("{:<20} {:<40} {:<16} {:<6} {:<10}".format("NAME", "LOCATION", "BIND ADDRESS", "PORT", "STATUS"))
    for input_channel in consulta:
        print("{:<20} {:<40} {:<16} {:<6} {:<10}".format(str(input_channel.input_channel_name), str(input_channel.input_channel_location),
                                                          str(input_channel.input_channel_address), str(input_channel.input_channel_port),
                                                          str(input_channel.input_channel_status)))
def verifyChannelName(session,Channel,channel_name):
    if not channel_name.isalnum():
        while True:
            channel_name = input("Illegal channel name... enter an alphanumeric name: ")
            if channel_name.isalnum():
                return channel_name
    if not isUnique_channel(session, Channel, channel_name):
        while True:
            channel_name = input("That channel name already exists... enter a channel name: ")
            if isUnique_channel(session, Channel, channel_name):
                return channel_name
    return channel_name

def isUnique_Inputchannel(session,InputChannel,channel_name):
    consulta = session.query(InputChannel).filter_by(input_channel_name=channel_name).first()
    if consulta == None:
        return False
    return True
def newChannel(session,Channel, User):
    print("Creating new channel...")
    files = getAllChannels()

    questions = [
        {
            'type': 'list',
            'name': 'channel',
            'message': 'Choose the channel: ',
            'choices': files
        }
    ]

    answers = prompt(questions, style=style)
    channel = answers["channel"]
    config_files = []
    for file in os.listdir("channels//" + channel):
        if re.findall("\.conf", file):
            config_files.append(file)
    if len(config_files) == 0:
        print("Not config files found, please create one (Remember that file must end with .conf)")
    else:
        questions = [
            {
                'type': 'list',
                'name': 'confile',
                'message': 'Config files found, select one: ',
                'choices': config_files
            }
        ]

        answers = prompt(questions, style=style)
        confile = answers["confile"]
        config = configparser.RawConfigParser()
        config.read("channels//" + channel + "//" + confile)
        channel_name = str(config.get("channel","name"))
        channel_user = str(config.get("channel", "user"))
        channel_type = str(config.get("channel", "type"))

        if not verifyChannelName(session,Channel,channel_name):
            return False
        if not verify_user(session, User, channel_user):
            print("Wrong username... please enter a valid user.")
            return False
        questions = [
            {
                'type': 'confirm',
                'name': 'enable',
                'message': 'Do you want to enable this channel?'.format(channel),
                'default': True
            }
        ]
        answers = prompt(questions, style=style)
        new_channel = Channel(channel_name,channel_type, getApiKey(session, User, username=channel_user), str(config._sections[channel_type]),answers["enable"])
        session.add(new_channel)
        session.commit()
        print("NEW CHANNEL ADDED: ")
        print("NAME: "+ channel_name)
        print("KEY: " + str(getApiKey(session, User, channel_user)) + " USER: "+ channel_user)
        print("PARAMETERS: "+ str(config._sections[channel_type]))
        print("ENABLED: " + str(answers["enable"]))

def newInputChannel(session,InputChannel):
    print("Creating new input channel...")
    files = getAllInputChannelsModules()

    questions = [
        {
            'type': 'list',
            'name': 'channel',
            'message': 'Choose the channel: ',
            'choices': files
        }
    ]

    answers = prompt(questions, style=style)
    channel = answers["channel"]
    if isUnique_Inputchannel(session,InputChannel,channel):
        print("This input channel already exists, please select other channel...")
        newInputChannel(session,InputChannel)
    print("Input channels are disabled by default, you have to start it from the web service.")
    port = 0
    while not((port > 1) and (port < 65535)):
        port = int(input("Enter a valid port: "))
    new_input_channel = InputChannel(channel, "input_channels/"+channel, input("Enter a valid bind-address: "),port, False,"")
    session.add(new_input_channel)
    session.commit()
    import AlertGateway
    AlertGateway.InputChannels_servers = InputChannels_servers()

def deleteChannel(session,Channel,channel_id):
    session.query(Channel).filter_by(channel_id=channel_id).delete()
    session.commit()
    return True

def deleteInputChannel(session,InputChannel,channel_id):
    session.query(InputChannel).filter_by(input_channel_id=channel_id).delete()
    session.commit()
    return True

def removeChannel(session,Channel):
    channels = []
    for channel in session.query(Channel).all():
        channels.append(channel.channel_name)
    channels.append("BACK")
    questions = [
        {
            'type': 'list',
            'name': 'channel',
            'message': 'Select a channel to remove: ',
            'choices': channels
        }
    ]
    answers = prompt(questions, style=style)
    channel = answers["channel"]
    if channel == "BACK":
        return False
    questions = [
        {
            'type': 'confirm',
            'name': 'remove',
            'message': 'Do you confirm that you want to DELETE this channel: {} ?'.format(channel),
            'default': False
        }
    ]
    answers = prompt(questions, style=style)
    if answers["remove"]:
        session.query(Channel).filter_by(channel_name=channel).delete()
        return True
    else:
        removeChannel(session,Channel)

def removeInputChannel(session,InputChannel):
    channels = []
    for channel in getAllInputChannels(session,InputChannel):
        channels.append(channel.input_channel_name)
    channels.append("BACK")

    questions = [
        {
            'type': 'list',
            'name': 'channel',
            'message': 'Select a channel to remove: ',
            'choices': channels
        }
    ]
    answers = prompt(questions, style=style)
    channel = answers["channel"]
    if channel == "BACK":
        return False
    questions = [
        {
            'type': 'confirm',
            'name': 'remove',
            'message': 'Do you confirm that you want to DELETE this channel: {} ?'.format(channel),
            'default': False
        }
    ]
    answers = prompt(questions, style=style)
    if answers["remove"]:
        session.query(InputChannel).filter_by(input_channel_name=channel).delete()
        session.commit()
        return True
    else:
        removeInputChannel(session,InputChannel)

def changeUsername(session,User,id,name):
    consulta = session.query(User).get(id)
    consulta.user_name = name
    session.commit()
    return True

def changeUserpass(session,User,id,password):
    consulta = session.query(User).get(id)
    try:
        password_new = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt()).decode()
    except:
        password_new = bcrypt.hashpw(password, bcrypt.gensalt())
    consulta.user_pass = password_new
    session.commit()
    return True

def getUserByKey(session,User,key):
    consulta = session.query(User).filter_by(user_key=key).first()
    username = consulta.user_name
    return username


def getUserByid(session,User,id):
    consulta = session.query(User).get(id)
    return consulta

def getUserNameByid(session,User,id):
    consulta = session.query(User).get(id)
    return consulta.user_name

def getKeyByid(session,User,id):
    consulta = session.query(User).get(id)
    return consulta.user_key

def getMessagesByKey(session,Messages,key):
    consulta = session.query(Messages).filter_by(message_key=key).all()
    messages = []
    for message in consulta:
        messages.append(message)
    return messages

def getChannelsByKey(session,Channel,key):
    consulta = session.query(Channel).filter_by(channel_key=key).all()
    channels = []
    for channel in consulta:
        channels.append(channel)
    return channels

def newMessage(session,Message,User,key,channel,message,receiver):
    new_message = Message(getUserByKey(session,User,key),channel,message,receiver)
    session.add(new_message)
    session.commit()

def listUsers(session,User):
    consulta = session.query(User).all()
    print("TOTAL USERS : {}".format(len(consulta)))
    print("{:<12} {:<60} {:<10}".format("Username","Password","API KEY"))
    for user in consulta:
        print("{:<12} {:<60} {:<10}".format(str(user).split(";")[0],str(user).split(";")[1],str(user).split(";")[2]))
    #createGW.manageUsers(session)

def listMessages(session,Message):
    consulta = session.query(Message).all()
    print("TOTAL MESSAGES : {}".format(len(consulta)))
    print("{:<5} {:<30} {:<15} {:25} {:<40} {:<20}".format("ID","CHANNEL","SENDER", "RECEIVER","DATETIME","DATA"))
    for message in consulta:
        try:
            print("TRY")
            print("{:<5} {:<30} {:<15} {:<25} {:<40} {:<20}".format(str(message).split(";")[0],
                                                                    str(message).split(";")[1],
                                                                    str(message).split(";")[2],
                                                                    str(str(message).split(";")[3].split("/")[len(str(message).split(";")[3].split("/")) -1 ][:20]),
                                                                    str(message).split(";")[4],
                                                                    str(message).split(";")[5]))
        except:
            print("EXCEPT")
            print("{:<5} {:<30} {:<15} {:<25} {:<40} {:<20}".format(str(message).split(";")[0],
                                                                    str(message).split(";")[1],
                                                                    str(message).split(";")[2],
                                                                    str(message).split(";")[3],
                                                                    str(message).split(";")[4],
                                                                    str(message).split(";")[5]))

def addUser(session,User):
    username = input("Username: ")
    while True:
        password1 = getpass.getpass(prompt="Password: ")
        password2 = getpass.getpass(prompt="Repeat your password: ")
        if password1 == password2:
            break
    password = bcrypt.hashpw(password1.encode("utf8"), bcrypt.gensalt()).decode()
    user = User(username, password)
    session.add(user)
    session.commit()

def getApiKey(session,User,username):
    consulta = str(session.query(User).filter_by(user_name=username).first()).split(";")
    key = consulta[len(consulta)-1]
    return key

def verify_apiKey(session,User,key):
    consulta = str(session.query(User).filter_by(user_key=key).first()).split(";")
    consulta = consulta[len(consulta)-1]
    if str(consulta) == str(key):
        return True
    return False

def verify_user(session,User,user):
    consulta = session.query(User).filter_by(user_name=user).first()
    if consulta == None:
        return False
    return True

def verify_channel(session,Channel,key,channel):
    consulta = session.query(Channel).filter_by(channel_name=channel).first()
    try:
        if consulta.channel_enable == "False":
            return False, "Channel disabled."
        if consulta.channel_key == key:
            return consulta.channel_type,consulta.channel_parameters
        else:
            return False, "Forbidden."
    except:
        return False, "Not found"

def isUnique_channel(session,Channel,channel):
    consulta = str(session.query(Channel).filter_by(channel_name=channel).first()).split(";")
    if consulta[0] == 'None':
        return True
    return False

def getChannels(session,Channel,key):
    consulta = session.query(Channel).filter_by(channel_key=key).all()
    try:
        if consulta[0] == 'None':
            return False
        return consulta
    except:
        return False

def getMessages(session,Message,key):
    consulta = session.query(Message).filter_by(message_sender=key).all()
    try:
        if consulta[0] == 'None':
            return False
        return consulta
    except:
        return False

def editChannelName(session,Channel):
    channels = []
    for channel in session.query(Channel).all():
        channels.append(channel.channel_name)
    channels.append("BACK")
    questions = [
        {
            'type': 'list',
            'name': 'channel',
            'message': 'Select a channel to edit: ',
            'choices': channels
        }
    ]
    answers = prompt(questions, style=style)
    channelOld = answers["channel"]

    questions = [
        {
            'type': 'input',
            'name': 'name',
            'message': 'Enter the new name for the channel:'
        }
    ]

    answers = prompt(questions, style=style)
    channelNew = answers["name"]
    verified_name = verifyChannelName(session, Channel, channelNew)
    if not verified_name:
        return False
    consulta = session.query(Channel).filter_by(channel_name=channelOld).first()
    consulta.channel_name = channelNew
    session.commit()

def editChannelStatus(session,Channel):
    channels = []
    for channel in session.query(Channel).all():
        channels.append(channel.channel_name)
    channels.append("BACK")
    questions = [
        {
            'type': 'list',
            'name': 'channel',
            'message': 'Select a channel to edit: ',
            'choices': channels
        }
    ]
    answers = prompt(questions, style=style)
    channelOld = answers["channel"]
    channel = session.query(Channel).filter_by(channel_name=channelOld).first()
    newstatus = False
    if channel.channel_enable == True:
        questions = [
            {
                'type': 'confirm',
                'name': 'newstatus',
                'message': 'Do you wan\'t to disable this channel?',
            }
        ]
        answers = prompt(questions, style=style)
        if answers["newstatus"]:
            newstatus = False
        else:
            return False
    else:
        questions = [
            {
                'type': 'confirm',
                'name': 'newstatus',
                'message': 'Do you wan\'t to enable this channel?',
            }
        ]
        answers = prompt(questions, style=style)
        if answers["newstatus"]:
            newstatus = True
        else:
            return False
    print("NEWSTATUS ",newstatus)
    consulta = session.query(Channel).filter_by(channel_name=channelOld).first()
    consulta.channel_enable = newstatus
    session.commit()
    return True, newstatus

def changeChannelName(session,Channel,id,name):
    if name.isalnum():
        if isUnique_channel(session,Channel,name):
            channel = session.query(Channel).get(id)
            channel.channel_name = name
            session.commit()
            return True
        else:
            return False
    else:
        return False

def changeChannelStatus(session,Channel,id,status):
    channel = session.query(Channel).get(id)
    channel.channel_enable = status
    session.commit()
    return True

def changeInputChannelStatus(session,InputChannel,User,id,status,user):
    channel = session.query(InputChannel).get(id)
    if status == True:
        channel.input_channel_status = status
        channel.input_channel_key = getKeyByid(session,User,user)
        session.commit()
    else:
        if (channel.input_channel_key == getKeyByid(session,User,user)) or (channel.input_channel_key == ""):
            channel.input_channel_status = status
            channel.input_channel_key = getKeyByid(session,User,user)
            session.commit()
        else:
            return False
    return True

def changeChannelParameters(session,Channel,id,new_parameters):
    channel = session.query(Channel).get(id)
    channel.channel_parameters = new_parameters
    session.commit()
    return True

def verifyLogin(session,User,username,password):
    consulta = session.query(User).filter_by(user_name=username).first()
    if consulta == None:
        return False, None
    try:
        if bcrypt.hashpw(password.encode("utf8"), consulta.user_pass.encode("utf8")).decode() == consulta.user_pass:
            return True, consulta
        else:
            return False, None
    except:
        if bcrypt.hashpw(password, consulta.user_pass).decode() == consulta.user_pass:
            return True, consulta
        else:
            return False, None

def removeUser(session,User,username):
    pass

def addChannel(session,Channel,channel_name, channel_type, key, parameters, status):
    if status == "Enabled":
        status = True
    else:
        status = False
    print("CHANNEL ALNUM",channel_name.isalnum())
    if channel_name.isalnum() and isUnique_channel(session,Channel,channel_name):
        channel = Channel(channel_name, channel_type, key, parameters, status)
        session.add(channel)
        session.commit()
        return True, "OK"
    else:
        return False, "Illegal Name"



def checkDBhealth(session):
    return True

def getAllChannels():
    files = []
    for file in os.listdir("channels"):
        if not file.startswith('.'):
            files.append(file)
    return files

def getAllInputChannelsModules():
    files = []
    for file in os.listdir("input_channels"):
        if not file.startswith('.'):
            files.append(file)
    return files
def getAllDBs():
    files = []
    for file in os.listdir("databases"):
        if not file.startswith('.'):
            files.append(file)
    return files
def getAllUsers(session,User):
    users = []
    consulta = session.query(User).all()
    for user in consulta:
        users.append(user.user_name)
    return users

def getAllInputChannels(session,InputChannel):
    users = []
    consulta = session.query(InputChannel).all()
    for channel in consulta:
        users.append(channel)
    return users

def getAllActiveInputChannels(session,InputChannel):
    users = []
    consulta = session.query(InputChannel).all()
    for channel in consulta:
        if channel.input_channel_status:
            users.append(channel)
    return users


def deleteUser(session,User,Channel,username):
    user = session.query(User).filter_by(user_name=username).first()
    channels = getChannelsByKey(session, Channel, user.user_key)
    for channel in channels:
        deleteChannel(session, Channel, channel.channel_id)
    session.query(User).filter_by(id=user.id).delete()
    session.commit()
    return True

def disableAllInputChannels(session,InputChannel):
    channels = session.query(InputChannel).all()
    for channel in channels:
        channel.input_channel_status = False
    session.commit()

def shutdownAllServers():
    servers = InputChannels_servers()
    servers.shutdownall()

