from sqlalchemy import create_engine
import jwt
import json
import time

def connectMysql():
    sql = 'mysql+pymysql'
    host = ''
    port = 3306
    db = ''
    user = ''
    passwd = ''

    engine = create_engine(f'{sql}://{user}:{passwd}@{host}:{port}/{db}', pool_recycle=300)
    return engine

## 데이터 파싱 + 규격화 하는 함수
def docParser(doc):
    token_key = ''
    rst = {}

    if doc.get('log_type') == 'lms-search':
        rst['success'] = 0
    elif doc.get('log_type') == 'lms-search-success':
        rst['success'] = 1
        item = doc['item']
        if item['type'] in ['catalog_id','product_info_id','casno']:
            rst[item['type']] = item['id']
        if 'filter' in doc.keys():
            for key in doc['filter'].keys():
                rst['filter_'+key+'_id'] = doc['filter'][key]['id']
                rst['filter_'+key+'_name'] = doc['filter'][key]['name']
        if 'offset' in doc.keys():
            rst['offset'] = doc['offset']
    else:
        return None

    if 'token' in doc.keys():
        if doc['token'] is None:
            token = 'NULL'
        else:
            try:
                token = jwt.decode(doc['token'], token_key, algorithms=['HS256'])
                rst['token'] = doc['token']
                rst['user_id'] = token['id']
            except:
                token = "decode_fail"

    for key in ['keyword','timestamp','client_ip','type']:
        try:
            rst[key] = doc[key]
        except:
            pass
    return rst

## 쿼리 짜는 함수
def query(data):
    keys = ', '.join(list(data.keys()))
    values = f'{tuple(data.values())}'
    sql = f"insert into research.lms_search_log ({keys}) values {values};"
    sql = sql.replace('%','%%')
    return sql