import datetime
import pytz
import uuid
from app import db

from app.models import Recipient2,Student, Tutor, Lead, ApSchedulerJobs, GoogleCredentials,ApSchedulerJobsFurtherState
import pandas
from sqlalchemy import select
import logging
import traceback
from sqlalchemy.dialects.postgresql import insert
#from app.service import SendMessagesToClients

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class AppDBUtil():
    def __init__(self):
        pass

    @classmethod
    def setupTestStudents(cls):

        students = Student.__table__.delete()
        db.session.execute(students)

        recipients = Recipient2.__table__.delete()
        db.session.execute(recipients)

        jobs = ApSchedulerJobs.__table__.delete()
        db.session.execute(jobs)

        statement = Student(student_id='s-130860', prospect_id='p-130860', student_first_name='Student_1', student_last_name='One', student_phone_number='6172917242', student_email='mo@vensti.com',
                                           parent_1_salutation='Mr.', parent_1_first_name='Father_1', parent_1_last_name='One', parent_1_phone_number='4104280093', parent_1_email='mobolaji.akinpelu@yahoo.com',
                                           parent_2_salutation='Ms.', parent_2_first_name='Mother_1', parent_2_last_name='On', parent_2_phone_number='4133136331', parent_2_email='c@vensti.com')



        db.session.add(statement)

        statement = Student(student_id='s-106702', prospect_id='p-106702', student_first_name='Student_2', student_last_name='Two', student_phone_number='4793011592', student_email='mo@prepwithmo.com',
                                           parent_1_salutation='Mr.', parent_1_first_name='Father_2', parent_1_last_name='Two', parent_1_phone_number='4437636418', parent_1_email='beejaei@yahoo.com',
                                           parent_2_salutation='Ms.', parent_2_first_name='Mother_2', parent_2_last_name='Two', parent_2_phone_number='4792950378', parent_2_email='b@vensti.com')

        db.session.add(statement)

        statement = Student(student_id='s-111111', prospect_id='p-111111', student_first_name='Student_3', student_last_name='Three', student_phone_number='7202785988', student_email='mobolajiakinpelu00@gmail.com',
                               parent_1_salutation='Mr.', parent_1_first_name='Father_3', parent_1_last_name='Three', parent_1_phone_number='9725847364', parent_1_email='ben_brucey@yahoo.com',
                               parent_2_salutation='Ms.', parent_2_first_name='Mother_3', parent_2_last_name='Three', parent_2_phone_number='8622357387', parent_2_email='a@vensti.com')

        db.session.add(statement)

        cls.executeDBQuery()

    @classmethod
    def getGoogleCredentials(cls):
        credentials = db.session.query(GoogleCredentials).order_by(GoogleCredentials.credential_id.desc()).first()
        return credentials

    @classmethod
    def setGoogleCredentials(cls,credentials):
        try:
            credentials_to_add = GoogleCredentials(token=credentials.token, refresh_token=credentials.refresh_token, token_uri=credentials.token_uri,
                                                   client_id=credentials.client_id, client_secret=credentials.client_secret, scopes=credentials.scopes)

            db.session.add(credentials_to_add)
            cls.executeDBQuery()
        except Exception as e:
            print("Error in setGoogleCredentials")
            print(e)
            traceback.print_exc()

    @classmethod
    def updateJobUIState(cls, job_id='',job_ui_state={}):
        job = db.session.query(ApSchedulerJobsFurtherState).filter(ApSchedulerJobsFurtherState.job_id == job_id).first()
        if job:
            job.job_ui_state = job_ui_state
            job.date_job_last_modified = datetime.datetime.now(pytz.timezone('US/Central'))
            cls.executeDBQuery()

    @classmethod
    def setJobStatus(cls, job_id='', job_status=''):
        job = db.session.query(ApSchedulerJobsFurtherState).filter(ApSchedulerJobsFurtherState.job_id == job_id).first()
        if job:
            job.job_status = job_status
            job.date_job_last_modified = datetime.datetime.now(pytz.timezone('US/Central'))
            cls.executeDBQuery()

    @classmethod
    def setJobApschedulerState(cls, job_id='',job_apscheduler_state=''):
        job = db.session.query(ApSchedulerJobsFurtherState).filter(ApSchedulerJobsFurtherState.job_id == job_id).first()
        if job:
            job.job_apscheduler_state = job_apscheduler_state
            job.date_job_last_modified = datetime.datetime.now(pytz.timezone('US/Central'))
            cls.executeDBQuery()


    @classmethod
    def removeJobFurtherState(cls, job_id=''):
        job = db.session.query(ApSchedulerJobsFurtherState).filter(ApSchedulerJobsFurtherState.job_id == job_id).first()
        db.session.delete(job)
        cls.executeDBQuery()

    @classmethod
    def getJobUIStateById(cls, job_id=''):
        job = db.session.query(ApSchedulerJobsFurtherState).filter(ApSchedulerJobsFurtherState.job_id == job_id).first()
        return job

    @classmethod
    def getJobById(cls, job_id=''):
        job = db.session.query(ApSchedulerJobs).filter(ApSchedulerJobs.id == job_id).first()
        return job

    @classmethod
    def getJobFurtherStateById(cls, job_id=''):
        job = db.session.query(ApSchedulerJobsFurtherState).filter(ApSchedulerJobsFurtherState.job_id == job_id).first()
        return job

    @classmethod
    def getAllJobs(cls, job_id=''):
       #jobs = db.session.query(ApSchedulerJobs,ApSchedulerJobsFurtherState).filter(ApSchedulerJobs.id == ApSchedulerJobsFurtherState.job_id).all()
       jobs = db.session.query(ApSchedulerJobsFurtherState).all()
       return jobs

    @classmethod
    def getStudentByEmail(cls, student_email=''):
        student = db.session.query(Student).filter((Student.student_email == student_email) & (Student.is_active == True)).first()
        return student

    @classmethod
    def getParentByEmail(cls, parent_email=''):
        parent = db.session.query(Student).filter(((Student.parent_1_email == parent_email) | (Student.parent_2_email == parent_email)) & (Student.is_active == True)).first()
        return parent

    @classmethod
    def getLeadByEmail(cls, lead_email=''):
        lead = db.session.query(Lead).filter(Lead.lead_email == lead_email).first()
        return lead

    @classmethod
    def getTutorByEmail(cls, tutor_email=''):
        tutor = db.session.query(Tutor).filter(Tutor.tutor_email == tutor_email).first()
        return tutor

    @classmethod
    def getStudentByPhoneNumber(cls, student_phone_number=''):
        student = db.session.query(Student).filter((Student.student_phone_number == student_phone_number) & (Student.is_active == True)).first()
        return student

    @classmethod
    def getParentByPhoneNumber(cls, parent_phone_number=''):
        parent = db.session.query(Student).filter(((Student.parent_1_phone_number == parent_phone_number) | (Student.parent_2_phone_number == parent_phone_number)) & (Student.is_active == True)).first()
        return parent

    @classmethod
    def getLeadByPhoneNumber(cls, lead_phone_number=''):
        lead = db.session.query(Lead).filter(Lead.lead_phone_number == lead_phone_number).first()
        return lead

    @classmethod
    def getTutorByPhoneNumber(cls, tutor_phone_number=''):
        tutor = db.session.query(Tutor).filter(Tutor.tutor_phone_number == tutor_phone_number).first()
        return tutor

    @classmethod
    def getRecipients(cls):
        recipients = db.session.query(Recipient2).filter(Recipient2.is_active == True).all()
        return recipients

    @classmethod
    def getRecipientByRecipientId(cls, recipient_id=''):
        recipient = db.session.query(Recipient2).filter(Recipient2.recipient_id == recipient_id).first()
        return recipient

    @classmethod
    def updateRecipientTags(cls, recipient_email = '', recipient_phone_number = '', recipient_tags=[]):
        recipient_to_update = db.session.query(Recipient2).filter(((Recipient2.recipient_email == recipient_email) | (Recipient2.recipient_phone_number == recipient_phone_number)) & (Recipient2.is_active == True)).first()
        if recipient_to_update:
            recipient_to_update.recipient_tags = recipient_tags
            cls.executeDBQuery()
            logger.debug("{} updated successfully with {}!".format(recipient_to_update, recipient_tags))

    @classmethod
    def updateRecipientType(cls, recipient_email='', recipient_phone_number='', recipient_type=''):
        recipient_to_update = db.session.query(Recipient2).filter(((Recipient2.recipient_email == recipient_email) | (Recipient2.recipient_phone_number == recipient_phone_number)) & (Recipient2.is_active == True)).first()
        if recipient_to_update:
            recipient_to_update.recipient_type = recipient_type
            cls.executeDBQuery()

    @classmethod
    def getAllRecipientIds(cls):
        recipients = Recipient2.query.all()
        recipient_ids = []
        for recipient in recipients:
            recipient_ids.append(recipient.recipient_id)
        logger.debug("All recipient ids are: {}".format(recipient_ids))
        return recipient_ids

    @classmethod
    def createRecipientId(cls):
        existing_recipient_ids = AppDBUtil.getAllRecipientIds()
        recipient_id = "r-" + str(uuid.uuid4().int >> 64)[:6]
        while recipient_id in existing_recipient_ids:
            logger.debug("Recipient id {} already exists".format(recipient_id))
            recipient_id = "r-" + str(uuid.uuid4().int >> 64)[:6]
        return recipient_id


    @classmethod
    def executeDBQuery(cls):
        try:
            db.session.commit()
        except Exception as e:
            # if any kind of exception occurs, rollback transaction
            db.session.rollback()
            traceback.print_exc()
            raise e
        finally:
            db.session.close()




