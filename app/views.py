from app.config import Config
from flask import render_template, flash, session, redirect, url_for, request, jsonify, send_file, Response
from werkzeug.urls import url_parse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


from app.service import ValidateLogin
from app.service import User
from flask_login import login_user,login_required,current_user,logout_user
from service import ProcessAndSendMessages
import os
import pytz
import datetime
import json
import termcolor
import colorama
colorama.init(strip=False)
from pprint import pprint
import requests
from requests.auth import HTTPBasicAuth
import traceback
import uuid
import google_auth_oauthlib,google
import pickle
from apscheduler.jobstores.base import JobLookupError
from service import AccessGoogleAPI



import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

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
            #flash('login successful')
            user = User(password)
            login_user(user)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('transaction_setup')
            return redirect(next_page)
        else:
            #flash('login failed')
            return redirect('/admin-login')

@server.route('/test')
def test_api_request():
    job = AppDBUtil.getJobById('j-151503')
    print("job is ",job)
    print("job state is ",job.job_state)

    #x = pickle.loads(job)
    y = pickle.loads(job.job_state)
    #print(x)
    print(y)
    return {'done':'done'}

@server.route("/pause_job",methods=['POST'])
def pause_job():
    job_id = request.form['job_id']
    try:
        #set to paused, then in case apscheduler ends the job, you go get a status from ApschedulerJobFurtherState
        if Config.jobstores['default'].lookup_job(job_id):
            Config.scheduler.pause_job(job_id, 'default')
            job =  AppDBUtil.getJobFurtherStateById(job_id)
            logger.info("Job paused is {}".format(job_id))
            AppDBUtil.setJobStatus(job_id=job_id, job_status='paused')
            result = {'status': 'success', 'job_status': str(job.job_status)}
        else:
            logger.info("Job {} can't be paused because it has ended.".format(job_id))
            result = {'status': 'success', 'job_status':'ended','message': "Can't pause job "+str(job_id)+" because it has ended."}

    except Exception as e:
        result = {'status': 'failure'}
        print("Exception in pausing job")
        print(e)
        traceback.print_exc()

    return jsonify(result)

@server.route("/get_job_status",methods=['POST'])
def get_job_status():
    job_id = request.form['job_id']
    try:
        job =  AppDBUtil.getJobFurtherStateById(job_id)
        logger.info("Job status is: {}".format(job.job_status))
        result = {'status':'success','job_status':str(job.job_status)}
    except Exception as e:
        result = {'status': 'failure'}
        print("Exception in getting job status")
        print(e)
        traceback.print_exc()

    return jsonify(result)

@server.route("/resume_job",methods=['POST'])
def resume_job():
    job_id = request.form['job_id']
    try:
        # set to paused, then in case apscheduler ends the job, you go get a status from ApschedulerJobFurtherState
        if Config.jobstores['default'].lookup_job(job_id):
            Config.scheduler.pause_job(job_id, 'default')
            job = AppDBUtil.getJobFurtherStateById(job_id)
            logger.info("Job resumed is {}".format(job_id))
            AppDBUtil.setJobStatus(job_id=job_id, job_status='active')
            result = {'status': 'success', 'job_status': str(job.job_status)}
        else:
            logger.info("Job {} can't be resumed because it has ended.".format(job_id))
            result = {'status': 'success', 'job_status':'ended','message': "Can't resume job " + str(job_id) + " because it has ended."}

    except Exception as e:
        result = {'status': 'failure'}
        print("Exception in resuming job")
        print(e)
        traceback.print_exc()

    return jsonify(result)

@server.route("/remove_job",methods=['POST'])
def remove_job():
    job_id = request.form['job_id']
    try:
        # job_in_apscheduler_job = AppDBUtil.getJobById(job_id)
        # AppDBUtil.setJobApschedulerState(job_id=job_id,job_apscheduler_state=job_in_apscheduler_job.job_state)
        # state_of_job_in_apscheduler_job = pickle.loads(job_in_apscheduler_job.job_state)
        # #trigger_type_of_job_in_apsceduler_state = str(state_of_job_in_apscheduler_job['trigger'].__class__.__name__).split('Trigger')[0]

        if Config.jobstores['default'].lookup_job(job_id):
            Config.scheduler.remove_job(job_id, 'default')
            logger.info("Removed {} in apschedulerjob".format(job_id))
        AppDBUtil.removeJobFurtherState(job_id)
        logger.info("Removed {} in apscheduler_job_further_state".format(job_id))
        result = {'status':'success'}
    except Exception as e:
        result = {'status': 'failure'}
        print("Exception in removing job")
        print(e)
        traceback.print_exc()

    return jsonify(result)


@server.route('/modify_job', defaults={'job_id': None,'job_medium_being_modified':None,'status_of_job_being_modified':None}, methods=['GET', 'POST'])
@server.route('/modify_job/<job_id>/<job_medium_being_modified>/<status_of_job_being_modified>',methods=['GET', 'POST'])
def modify_job(job_id,job_medium_being_modified,status_of_job_being_modified):
    if request.method == 'GET':
        logger.debug("job_id in GET call to modify_job is {}".format(job_id))
        return redirect(url_for('create_job',job_id=job_id,job_medium_being_modified=job_medium_being_modified,status_of_job_being_modified=status_of_job_being_modified))
    elif request.method == 'POST':
        pass

@server.route("/manage_job",methods=['GET', 'POST'])
def manage_job():
    if request.method == 'GET':
        logger.debug("GET call to manage_job")
        all_jobs_as_list = []
        all_jobs = AppDBUtil.getAllJobs()
        for further_job_state in all_jobs:
            job_apscheduler_state = pickle.loads(further_job_state.job_apscheduler_state)
            this_job_as_dict = {}
            this_job_as_dict['id'] = job_apscheduler_state['id']
            this_job_as_dict['type'] = 'Email' if 'Email' in job_apscheduler_state['func'] else 'SMS'
            trigger_type = str(job_apscheduler_state['trigger'].__class__.__name__).split('Trigger')[0]
            this_job_as_dict['type'] = this_job_as_dict['type']+'/'+trigger_type
            this_job_as_dict['description'] = job_apscheduler_state['name']
            this_job_as_dict['next_run_time'] = job_apscheduler_state['next_run_time'].strftime("%m/%d/%Y, %I:%M %p") if job_apscheduler_state.get('next_run_time') and job_apscheduler_state.get('next_run_time') >= datetime.datetime.now(pytz.timezone('US/Central'))  else "No next run time."

            if  trigger_type == 'Date':
                this_job_as_dict['last_run_time'] = job_apscheduler_state['next_run_time'].strftime("%m/%d/%Y, %I:%M %p") if job_apscheduler_state.get('next_run_time') else "No last run time."
            else:
                if job_apscheduler_state['trigger'].end_date:
                    this_job_as_dict['last_run_time'] = job_apscheduler_state['trigger'].end_date.strftime("%m/%d/%Y, %I:%M %p")
                else:
                    this_job_as_dict['last_run_time'] = 'No last run time'

            this_job_as_dict['date_job_created'] = further_job_state.date_job_created.strftime("%m/%d/%Y, %I:%M %p")
            this_job_as_dict['date_job_last_modified'] = further_job_state.date_job_last_modified.strftime("%m/%d/%Y, %I:%M %p")
            this_job_as_dict['status'] = further_job_state.job_status
            all_jobs_as_list.append(this_job_as_dict)

        return render_template('manage_job.html',all_jobs=all_jobs_as_list)
    elif request.method == 'POST':
        pass

@server.route('/send_attached_file_to_client', defaults={'id_of_attached_file_if_any': None}, methods=['GET', 'POST'])
@server.route('/send_attached_file_to_client/<id_of_attached_file_if_any>',methods=['GET', 'POST'])
def send_attached_file_to_client(id_of_attached_file_if_any):
    if request.method == 'GET':
        accessGoogleAPI = AccessGoogleAPI()
        file_and_its_details = accessGoogleAPI.getFilesFromGoogle([id_of_attached_file_if_any])
        logger.debug("file id in GET call to send_attachment_from_google_to_client is {}".format(id_of_attached_file_if_any))
        print(file_and_its_details[id_of_attached_file_if_any])
        file_and_its_details[id_of_attached_file_if_any][1].seek(0)
        return send_file(path_or_file=file_and_its_details[id_of_attached_file_if_any][1],download_name=file_and_its_details[id_of_attached_file_if_any][0],as_attachment=True)

@server.route('/create_job', defaults={'job_id': None,'job_medium_being_modified':None,'status_of_job_being_modified':None}, methods=['GET', 'POST'])
@server.route('/create_job/<job_id>/<job_medium_being_modified>/<status_of_job_being_modified>',methods=['GET', 'POST'])
def create_job(job_id, job_medium_being_modified, status_of_job_being_modified):
    stored_google_credentials = AppDBUtil.getGoogleCredentials()
    print(stored_google_credentials)
    if not stored_google_credentials:
        print("no credentials")
        return redirect('authorize')
    else:
        print("credentials exist")

    recipients = AppDBUtil.getRecipients()
    processed_recipients = []
    email_to_phone_number_dict = {}
    phone_number_to_email_dict = {}
    for recipient in recipients:
        recipient_as_dict = {}
        recipient_as_dict['recipient_id'] = recipient.recipient_id
        recipient_as_dict['recipient_salutation'] = recipient.recipient_salutation
        recipient_as_dict['recipient_first_name'] = recipient.recipient_first_name
        recipient_as_dict['recipient_last_name'] = recipient.recipient_last_name
        recipient_as_dict['recipient_phone_number'] = recipient.recipient_phone_number
        recipient_as_dict['recipient_email'] = recipient.recipient_email
        recipient_as_dict['recipient_type'] = recipient.recipient_type
        recipient_as_dict['recipient_tags'] = recipient.recipient_tags
        recipient_as_dict['recipient_description'] = recipient.recipient_description
        recipient_as_dict['is_active'] = recipient.is_active
        processed_recipients.append(recipient_as_dict)
        email_to_phone_number_dict[recipient.recipient_email] = recipient.recipient_phone_number
        phone_number_to_email_dict[recipient.recipient_phone_number] = recipient.recipient_email
    if request.method == 'GET':
        job = AppDBUtil.getJobUIStateById(job_id)
        job_ui_state = job.job_ui_state if job else None
        #ids_of_attached_files_if_any = job_ui_state['ids_of_attached_files_if_any'] if job_ui_state else None
        return render_template('create_job.html', recipients=json.dumps(processed_recipients), email_to_phone_number_dict=json.dumps(email_to_phone_number_dict), phone_number_to_email_dict=json.dumps(phone_number_to_email_dict), job_id=job_id, job_medium_being_modified=job_medium_being_modified, status_of_job_being_modified=status_of_job_being_modified, job_ui_state=json.dumps(job_ui_state))
    elif request.method == 'POST':
        create_job_request_dict = request.form.to_dict()
        print("create_job_request_dict is ",create_job_request_dict)

        job_id = create_job_request_dict.get('job_id')
        job_medium_being_modified = create_job_request_dict.get('job_medium_being_modified')
        create_or_modify = create_job_request_dict.get('createMessageJobsButton',create_job_request_dict.get('modifyMessageJobsButton')).split('MessageJobsButton')[0]

        logger.debug("job_id in POST call to create_job is {}".format(job_id))

        processAndSendMessages = ProcessAndSendMessages()

        if not create_job_request_dict.get('disableEmailMessage'):
            try:
                print("ready to send email")

                parsed_email_addresses_from_form = processAndSendMessages.parseEmailAddressesFromForm(create_job_request_dict.get('allEmailRecipients', ''))
                create_job_request_email_attachments = request.files.getlist('emailFileUploadInput')

                email_messages_to_setup =  {
                'send_email': 'yes',
                'email_description': create_job_request_dict['emailDescription'] if create_job_request_dict['emailDescription'] else 'email_default_description',
                'email_message': {'subject': create_job_request_dict['emailSubject'],'content': create_job_request_dict['emailContent']},
                'email_recipients': parsed_email_addresses_from_form,
                }

                if create_job_request_dict['emailJobType'] == 'emailDateJob':
                    email_messages_to_setup['email_job_parameters'] = {'run_date': datetime.datetime.strptime(create_job_request_dict['email_run_date_and_time'], '%Y-%m-%dT%H:%M')}
                    email_messages_to_setup['email_job_type'] = 'email_date_trigger'
                elif create_job_request_dict['emailJobType'] == 'emailCronJob':
                    email_messages_to_setup['email_job_parameters'] = {'year': create_job_request_dict['email_cron_year'],
                                                                   'month': create_job_request_dict['email_cron_month'],
                                                                   'day': create_job_request_dict['email_cron_day'],
                                                                   'week': create_job_request_dict['email_cron_week'],
                                                                   'day_of_week': create_job_request_dict['email_cron_day_of_week'],
                                                                   'hour': create_job_request_dict['email_cron_hour'],
                                                                   'minute': create_job_request_dict['email_cron_minute'],
                                                                   'second': create_job_request_dict['email_cron_second'],
                                                                   'start_date': datetime.datetime.strptime(create_job_request_dict['email_cron_start_date_and_time'], '%Y-%m-%dT%H:%M'),
                                                                   'end_date': datetime.datetime.strptime(create_job_request_dict['email_cron_end_date_and_time'], '%Y-%m-%dT%H:%M')
                                                                   }
                    email_messages_to_setup['email_job_type'] = 'email_cron_trigger'
                elif create_job_request_dict['emailJobType'] == 'emailIntervalJob':
                    email_messages_to_setup['email_job_parameters'] = {'days': int(create_job_request_dict['email_interval_days']),
                                                                   'weeks': int(create_job_request_dict['email_interval_weeks']),
                                                                   'hours': int(create_job_request_dict['email_interval_hours']),
                                                                   'minutes': int(create_job_request_dict['email_interval_minutes']),
                                                                   'seconds': int(create_job_request_dict['email_interval_seconds']),
                                                                   'start_date': datetime.datetime.strptime(create_job_request_dict['email_interval_start_date_and_time'], '%Y-%m-%dT%H:%M'),
                                                                   'end_date': datetime.datetime.strptime(create_job_request_dict['email_interval_end_date_and_time'], '%Y-%m-%dT%H:%M')
                                                                   }
                    email_messages_to_setup['email_job_type'] = 'email_interval_trigger'

                if create_or_modify == 'create':
                    email_job_id = "j-" + str(uuid.uuid4().int >> 64)[:6]
                elif create_or_modify == 'modify':
                    if job_id and job_medium_being_modified=='Email':
                        email_job_id = job_id
                    else:
                        logger.debug("Unexpected: Logic should not fall under this branch. ")

                emails_subjects = [email_messages_to_setup['email_message']['subject']] * len(email_messages_to_setup['email_recipients'])
                emails_contents = [email_messages_to_setup['email_message']['content']] * len(email_messages_to_setup['email_recipients'])
                zipped_and_processed_recipients_subjects_contents = processAndSendMessages.processEmailMessagesToSend(recipients_emails=email_messages_to_setup['email_recipients'], emails_subjects=emails_subjects, emails_contents=emails_contents)

                ids_of_files_uploaded_to_google = processAndSendMessages.processUploadedFiles(uploadedFiles=create_job_request_email_attachments,job_id=email_job_id,is_email_or_sms='email')
                print("create_jobs: ids_of_attached_files_if_any",ids_of_files_uploaded_to_google)

                processAndSendMessages.createJobToSendEmailMessages(email_messages_to_setup=email_messages_to_setup, zipped_and_processed_recipients_subjects_contents=zipped_and_processed_recipients_subjects_contents,job_id=email_job_id,ids_of_files_uploaded_to_google=ids_of_files_uploaded_to_google,create_or_modify=create_or_modify)

                job_ui_state = dict(create_job_request_dict)  # or orig.copy()
                job_ui_state.update({'ids_of_attached_files_if_any':ids_of_files_uploaded_to_google})
                AppDBUtil.updateJobUIState(email_job_id, job_ui_state)
                flash("Successfully set up email message job.")
            except Exception as e:
                print("Error in email")
                print(e)
                traceback.print_exc()
                flash("Failed to set up email message job.")
        if not create_job_request_dict.get('disableSMSMessage'):
            try:
                print("ready to send sms")

                parsed_phone_numbers_from_form = processAndSendMessages.parsePhoneNumbersFromForm(create_job_request_dict.get('allSMSRecipients', ''))
                create_job_request_sms_attachments = request.files.getlist('smsFileUploadInput')

                sms_messages_to_setup = {
                    'send_sms': 'yes',
                    'sms_description': create_job_request_dict['smsDescription'] if create_job_request_dict['smsDescription'] else 'sms_default_description',
                    'sms_message': {'subject': create_job_request_dict['smsSubject'],'content': create_job_request_dict['smsContent']},
                    'sms_recipients': parsed_phone_numbers_from_form,
                }

                if create_job_request_dict['smsJobType'] == 'smsDateJob':
                    sms_messages_to_setup['sms_job_parameters'] = {'run_date': datetime.datetime.strptime(create_job_request_dict['sms_run_date_and_time'], '%Y-%m-%dT%H:%M')}
                    sms_messages_to_setup['sms_job_type'] = 'sms_date_trigger'
                elif create_job_request_dict['smsJobType'] == 'smsCronJob':
                    # TODO require all fields for cron (and maybe interval) on front end so you dont have to deal with intricacies of APScheduler default
                    sms_messages_to_setup['sms_job_parameters'] = {'year': create_job_request_dict['sms_cron_year'],
                                                                   'month': create_job_request_dict['sms_cron_month'],
                                                                   'day': create_job_request_dict['sms_cron_day'],
                                                                   'week': create_job_request_dict['sms_cron_week'],
                                                                   'day_of_week': create_job_request_dict['sms_cron_day_of_week'],
                                                                   'hour': create_job_request_dict['sms_cron_hour'],
                                                                   'minute': create_job_request_dict['sms_cron_minute'],
                                                                   'second': create_job_request_dict['sms_cron_second'],
                                                                   'start_date': datetime.datetime.strptime(create_job_request_dict['sms_cron_start_date_and_time'], '%Y-%m-%dT%H:%M'),
                                                                   'end_date': datetime.datetime.strptime(create_job_request_dict['sms_cron_end_date_and_time'], '%Y-%m-%dT%H:%M')
                                                                   }
                    sms_messages_to_setup['sms_job_type'] = 'sms_cron_trigger'
                elif create_job_request_dict['smsJobType'] == 'smsIntervalJob':
                    # TODO require all fields for cron (and maybe interval) on front end so you dont have to deal with intricacies of APScheduler default
                    sms_messages_to_setup['sms_job_parameters'] = {'days': int(create_job_request_dict['sms_interval_days']),
                                                                   'weeks': int(create_job_request_dict['sms_interval_weeks']),
                                                                   'hours': int(create_job_request_dict['sms_interval_hours']),
                                                                   'minutes': int(create_job_request_dict['sms_interval_minutes']),
                                                                   'seconds': int(create_job_request_dict['sms_interval_seconds']),
                                                                   'start_date': datetime.datetime.strptime(create_job_request_dict['sms_interval_start_date_and_time'], '%Y-%m-%dT%H:%M'),
                                                                   'end_date': datetime.datetime.strptime(create_job_request_dict['sms_interval_end_date_and_time'], '%Y-%m-%dT%H:%M')
                                                                   }
                    sms_messages_to_setup['sms_job_type'] = 'sms_interval_trigger'

                if create_or_modify == 'create':
                    sms_job_id = "j-" + str(uuid.uuid4().int >> 64)[:6]
                elif create_or_modify == 'modify':
                    if job_id and job_medium_being_modified == 'SMS':
                        sms_job_id = job_id
                    else:
                        logger.debug("Unexpected: Logic should not fall under this branch. ")

                sms_contents = [sms_messages_to_setup['sms_message']['content']] * len(sms_messages_to_setup['sms_recipients'])
                zipped_and_processed_recipients_contents = processAndSendMessages.processSMSMessagesToSend(recipients_phone_numbers=sms_messages_to_setup['sms_recipients'], sms_contents=sms_contents)

                ids_of_files_uploaded_to_google = processAndSendMessages.processUploadedFiles(uploadedFiles=create_job_request_sms_attachments, job_id=sms_job_id,is_email_or_sms='sms')
                print("create_jobs: ids_of_attached_files_if_any: ", ids_of_files_uploaded_to_google)

                processAndSendMessages.createJobToSendSMSMessages(sms_messages_to_setup=sms_messages_to_setup, zipped_and_processed_recipients_contents=zipped_and_processed_recipients_contents,job_id=sms_job_id,ids_of_files_uploaded_to_google=ids_of_files_uploaded_to_google,create_or_modify=create_or_modify)
                job_ui_state = dict(create_job_request_dict)  # or orig.copy()
                job_ui_state.update({'ids_of_attached_files_if_any':ids_of_files_uploaded_to_google})
                AppDBUtil.updateJobUIState(sms_job_id, job_ui_state)
                flash("Successfully set up sms message job.")
            except Exception as e:
                print("Error in sms")
                print(e)
                traceback.print_exc()
                flash("Failed to set up sms message job.")

        return redirect(url_for('create_job'))

        #return render_template('create_job.html', recipients=json.dumps(processed_recipients))

#TODO implement copious but nuanced debugging messgaes to make debuggin easier, especially since ApScheduelr deletes somethings that will help on its own

@server.route('/placeholder',methods=['GET', 'POST'])
@login_required
def placeholder():
    AppDBUtil.setupTestStudents()
    AppDBUtil.updateRecipientTags(recipient_email='mo@vensti.com', recipient_phone_number='4437636418', recipient_tags=['cohort-1-2022', 'essays-2022'])
    AppDBUtil.updateRecipientType(recipient_email='mo@vensti.com', recipient_phone_number='4437636418', recipient_type='student')
    AppDBUtil.updateRecipientTags(recipient_email='mobolaji.akinpelu@yahoo.com', recipient_tags=['cohort-1-2022-father'])
    AppDBUtil.updateRecipientType(recipient_email='mobolaji.akinpelu@yahoo.com', recipient_type='parent')
    recipients = AppDBUtil.getRecipients()

    #TODO add logging with python logging module that you will view in logtail

    #TODO copy yourself in every email so you can get to see bugs etc as the system evolves

    #TODO rememebr to sent email_description and text_description defualt values to 'default' in the ui bevcause they are used for job name and that requires a non-empty string
    #TODO set up cron ui options to accept day as mon,sun, etc as opposed to 0,1 per the docs https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html

    return str(recipients[0].__dict__)

@server.route('/authorize')
def authorize():
    print("in authorize")
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        Config.CLIENT_SECRETS_FILE, scopes=Config.SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    session['state'] = state

    return redirect(authorization_url)

@server.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']
    print("state is ", state)

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        Config.CLIENT_SECRETS_FILE, scopes=Config.SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    AppDBUtil.setGoogleCredentials(credentials)

    #session['credentials'] = AccessGoogleAPI.credentials_to_dict(credentials)

    return redirect(url_for('create_job'))



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

def dummy_background_job():
    try:
        print("dummy background job for local and dev")
    except Exception as e:
        print("Error in executing dummy background job")
        print(e)
        traceback.print_exc()

def default_background_job():
    try:
        print("Default background job started")
    except Exception as e:
        print("Error in sending reminders")
        print(e)
        traceback.print_exc()

@server.before_first_request
def start_background_jobs_before_first_request():

    if os.environ['DEPLOY_REGION'] != 'prod':
        pass
        #scheduler.add_job(dummy_background_job, 'cron', minute='55')
        #print("Default background job added")
        Config.scheduler.add_job(default_background_job, 'cron', hour='21', minute='00')
    else:
        Config.scheduler.add_job(default_background_job, 'cron', hour='21', minute='00')

    #Config.scheduler.start()



    #THE KEY TO GETTING TIMEZONE RIGHT IS SETTING IT AS AN ENVIRONMENT VARIABLE ON DIGITAL OCEAN SERVER
    # import datetime,time
    # stamp = int(datetime.datetime.now().timestamp())
    # date = datetime.datetime.fromtimestamp(stamp)
    # print("1. ",date)
    # print("2. timezone info is: ",datetime.datetime.today().astimezone().tzinfo)
    # print("3. ",datetime.datetime.today())
    # print("4. ",datetime.datetime.fromtimestamp(int(time.mktime(datetime.datetime.today().timetuple()))))






