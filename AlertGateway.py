import importlib
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField, validators
from flask_login import login_user, LoginManager, current_user, login_required, logout_user
import gw_manager
import os
from PyInquirer import style_from_dict, Token, prompt
import sys
from db_structure import *
import input_channels
from input_channels import InputChannels_servers

app = Flask(__name__)


class formEditChannel(FlaskForm):
    channel_name = StringField("New Name")
    channel_enable = SelectField('Status')
    channel_parameters = StringField("Change parameters")
    channel_type = SelectField("Channel type")
    submit = SubmitField('Submit')

class formEditUser(FlaskForm):
    user_name = StringField("New User")
    user_password = PasswordField("New password",[validators.EqualTo('confirm_password', message="Passwords must match")])
    confirm_password = PasswordField("Repeat password")
    submit = SubmitField('Submit')



@app.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect(url_for('profile'))


@app.route('/profile',methods=['GET'])
@login_required
def profile():
    messages = gw_manager.getMessages(session,Message,gw_manager.getUserNameByid(session,User,current_user.get_id()))
    channels = gw_manager.getChannels(session,Channel,gw_manager.getKeyByid(session,User,current_user.get_id()))
    input_channels = gw_manager.getAllInputChannels(session,InputChannel)
    name = gw_manager.getUserNameByid(session,User,current_user.get_id())
    form = formEditChannel()
    form.channel_enable.choices = ["Enabled", "Disabled"]
    form.channel_type.choices = gw_manager.getAllChannels()
    form.process()
    if channels == False:
        channels = []
    if messages == False:
        messages = []
    if input_channels == False:
        input_channels = []
    return render_template("profile.html",input_channels=input_channels,channels=channels,messages=messages,name=name,form=form,user=gw_manager.getUserByid(session,User,current_user.get_id()))

@app.route('/login',methods=['GET'])
def login():
    return render_template('login.html')

@app.route("/editUser/<int:user_id>", methods=["GET"])
@login_required
def edit_user(user_id):
    user = gw_manager.getUserByid(session,User,user_id)
    form = formEditUser()
    form.user_name.default= user.user_name
    form.process()
    return render_template("editUser.html",user=user, form=form)

@app.route("/editUser/<int:user_id>", methods=["POST"])
@login_required
def edit_user_post(user_id):
    user = gw_manager.getUserByid(session, User, user_id)
    form = formEditUser()
    new_user_name = form.user_name.data
    new_password = form.user_password.data
    confirm = form.confirm_password.data
    if (not new_user_name == ""):
        if (not new_user_name == user.user_name):
            if (not gw_manager.verify_user(session, User, user.user_name)):
                flash("User changed!", "notification is-success")
                gw_manager.changeUsername(session,User,user_id,new_user_name)
            else:
                flash("Illegal username", "notification is-danger")

    if not  new_password == "":
        t,u = gw_manager.verifyLogin(session,User,new_user_name,new_password)
        if not t:
            if new_password == confirm:
                gw_manager.changeUserpass(session,User,user_id,new_password)
                flash("Password changed!", "notification is-success")
            else:
                flash("Passwords must match", "notification is-danger")
                redirect(url_for('profile'))
        else:
            flash("Please enter a new password.", "notification is-danger")
            redirect(url_for('profile'))
    return redirect(url_for('profile'))

@app.route('/deleteChannel/<int:channel_id>',methods=["POST"])
@login_required
def delete_channel(channel_id):
    if gw_manager.deleteChannel(session,Channel,channel_id):
        flash("Channel deleted!","notification is-success")
        return redirect(url_for('profile'))
    else:
        flash("Channel not deleted!", "notification is-danger")
        return redirect(url_for('profile'))

@app.route('/editChannel/<int:channel_id>',methods=["GET","POST"])
@login_required
def edit_channel(channel_id):
    form = formEditChannel()
    channel = session.query(Channel).get(channel_id)
    if request.method == "GET":
        form.channel_enable.choices = ["Enabled", "Disabled"]
        form.channel_type.choices = [channel.channel_type]
        form.channel_name.default = channel.channel_name
        form.channel_enable.default = channel.channel_enable
        form.channel_parameters.default = channel.channel_parameters
        form.process()
        return render_template("editChannel.html",title="Edit channel",form=form,channel_id=channel_id)
    elif request.method == "POST":
        print(form.channel_name.data)
        print(form.channel_parameters.data)
        if channel.channel_name != form.channel_name.data:
            if not gw_manager.changeChannelName(session,Channel,channel_id,form.channel_name.data):
                flash("Can't set this name...","notification is-danger")
                return redirect(url_for('profile'))
        channel_status = False
        if form.channel_enable.data == "Enabled":
            channel_status = True
        if not channel.channel_enable == channel_status:
            if not gw_manager.changeChannelStatus(session,Channel,channel_id,channel_status):
                flash("Can't set this status...", "notification is-danger")
                flash("Channel edited!", "notification is-success")
                return redirect(url_for('profile'))
        if not gw_manager.changeChannelParameters(session,Channel,channel_id,form.channel_parameters.data):
            flash("Can't set this parameters...", "notification is-danger")
            flash("Channel edited!", "notification is-success")
            return redirect(url_for('profile'))
        flash("Channel edited!", "notification is-success")
        return redirect(url_for('profile'))

@app.route('/newChannel/',methods=["POST"])
@login_required
def add_channel():
    form = formEditChannel()
    print(form.channel_name.data)
    print(form.channel_enable.data)
    print(form.channel_parameters.data)
    print(form.channel_type.data)
    result, comment = gw_manager.addChannel(session,Channel,form.channel_name.data, form.channel_type.data, gw_manager.getKeyByid(session,User,current_user.get_id()),form.channel_parameters.data,form.channel_enable.data)
    if result:
        return redirect(url_for("profile"))
    else:
        flash(comment,"notification is-danger")
        return redirect(url_for("profile"))
@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    result, user = gw_manager.verifyLogin(session, User, username, password)
    if not result:
        flash('Please check your login details and try again.')
        return redirect(url_for('login')) # if the user doesn't exist or password is wrong, reload the page
    login_user(user, remember=remember)
    # if the above check passes, then we know the user has the right credentials
    return redirect(url_for('profile'))
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/changeInputChannelStatus/<int:input_channel_id>')
@login_required
def change_inputChannel_status(input_channel_id):
    channel = session.query(InputChannel).get(input_channel_id)
    predict = {}
    predict["funct"] = "input_channels." + channel.input_channel_location.split("/")[
        len(channel.input_channel_location.split("/")) - 1]
    ch = importlib.import_module(predict["funct"])
    try:
        rest_server = processes[channel.input_channel_name]
    except:
        rest_server = InputChannels_servers().getProcesses()[channel.input_channel_name]
    if channel.input_channel_status == False:
        ch.start(rest_server)
        gw_manager.changeInputChannelStatus(session,InputChannel,User,channel.input_channel_id,True, current_user.get_id())
        return redirect(url_for('profile'))
    else:
        if gw_manager.changeInputChannelStatus(session, InputChannel,User, channel.input_channel_id, False, current_user.get_id()):
            processes[channel.input_channel_name] = ch.createServer(bind_address=channel.input_channel_address, port=channel.input_channel_port)
            ch.stop(rest_server)
            return redirect(url_for('profile'))
        else:
            flash("Your user can not shutdown this input channel!", "notification is-danger")
            return redirect(url_for('profile'))


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
    if dblist == []:
        print("Can't retrieve any db, please create one with GatewayManager.")
        exit()
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
        else:
            print("Corrupt DB exiting...")
            exit(-1)



if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    login_manager = LoginManager()
    selectDB()
    login_manager.login_view = 'login'
    gw_manager.disableAllInputChannels(session,InputChannel)
    login_manager.init_app(app)
    inputchannels = gw_manager.getAllActiveInputChannels(session, InputChannel)
    processes = InputChannels_servers().getProcesses()
    @login_manager.user_loader
    def load_user(id):
        return gw_manager.getUserByid(session, User, id)
    app.run(debug=False,host='0.0.0.0', port=443, ssl_context="adhoc")