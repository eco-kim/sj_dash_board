from confluent_kafka import Consumer
import os
import re
import json
import requests
import jwt

kafkaConfig = json.load('../config/kafka.json')['kafka']['kafkaConfig']
BASE_DIR = ''
##컨슈머, 토픽 복구모듈
##덤프모듈 


## DB에 들어간 로그 중 마지막 timestamp 확인
def dbCheck(conn):
    query = 'select * from research.kitech_api_keyword order by timestamp desc limit 1;'
    rst = conn.execute(query).fetchone()

## raw text 로그에서 누락된 부분 찾기
def logFromText(timestamp):
    with open('HOME/research-log/lme_search.log', 'r') as f:
        lines = f.readlines()
    nlines = len(lines)
    rst = []
    for j in range(1,nlines):
        log = dict(json.loads(lines[(-1)*j]))
        rst.append(log)
        if log['timestamp'] == timestamp:
            rst.pop()
            break
    return rst[::-1]

## 데이터 파싱 + 규격화 하는 함수
def docParser(doc):
    rst = {}

    if doc['test']:
        rst['test'] = 1
    else:
        rst['test'] = 0

    if doc['type'] == 'lme-search':
        rst['success'] = 0
        rst['catalog_id'] = None
    elif doc['type'] == 'lme-search-success':
        rst['success'] = 1
        rst['catalog_id'] = doc['catalog_id']
    else:
        rst['success'] = None
    
    rst['user_id'] = jwt.decode(doc['token'], options={'verify_signature':False})

    for key in ['keyword','attempt','timestamp']:
        try:
            rst[key] = doc[key]
        except:
            pass
    return rst

## 쿼리 짜는 함수
def query(data):
    keys = ', '.join(list(data.keys()))
    values = f'{tuple(data.values())}'
    sql = f"insert into research.lme_search_log ({keys}) values {values};"
    sql = sql.replace("%", "%%")
    return sql

##누락된 것 업로드
def loadToMysql(conn, missingLogs):
    for data in missingLogs:
        temp = docParser(data)
        sql = query(temp)
        conn.execute(sql)

## offset lag 체크
def checkOffsetLag():
    cmd = f'{kafkaConfig["KAFKA_DIR"]}/bin/kafka-consumer-groups --bootstrap-server {kafkaConfig["bootstrap.servers"]} --group {kafkaConfig["group.id"]} --describe'
    stream = os.popen(cmd)
    output = stream.read().split('\n')[2]
    data = re.findall(r'[0-9]+', output)
    currOffset = int(data[1])
    logEndOffset = int(data[2])
    return currOffset, logEndOffset

## 컨슈머 재가동
def consumerRestart(consumer):
    os.system(f'nohup python {consumer} & > {BASE_DIR}/nohup.out')

## 중복체크
def duplicate(engine):
    query = '''select 
                concat(user_id, "**", timestamp, "**", ifnull(attempt,0)) as idx, 
                count(distinct(id)) as count
            from research.lme_search_log
                group by user_id, timestamp, ifnull(attempt, 0)
                having count > 1;'''
    
    with engine.connect() as conn:
        pass
    
    return

## 1. 컨슘 - 디비 차이 있는지 체크 후 컨슘됐지만 디비에 안올라간것 먼저 처리
## 2. 컨슘이 안된것 있는지 오프셋 체크 후 처리, 컨슘이 중복될수도있는데 어떻게처리할지 결정해야함.
## 3. 중복 데이터 처리