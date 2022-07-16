from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from flask_login import UserMixin
import uuid
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import db_selector

try:
    engine = create_engine('sqlite:///databases/' + db_selector.getDB() + '?check_same_thread=False')
    Session = sessionmaker(bind=engine)
    session = Session()
    Base = declarative_base()
    Base.metadata.create_all(engine)


    class User(UserMixin, Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True, autoincrement=True)
        user_name = Column(String(16), nullable=False)
        user_pass = Column(String(100), nullable=False)
        user_key = Column(String(100), nullable=False)

        def __init__(self, user_name, user_pass):
            self.user_name = user_name
            self.user_pass = user_pass
            self.user_key = uuid.uuid4().hex

        def __repr__(self):
            return f'Usuario({self.id}, {self.user_name}, {self.user_pass}, {self.user_key})'

        def __str__(self):
            return self.user_name + ";" + self.user_pass + ";" + str(self.user_key)


    class Channel(Base):
        __tablename__ = 'channels'
        channel_id = Column(Integer, primary_key=True, autoincrement=True)
        channel_name = Column(String(20), nullable=False)
        channel_type = Column(String(20), nullable=True)
        channel_enable = Column(Boolean, unique=False, default=True, nullable=True)
        channel_key = Column(String(200), ForeignKey("users.user_key"), nullable=False)
        channel_parameters = Column(String(1000), nullable=True)

        def __init__(self, channel_name, channel_type, channel_key, channel_parameters, channel_enable):
            self.channel_name = channel_name
            self.channel_type = channel_type
            self.channel_key = channel_key
            self.channel_parameters = channel_parameters
            self.channel_enable = channel_enable

        def __repr__(self):
            return f'Channel({self.channel_name},{self.channel_type}, {self.channel_key}, {self.channel_parameters},{self.channel_enable})'

        def __str__(self):
            return self.channel_name + ";" + str(
                self.channel_enable) + ";" + self.channel_type + ";" + self.channel_key + ";" + str(self.channel_parameters)


    class InputChannel(Base):
        __tablename__ = 'input_channels'
        input_channel_id = Column(Integer, primary_key=True, autoincrement=True)
        input_channel_name = Column(String(20), nullable=False)
        input_channel_location = Column(String(100), nullable=False)
        input_channel_address = Column(String(20), nullable=False)
        input_channel_port = Column(Integer, nullable=False)
        input_channel_status = Column(Boolean, unique=False, default=True, nullable=True)
        input_channel_key = Column(String(200), ForeignKey("users.user_key"), nullable=False)

        def __init__(self, input_channel_name, input_channel_location, input_channel_address, input_channel_port,
                     input_channel_status,input_channel_key):
            self.input_channel_address = input_channel_address
            self.input_channel_location = input_channel_location
            self.input_channel_name = input_channel_name
            self.input_channel_port = input_channel_port
            self.input_channel_status = input_channel_status
            self.input_channel_key = input_channel_key
        def __repr__(self):
            return f'Channel({self.input_channel_id},{self.input_channel_name},{self.input_channel_location}, {self.input_channel_address}, {self.input_channel_port})'


    class Message(Base):
        __tablename__ = 'messages'
        message_id = Column(Integer, primary_key=True, autoincrement=True)
        message_sender = Column(String(20), ForeignKey("users.user_name"), nullable=False)
        message_receiver = Column(String(50), nullable=False)
        message_data = Column(String(20), nullable=False)
        message_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
        message_channel = Column(String(20), ForeignKey("channels.channel_name"), nullable=False)

        def __init__(self, message_sender, message_channel, message_data, message_receiver):
            self.message_channel = message_channel
            self.message_sender = message_sender
            self.message_receiver = message_receiver
            self.message_data = message_data
            self.message_date = datetime.datetime.now()

        def __repr__(self):
            return f'Message({self.message_channel},{self.message_sender}, {self.message_data})'

        def __str__(self):
            return str(
                self.message_id) + ";" + self.message_channel + ";" + self.message_sender + ";" + self.message_receiver + ";" + str(
                self.message_date) + ";" + self.message_data
except:
    pass

def createDb(path):
    engine = create_engine('sqlite:///databases/' + path + '?check_same_thread=False')
    Session = sessionmaker(bind=engine)
    session = Session()
    Base = declarative_base()
    class User(UserMixin, Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True, autoincrement=True)
        user_name = Column(String(16), nullable=False)
        user_pass = Column(String(100), nullable=False)
        user_key = Column(String(100), nullable=False)

        def __init__(self, user_name, user_pass):
            self.user_name = user_name
            self.user_pass = user_pass
            self.user_key = uuid.uuid4().hex

        def __repr__(self):
            return f'Usuario({self.id}, {self.user_name}, {self.user_pass}, {self.user_key})'

        def __str__(self):
            return self.user_name + ";" + self.user_pass + ";" + str(self.user_key)


    class Channel(Base):
        __tablename__ = 'channels'
        channel_id = Column(Integer, primary_key=True, autoincrement=True)
        channel_name = Column(String(20), nullable=False)
        channel_type = Column(String(20), nullable=True)
        channel_enable = Column(Boolean, unique=False, default=True, nullable=True)
        channel_key = Column(String(200), ForeignKey("users.user_key"), nullable=False)
        channel_parameters = Column(String(1000), nullable=True)

        def __init__(self, channel_name, channel_type, channel_key, channel_parameters, channel_enable):
            self.channel_name = channel_name
            self.channel_type = channel_type
            self.channel_key = channel_key
            self.channel_parameters = channel_parameters
            self.channel_enable = channel_enable

        def __repr__(self):
            return f'Channel({self.channel_name},{self.channel_type}, {self.channel_key}, {self.channel_parameters},{self.channel_enable})'

        def __str__(self):
            return self.channel_name + ";" + str(
                self.channel_enable) + ";" + self.channel_type + ";" + self.channel_key + ";" + str(self.channel_parameters)


    class InputChannel(Base):
        __tablename__ = 'input_channels'
        input_channel_id = Column(Integer, primary_key=True, autoincrement=True)
        input_channel_name = Column(String(20), nullable=False)
        input_channel_location = Column(String(100), nullable=False)
        input_channel_address = Column(String(20), nullable=False)
        input_channel_port = Column(Integer, nullable=False)
        input_channel_status = Column(Boolean, unique=False, default=True, nullable=True)
        input_channel_key = Column(String(200), ForeignKey("users.user_key"), nullable=False)
        def __init__(self, input_channel_name, input_channel_location, input_channel_address, input_channel_port,
                     input_channel_status):
            self.input_channel_address = input_channel_address
            self.input_channel_location = input_channel_location
            self.input_channel_name = input_channel_name
            self.input_channel_port = input_channel_port
            self.input_channel_status = input_channel_status

        def __repr__(self):
            return f'Channel({self.input_channel_id},{self.input_channel_name},{self.input_channel_location}, {self.input_channel_address}, {self.input_channel_port})'


    class Message(Base):
        __tablename__ = 'messages'
        message_id = Column(Integer, primary_key=True, autoincrement=True)
        message_sender = Column(String(20), ForeignKey("users.user_name"), nullable=False)
        message_receiver = Column(String(50), nullable=False)
        message_data = Column(String(20), nullable=False)
        message_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
        message_channel = Column(String(20), ForeignKey("channels.channel_name"), nullable=False)

        def __init__(self, message_sender, message_channel, message_data, message_receiver):
            self.message_channel = message_channel
            self.message_sender = message_sender
            self.message_receiver = message_receiver
            self.message_data = message_data
            self.message_date = datetime.datetime.now()

        def __repr__(self):
            return f'Message({self.message_channel},{self.message_sender}, {self.message_data})'

        def __str__(self):
            return str(
                self.message_id) + ";" + self.message_channel + ";" + self.message_sender + ";" + self.message_receiver + ";" + str(
                self.message_date) + ";" + self.message_data
    Base.metadata.create_all(engine)
    return User, Channel, Message, session, InputChannel