import os
from twilio.rest import Client as TwilioClient
from app.aws import AWSInstance
basedir = os.path.abspath(os.path.dirname(__file__))
awsInstance = AWSInstance()

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

import traceback

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class Config(object):
    try:
        if os.environ['DEPLOY_REGION'] == 'local':

            logger.debug("Environment is local")

            os.environ["url_to_start_reminder"] = "http://127.0.0.1:5003/"
            flask_secret_key = os.environ.get('flask_secret_key')
            SECRET_KEY = os.environ.get('flask_secret_key')
            dbUserName = os.environ.get('dbUserNameLocal')
            dbPassword = os.environ.get('dbPasswordLocal')
            SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://'+str(dbUserName)+':'+str(dbPassword)+'@host/mobolajioo'
            SQLALCHEMY_TRACK_MODIFICATIONS = False

            twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
            twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']
            twilio_sms_number = os.environ['TWILIO_SMS_NUMBER']
            twilio_messaging_service_sid = os.environ['TWILIO_MESSAGING_SERVICE_SID']

            twilioClient = TwilioClient(twilio_account_sid, twilio_auth_token)

            MAX_CONTENT_LENGTH = 1024 * 1024
            UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif', '.jpeg', '.pdf', '.txt', '.doc', '.docx', '.xlsx', '.xls', '.tiff']
            UPLOAD_PATH = '/app/data/uploads'

            SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.file']
            CLIENT_SECRETS_FILE = '/app/data/credentials.json'

            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
            os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

            Google_Drive_Email_Attachment_Folder = '14dATc_XlxaqktxDXkIhk8s2KpnMyH5JQ'
            Google_Drive_SMS_Attachment_Folder = '1wOLeYUMJFAuzOxw0BjG2YQnZ7HBHsUZg'

            jobstores = {
                # 'mongo': SQLAlchemyJobStore(),
                'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
            }
            executors = {
                'default': ThreadPoolExecutor(2),
                # 'processpool': ProcessPoolExecutor(5)
            }
            job_defaults = {
                # 'coalesce': False,
                # 'max_instances': 3
            }

            scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone='US/Central')
            # scheduler.start()



        elif os.environ['DEPLOY_REGION'] == 'dev':

            logger.debug("Environment is dev")

            os.environ["url_to_start_reminder"] = "https://dev-messages-prepwithmo-hnhgb.ondigitalocean.app/"
            flask_secret_key = awsInstance.get_secret("vensti_admin", "flask_secret_key")
            SECRET_KEY = awsInstance.get_secret("vensti_admin", "flask_secret_key")
            dbUserName = awsInstance.get_secret("do_db_cred", "dev_username")
            dbPassword = awsInstance.get_secret("do_db_cred", "dev_password")
            SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://'+str(dbUserName)+':'+str(dbPassword)+'@app-27fee962-3fa3-41cb-aecc-35d29dbd568e-do-user-9096158-0.b.db.ondigitalocean.com:25060/db'
            SQLALCHEMY_TRACK_MODIFICATIONS = False

            twilio_account_sid = awsInstance.get_secret("twilio_cred", "TWILIO_ACCOUNT_SID")
            twilio_auth_token = awsInstance.get_secret("twilio_cred", "TWILIO_AUTH_TOKEN")
            twilioClient = TwilioClient(twilio_account_sid, twilio_auth_token)

            MAX_CONTENT_LENGTH = 1024 * 1024
            UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif']
            UPLOAD_PATH = '/app/data/uploads'

            SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.file']
            CLIENT_SECRETS_FILE = '/app/data/credentials.json'

            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
            os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

            Google_Drive_Email_Attachment_Folder = '14dATc_XlxaqktxDXkIhk8s2KpnMyH5JQ'
            Google_Drive_SMS_Attachment_Folder = '1wOLeYUMJFAuzOxw0BjG2YQnZ7HBHsUZg'

            jobstores = {
                # 'mongo': SQLAlchemyJobStore(),
                'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
            }
            executors = {
                'default': ThreadPoolExecutor(2),
                # 'processpool': ProcessPoolExecutor(5)
            }
            job_defaults = {
                # 'coalesce': False,
                # 'max_instances': 3
            }

            scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone='US/Central')
            #scheduler.start()





        elif os.environ['DEPLOY_REGION'] == 'prod':

            logger.debug("Environment is prod")

            os.environ["url_to_start_reminder"] = "https://pay.perfectscoremo.com/"
            flask_secret_key = awsInstance.get_secret("vensti_admin", "flask_secret_key")
            SECRET_KEY = awsInstance.get_secret("vensti_admin", "flask_secret_key")
            dbUserName = awsInstance.get_secret("do_db_cred", "username")
            dbPassword = awsInstance.get_secret("do_db_cred", "password")
            SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://' + str(dbUserName) + ':' + str(dbPassword) + '@app-36443af6-ab5a-4b47-a64e-564101e951d6-do-user-9096158-0.b.db.ondigitalocean.com:25060/db'
            SQLALCHEMY_TRACK_MODIFICATIONS = False

            twilio_account_sid = awsInstance.get_secret("twilio_cred", "TWILIO_ACCOUNT_SID")
            twilio_auth_token = awsInstance.get_secret("twilio_cred", "TWILIO_AUTH_TOKEN")
            twilioClient = TwilioClient(twilio_account_sid, twilio_auth_token)

            MAX_CONTENT_LENGTH = 1024 * 1024
            UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif']
            UPLOAD_PATH = '/app/data/uploads'

            #os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

            jobstores = {
                # 'mongo': SQLAlchemyJobStore(),
                'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
            }
            executors = {
                'default': ThreadPoolExecutor(2),
                # 'processpool': ProcessPoolExecutor(5)
            }
            job_defaults = {
                # 'coalesce': False,
                # 'max_instances': 3
            }

            scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone='US/Central')
            # scheduler.start()





    except Exception as e:
        print("error in initialization")
        print(e)
        traceback.print_exc()
        #trigger11

