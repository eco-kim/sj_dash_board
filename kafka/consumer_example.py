from confluent_kafka import Consumer, KafkaException
from transform_load import connectMysql, docParser, query
import json
import glob

logDir = ''
engine = connectMysql()

topic = ''
c = Consumer({
    'bootstrap.servers': '',
    'group.id': topic,
    'enable.auto.commit': True
})

c.subscribe(['src.'+topic])

temp = glob.glob(logDir+topic+'.log')
if len(temp) == 0:
    with open(logDir+topic+'.log','w') as f:
        f.write('log start\n')

try:
    while True:
        msg = c.poll(1000)
        if msg is None:
            continue

        if msg.error():
            raise KafkaException(msg.error())

        else:
            doc = dict(json.loads(msg.value()))

            with open(logDir+topic+'.log','a') as f:
                f.write(json.dumps(doc)+'\n')

            try:
                data = docParser(doc)
                if data:
                    query0 = query(data)
                    with engine.connect() as conn:
                        conn.execute(query0)
            except Exception as e:
                print(e)

except KeyboardInterrupt:
        print("Ctrl + C")
        c.close()