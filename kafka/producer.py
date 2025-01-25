
import logging
import os
import time
import random 
import json

import threading
from multiprocessing import Process
import pandas as pd

from kafka import KafkaProducer, KafkaConsumer


# The topic has 3 partitions defined in docker-compose.yml
NUM_PROCESSES = 3
# Note the topic has to match the topic defined in docker-compose.yml
KAFKA_TOPIC_ORDER = 'topic_order_info'
CSV_FILE_LOCATION = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 'data', 'Ecommerce_data.csv')

logging.basicConfig(level=logging.INFO)


def consumer_process(process_id):
    '''
    Worker process. There are multi worker processes; and each worker process is supposed to be
    responsible for a segment of the ring of consistent hashing.
    '''
    consumer = KafkaConsumer(bootstrap_servers='localhost:9092',
                             key_deserializer=lambda k: k.decode('utf-8'),
                             value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                             group_id='demo_group')
    consumer.subscribe([KAFKA_TOPIC_ORDER])

    logging.info(f'PROCESS {process_id} waiting for message')
    user_to_order_quantity = {}
    for msg in consumer:
        uid = msg.key
        order_info = msg.value

        if len(order_info) > 0:
            # logging.info(f'PROCESS {process_id}: received msg')
            if uid not in user_to_order_quantity:
                user_to_order_quantity[uid] = 0
            user_to_order_quantity[uid] += order_info.get('order_quantity', 0)
        else:
            logging.info(f'PROCESS {process_id}: ****** user {uid} ordered {user_to_order_quantity.get(uid, 0)} orders')

    logging.info(f'PROCESS {process_id} exiting')


def main():
    # start a few worker processes
    logging.info('Starting processes...')
    processes = {}
    for i in range(NUM_PROCESSES):
        processes[i] = Process(target=consumer_process, args=(i,))
        processes[i].start()

    producer = KafkaProducer(bootstrap_servers='localhost:9092',
                             key_serializer=lambda k: k.encode('utf-8'),
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    
    df = pd.read_csv(CSV_FILE_LOCATION)
    count = 0
    for _, row in df.iterrows():
        uid = row['customer_id']
        order_info = {
            'order_id': row.get('order_id', ''),
            'product_name': row.get('product_name', ''),
            'order_quantity': row.get('order_quantity', ''),
            'profit_per_order': row.get('profit_per_order', ''),
        }

        producer.send(KAFKA_TOPIC_ORDER, key=uid, value=order_info)
        
        count += 1
        if count % 1000 == 0:
            time.sleep(0.5)
    logging.info(f'MAIN PROCESS: send {count} message')

    # wait for message to be sent
    producer.flush()

    # Send empty message for particular user, to get the total number of orders (sum of `order_quantity` field)
    # This user (C_ID_36240) has 19 orders in total
    customer_id = 'C_ID_36240'
    producer.send(KAFKA_TOPIC_ORDER, key=customer_id, value={})
    
    order_quantity = df.groupby('customer_id')['order_quantity'].sum()[customer_id]
    logging.info(f'MAIN: {customer_id} should have an order quantity of {order_quantity}')

    logging.info('MAIN: sleep 10 seconds for child process to print result; you can press CTRL+C to terminate at any time')
    time.sleep(10)
    logging.info(f'MAIN: Exiting')


if __name__ == "__main__":
    main()