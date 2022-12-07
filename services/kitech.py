import pandas as pd
import json
from lib import mysql
from commons import calc
from datetime import date

with open('config/tables.json', 'r') as f:
    tables = json.load(f)

def usage(windowSize='daily', dateStart=None, dateEnd=None):  ##dateXXX : 조회하려는 기간의 시작~끝 날짜 form : {year: int, month: int, day: int}
    t0, t1 = calc.windowTimestamp(windowSize, dateStart, dateEnd)
    engine = mysql.createEngine("RnD")

    tableInfo = tables["kitech_api"]
    table = f'{tableInfo["schema"]}.{tableInfo["table"]}'

    query = f"select id, timestamp from {table} where timestamp >= {t0} and timestamp < {t1};"
    
    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn)

    engine.dispose()

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