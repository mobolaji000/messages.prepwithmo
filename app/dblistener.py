from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import select
import psycopg2
import traceback


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)




class DBListener():
    def __init__(self, url=None,db=None,port=None,username=None, password=None):
        # self.dbUserName = os.environ.get('dbUserNameLocal')
        # self.dbPassword = os.environ.get('dbPasswordLocal')

        # self.connection = psycopg2.connect(host='192.168.1.135', user=os.environ.get('dbUserNameLocal'),
        #                                    password=os.environ.get('dbPasswordLocal'),
        #                                    dbname='mobolajioo', port=5432,
        #                                    keepalives=1, keepalives_idle=30, keepalives_interval=10, keepalives_count=5)

        self.username = username
        self.password = password
        self.url = url
        self.db = db
        self.port = port





#This file contains database level notifcations for "updates" to certain tables e.g. student, lead, tutor etc
#This is as opposed to models.py, which contains similar notifications but only at the ORM level for inserts
#The idea is that most inserts will occur through defined routes/views which will then hit the necessary ORM listener
#But editing databases is a usecase faced often enough (e.g. student inserts wrong email on signup) and the listners here propagte such changes as necessary
    def dblisten(self):
        try:

            self.connection = psycopg2.connect(host=self.url, user=self.username,
                                               password=self.password, dbname=self.db, port=self.port,
                                               keepalives=1, keepalives_idle=30, keepalives_interval=10, keepalives_count=5)

            self.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

            self.cursor = self.connection.cursor()

            self.cursor.execute(f"LISTEN student_table_changed;")
            self.cursor.execute(f"LISTEN lead_table_changed;")
            self.cursor.execute(f"LISTEN tutor_table_changed;")
            self.cursor.execute(f"LISTEN prospect_table_changed;")

            while True:
                select.select([self.connection], [], [])
                self.connection.poll()
                while self.connection.notifies:
                    notification = self.connection.notifies.pop(0)
                    logger.debug("Notification is: {} {} {}".format(notification.pid,notification.channel,notification.payload))
                    channel = notification.channel
                    payload = notification.payload

                    basics = payload.split("-Basics End")[0]
                    logger.info("basics are {}".format(basics))
                    details = payload.split("-Basics End")[1]
                    logger.info("details are {}".format(details))
                    operation = basics.split(" and ")[0].split(" = ")[1]
                    logger.info("operation is {}".format(operation))
                    id = basics.split(" and ")[1].split(" = ")[1]
                    logger.info("id is {}".format(id))

                    if channel == 'student_table_changed':
                        self.updateRecipientFromStudentAndParent(id=id, details=details, operation=operation)
                    elif channel == 'lead_table_changed':
                        self.updateRecipientFromLead(id=id, details=details, operation=operation)
                    elif channel == 'tutor_table_changed':
                        self.updateRecipientFromTutor(id=id, details=details, operation=operation)
                    elif channel == 'prospect_table_changed':
                        self.updateRecipientFromProspect(id=id, details=details, operation=operation)

        except Exception as e:
            print("Error dblisten")
            print(e)
            traceback.print_exc()

    def updateRecipientFromStudentAndParent(self,id=None, details=None, operation=None):

        student_details = details.partition("Student Details Start-")[2].partition("-Student Details End")[0]
        parent_1_details = details.partition("Parent_1 Details Start-")[2].partition("-Parent_1 Details End")[0]
        parent_2_details = details.partition("Parent_2 Details Start-")[2].partition("-Parent_2 Details End")[0]

        # TODO understand the psycopg2 notions of begin, commit, transaction, connection to understand why your execute statements work without commiting and what (e.g. rollback) will happen in the case of an errror https://www.psycopg.org/psycopg3/docs/basic/transactions.html
        if operation == 'UPDATE':  # or operation == "INSERT":

            if student_details:
                student_first_name = student_details.split('-')[0]
                student_last_name = student_details.split('-')[1]
                student_phone_number = student_details.split('-')[2]
                student_email = student_details.split('-')[3]
                student_is_active = student_details.split('-')[4]

                self.cursor.execute('''UPDATE recipient SET 
                                                   recipient_salutation=%s,
                                                   recipient_first_name=%s,
                                                   recipient_last_name=%s,
                                                   recipient_phone_number=%s,
                                                   recipient_email=%s,
                                                   is_active=%s
                                                   where recipient_source_id = %s and recipient_type = %s''',
                               ('', student_first_name, student_last_name, student_phone_number, student_email, student_is_active, id, 'student'))

                logger.info("Recipient successfully updated from student")

                # executeDBQuery()

            if parent_1_details:
                parent_1_salutation = parent_1_details.split('-')[0]
                parent_1_first_name = parent_1_details.split('-')[1]
                parent_1_last_name = parent_1_details.split('-')[2]
                parent_1_phone_number = parent_1_details.split('-')[3]
                parent_1_email = parent_1_details.split('-')[4]
                parent_1_is_active = parent_1_details.split('-')[5]

                self.cursor.execute('''UPDATE recipient SET 
                                                                      recipient_salutation=%s,
                                                                      recipient_first_name=%s,
                                                                      recipient_last_name=%s,
                                                                      recipient_phone_number=%s,
                                                                      recipient_email=%s,
                                                                      is_active=%s
                                                                      where recipient_source_id = %s and recipient_type = %s''',
                               (parent_1_salutation, parent_1_first_name, parent_1_last_name, parent_1_phone_number, parent_1_email, parent_1_is_active,  id, 'parent_1'))

                logger.info("Recipient successfully updated from parent_1")

            if parent_2_details:
                parent_2_salutation = parent_2_details.split('-')[0]
                parent_2_first_name = parent_2_details.split('-')[1]
                parent_2_last_name = parent_2_details.split('-')[2]
                parent_2_phone_number = parent_2_details.split('-')[3]
                parent_2_email = parent_2_details.split('-')[4]
                parent_2_is_active = parent_2_details.split('-')[5]

                self.cursor.execute('''UPDATE recipient SET 
                                                                      recipient_salutation=%s,
                                                                      recipient_first_name=%s,
                                                                      recipient_last_name=%s,
                                                                      recipient_phone_number=%s,
                                                                      recipient_email=%s,
                                                                      is_active=%s
                                                                      where recipient_source_id = %s and recipient_type = %s''',
                               (parent_2_salutation, parent_2_first_name, parent_2_last_name, parent_2_phone_number, parent_2_email, parent_2_is_active, id, 'parent_2'))

                logger.info("Recipient successfully updated from parent_2")

            # cursor.execute("DELETE FROM recipient WHERE recipient_source_id = %s", (id,))
            # connection.commit()


    def updateRecipientFromTutor(self,id=None, details=None, operation=None):
        tutor_details = details.partition("Tutor Details Start-")[2].partition("-Tutor Details End")[0]

        if operation == 'UPDATE':

            if tutor_details:
                tutor_first_name = tutor_details.split('-')[0]
                tutor_last_name = tutor_details.split('-')[1]
                tutor_phone_number = tutor_details.split('-')[2]
                tutor_email = tutor_details.split('-')[3]
                tutor_is_active = tutor_details.split('-')[4]

                self.cursor.execute('''UPDATE recipient SET 
                                                   recipient_salutation=%s,
                                                   recipient_first_name=%s,
                                                   recipient_last_name=%s,
                                                   recipient_phone_number=%s,
                                                   recipient_email=%s,
                                                   is_active=%s
                                                   where recipient_source_id = %s and recipient_type = %s''',
                               ('', tutor_first_name, tutor_last_name, tutor_phone_number, tutor_email, tutor_is_active, id, 'tutor'))

                logger.info("Recipient successfully updated from tutor")

    def updateRecipientFromLead(self,id=None, details=None, operation=None):

        lead_details = details.partition("Lead Details Start-")[2].partition("-Lead Details End")[0]

        if operation == 'UPDATE':

            if lead_details:
                lead_name = lead_details.split('-')[0]
                lead_phone_number = lead_details.split('-')[1]
                lead_email = lead_details.split('-')[2]

                self.cursor.execute('''UPDATE recipient SET 
                                                   recipient_salutation=%s,
                                                   recipient_first_name=%s,
                                                   recipient_last_name=%s,
                                                   recipient_phone_number=%s,
                                                   recipient_email=%s
                                                   where recipient_source_id = %s and recipient_type = %s''',
                               ('', lead_name, lead_name, lead_phone_number, lead_email, id, 'lead'))

                logger.info("Recipient successfully updated from lead")

    def updateRecipientFromProspect(self,id=None, details=None, operation=None):

        prospect_details = details.partition("Prospect Details Start-")[2].partition("-Prospect Details End")[0]

        if operation == 'UPDATE':

            if prospect_details:
                prospect_first_name = prospect_details.split('-')[0]
                prospect_last_name = prospect_details.split('-')[1]
                prospect_phone_number = prospect_details.split('-')[2]
                prospect_email = prospect_details.split('-')[3]

                self.cursor.execute('''UPDATE recipient SET 
                                                   recipient_salutation=%s,
                                                   recipient_first_name=%s,
                                                   recipient_last_name=%s,
                                                   recipient_phone_number=%s,
                                                   recipient_email=%s
                                                   where recipient_source_id = %s and recipient_type = %s''',
                               ('', prospect_first_name, prospect_last_name, prospect_phone_number, prospect_email, id, 'prospect'))

                logger.info("Recipient successfully updated from prospect")

# def createRecipientId():
#     #existing_recipient_ids = AppDBUtil.getAllRecipientIds()
#     recipient_id = "r-" + str(uuid.uuid4().int >> 64)[:6]
#     # while recipient_id in existing_recipient_ids:
#     #     logger.debug("Recipient id {} already exists".format(recipient_id))
#     #     recipient_id = "r-" + str(uuid.uuid4().int >> 64)[:6]
#     return recipient_id


# def executeDBQuery():
#     try:
#         connection.commit()
#     except Exception as e:
#         # if any kind of exception occurs, rollback transaction
#         connection.rollback()
#         traceback.print_exc()
#         raise e
#     finally:
#         pass
#         #cursor.close()