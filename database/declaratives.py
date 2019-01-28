import os

from sqlalchemy import Column, ForeignKey, Integer, String, BLOB, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Integration(Base):
    __tablename__ = 'integration'
    id = Column(Integer, primary_key=True)
    app_name = Column(String(250), nullable=False)
    secret = Column(String(250), nullable=False)
    oauth_token = Column(String(250), nullable=False)
    bot_username = Column(String(250), nullable=False)
    server_url = Column(String(250), nullable=False)


class Settings(Base):
    __tablename__ = 'preferences'
    id = Column(Integer, primary_key=True)

    # Merge request validation pattern
    mr_matcher = Column(String(250))

    # If an MR fails
    mr_failed_content = Column(String(1000))

    # if matcher is disable, this is the default
    mr_accepted_content = Column(String(1000))

    # Default MR assignee
    mr_default_assignee = Column(String(250))

    integration_id = Column(Integer, ForeignKey('integration.id'))
    integration = relationship(Integration)


db_username = os.environ.get('EIVOR_DB_USERNAME')
db_password = os.environ.get('EIVOR_DB_PASSWORD')
db_url = os.environ.get('EIVOR_DB_URL')

engine = create_engine(
    'postgres://{}:{}@{}'.format(db_username, db_password, db_url))
Base.metadata.create_all(engine)
Base.metadata.bind = engine

db_session = sessionmaker()
db_session.bind = engine
db_session = db_session()
