from app import db, metadata
from sqlalchemy.dialects.postgresql import JSONB, BYTEA
from sqlalchemy import event, DDL
from sqlalchemy.sql import text
from queries import student_table_trigger_text,tutor_table_trigger_text,lead_table_trigger_text,prospect_table_trigger_text
from app import Config

from redis import Redis
from rq import Queue
from dblistener import DBListener
import os

from apscheduler.events import EVENT_JOB_ADDED, EVENT_JOB_REMOVED, EVENT_JOB_MODIFIED
import traceback

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class Message(db.Model):
    message_id = db.Column(db.String(8), primary_key=True, index=True, nullable=False, unique=True, default='')

    def __repr__(self):
        return '<Message {}>'.format(self.message_id)

class ApSchedulerJobsFurtherState(db.Model):
    job_id = db.Column(db.String, primary_key=True, index=True, nullable=False)
    date_job_created = db.Column(db.DateTime(timezone=True), index=True, server_default=db.func.now())

    date_job_last_modified = db.Column(db.DateTime(timezone=True), index=True, server_default=db.func.now())
    job_status = db.Column(db.Enum('active', 'paused', 'ended', name='job_status'), index=True, server_default='active')
    job_ui_state = db.Column(JSONB, index=True, nullable=False, server_default='{}')
    job_apscheduler_state = db.Column(BYTEA, index=True, nullable=False, server_default='')


    def __repr__(self):
        return '<ApSchedulerJobsFurtherState {}>'.format(self.job_id)


class GoogleCredentials(db.Model):
    credential_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    date_credential_created = db.Column(db.DateTime(timezone=True), index=True, server_default=db.func.now())
    token = db.Column(db.String, nullable=False, default='')
    refresh_token = db.Column(db.String, nullable=False, default='')
    token_uri = db.Column(db.String, nullable=False, default='')
    client_id = db.Column(db.String, nullable=False, default='')
    client_secret = db.Column(db.String, nullable=False, default='')
    scopes = db.Column(db.ARRAY(db.String), nullable=False, default='')

    def __repr__(self):
        return '<Credential {}>'.format(self.credential_id)



class Recipient(db.Model):
    recipient_id = db.Column(db.String(8), primary_key=True, index=True, nullable=False, unique=True, default='')
    date_recipient_created = db.Column(db.DateTime(timezone=True), index=True, server_default=db.func.now())
    recipient_salutation = db.Column(db.String(6), index=True, nullable=True, default='')
    recipient_first_name = db.Column(db.String(64), index=True, nullable=True, default='')
    recipient_last_name = db.Column(db.String(64), index=True, nullable=True, default='')
    recipient_phone_number = db.Column(db.String(22), index=True, unique=True, nullable=True, default='')
    recipient_email = db.Column(db.String(120), index=True, unique=True, nullable=True, default='')
    recipient_type = db.Column(db.Enum('parent_1', 'parent_2', 'student', 'lead', 'tutor', 'prospect', 'other', name='recipient_type'), index=True, nullable=True, default='')
    recipient_tags = db.Column(db.ARRAY(db.String), index=True, nullable=True, default='')
    recipient_description = db.Column(db.String(200), index=True, nullable=True, default='')
    recipient_source_id = db.Column(db.String(8), index=True, nullable=True, unique=False, default='')
    is_active = db.Column(db.Boolean, unique=False,nullable=False, server_default='True')

    #TODO possible but unlikely bug: if a former studnet goes on to be a tutor, there will be an error as phone numer and email should be unique; maybe research how ot make a compound priamry key and then do that using phone-number, email, and recipient type

    #how to edit enum type##
    #https://stackoverflow.com/questions/1771543/adding-a-new-value-to-an-existing-enum-type/7834949#7834949
    #https://stackoverflow.com/questions/25811017/how-to-delete-an-enum-type-value-in-postgres

    def __repr__(self):
        return '<Recipient {}>'.format(self.recipient_id)

class Lead(db.Model):
    __tablename__ = 'lead'
    __table_args__ = {'autoload': True, 'autoload_with': db.engine}


    def __repr__(self):
        return '<Lead created with lead_id {}>'.format(self.lead_id)

class Prospect(db.Model):
    __tablename__ = 'prospect'
    __table_args__ = {'autoload': True, 'autoload_with': db.engine}


    def __repr__(self):
        return '<Prospect created with prospect_id {}>'.format(self.lead_id)

class ApSchedulerJobs(db.Model):

    __tablename__ = 'apscheduler_jobs'
    __table_args__ = {'autoload': True, 'autoload_with': db.engine}


    def __repr__(self):
        return '<Job {} created is: >'.format(self.job_state)

class Tutor(db.Model):

    __tablename__ = 'tutor'
    __table_args__ = {'autoload': True, 'autoload_with': db.engine}


    def __repr__(self):
        return '<Tutor {} created>'.format(self.tutor_first_name)

class Student(db.Model):

    __tablename__ = 'student'
    __table_args__ = {'autoload': True,'autoload_with': db.engine}


    def __repr__(self):
        return '<Student {} created with student info {} {}>'.format(self.parent_1_last_name, self.student_id)

def listen_for_job_added(event):
    try:
        with db.engine.begin() as connection:
            apscheduler_job_further_state = ApSchedulerJobsFurtherState.__table__
            apscheduler_job = ApSchedulerJobs.__table__
            job = connection.execute(apscheduler_job.select().where(apscheduler_job.c.id==event.job_id)).first()
            #TODO you need more nuanced setting of status ie. for the three different trigger types, what shpuld their startus be when inserted, modified, and removed
            connection.execute(apscheduler_job_further_state.insert().values(job_id=event.job_id,job_apscheduler_state=job.job_state,job_status='active'))
        logger.info("Job inserted is: {}".format(event.job_id))
    except Exception as e:
        logger.error("Error in inserting {}".format(event.job_id))
        logger.error(e)
        traceback.print_exc()

def listen_for_job_removed(event):
    try:
        with db.engine.begin() as connection:
            apscheduler_job_further_state = ApSchedulerJobsFurtherState.__table__
            connection.execute(apscheduler_job_further_state.update().where(apscheduler_job_further_state.c.job_id==event.job_id).values(job_status='ended'))

        #connection.execute(apscheduler_job_further_state.delete().where(apscheduler_job_further_state.c.job_id==event.job_id))
        logger.info("Job removed is: {}".format(event.job_id))
    except Exception as e:
        logger.error("Error in removing {}".format(event.job_id))
        logger.error(e)
        traceback.print_exc()

def listen_for_job_modified(event):
    try:
        with db.engine.begin() as connection:
            apscheduler_job_further_state = ApSchedulerJobsFurtherState.__table__
            apscheduler_job = ApSchedulerJobs.__table__

            job = connection.execute(apscheduler_job.select().where(apscheduler_job.c.id == event.job_id)).first()
            connection.execute(apscheduler_job_further_state.update().where(apscheduler_job_further_state.c.job_id==event.job_id).values(job_apscheduler_state=job.job_state))
            #
            #
            # job_apscheduler_state = pickle.loads(job.job_apscheduler_state)
            # job_trigger_type = str(job_apscheduler_state['trigger'].__class__.__name__).split('Trigger')[0]#
            # job_status = ''
            #
            # if job_trigger_type == 'Date':
            #     job_status = 'active'

        logger.info("Job modified is: {}".format(event.job_id))
    except Exception as e:
        logger.error("Error in modifying {}".format(event.job_id))
        logger.error(e)
        traceback.print_exc()

Config.scheduler.add_listener(listen_for_job_added, EVENT_JOB_ADDED)
Config.scheduler.add_listener(listen_for_job_removed, EVENT_JOB_REMOVED)
Config.scheduler.add_listener(listen_for_job_modified, EVENT_JOB_MODIFIED)

#event.listen(Recipient.__table__, 'after_create', trig_ddl.execute_if(dialect='postgresql'))

q = Queue(connection=Redis(host='redis', port=6379, decode_responses=True),default_timeout=-1)
result = q.enqueue(DBListener(os.environ.get('psycopg_url'), os.environ.get('psycopg_db'), os.environ.get('psycopg_port'), Config.dbUserName, Config.dbPassword).dblisten)

@event.listens_for(Student, 'after_insert')
def receive_after_insert(mapper, connection, target):
    from dbUtil import AppDBUtil
    try:
        recipient = Recipient.__table__
        recipient_id = AppDBUtil.createRecipientId()
        connection.execute(recipient.insert().values(recipient_id=recipient_id,recipient_email=target.student_email,recipient_first_name=target.student_first_name,recipient_last_name=target.student_last_name,recipient_phone_number=target.student_phone_number,recipient_type='student',is_active=target.is_active,recipient_source_id=target.student_id))
        logger.info("Recipient {} inserted based on Student {}".format(recipient_id,target.student_id))


        if target.parent_1_email or target.parent_1_phone_number:
            recipient_id = AppDBUtil.createRecipientId()
            connection.execute(recipient.insert().values(recipient_id=recipient_id, recipient_email=target.parent_1_email, recipient_first_name=target.parent_1_first_name, recipient_last_name=target.parent_1_last_name,recipient_phone_number=target.parent_1_phone_number,recipient_salutation=target.parent_1_salutation,recipient_type='parent_1', is_active=target.is_active,recipient_source_id=target.student_id))
            logger.info("Recipient {} inserted based on Student {}".format(recipient_id, target.student_id))

        if target.parent_2_email or target.parent_2_phone_number:
            recipient_id = AppDBUtil.createRecipientId()
            connection.execute(recipient.insert().values(recipient_id=recipient_id, recipient_email=target.parent_2_email, recipient_first_name=target.parent_2_first_name, recipient_last_name=target.parent_2_last_name,recipient_phone_number=target.parent_2_phone_number,recipient_salutation=target.parent_2_salutation,recipient_type='parent_2',is_active=target.is_active,recipient_source_id=target.student_id))
            logger.info("Recipient {} inserted based on Student {}".format(recipient_id, target.student_id))

    except Exception as e:
        logger.error("Error in Student receive_after_insert")
        logger.error(e)
        traceback.print_exc()


@event.listens_for(Lead, 'after_insert')
def receive_after_insert(mapper, connection, target):
    from dbUtil import AppDBUtil
    try:
        recipient = Recipient.__table__
        recipient_id = AppDBUtil.createRecipientId()
        connection.execute(recipient.insert().values(recipient_id=recipient_id,recipient_email=target.lead_email,recipient_first_name=target.lead_name,recipient_last_name=target.lead_name,recipient_phone_number=target.lead_phone_number,recipient_type='lead',recipient_source_id=target.lead_id))
        #TODO uncomment after figuring out how to add is_active to recipient table
        #connection.execute(recipient.insert().values(recipient_id=recipient_id,recipient_email=target.lead_email,recipient_first_name=target.lead_name,recipient_last_name=target.lead_name,recipient_phone_number=target.lead_phone_number,recipient_type='lead',is_active=target.is_active,recipient_source_id=target.lead_id))

        logger.info("Recipient {} inserted based on Lead {}".format(recipient_id,target.lead_id))

    except Exception as e:
        logger.error("Error in Lead receive_after_insert")
        logger.error(e)
        traceback.print_exc()


@event.listens_for(Prospect, 'after_insert')
def receive_after_insert(mapper, connection, target):
    from dbUtil import AppDBUtil
    try:
        recipient = Recipient.__table__
        recipient_id = AppDBUtil.createRecipientId()
        connection.execute(recipient.insert().values(recipient_id=recipient_id,recipient_email=target.prospect_email,recipient_first_name=target.prospect_first_name,recipient_last_name=target.prospect_last_name,recipient_phone_number=target.prospect_phone_number,recipient_type='prospect',recipient_source_id=target.prospect_id))
        logger.info("Recipient {} inserted based on Prospect {}".format(recipient_id,target.prospect_id))

    except Exception as e:
        logger.error("Error in Prospect receive_after_insert")
        logger.error(e)
        traceback.print_exc()

@event.listens_for(Tutor, 'after_insert')
def receive_after_insert(mapper, connection, target):
    from dbUtil import AppDBUtil
    try:
        recipient = Recipient.__table__
        recipient_id = AppDBUtil.createRecipientId()
        connection.execute(recipient.insert().values(recipient_id=recipient_id,recipient_email=target.tutor_email,recipient_first_name=target.tutor_first_name,recipient_last_name=target.tutor_last_name,recipient_phone_number=target.tutor_phone_number,recipient_type='tutor',recipient_source_id=target.user_id))
        logger.info("Recipient {} inserted based on Tutor {}".format(recipient_id,target.user_id))

    except Exception as e:
        logger.error("Error in Tutor receive_after_insert")
        logger.error(e)
        traceback.print_exc()

@event.listens_for(Student, 'after_update')
def receive_after_update(mapper, connection, target):
    #TODO There is currently no way to update a student via the ORM in the entire prepwithmo applications suite. So it is pointless to develop this method as it will only execute if after an update via the ORM. Whenever update via the ORM is available, the way to develop this will be to create a column in receipient called recipient_source_id, which will contain the ids of the source of the recipient e.g. student-id, tutor-id etc and a foreign key relation ship from the applicabnle tables to the recipient table. When values in these accompanying tables get updated, their ids will be used to check the recipient_source_id column to know which row in the recipient table needs to be updated.
    pass

    # from dbUtil import AppDBUtil
    # try:
    #     recipient = Recipient.__table__
    #     recipient_id = AppDBUtil.createRecipientId()
    #     connection.execute(recipient.update().where(recipient.recipient_source_id == target.student_id).values(recipient_email=target.student_email, recipient_first_name=target.student_first_name, recipient_last_name=target.student_last_name, recipient_phone_number=target.student_phone_number,recipient_type='student', is_active=target.is_active))
    #
    #     if target.parent_1_email or target.parent_1_phone_number:
    #         recipient_id = AppDBUtil.createRecipientId()
    #         connection.execute(recipient.insert().values(recipient_id=recipient_id, recipient_email=target.parent_1_email, recipient_first_name=target.parent_1_first_name, recipient_last_name=target.parent_1_last_name,recipient_phone_number=target.parent_1_phone_number, recipient_type='parent_1', is_active=target.is_active))
    #     if target.parent_2_email or target.parent_2_phone_number:
    #         recipient_id = AppDBUtil.createRecipientId()
    #         connection.execute(recipient.insert().values(recipient_id=recipient_id, recipient_email=target.parent_2_email, recipient_first_name=target.parent_2_first_name, recipient_last_name=target.parent_2_last_name,recipient_phone_number=target.parent_2_phone_number, recipient_type='parent_2', is_active=target.is_active))
    #
    # except Exception as e:
    #     print("Error in receive_after_insert")
    #     print(e)
    #     traceback.print_exc()
        #connection.execute(update(Tutor).where(target.id == Tutor.__table__.c.user_id).values(tutor_email=target.email,tutor_first_name=target.first_name,tutor_last_name=target.last_name,tutor_phone_number=target.phone_number,is_active=target.active))


@event.listens_for(Student, 'after_delete')
def receive_after_delete(mapper, connection, target):
    #TODO probably dont want to delete recipients even if the upstrema source is deleted
    pass
    #children = relationship("Child", cascade="all,delete", backref="parent")
    #https://stackoverflow.com/questions/5033547/sqlalchemy-cascade-delete


db.create_all()

try:
    db.session.commit()
    with db.engine.connect() as con:
        con.execute(text(student_table_trigger_text))
        con.execute(text(tutor_table_trigger_text))
        con.execute(text(lead_table_trigger_text))
        con.execute(text(prospect_table_trigger_text))
except:
    db.session.rollback()
    raise
finally:
    db.session.close()

