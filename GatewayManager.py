# -*- coding: utf-8 -*-
import db_structure
#from __future__ import print_function, unicode_literals
from PyInquirer import style_from_dict, Token, prompt
import os
import gw_manager
import sys
import db_selector
from db_structure import *

style = style_from_dict({
    Token.QuestionMark: '#E91E63 bold',
    Token.Selected: '#673AB7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#2196f3 bold',
    Token.Question: '',
})


def manageChannels(session,Channel,InputChannel):
    questions = [
        {
            'type': 'list',
            'name': 'action',
            'message': 'Que acción deseas tomar?',
            'choices': ["List active output channels","List active input channels","Create new output channel","Create new input channel","Remove channel","Remove input channel","Edit channel","BACK"],
            'filter': lambda val: val.lower()
        }
    ]

    answers = prompt(questions, style=style)
    if answers["action"] == "list active output channels":
        gw_manager.listChannels(session,Channel)
        manageChannels(session,Channel,InputChannel)
    elif answers["action"] == "list active input channels":
        gw_manager.listInputChannels(session,InputChannel)
        manageChannels(session,Channel,InputChannel)
    elif answers["action"] == "create new output channel":
        gw_manager.newChannel(session,Channel, User)
        if manageChannels(session,Channel,InputChannel) == False:
            print("Can't create a new channel.")
    elif answers["action"] == "create new input channel":
        gw_manager.newInputChannel(session,InputChannel)
        if manageChannels(session,Channel,InputChannel) == False:
            print("Can't create a new channel.")
    elif answers["action"] == "remove channel":
        if gw_manager.removeChannel(session,Channel):
            print("Channel deleted.")
    elif answers["action"] == "remove input channel":
        if gw_manager.removeInputChannel(session, InputChannel):
            print("Channel deleted.")
        manageChannels(session,Channel,InputChannel)
    elif answers["action"] == "edit channel":
        response = gw_manager.selectOption(["Edit name","Edit status", "BACK"])
        if response == "edit name":
            gw_manager.editChannelName(session,Channel)
            manageChannels(session,Channel,InputChannel)
        elif response == "edit status":
            gw_manager.editChannelStatus(session,Channel)
            manageChannels(session,Channel,InputChannel)
        manageChannels(session,Channel,InputChannel)


def manageUsers(session,User):
    questions = [
        {
            'type': 'list',
            'name': 'action',
            'message': 'Que acción deseas tomar?',
            'choices': ["List users","Add user","Remove user","Get api key","BACK"],
            'filter': lambda val: val.lower()
        }
    ]

    answers = prompt(questions, style=style)

    if answers["action"] == "list users":
        gw_manager.listUsers(session,User)
        manageUsers(session, User)
    elif answers["action"] == "add user":
        gw_manager.addUser(session,User)
        manageUsers(session, User)
    elif answers["action"] == "remove user":
        questions = [
            {
                'type': 'list',
                'name': 'user',
                'message': 'Select a user to remove: ?',
                'choices': gw_manager.getAllUsers(session, User),
            }
        ]

        answers = prompt(questions, style=style)
        username = answers["user"]
        gw_manager.deleteUser(session,User,Channel,username)
        manageUsers(session, User)
    elif answers["action"] == "get api key":
        key = gw_manager.getApiKey(session,User,str(input("Username: ")))
        print(key)
        manageUsers(session, User)
def selectDB():
    import db_selector
    style = style_from_dict({
        Token.QuestionMark: '#E91E63 bold',
        Token.Selected: '#673AB7 bold',
        Token.Instruction: '',  # default
        Token.Answer: '#2196f3 bold',
        Token.Question: '',
    })
    dblist = gw_manager.getAllDBs()

    questions = [
        {
            'type': 'rawlist',
            'name': 'database',
            'message': 'Choose the database:',
            'choices': dblist
        }
    ]
    if len(sys.argv) < 2:
        answers = prompt(questions, style=style)
        if gw_manager.checkDBhealth(answers["database"]):
            db_name = answers["database"]
            db_selector.selectDB(db_name)
            #return db_structure.db(db_name)
        else:
            print("Corrupt DB exiting...")
            exit(-1)
    else:
        if gw_manager.checkDBhealth(sys.argv[1]):
            db_name = sys.argv[1]
            db_selector.selectDB(db_name)
            #return db_structure.db(db_name)
        else:
            print("Corrupt DB exiting...")
            exit(-1)


def manageMessages(session,Messages):
    questions = [
        {
            'type': 'list',
            'name': 'action',
            'message': 'Que acción deseas tomar?',
            'choices': ["List messages","Send test message","BACK"],
            'filter': lambda val: val.lower()
        }
    ]

    answers = prompt(questions, style=style)

    if answers["action"] == "list messages":
        gw_manager.listMessages(session,Message)
        manageMessages(session, Message)

print('------------------------------- WELCOME TO ALERT GATEWAY MANAGER -------------------------------')

questions = [
    {
        'type': 'confirm',
        'name': 'newDB',
        'message': 'Do you wan\'t to create a new DB?',
        'default': False
    }
]
if len(sys.argv) < 2:
    answers = prompt(questions, style=style)
    db_name = "alertgw.db"

    if not answers["newDB"]:
        selectDB()
    else:
        questions = [
            {
                'type': 'input',
                'name': 'database',
                'message': 'Enter the db name (alertgw.db by default):',
                'default': 'alertgw.db'
            }
        ]

        answers = prompt(questions, style=style)
        f = open("databases/"+str(answers["database"]), "w+").close()
        db_selector.selectDB(answers["database"])
        db_structure.createDb(answers["database"])
else:
    selectDB()

while True:
    questions = [
        {
            'type': 'list',
            'name': 'action',
            'message': 'Choose an action:',
            'choices': ["Manage channels","Manage users", "Manage messages","EXIT"],
            'filter': lambda val: val.lower()
        }
    ]

    answers = prompt(questions, style=style)
    if answers["action"] == "manage channels":
        manageChannels(session,Channel,InputChannel)

    elif answers["action"] == "manage users":
        manageUsers(session,User)
    elif answers["action"] == "manage messages":
        manageMessages(session,Message)
    else:
        exit(0)
