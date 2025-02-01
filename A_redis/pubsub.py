

import logging
import time
import random 

import threading
from multiprocessing import Process
import redis


NUM_PROCESSES = 5

logging.basicConfig(level=logging.INFO)


def get_channel_name(process_id):
    return f'process-{process_id}'


def worker_process(process_id):
    '''
    Worker process. There are multi worker processes; and each worker process is supposed to be
    responsible for a segment of the ring of consistent hashing.
    '''
    rl = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # message queue to receive message
    cv = threading.Condition()
    msg_que = []

    # define the handler for pubsub messages from other workers
    # this handler runs in a different thread and put message into the msg_que
    def handle_msg(msg):
        nonlocal msg_que

        with cv:
            msg_que.append((msg['channel'], msg['data']))
            cv.notify()

    # Register pubsub message handler for topics by other workers
    p = rl.pubsub()
    process_ids = [i for i in range(NUM_PROCESSES)]
    process_ids.remove(process_id)
    sub_dict = {get_channel_name(i): handle_msg for i in process_ids}
    p.subscribe(**sub_dict)
    thread = p.run_in_thread(sleep_time=0.1)
    logging.info(f'subscribed channels: {sub_dict}')

    # Wait for messages from the message handler, and also publish messages occasionally
    while True:
        #  Wait and get the messages from the message handler 
        sleep_time = random.randint(1, 20)
        with cv:
            cv.wait(sleep_time)
            if len(msg_que) > 0:
                channel, new_msg = msg_que.pop(0)
                logging.info(f'received a new value: {new_msg} from {channel}')
                continue

        # Send a message to other workers
        val = random.randint(1, 1000)
        rl.publish(get_channel_name(process_id), val)
        logging.info(f'PROCESS {process_id}: send a value of {val}')


def main():
    # start a few worker processes
    logging.info('Starting processes...')
    processes = {}
    for i in range(NUM_PROCESSES):
        processes[i] = Process(target=worker_process, args=(i,))
        processes[i].start()
    

    logging.info('MAIN: Starting loop...')
    while True:
        time.sleep(10)
        logging.info(f'MAIN: main process is alive')


if __name__ == "__main__":
    main()