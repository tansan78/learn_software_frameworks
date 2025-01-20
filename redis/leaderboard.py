"""
Leaderboard: https://redis.io/solutions/leaderboards/
"""

import logging
import time
import random 

from multiprocessing import Process, Queue
import redis


NUM_PROCESSES = 2
NUM_PLAYERS = 100
LEADERBOARD_KEY = 'leaderboard'
logging.basicConfig(level=logging.INFO)


def worker_process(process_id, rcv_que, rspd_que):
    """
        process_id: unique process identifier
        rcv_que: the cross-process queue for main process to send message; the message is a tuple of
            (
                - command type: 0 means updating the score of a user, 1 means getting the rank of a user
                - user id
                - score if the command type is 0, and None otherwise
            )
        rspd_que: the cross-process queue for current process to send response (rank of user) back to main process
            (
                - user id
                - rank
            )
    """
    rl = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Wait for messages from the message handler, and also publish messages occasionally
    while True:
        msg = rcv_que.get(block=True)
        logging.info(f'PROCESS {process_id} recsived {msg}')

        if msg[0] == 0:
            user_id = msg[1]
            score = msg[2]
            rl.zadd(LEADERBOARD_KEY, {user_id: score})
        elif msg[0] == 1: 
            user_id = msg[1]
            rank = rl.zrevrank(LEADERBOARD_KEY, user_id)
            rspd_que.put([user_id, rank])
        else:
            logging.warning(f'PROCESS {process_id} Unknown command {str(msg[0])}')


def main():
    # clean up the left over from last round
    rl = redis.Redis(host='localhost', port=6379, decode_responses=True)
    rl.delete(LEADERBOARD_KEY)

    # start a few worker processes
    logging.info('Starting processes...')
    processes = []
    send_ques = []
    recv_ques = []
    for i in range(NUM_PROCESSES):
        sq = Queue()
        send_ques.append(sq)
        rq = Queue()
        recv_ques.append(rq)

        processes.append(Process(target=worker_process, args=(i, sq, rq)))
        processes[-1].start()
    
    # build a local skip list, so we can verify the result from worker proccesses
    user_scores = [-1] * NUM_PLAYERS

    logging.info('MAIN: Starting loop...')
    for i in range(1):
        # update user scores
        logging.info('Update user scores...')
        for i in range(100):
            user_id = random.randint(0, NUM_PLAYERS-1)
            score = random.randint(0, 10000)
            process_to_update = random.randint(0, len(processes)-1)

            send_ques[process_to_update].put([0, user_id, score])
            user_scores[user_id] = score
        
        # give some time for worker process to update redis
        time.sleep(5)
        
        # get the rank from a random user from one of the processes
        logging.info('Check user ranks...')
        for i in range(2):
            process_to_query = random.randint(0, len(processes)-1)

            user_id = random.randint(0, NUM_PLAYERS-1)
            if user_scores[user_id] < 0:
                logging.info('Skip because sampled user id has no score')
                continue

            send_ques[process_to_query].put([1, user_id, 0])
            _, rank = recv_ques[process_to_query].get(block=True)
            rank = int(rank)
            logging.info(f'Get rank for user {user_id} from process {process_to_query}, and the rank is {rank}')

            # get the factual rank
            factual_rank = 0
            for score in user_scores:
                if score > user_scores[user_id]:
                    factual_rank += 1
            
            if int(rank) == factual_rank:
                logging.info(f'MATCHED! Rank of user ({user_id}) is {factual_rank}')
            else:
                logging.warning(f'NOT matched! Rank of user ({user_id}) is (factual_rank: {factual_rank}) and reported rank: {rank})')

        # table a break
        time.sleep(5)


if __name__ == "__main__":
    main()



def func(arg):
    print(type(arg))