from app.models import Transaction,InstallmentPlan,InvoiceToBePaid,Prospect,Student,Lead
from app import db

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




