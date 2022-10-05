from sqlalchemy import create_engine
import json

def createEngine(dbName):
    with open('config/db.json','r') as f:
        db = json.load(f)[dbName]
    engine = create_engine(f"mysql+pymysql://{db['user']}:{db['passwd']}@{db['host']}/{db['db']}")
    return engine
