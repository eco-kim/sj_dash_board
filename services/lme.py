import pandas as pd
import json
from lib import mysql
from commons import calc
from datetime import date, datetime

with open('config/tables.json', 'r') as f:
    tables = json.load(f)

def select(t0, t1):
    tableInfo = tables['lme_search']
    table = f'{tableInfo["schema"]}.{tableInfo["table"]}'
    engine = mysql.createEngine("RnD")

    query1 = f"select id, user_id, timestamp from {table} where timestamp >= {t0} and timestamp < {t1};"
    query2 = f"select institute_id, test from research.lme_institute;"
    with engine.connect() as conn:
        df = pd.read_sql_query(query1, conn)
        testinfo = pd.read_sql_query(query2, conn)

    engine.dispose()

    engine = mysql.createEngine("LM_SERVICE")
    query = f"""SELECT a.institute_id, a.user_id, b.name as institute_name FROM labmanager.institute_member a
            join labmanager.institute b
            on a.institute_id=b.id;"""
    with engine.connect() as conn:
        member = pd.read_sql_query(query, conn)

    engine.dispose()

    member = member.set_index('user_id')
    df = df.join(member, on='user_id',how='inner')
    
    testinfo = testinfo.set_index('institute_id')
    df = df.join(testinfo, on='institute_id',how='inner')
    df = df[df.test!=1]
    return df

def usage(settings): ## settings = {'windowSize':'daily'/'weekly','monthly', 'dateStart'/'dateEnd':'YYYY-MM-DD'}
    windowSize = settings['windowSize']
    dateStart, dateEnd = datetime.fromisoformat(settings['dateStart']), datetime.fromisoformat(settings['dateEnd'])
    t0, t1 = calc.windowTimestamp(windowSize, dateStart, dateEnd)
    df = select(t0, t1)

    if windowSize == 'daily':
        bins, labels = calc.dailyWindow(t0, t1)
    elif windowSize == 'weekly':
        bins, labels = calc.weeklyWindow(t0, t1)    
    else:
        bins, labels = calc.monthlyWindow(t0, t1)
    
    df2 = pd.DataFrame(pd.cut(df.timestamp.values, bins, right=False, labels=labels[:-1]).describe().counts)
    df2 = df2.reset_index()
    df2 = df2.rename(columns={'categories':'date'})
    return df2

def institute(settings):
    t0 = calc.isoFormatToTimestamp(settings['dateStart'])
    t1 = calc.isoFormatToTimestamp(settings['dateEnd'])

    df = select(t0,t1)

    df2 = pd.DataFrame(df.groupby('institute_name')['id'].count())
    df2 = df2.sort_values(by='id',ascending=False)
    df2 = df2.reset_index()
    df2 = df2.rename(columns={'institute_name':'institute','id':'counts'})

    top = settings['top']
    if top == 'max':
        top = df2.shape[0]
    else:
        top = int(top)
    return df2.iloc[:top]