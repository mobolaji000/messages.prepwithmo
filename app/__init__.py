from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from sqlalchemy import MetaData

metadata = MetaData()

# if not Config.scheduler.running:
#     Config.scheduler.start()#



server = Flask(__name__)
server.config.from_object(Config)




# print("testing Config contents")
# print(Config.__dict__)

db = SQLAlchemy(server,engine_options={"pool_pre_ping": True},session_options={'expire_on_commit': False},metadata=metadata)

# from sqlalchemy.ext.automap import automap_base
# Base = automap_base()
# Base.prepare(db.engine, reflect=True)

from app import views, models
migrate = Migrate(server, db)
bootstrap = Bootstrap(server)







