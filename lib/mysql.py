from sqlalchemy import create_engine
import json


def createEngine(db):
    engine = create_engine(f"mysql+pymysql://{db['user']}:{db['passwd']}@{db['host']}/{db['db']}")
    return engine
