"""
This system is to get the friend's locations for a user in real-time.

You need to define the functions to
- send/publish update for the new location of a user: publish_user_location()
- receive/subscribe to the location update of the friends of a user: subscribe_friends_update()
"""
from typing import List, Dict, Tuple
import logging
import time
import random 
import pickle

import threading
from multiprocessing import Process
import redis


NUM_PROCESSES = 3

USER_LIST = [f"{i:05}" for i in range(10)]
FRIENDS = {
    "00000": ["00001", "00002"],
    "00001": ["00000", "00002"],
    "00002": ["00000", "00001"],

    "00003": ["00009", "00004", "00005", "00006", "00007", "00008"],
    "00004": ["00003", "00009", "00005", "00006", "00007", "00008"],
    "00005": ["00003", "00004", "00009", "00006", "00007", "00008"],
    "00006": ["00003", "00004", "00005", "00009", "00007", "00008"],
    "00007": ["00003", "00004", "00005", "00006", "00009", "00008"],
    "00008": ["00003", "00004", "00005", "00006", "00007", "00009"],
    "00009": ["00003", "00004", "00005", "00006", "00007", "00008"],
}

logging.basicConfig(level=logging.INFO)


def get_friends(user_id):
    return FRIENDS[user_id]


def notify_user_about_friend_location(rclient, user_id, friend_id, lat: float, lng: float):
    # if we have a websocket, we would use the WebSocket to send the friend's new location to the user immediately;
    # however, here we simply write the friend's new location to redis for this user.
    rclient.hset(f'{user_id}_friends_locations', key=friend_id, value=pickle.dumps((lat, lng)))


def get_user_nearby_friend_locations(rclient, user_id) -> Dict[str, Tuple[float, float]]:
    # Get the locations of all friends of a user
    raw_friends_locations = rclient.hgetall(f'{user_id}_friends_locations')
    friends_locations = {}
    for k, v in raw_friends_locations.items():
        friends_locations[k.decode('utf-8')] = pickle.loads(v)
    return friends_locations


def worker_process(process_id, responsible_users: List[str]):
    '''
    This emulates the WebSocker worker or background worker which tracks friends' location update.

    Note multi workers will be started. Each worker is responsible for a group of users.
    '''
    # rl = redis.Redis(host='localhost', port=6379, decode_responses=True)
    rclient = redis.Redis(host='localhost', port=6379)
    
    for user_id in responsible_users:
        subscribe_friends_update(rclient, user_id)

    # Wait for messages from the message handler, and also publish messages occasionally
    while True:
        #  Wait and get the messages from the message handler 
        time.sleep(10)
        logging.info(f'PROCESS {process_id}: is alive')


def main():
    # Clean up possible location history from previous runs
    rclient = redis.Redis(host='localhost', port=6379)
    for user_id in USER_LIST:
        rclient.delete(f'{user_id}_friends_locations')

    # start a few worker processes
    logging.info('Starting processes...')
    processes = {}
    num_user_per_worker = len(USER_LIST) // NUM_PROCESSES
    for i in range(NUM_PROCESSES):
        if i == NUM_PROCESSES - 1:
            responsible_users = USER_LIST[(num_user_per_worker * i):]
        else:
            responsible_users = USER_LIST[(num_user_per_worker * i): (num_user_per_worker * (i + 1))]

        processes[i] = Process(target=worker_process, args=(i, responsible_users))
        processes[i].start()
    

    # Send some random user location updates
    logging.info('MAIN: Starting send user update ...')
    user_last_location = {}
    random.seed(1)
    for i in range(1000):
        user_id = random.choice(USER_LIST)
        location = (random.uniform(0, 10), random.uniform(0, 10))
        user_last_location[user_id] = location
        publish_user_location(rclient, user_id, location[0], location[1])

        sleep_time = random.uniform(0, 1)
        time.sleep(sleep_time)

    time.sleep(3)

    # verify that user has friend's last location
    for i in range(3):
        target_user_id = random.choice(USER_LIST)
        logging.info(f'MAIN: verify location of user {target_user_id} ...')
        if target_user_id not in user_last_location:
            continue
        target_user_last_loc = user_last_location[target_user_id]

        # Fetch the location of this user from her/his friend side
        friends = get_friends(target_user_id)
        for friend_id in friends:
            user_friend_location = get_user_nearby_friend_locations(rclient, friend_id)
            if target_user_id not in user_friend_location:
                logging.error(f"User {target_user_id}'s is not found at friend {friend_id} 's location cache")
                continue

            location_at_friends = user_friend_location.get(target_user_id, (0, 0))
            if target_user_last_loc[0] == location_at_friends[0] and\
                target_user_last_loc[1] == location_at_friends[1]:
                logging.info(f"User {target_user_id}'s location is verified successfully with friend {friend_id}")
            else:
                logging.error(f"User {target_user_id}'s location does not match the records at her friend side; " +
                              f"The actual last location is ({target_user_last_loc[0]}, {target_user_last_loc[1]}), but " +
                              f"the location at friend {friend_id} is: ({location_at_friends[0]}, {location_at_friends[1]})")

    # Try to stop all processes
    for proc in processes.values():
        proc.terminate()
    for proc in processes.values():
        proc.join()


def get_user_channel_name(user_id: str):
    return f'user-{user_id}'


def get_user_id_from_channel_name(channel_name: str):
    return channel_name[len("user-"):]


def publish_user_location(rclient, user_id: str, lat: float, lng: float):
    rclient.publish(get_user_channel_name(user_id), pickle.dumps((lat, lng)))


def subscribe_friends_update(rclient, user_id: str) -> threading.Thread:
    # define the handler for pubsub messages from other workers
    # this handler runs in a different thread and put message into the msg_que
    def handle_msg(msg):
        nonlocal user_id
        nonlocal rclient

        friend_id = get_user_id_from_channel_name(msg['channel'])
        location = pickle.loads(msg['data'])
        notify_user_about_friend_location(rclient, user_id, friend_id, location[0], location[1])

    # Register pubsub message handler for topics by other workers
    channels_handler_map = {}
    for friend_id in get_friends(user_id):
        channel_name = get_user_channel_name(friend_id)
        channels_handler_map[channel_name] = handle_msg

    p = rclient.pubsub()
    p.subscribe(**channels_handler_map)
    thread = p.run_in_thread(sleep_time=0.1)

    logging.info(f'subscribed channels: {channels_handler_map.keys()} for {user_id}')

    return thread


if __name__ == "__main__":
    main()