"""
Leaderboard: https://redis.io/solutions/leaderboards/

Track the top players and also get the rank of a specific player.

Implement:
- receive_user_new_score(): store user score
- get_top_players(): get top players
- get_user_rank(): get rank of a specific player
"""

from typing import Dict
import logging
import time
import random 

from multiprocessing import Process, Queue
import redis


NUM_PROCESSES = 2
NUM_PLAYERS = 100
LEADERBOARD_KEY = 'leaderboard'
logging.basicConfig(level=logging.INFO)


def worker_process(process_id, rcv_que):
    """
    This emulates the web server process, which receives the new scores of users.

    Parameters:
    - process_id: unique process identifier
    - rcv_que: the cross-process queue for main process to send message; the message is a tuple of
               (user id, , score)
    """
    rl = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Wait for messages from the message handler, and also publish messages occasionally
    while True:
        msg = rcv_que.get(block=True)
        # logging.info(f'PROCESS {process_id} recsived {msg}')

        user_id = msg[0]
        score = msg[1]
        receive_user_new_score(rl, user_id, score)


def main():
    random.seed(1)
    
    # clean up the left over from last round
    rl = redis.Redis(host='localhost', port=6379, decode_responses=True)
    rl.delete(LEADERBOARD_KEY)

    # start a few worker processes, and use queue to send user score update
    logging.info('Starting processes...')
    processes = []
    send_ques = []
    for i in range(NUM_PROCESSES):
        sq = Queue()
        send_ques.append(sq)

        processes.append(Process(target=worker_process, args=(i, sq)))
        processes[-1].start()
    
    # build a local list to track user scores, so we can verify the result
    user_scores = [-1] * NUM_PLAYERS

    # update user scores
    logging.info('Update user scores...')
    for i in range(1000):
        user_id = random.randint(0, NUM_PLAYERS-1)
        score = random.randint(0, 10000)
        user_scores[user_id] = score

        # Send the user id and score to the worker process
        process_to_update = random.randint(0, len(processes)-1)
        send_ques[process_to_update].put([user_id, score])
        
    # give some time for worker process to update redis
    logging.info('MAIN: Waiting a few seconds ...')
    time.sleep(2)
    
    # Verify the rank for a random user
    logging.info('MAIN: Check user ranks...')
    for i in range(5):
        user_id = random.randint(0, NUM_PLAYERS-1)
        if user_scores[user_id] < 0:
            logging.info('Skip because sampled user id has no score')
            continue

        # get the factual rank
        factual_rank = 0
        for score in user_scores:
            if score > user_scores[user_id]:
                factual_rank += 1
        
        # Fetch from the redis
        rank = get_user_rank(rl, user_id)

        if rank == factual_rank:
            logging.info(f'MATCHED! Rank of user ({user_id}) is {factual_rank}')
        else:
            logging.warning(f'NOT matched! Rank of user ({user_id}) is (factual_rank: {factual_rank}) and reported rank: {rank})')

    # Try to stop all processes
    for proc in processes:
        proc.terminate()
    for proc in processes:
        proc.join()


def receive_user_new_score(rclient, user_id: int, score: int):
    rclient.zadd(LEADERBOARD_KEY, {user_id: score})


def get_top_players(rclient, top_n=3) -> Dict[int, int]:
    raw_uids = rclient.zrevrange(LEADERBOARD_KEY, 0, top_n)
    uids = [int(id_str) for id_str in raw_uids]
    return uids


def get_user_rank(rclient, user_id: int):
    return rclient.zrevrank(LEADERBOARD_KEY, user_id)


if __name__ == "__main__":
    main()
