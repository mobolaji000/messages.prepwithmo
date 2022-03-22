from flask import render_template, flash, make_response, redirect, url_for, request, jsonify, Response
from werkzeug.urls import url_parse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
from app.service import ValidateLogin
from app.service import User
from flask_login import login_user,login_required,current_user,logout_user
import ast
import time
import json
import os
import math
import uuid
import traceback
from app.config import stripe
from apscheduler.schedulers.background import BackgroundScheduler

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# handler = logging.StreamHandler()
# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# handler.setFormatter(formatter)
# logger.addHandler(handler)

from app import server
from app.aws import AWSInstance
from app.dbUtil import AppDBUtil
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = 'admin_login'

server.config.from_object(Config)
server.logger.setLevel(logging.DEBUG)
db = SQLAlchemy(server)
migrate = Migrate(server, db)
awsInstance = AWSInstance()


@server.route("/")
def hello():
    #server.logger.debug('Processing default request')
    return ("You have landed on the wrong page")

@server.route("/health")
def health():
    print("healthy!")
    return render_template('health.html')

@server.route('/admin-login',methods=['GET','POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin.html')
    elif request.method == 'POST':
        next_page = request.args.get('next')
        username = request.form.to_dict()['username']
        password = request.form.to_dict()['password']
        validateLogin = ValidateLogin(username, password)
        if validateLogin.validateUserName() and validateLogin.validatePassword():
            flash('login successful')
            user = User(password)
            login_user(user)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('transaction_setup')
            return redirect(next_page)
        else:
            flash('login failed')
            return redirect('/admin-login')

@server.route('/placeholder',methods=['GET', 'POST'])
def placeholder():
    return render_template('admin.html')

@server.route('/success')
def success():
    return render_template('success.html')

@server.route('/error')
def error(error_message):
    return render_template('error.html',error_message=error_message)

@server.route('/failure')
def failure():
    return render_template('failure.html')

@login_manager.user_loader
def load_user(password):
    return User(awsInstance.get_secret("vensti_admin", 'password'))

@server.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin_login'))



@server.before_first_request
def start_background_jobs_before_first_request():
    def default_background_job():
        try:
            print("Default background job started")
        except Exception as e:
            print("Error in sending reminders")
            print(e)
            traceback.print_exc()


    scheduler = BackgroundScheduler(timezone='US/Central')

    if os.environ['DEPLOY_REGION'] != 'prod':
    #if os.environ['DEPLOY_REGION'] != 'local':
        scheduler.add_job(lambda: print("dummy reminders job for local and dev"), 'cron', minute='55')
    else:
        scheduler.add_job(default_background_job, 'cron', hour='21', minute='00')

    print("Default background job added")

    #THE KEY TO GETTING TIMEZONE RIGHT IS SETTING IT AS AN ENVIRONMENT VARIABLE ON DIGITAL OCEAN SERVER
    # import datetime,time
    # stamp = int(datetime.datetime.now().timestamp())
    # date = datetime.datetime.fromtimestamp(stamp)
    # print("1. ",date)
    # print("2. timezone info is: ",datetime.datetime.today().astimezone().tzinfo)
    # print("3. ",datetime.datetime.today())
    # print("4. ",datetime.datetime.fromtimestamp(int(time.mktime(datetime.datetime.today().timetuple()))))

    scheduler.start()
