

import logging
import time
import random 

from multiprocessing import Process

from kazoo.client import KazooClient
import kazoo.exceptions as ke


RING_LENG = 10_000
SLEEPING_INTERVAL = 5
MAX_NUM_PROCESS = 10
DEFAULT_PATH = '/membership_ring'

logging.basicConfig(level=logging.INFO)


def worker_process(process_id):
    '''
    Worker process. There are multi worker processes; and each worker process is supposed to be
    responsible for a segment of the ring of consistent hashing.
    '''
    zk = KazooClient(hosts='127.0.0.1:2181')
    zk.start()

    # ******* WRITE YOUR HASHING CODE HERE ******
    # Please create node in the DEFAULT_PATH directory, so the main process can observe the nodes


    # loop to keep the process alive
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
    zk.ensure_path(DEFAULT_PATH)
    
    # define a function to get the status of the ring of consistent hashing
    def print_status():
        # get the available node; `include_data` seems not working
        logging.info('MAIN: Status of zookeeper membership: ')
        worker_nodes, _ = zk.get_children(DEFAULT_PATH, include_data=True)
        worker_nodes = sorted(worker_nodes)
        for i in range(len(worker_nodes)):
            enode = worker_nodes[i]
            prev_enode = worker_nodes[i-1] if i > 0 else worker_nodes[-1]
            data, _ = zk.get(f'{DEFAULT_PATH}/{enode}')
            data = data.decode("utf-8")
            logging.info(f'MAIN: -- worker process {data} is responsible for range from {prev_enode} to {enode}')
    
    # randomly kill or add worker process, to test the load rebalancing
    logging.info('MAIN: Starting loop...')
    while True:
        time.sleep(SLEEPING_INTERVAL)
        logging.info(f'MAIN: main process is alive')

        r = random.random()
        if r < 0.33:
            if len(processes) <= 2:
                continue

            # kill a process
            p = random.choice(list(processes.keys()))
            logging.info(f'MAIN: decided to KILL process {p}')
            processes[p].kill()
            processes[p].join(timeout=5)
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

        # print the status of the consistent hash
        print_status()


if __name__ == "__main__":
    main()
