from datetime import datetime
import numpy as np
import pandas as pd
import time


##api 호출수, dau, mau 등 계산하는 모듈 들어갈 예정.

##select 를 이쪽에 넣을지, lib에 넣을지.

## req.mon, req.day, req.

##lms search : id, success, user_id, keyword, catalog_id, timestamp, attempt, test 0/1

##kitech : id, api, keyword, response, timestamp, remote_addr, user_agent

def timestampJSscale():
    t0 = int(round(time.time()*1000,0))
    return t0

def dateToTimestamp(yr,mon,day):
    date = datetime(yr,mon,day)
    timestamp = datetime.timestamp(date)
    return timestamp

def activeUsers(engine, table, t0, t1):
    query = f"select count(distinct(user_id)) from {table} where timestamp >= {t0} and timestampe <= {t1};"
    with engine.connect() as conn:
        rst = conn.execute(query).fetchone()
    return rst

def apiUsage(engine, table, api, t0, t1):
    query = f"select count(distinct(id)) from {table} where timestamp >= {t0} and timestampe <= {t1} and api = '{api}';"
    with engine.connect() as conn:
        rst = conn.execute(query).fetchone()
    return rst
