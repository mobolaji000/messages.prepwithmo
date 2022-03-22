from app import db

class Message(db.Model):
    message_id = db.Column(db.String(8), primary_key=True, index=True, nullable=False, unique=True, default='')

    def __repr__(self):
        return '<Message {}>'.format(self.message_id)

db.create_all()
try:
    db.session.commit()
except:
    # if any kind of exception occurs, rollback transaction
    db.session.rollback()
    raise
finally:
    db.session.close()

