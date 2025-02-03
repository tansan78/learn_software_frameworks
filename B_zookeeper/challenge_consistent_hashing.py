
"""
Implement two functions
- register_node()
- get_hash_ring()
"""

from typing import Tuple, List
import logging
import time
import random 

from multiprocessing import Process

from kazoo.client import KazooClient
import kazoo.exceptions as ke


RING_LENG = 10_000
SLEEPING_INTERVAL = 5
MAX_NUM_PROCESS = 10
RING_PATH = '/membership_ring'

logging.basicConfig(level=logging.INFO)


def worker_process(process_id):
    '''
    Worker process. There are multi worker processes; and each worker process is supposed to be
    responsible for a segment of the ring of consistent hashing.
    '''
    zk = KazooClient(hosts='127.0.0.1:2181')
    zk.start()
    zk.ensure_path(RING_PATH)

    register_node(zk, process_id)

    # Loop to keep the existing of it emphemral node
    while True:
        time.sleep(SLEEPING_INTERVAL)
        logging.info(f'server {process_id} is alive')


def main():
    # start 2 processes initially
    logging.info('Starting processes...')
    processes = {}
    for i in range(2):
        processes[i] = Process(target=worker_process, args=(i,))
        processes[i].start()
    
    zk = KazooClient(hosts='127.0.0.1:2181')
    zk.start()
    zk.ensure_path(RING_PATH)
    
    logging.info('MAIN: Starting loop...')
    while True:
        r = random.random()
        if r < 0.33:
            if len(processes) <= 2:
                continue

            # kill a process
            p = random.choice(list(processes.keys()))
            logging.info(f'MAIN: decided to KILL process {p}')
            processes[p].kill()
            processes[p].join(timeout=10)
            processes[p].close()
            del processes[p]
            logging.info(f'MAIN: killed process {p}')
        elif r < 0.66:
            if len(processes) >= MAX_NUM_PROCESS:
                continue

            # add a new process

            # find a new idle process id
            p = random.randint(1, 100)
            while p in processes:
                p = random.randint(1, 100)

            logging.info(f'MAIN: decided to ADD a new process {p}')
            processes[p] = Process(target=worker_process, args=(p,))
            processes[p].start()
            logging.info(f'decided to add a new process {p}')
        else:
            logging.info('MAIN: decided do NOTHING')

        time.sleep(SLEEPING_INTERVAL)
        logging.info(f'MAIN: main process is alive with processes: {processes.keys()}')

        # print the status of the consistent hash
        ring_ranges, ring_processes = get_hash_ring(zk)
        logging.info(f'MAIN: hash ring status: {ring_ranges}, {ring_processes}')

        if set(ring_processes) != set(processes.keys()):
            logging.error(f'[NOT CRITICAL] The ring processes ({ring_processes}) do not match" +\
                          f" factual processes ({processes.keys()}); this might be caused by Zookeeper delays')
        

def register_node(zk, process_id):
    """
    IMPLEMENT THIS FUNCTION
    """
    pass


def get_hash_ring(zk) -> Tuple[List, List]:
    """
    IMPLEMENT THIS FUNCTION

    Return two lists:
    - the first list contains the range ending point of the hash ring
    - the second list contains the corresponding process id
    """
    # get the available node; `include_data` seems not working
    ranges = []
    process = []

    return (ranges, process)


if __name__ == "__main__":
    main()
