
import logging
import os
import time

from multiprocessing import Process

import pika

# The topic has 3 partitions defined in docker-compose.yml
NUM_PROCESSES = 3
# Note the topic has to match the topic defined in docker-compose.yml
QUE_NAME = 'topic_order_info'
CSV_FILE_LOCATION = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 'data', 'Ecommerce_data.csv')

logging.basicConfig(level=logging.INFO)


def consumer_process(process_id):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        logging.info(f" [x] Received {body}")

    channel.basic_consume(queue='hello',
                          auto_ack=True,
                          on_message_callback=callback)
    logging.info(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    logging.info(f'PROCESS {process_id} exiting')


def main():
    # start a few worker processes
    logging.info('Starting processes...')
    processes = {}
    for i in range(1):
        processes[i] = Process(target=consumer_process, args=(i,))
        processes[i].start()
    
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='customer_segment',
                             exchange_type='topic')

    channel.queue_declare(queue='hello')
    channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')
    connection.close()

    logging.info(f'MAIN PROCESS: send message')


    logging.info('MAIN: sleep 10 seconds for child process to print result; you can press CTRL+C to terminate at any time')
    time.sleep(10)
    logging.info(f'MAIN: Exiting')


if __name__ == "__main__":
    main()