

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

    # Listen to node changes, and update leader/master
    _leader_id_per_process = -1
    @zk.ChildrenWatch(path=DEFAULT_PATH)
    def update_leader(children):
        nonlocal _leader_id_per_process
        
        logging.info(f'PROCESS {process_id}: children node update detected')

        process_prefix = 'proc_'
        process_id_prefix = 'proc_000_'
        seq_no_to_process_id = {}
        for c in children:
            process_id_str = c[len(process_prefix):len(process_prefix)+3]
            seq_no_str = c[len(process_id_prefix):]
            seq_no_to_process_id[int(seq_no_str)] = int(process_id_str)
        
        # find leader
        sorted_seq_nos = sorted(list(seq_no_to_process_id.keys()))
        _leader_id_per_process = seq_no_to_process_id[sorted_seq_nos[0]]
        
        logging.info(f'PROCESS {process_id}: find out the new leader is the process: {_leader_id_per_process}')

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
