import pandas as pd
import json
from lib import mysql
from commons import calc
from datetime import date, datetime

with open('config/tables.json', 'r') as f:
    tables = json.load(f)

testIP = ['0.0.0.1','220.117.114.5','220.117.114.30','218.152.140.66']

def select(t0,t1):
    engine = mysql.createEngine("RnD")

    tableInfo = tables["lms_search"]
    table = f'{tableInfo["schema"]}.{tableInfo["table"]}'

    query = f"select id, timestamp, user_id, client_ip from {table} where timestamp >= {t0} and timestamp < {t1};"
    
    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn)

    df = df[~df.client_ip.isin(testIP)]
    engine.dispose()
    return df

def usage(settings):
    windowSize = settings['windowSize']
    dateStart, dateEnd = datetime.fromisoformat(settings['dateStart']), datetime.fromisoformat(settings['dateEnd'])
    t0, t1 = calc.windowTimestamp(windowSize, dateStart, dateEnd)

    df = select(t0,t1)

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

def activeUsers(settings):
    windowSize = settings['windowSize']
    dateStart, dateEnd = datetime.fromisoformat(settings['dateStart']), datetime.fromisoformat(settings['dateEnd'])
    t0, t1 = calc.windowTimestamp(windowSize, dateStart, dateEnd)

    df = select(t0,t1)

    if windowSize == 'daily':
        bins, labels = calc.dailyWindow(t0, t1)
    elif windowSize == 'weekly':
        bins, labels = calc.weeklyWindow(t0, t1)
    else:
        bins, labels = calc.monthlyWindow(t0, t1)

    df = df.fillna('')
    df['client'] = df.client_ip.str.cat(df.user_id)
    df['window'] = pd.cut(df['timestamp'], bins, right=False, labels=labels[:-1])
    df2 = pd.DataFrame(df.groupby('window').client.nunique())
    df2 = df2.reset_index()
    df2 = df2.rename(columns={'window':'date','client':'counts'})

    return df2