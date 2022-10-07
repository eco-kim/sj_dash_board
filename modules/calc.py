from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import time
import json
from lib import mysql
import calendar

##api 호출수, dau, mau 등 계산하는 모듈 들어갈 예정.

##select를 이쪽에 넣을지, lib에 넣을지.

##req.mon, req.day, req.

##lms search : id, success, user_id, keyword, catalog_id, timestamp, attempt, test 0/1

##kitech : id, api, keyword, response, timestamp, remote_addr, user_agent

with open('config/tables.json', 'r') as f:
    tables = json.load(f)

def dateToTimestamp(date): ##form : {year: int, month: int, day: int}
    date = datetime(date['year'], date['month'], date['day'])
    timestamp = datetime.timestamp(date)
    timestamp = int(round(timestamp*1000,0))
    return timestamp ##JS scale

def timestampToDatetime(timestamp): ##JS scale timestamp
    date = datetime.fromtimestamp(timestamp/1000)
    return date

def activeUsers(engine, table, t0, t1):  ##t0, t1 : JS scale timestamp 
    query = f"select id, user_id, timestamp from {table} where timestamp >= {t0} and timestampe < {t1};"
    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn)
    return df

def usageSelect(engine, service, t0, t1, api=None):  ##t0, t1 : JS scale timestamp
    tableInfo = tables[service]
    table = f'{tableInfo["schema"]}.{tableInfo["table"]}'

    if api is not None:
        query = f"select id, timestamp from {table} where timestamp >= {t0} and timestamp < {t1} and api = '{api}';"
    else:
        query = f"select id, timestamp from {table} where timestamp >= {t0} and timestamp < {t1};"
    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn)
    return df

def labelFormat(date):
    label = str(date.year)+'-'+str(date.month).zfill(2)+'-'+str(date.day).zfill(2)
    return label

def dailyWindow(t0, t1):
    dt = 1000*60*60*24
    date0 = timestampToDatetime(t0)
    bins = [t0]
    labels = [labelFormat(date0)]
    while t0 <= t1:
        t0 += dt
        date0 = date0 + timedelta(days=1)
        bins.append(t0)
        labels.append(labelFormat(date0))
    return bins, labels

def weeklyWindow(t0, t1):
    dt = 1000*60*60*24*7
    date = timestampToDatetime(t0)
    weekday = calendar.weekday(date.year, date.month, date.day)
    date0 = date - timedelta(days=weekday)
    t0 = int(round(date0.timestamp()*1000,0))
    bins = [t0]
    labels = [labelFormat(date0)]
    while t0 <= t1:
        t0 += dt
        date0 = date0 + timedelta(days=7)
        bins.append(t0)
        labels.append(labelFormat(date0))
    return bins, labels

def monthlyWindow(t0, t1): 
    date0 = datetime.fromtimestamp(t0/1000)
    yr0, mon0 = date0.year, date0.month
    date1 = datetime.fromtimestamp(t1/1000)
    yr1, mon1 = date1.year, date1.month

    ##초안 // 리팩토링 필요
    bins = []
    labels = []
    if yr0 == yr1:
        if mon1<=11 :
            for mon in range(mon0, mon1+2):
                bins.append(dateToTimestamp({'year':yr0,'month':mon,'day':1}))
                labels.append(f'{yr0}-{str(mon).zfill(2)}')
        else:
            for mon in range(mon0, 13):
                bins.append(dateToTimestamp({'year':yr0,'month':mon,'day':1}))
                labels.append(f'{yr0}-{str(mon).zfill(2)}')
            bins.append(dateToTimestamp({'year':yr0+1,'month':1,'day':1}))
            labels.append(f'{yr0+1}-{str(1).zfill(2)}')
    else:
        if mon1<=11 :
            for mon in range(mon0, 13):
                bins.append(dateToTimestamp({'year':yr0,'month':mon,'day':1}))
                labels.append(f'{yr0}-{str(mon).zfill(2)}')
            for mon in range(1,mon1+2):
                bins.append(dateToTimestamp({'year':yr1,'month':mon,'day':1}))
                labels.append(f'{yr1}-{str(mon).zfill(2)}')
        else:
            for mon in range(mon0, 13):
                bins.append(dateToTimestamp({'year':yr0,'month':mon,'day':1}))
                labels.append(f'{yr0}-{str(mon).zfill(2)}')
            for mon in range(1, 13):
                bins.append(dateToTimestamp({'year':yr1,'month':mon,'day':1}))
                labels.append(f'{yr1}-{str(mon).zfill(2)}')
            bins.append(dateToTimestamp({'year':yr1+1,'month':1,'day':1}))
            labels.append(f'{yr1+1}-{str(1).zfill(2)}')

    return bins, labels


def apiDataFrame(service, api=None, windowSize='daily', dateStart=None, dateEnd=None):  ##dateXXX : 조회하려는 기간의 시작~끝 날짜 form : {year: int, month: int, day: int}
    if dateEnd is None:
        temp = datetime.now()
        temp = datetime(temp.year, temp.month, temp.day)+timedelta(days=1)
        dateEnd = {'year':temp.year, 'month':temp.month, 'day':temp.day}

    if dateStart is None:
        if windowSize == 'daily': #default 30일 조회
            temp = datetime(dateEnd['year'],dateEnd['month'],dateEnd['day'])-timedelta(days=30)
        
        elif windowSize == 'weekly': ##default 20주 조회
            temp = datetime(dateEnd['year'],dateEnd['month'],dateEnd['day'])-timedelta(days=140)

        elif windowSize == 'monthly': ##defalut 1년 조회, 최대 2년까지만가능
            temp = datetime(dateEnd['year']-1,dateEnd['month'],dateEnd['day'])

        dateStart = {'year':temp.year, 'month':temp.month, 'day':temp.day}

    t0, t1 = dateToTimestamp(dateStart), dateToTimestamp(dateEnd)
    engine = mysql.createEngine("RnD")

    df = usageSelect(engine, service, t0, t1, api)

    engine.dispose()

    if windowSize == 'daily':
        bins, labels = dailyWindow(t0, t1)

    elif windowSize == 'weekly':
        bins, labels = weeklyWindow(t0, t1)
    
    else:
        bins, labels = monthlyWindow(t0, t1)
    
    df2 = pd.DataFrame(pd.cut(df.timestamp.values, bins, labels=labels[:-1]).describe().counts)
    df2 = df2.reset_index()
    df2 = df2.rename(columns={'categories':'date'})
    return df2
