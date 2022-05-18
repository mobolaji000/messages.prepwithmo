from flask import abort
import re
import flask
from pathlib import Path
import imghdr
from werkzeug.utils import secure_filename
from app.aws import AWSInstance
import google
import os
from app.dbUtil import AppDBUtil
from flask_login import UserMixin
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from app.config import Config
import traceback
from googleapiclient.http import MediaFileUpload,MediaIoBaseDownload
import io
from googleapiclient.discovery import build
import requests


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

import ssl
ssl._create_default_https_context =  ssl._create_unverified_context


class ValidateLogin():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.awsInstance = AWSInstance()

    def validateUserName(self):
        return True if self.username == self.awsInstance.get_secret("vensti_admin", "username") else False

    def validatePassword(self):
        return True if self.password == self.awsInstance.get_secret("vensti_admin", "password") else False


class User(UserMixin):
    def __init__(self, password):
        self.password = password
        self.awsInstance = AWSInstance()

    def is_authenticated(self):
        return True
        # return True if self.password == self.awsInstance.get_secret("vensti_admin","password") else False

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.awsInstance.get_secret("vensti_admin", "password"))

class ProcessAndSendMessages():
    def __init__(self):
        pass

    def validate_image(self,stream):
        header = stream.read(512)  # 512 bytes should be enough for a header check
        stream.seek(0)  # reset stream pointer
        format = imghdr.what(None, header)
        if not format:
            return None
        #print(format)
        #return '.jpg' + format == 'jpeg'
        #return '.' + format
        format_to_return = '.' + (format if format != 'jpeg' else 'jpg')
        logger.debug('Detected file extension is: ' + str(format_to_return))
        return format_to_return

    def processUploadedFiles(self,uploadedFiles=[],job_id='',is_email_or_sms=''):
        accessGoogleAPI = AccessGoogleAPI()
        ids_of_files_uploaded_to_google = []
        for index,uploaded_file in enumerate(uploadedFiles):
            if uploaded_file.filename != '':
                filename = secure_filename(uploaded_file.filename)
                if filename != '':
                    file_ext = os.path.splitext(filename)[1].replace('jpeg','jpg')
                    logger.debug('Uploaded file extension is: ' + str(file_ext))
                    if file_ext.lower() not in Config.UPLOAD_EXTENSIONS or file_ext.lower() != self.validate_image(uploaded_file.stream):
                        raise ValueError('Unacceptable file type.')
                    Path(Config.UPLOAD_PATH).mkdir(parents=True, exist_ok=True)
                    uploaded_file.save(os.path.join(Config.UPLOAD_PATH, filename))
                    id_of_file_uploaded_to_google = accessGoogleAPI.writeFilesToGoogle(os.path.join(Config.UPLOAD_PATH, filename), job_id=job_id,is_email_or_sms=is_email_or_sms)
                    ids_of_files_uploaded_to_google.append(id_of_file_uploaded_to_google)
        return ids_of_files_uploaded_to_google

    def parseEmailAddressesFromForm(self, allEmailRecipientsFromForm=''):
        eachSetOfEmailRecipients = allEmailRecipientsFromForm.split('\r\n')
        parsedListOfEmailRecipients = []
        for setOfEmailRecipients in eachSetOfEmailRecipients:
            splitSetOfEmailRecipients = re.split(',| - ', setOfEmailRecipients)
            setOfEmailRecipientsAsList = [ splitSetOfEmailRecipients[i].strip('[]') for i,a in enumerate(splitSetOfEmailRecipients) if i%2 == 1]
            if setOfEmailRecipientsAsList:
                parsedListOfEmailRecipients.append(setOfEmailRecipientsAsList)
        return parsedListOfEmailRecipients

    def parsePhoneNumbersFromForm(self, allSMSRecipientsFromForm=''):
        eachSetOfSMSRecipients = allSMSRecipientsFromForm.split('\r\n')
        parsedListOfSMSRecipients = []
        for setOfSMSRecipients in eachSetOfSMSRecipients:
            splitSetOfSMSRecipients = re.split(',| - ', setOfSMSRecipients)
            setOfSMSRecipientsAsList = [ splitSetOfSMSRecipients[i].strip('[]') for i,a in enumerate(splitSetOfSMSRecipients) if i%2 == 1]
            if setOfSMSRecipientsAsList:
                parsedListOfSMSRecipients.append(setOfSMSRecipientsAsList)
        return parsedListOfSMSRecipients

    def processSMSMessageReplacements(self, recipient_phone_number=[], message=''):
        # call the db to get the replacements from within this function

        # TODO apply strong error handling on client side for paremeters i.e. it should be impossible to have {lead_name} for a message whose recipient is not a lead; might have to add recipient type to Recipeint table

        relevant_recipient = AppDBUtil.getStudentByPhoneNumber(recipient_phone_number[0][-10:])
        if not relevant_recipient:
            relevant_recipient = AppDBUtil.getParentByPhoneNumber(recipient_phone_number[0][-10:])
        elif not relevant_recipient:
            relevant_recipient = AppDBUtil.getTutorByPhoneNumber(recipient_phone_number[0][-10:])
        elif not relevant_recipient:
            relevant_recipient = AppDBUtil.getLeadByPhoneNumber(recipient_phone_number[0][-10:])

        #print("message is: ",message)

        if relevant_recipient:

            replacement_message = message.replace('{student_first_name}', relevant_recipient.student_first_name)
            replacement_message = replacement_message.replace('{student_last_name}', relevant_recipient.student_last_name)
            replacement_message = replacement_message.replace('{parent_1_salutation}', relevant_recipient.parent_1_salutation)
            replacement_message = replacement_message.replace('{parent_1_first_name}', relevant_recipient.parent_1_first_name)
            replacement_message = replacement_message.replace('{parent_1_last_name}', relevant_recipient.parent_1_last_name)
            replacement_message = replacement_message.replace('{parent_2_first_name}', relevant_recipient.parent_2_first_name)
            replacement_message = replacement_message.replace('{parent_2_last_name}', relevant_recipient.parent_2_last_name)
            replacement_message = replacement_message.replace('{parent_2_salutation}', relevant_recipient.parent_2_salutation)

        else:
            #TODO break, print error to logs, send a messgae to mo about message replaement failure, and dont send anything
            print("break, print error to logs, send a messgae to mo about message replaement failure, and dont send anything")

        #print("replacemnt is: ", replacement_message)

        return replacement_message

    def processEmailMessageReplacements(self, recipient_email=[], message=''):
        # call the db to get the replacements from within this function

        # TODO apply strong error handling on client side for paremeters i.e. it should be impossible to have {lead_name} for a message whose recipient is not a lead; might have to add recipient type to Recipeint table

        relevant_recipient = AppDBUtil.getStudentByEmail(recipient_email[0])
        if not relevant_recipient:
            relevant_recipient = AppDBUtil.getParentByEmail(recipient_email[0])
        elif not relevant_recipient:
            relevant_recipient = AppDBUtil.getTutorByEmail(recipient_email[0])
        elif not relevant_recipient:
            relevant_recipient = AppDBUtil.getLeadByEmail(recipient_email[0])

        #print("message is: ",message)

        if relevant_recipient:

            replacement_message = message.replace('{student_first_name}', relevant_recipient.student_first_name)
            replacement_message = replacement_message.replace('{student_last_name}', relevant_recipient.student_last_name)
            replacement_message = replacement_message.replace('{parent_1_salutation}', relevant_recipient.parent_1_salutation)
            replacement_message = replacement_message.replace('{parent_1_first_name}', relevant_recipient.parent_1_first_name)
            replacement_message = replacement_message.replace('{parent_1_last_name}', relevant_recipient.parent_1_last_name)
            replacement_message = replacement_message.replace('{parent_2_first_name}', relevant_recipient.parent_2_first_name)
            replacement_message = replacement_message.replace('{parent_2_last_name}', relevant_recipient.parent_2_last_name)
            replacement_message = replacement_message.replace('{parent_2_salutation}', relevant_recipient.parent_2_salutation)

        else:
            # TODO break, print error to logs, send a messgae to mo about message replaement failure, and dont send anything
            print("break, print error to logs, send a messgae to mo about message replaement failure, and dont send anything")

        #print("replacemnt is: ", replacement_message)

        return replacement_message

    def processSMSMessagesToSend(self,recipients_phone_numbers=[], sms_contents=[]):
        processed_contents = []

        for recipient_phone_number, content in zip(recipients_phone_numbers,sms_contents):
            processed_contents.append(self.convertMessageToIdealSMSForm(self.processSMSMessageReplacements(recipient_phone_number, content)))

        zipped_and_processed_recipients_contents = zip(recipients_phone_numbers, processed_contents)
        return zipped_and_processed_recipients_contents

    def processEmailMessagesToSend(self, recipients_emails=[], emails_subjects=[], emails_contents=[]):

        processed_subjects = []
        processed_contents = []

        for recipient_email, subject, content in zip(recipients_emails, emails_subjects, emails_contents):
            processed_subjects.append(self.processEmailMessageReplacements(recipient_email, subject))
            processed_contents.append(self.convertMessageToHTML(self.processEmailMessageReplacements(recipient_email, content)))

        zipped_and_processed_recipients_subjects_contents = zip(recipients_emails, processed_subjects, processed_contents)
        return zipped_and_processed_recipients_subjects_contents

    def createJobToSendSMSMessages(self,sms_messages_to_setup={},zipped_and_processed_recipients_contents=zip(),job_id='', ids_of_files_uploaded_to_google=[],create_or_modify=''):

        if create_or_modify == 'create':
            if sms_messages_to_setup['sms_job_type'] == 'sms_date_trigger':
                Config.scheduler.add_job(self.sendSMSMessage, DateTrigger(**sms_messages_to_setup['sms_job_parameters'], timezone='US/Central'),
                                         kwargs={'zipped_and_processed_recipients_contents': zipped_and_processed_recipients_contents, 'ids_of_files_uploaded_to_google': ids_of_files_uploaded_to_google}, id=job_id,
                                         name=sms_messages_to_setup['sms_description'])
            elif sms_messages_to_setup['sms_job_type'] == 'sms_cron_trigger':
                Config.scheduler.add_job(self.sendSMSMessage, CronTrigger(**sms_messages_to_setup['sms_job_parameters'], timezone='US/Central'),
                                         kwargs={'zipped_and_processed_recipients_contents': zipped_and_processed_recipients_contents, 'ids_of_files_uploaded_to_google': ids_of_files_uploaded_to_google}, id=job_id,
                                         name=sms_messages_to_setup['sms_description'])
            elif sms_messages_to_setup['sms_job_type'] == 'sms_interval_trigger':
                Config.scheduler.add_job(self.sendSMSMessage, IntervalTrigger(**sms_messages_to_setup['sms_job_parameters'], timezone='US/Central'),
                                         kwargs={'zipped_and_processed_recipients_contents': zipped_and_processed_recipients_contents, 'ids_of_files_uploaded_to_google': ids_of_files_uploaded_to_google}, id=job_id,
                                         name=sms_messages_to_setup['sms_description'])

        elif create_or_modify == 'modify':
            if sms_messages_to_setup['sms_job_type'] == 'sms_date_trigger':
                Config.scheduler.modify_job(job_id=job_id, jobstore='default', func=self.sendSMSMessage, args=[],
                                            kwargs={'zipped_and_processed_recipients_contents': zipped_and_processed_recipients_contents, 'ids_of_files_uploaded_to_google': ids_of_files_uploaded_to_google},
                                            name=sms_messages_to_setup['sms_description'])

                Config.scheduler.reschedule_job(job_id=job_id, jobstore='default', trigger=DateTrigger(**sms_messages_to_setup['email_job_parameters'], timezone='US/Central'))

            elif sms_messages_to_setup['sms_job_type'] == 'sms_cron_trigger':
                Config.scheduler.modify_job(job_id=job_id, jobstore='default', func=self.sendSMSMessage, args=[],
                                            kwargs={'zipped_and_processed_recipients_contents': zipped_and_processed_recipients_contents, 'ids_of_files_uploaded_to_google': ids_of_files_uploaded_to_google},
                                            name=sms_messages_to_setup['sms_description'])

                Config.scheduler.reschedule_job(job_id=job_id, jobstore='default', trigger=CronTrigger(**sms_messages_to_setup['email_job_parameters'], timezone='US/Central'))

            elif sms_messages_to_setup['sms_job_type'] == 'sms_interval_trigger':
                Config.scheduler.modify_job(job_id=job_id, jobstore='default', func=self.sendSMSMessage, args=[],
                                            kwargs={'zipped_and_processed_recipients_contents': zipped_and_processed_recipients_contents, 'ids_of_files_uploaded_to_google': ids_of_files_uploaded_to_google},
                                            name=sms_messages_to_setup['sms_description'])

                Config.scheduler.reschedule_job(job_id=job_id, jobstore='default', trigger=IntervalTrigger(**sms_messages_to_setup['email_job_parameters'], timezone='US/Central'))

    def createJobToSendEmailMessages(self, email_messages_to_setup={}, zipped_and_processed_recipients_subjects_contents=zip(), job_id='', ids_of_files_uploaded_to_google=[],create_or_modify=''):

        if create_or_modify == 'create':
            if email_messages_to_setup['email_job_type'] == 'email_date_trigger':
                Config.scheduler.add_job(self.sendEmailMessage, DateTrigger(**email_messages_to_setup['email_job_parameters'], timezone='US/Central'),
                                         kwargs={'zipped_and_processed_recipients_subjects_contents': zipped_and_processed_recipients_subjects_contents, 'ids_of_files_uploaded_to_google':ids_of_files_uploaded_to_google}, id=job_id, name=email_messages_to_setup['email_description'])
            elif email_messages_to_setup['email_job_type'] == 'email_cron_trigger':
                Config.scheduler.add_job(self.sendEmailMessage, CronTrigger(**email_messages_to_setup['email_job_parameters'], timezone='US/Central'),
                                         kwargs={'zipped_and_processed_recipients_subjects_contents': zipped_and_processed_recipients_subjects_contents, 'ids_of_files_uploaded_to_google':ids_of_files_uploaded_to_google}, id=job_id, name=email_messages_to_setup['email_description'])
            elif email_messages_to_setup['email_job_type'] == 'email_interval_trigger':
                Config.scheduler.add_job(self.sendEmailMessage, IntervalTrigger(**email_messages_to_setup['email_job_parameters'], timezone='US/Central'),
                                         kwargs={'zipped_and_processed_recipients_subjects_contents': zipped_and_processed_recipients_subjects_contents, 'ids_of_files_uploaded_to_google':ids_of_files_uploaded_to_google}, id=job_id, name=email_messages_to_setup['email_description'])
        elif create_or_modify == 'modify':
            if email_messages_to_setup['email_job_type'] == 'email_date_trigger':
                Config.scheduler.modify_job(job_id=job_id,jobstore='default',func=self.sendEmailMessage,args=[],
                                         kwargs={'zipped_and_processed_recipients_subjects_contents': zipped_and_processed_recipients_subjects_contents, 'ids_of_files_uploaded_to_google': ids_of_files_uploaded_to_google},
                                         name=email_messages_to_setup['email_description'])

                Config.scheduler.reschedule_job(job_id=job_id, jobstore='default', trigger=DateTrigger(**email_messages_to_setup['email_job_parameters'], timezone='US/Central'))


            elif email_messages_to_setup['email_job_type'] == 'email_cron_trigger':
                Config.scheduler.modify_job(job_id=job_id,jobstore='default',func=self.sendEmailMessage,args=[],
                                         kwargs={'zipped_and_processed_recipients_subjects_contents': zipped_and_processed_recipients_subjects_contents, 'ids_of_files_uploaded_to_google': ids_of_files_uploaded_to_google},
                                         name=email_messages_to_setup['email_description'])

                Config.scheduler.reschedule_job(job_id=job_id, jobstore='default', trigger=CronTrigger(**email_messages_to_setup['email_job_parameters'], timezone='US/Central'))


            elif email_messages_to_setup['email_job_type'] == 'email_interval_trigger':
                Config.scheduler.modify_job(job_id=job_id,jobstore='default',func=self.sendEmailMessage, args=[],
                                         kwargs={'zipped_and_processed_recipients_subjects_contents': zipped_and_processed_recipients_subjects_contents, 'ids_of_files_uploaded_to_google': ids_of_files_uploaded_to_google},
                                         name=email_messages_to_setup['email_description'])

                Config.scheduler.reschedule_job(job_id=job_id, jobstore='default', trigger=IntervalTrigger(**email_messages_to_setup['email_job_parameters'], timezone='US/Central'))


    def convertMessageToIdealSMSForm(self, message):
        #could be used in the future for any sms processing
       return message


    def convertMessageToHTML(self,message):
        message_as_list = message.split('\r\n')
        html_message = ''
        html_message = html_message + """<html><head></head><body>"""
        for item in message_as_list:
            html_message = html_message + """<span>""" + item + "</span><br>"
        html_message = html_message + """</body></html>"""
        return html_message



    def sendEmailMessage(self, zipped_and_processed_recipients_subjects_contents=zip(),ids_of_files_uploaded_to_google=[]):
        # TODO implement failsafe where if postprocessed message contains { or }, message is not sent and you are sent a text notification

        accessGoogleAPI = AccessGoogleAPI()
        email_attachments_and_their_details = accessGoogleAPI.getFilesFromGoogle(ids_of_files_uploaded_to_google)

        awsInstance = AWSInstance()
        for recipients_emails,subject,content in zipped_and_processed_recipients_subjects_contents:
            awsInstance.send_email(to_addresses=recipients_emails, subject=subject,message=content,email_attachments_and_their_details=email_attachments_and_their_details)
            logger.debug('{} just sent to {}'.format(content, recipients_emails))


    def sendSMSMessage(self, zipped_and_processed_recipients_contents=zip(),ids_of_files_uploaded_to_google=[]):
        accessGoogleAPI = AccessGoogleAPI()
        sms_attachments_and_their_details = accessGoogleAPI.getFilesFromGoogle(ids_of_files_uploaded_to_google)

        for recipients_phone_numbers, content in zipped_and_processed_recipients_contents:

            # cls.twilioClient.messaging.services('MGd37b2dce09791f42239043b6e949f96b').delete()
            conversations = Config.twilioClient.conversations.conversations.list(limit=50)
            for record in conversations:
                print(record.sid)
                Config.twilioClient.conversations.conversations(record.sid).delete()

            conversation = Config.twilioClient.conversations.conversations.create(messaging_service_sid=Config.twilio_messaging_service_sid, friendly_name='MessageJobs')
            print("conversation created!")
            print(conversation.sid)

            Config.twilioClient.conversations.conversations(conversation.sid).participants.create(messaging_binding_projected_address=Config.twilio_sms_number)

            for phone_number in recipients_phone_numbers:
                print(phone_number)
                Config.twilioClient.conversations.conversations(conversation.sid).participants.create(messaging_binding_address='+1'+phone_number)

            Config.twilioClient.conversations.conversations(conversation.sid).messages.create(body=content, author=Config.twilio_sms_number)
            self.sendSMSMedia(conversation=conversation, sms_attachments_and_their_details=sms_attachments_and_their_details)

            logger.debug('{} just sent to {}'.format(content, recipients_phone_numbers))

    def sendSMSMedia(self, conversation='', sms_attachments_and_their_details={}):
        for attachment_id, (attachment_name, attachment) in sms_attachments_and_their_details.items():
            api_url = "https://mcs.us1.twilio.com/v1/Services/" + conversation.chat_service_sid + "/Media"

            #TODO how will you handle other file types e.g. png, pdf etc. you have to as it does not send otherwise: https://www.twilio.com/docs/sms/accepted-mime-types
            #TODO there's a 5MB limit for sending media with Twilio
            headers = {'Content-Type': 'image/jpeg'}
            response = requests.post(api_url, auth=(Config.twilio_account_sid, Config.twilio_auth_token), data=attachment.getbuffer(), verify=False, headers=headers)

            #print(response.json())
            logger.debug('Media message status code is {}'.format(response.status_code))
            media_sid = response.json()['sid']
            Config.twilioClient.conversations.conversations(conversation.sid).messages.create(media_sid=media_sid, author=Config.twilio_sms_number)
            logger.debug('Media {} just sent to conversation {}'.format(media_sid, conversation))

class AccessGoogleAPI():
    def __init__(self):
        pass

    @classmethod
    def credentials_to_dict(cls, credentials):
        return {'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes}


    @classmethod
    def getCredentials(cls):
        stored_google_credentials = AppDBUtil.getGoogleCredentials()
        credentials = google.oauth2.credentials.Credentials(**AccessGoogleAPI.credentials_to_dict(stored_google_credentials))
        return credentials


    def getFilesFromGoogle(self, ids_of_files_uploaded_to_google=[]):
        #try:
        credentials = self.getCredentials()
        files_and_their_details = {}
        drive_service = build('drive', 'v3', credentials=credentials)
        logger.debug("getFilesFromGoogle: ids_of_files_uploaded_to_google: "+ str(ids_of_files_uploaded_to_google))
        for id in ids_of_files_uploaded_to_google:
            request = drive_service.files().get_media(fileId=id,fields='name')
            file_name = drive_service.files().get(fileId=id,fields='name').execute()['name']
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logger.debug ("Download {}".format(str(int(status.progress() * 100))))
            files_and_their_details[id] = (file_name,fh)
        return files_and_their_details
        # except Exception as e:
        #     print("Error in getFilesFromGoogle")
        #     print(e)
        #     traceback.print_exc()
        #     raise e


    def writeFilesToGoogle(self, filename='', job_id='',is_email_or_sms=''):
        #try:
        credentials = self.getCredentials()
        drive_service = build('drive', 'v3', credentials=credentials)

        root_folder_id = Config.Google_Drive_Email_Attachment_Folder if is_email_or_sms=='email' else Config.Google_Drive_SMS_Attachment_Folder if is_email_or_sms=='sms' else ''

        folder_exists = drive_service.files().list(q="mimeType='application/vnd.google-apps.folder' and name='{}'".format(job_id),spaces='drive',fields='nextPageToken, files(id, name)',pageToken=None).execute()
        if folder_exists['files']:
            folder_for_attachments = folder_exists['files'][0]
        else:
            folder_metadata = {
                'name': job_id,
                'parents': [root_folder_id],
                'mimeType': 'application/vnd.google-apps.folder'
            }

            folder_for_attachments = drive_service.files().create(body=folder_metadata, fields='id').execute()


        file_metadata = {
            'name': filename.split('/')[-1],
            'parents': [folder_for_attachments.get('id')]
        }

        logger.debug("writeFilesToGoogle: job_id written to Google: "+ str(job_id))

        media = MediaFileUpload(filename,resumable=True)
        file = drive_service.files().create(body=file_metadata,media_body=media,fields='id').execute()
        logger.debug('File ID: %s' % file.get('id'))

        # Save credentials back to session in case access token was refreshed.
        # ACTION ITEM: In a production app, you likely want to save these
        #              credentials in a persistent database instead.

        #TODO understand and implement token refresh process for Google; perhaps this is it i.e Google automatically refreshes it and you have to remember to persist it

        AppDBUtil.setGoogleCredentials(credentials)
        return file.get('id')
        # except Exception as e:
        #     print("Error in writeFilesToGoogle")
        #     print(e)
        #     traceback.print_exc()
        #     raise e
