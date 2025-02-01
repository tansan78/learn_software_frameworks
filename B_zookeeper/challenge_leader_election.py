

import logging
import time
import random 

from multiprocessing import Process

import kazoo.client as kc
import kazoo.exceptions as ke


RING_LENG = 10_000
SLEEPING_INTERVAL = 5
DEFAULT_PATH = '/lead_election'

logging.basicConfig(level=logging.INFO)


def server_process(process_id):
    zk = kc.KazooClient(hosts='127.0.0.1:2181')
    zk.start()

    zk.ensure_path(DEFAULT_PATH)

    # create emphemral node in zookeeper with sequence number
    try:
        zk.create(f'{DEFAULT_PATH}/proc_{process_id:03d}_', ephemeral=True, sequence=True)
    except ke.NodeExistsError as e:
        logging.warning(f'Hash collision; might be caused duplicated processed id {process_id}; quitting...')
        return

    # ******* WRITE YOUR HASHING CODE HERE ******
    # Please create node in the DEFAULT_PATH directory, so the main process can observe the nodes

    # loop to keep the process alive
    while True:
        time.sleep(SLEEPING_INTERVAL)
        logging.info(f'PROCESS {process_id}: alive and the leader is {_leader_id_per_process}')


def main():
    # start 2 worker processes initially
    logging.info('Starting processes...')
    processes = {}
    for i in range(2):
        processes[i] = Process(target=server_process, args=(i,))
        processes[i].start()
    

    # randomly kill or add worker process, to test the leader election
    logging.info('MAIN: Starting loop...')
    while True:
        time.sleep(SLEEPING_INTERVAL)
        logging.info(f'MAIN: main process is alive')

        r = random.random()
        if r < 0.33:
            # kill a process
            p = random.choice(list(processes.keys()))
            logging.info(f'MAIN: decided to kill process {p}')
            processes[p].terminate()
            processes[p].join(timeout=5)
            processes[p].close()
            del processes[p]
            logging.info(f'MAIN: killed process {p}')
        elif r < 0.66 and len(processes) < 10:
            # add a new process

            # find a new idle process id
            p = random.randint(1, 100)
            while p in processes:
                p = random.randint(1, 100)

            logging.info(f'MAIN: decided to add a new process {p}')
            processes[p] = Process(target=server_process, args=(p,))
            processes[p].start()
            logging.info(f'decided to add a new process {p}')
        else:
            logging.info('MAIN: decided do nothing')


if __name__ == "__main__":
    main()
