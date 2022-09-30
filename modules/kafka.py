from confluent_kafka import Consumer, KafkaExceptionx
import os
import re


##컨슈머, 토픽 복구모듈
##덤프모듈 


BASE_DIR = ''
KAFKA_DIR = '/usr/local/confluent-5.5.0'
KAFKA_CONFIG = {
    'bootstrap.servers': 'zk01.smartjack.private:9092,zk02.smartjack.private:9092,zk03.smartjack.private:9092',
    'group.id': 'lme-search'
}

def checkOffsetLag():
    cmd = f'{KAFKA_DIR}/bin/kafka-consumer-groups --bootstrap-server {KAFKA_CONFIG["bootstrap.servers"]} --group {KAFKA_CONFIG["group.id"]} --describe'
    stream = os.popen(cmd)
    output = stream.read().split('\n')[2]
    data = re.findall(r'[0-9]+', output)
    currOffset = int(data[1])
    logEndOffset = int(data[2])
    return currOffset, logEndOffset

