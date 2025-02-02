
## Redis

Redis is an open-source, in-memory data structure store known for its exceptional speed and versatility, making it a popular choice among engineers for a wide range of applications. Originally designed as a caching solution, Redis has evolved into a robust platform that supports various data structures such as strings, hashes, lists, sets, sorted sets, and more.

It is typical for Redis to support up to 1M QPS.

### Strengths
- **High Performance**:
Redis stores data in memory, providing lightning-fast read and write operations. This makes it ideal for applications where low latency is critical.

- **Rich Data Structures**:
The support for diverse data types allows Redis to be used for more than just simple key-value caching. It can handle queues, real-time analytics, leaderboards, and more.

- **Built-in Replication and Persistence Options**:
Redis supports master-slave replication for high availability and can persist data to disk with configurable snapshots or append-only files, balancing speed with durability.

- **Pub/Sub Messaging**:
The built-in publish/subscribe functionality makes Redis suitable for real-time messaging and notifications, allowing it to serve as a lightweight message broker.

### Weakness
- **Data Durability Concerns**:
While Redis offers persistence, the in-memory nature means that without proper configuration, there is a risk of data loss in scenarios like sudden power failures

- **Limited Query Capabilities**:
Redis is optimized for fast access to simple data structures, but it does not offer the advanced querying capabilities of relational databases.

- **Single-Threaded Model**:
The core Redis server operates on a single thread for command execution, which simplifies concurrency but can become a bottleneck in certain high-throughput scenarios

### Key Data Structures
- **Lists**:
How it works: Ordered collections implemented as linked lists, allowing for fast insertion at the head or tail.
Typical use case: Task queues, message buffers, or implementing a feed where order matters.
- **Hashes**:
How it works: Collections of field-value pairs, similar to dictionaries or objects.
Typical use case: Storing object attributes, such as user profiles or configuration settings, where each field is accessed individually.
- **Sorted Sets**:
How it works: Similar to sets but each member is associated with a score, maintaining elements ordered by their score.
Typical use case: Leaderboards, ranking systems, or time-based event ordering.
- **Pub/Sub (Publish/Subscribe)**: Unlike some messaging systems, Redis Pub/Sub does not store messages. If a subscriber is not actively listening at the time of publication, it will miss the message. 

## Code Challenges
Before starting, please read the [How to Use section](#how-ti-use)

### Nearby friends
Design a system to track the locations of friends in real-time (the latency of <1 second)

In the big-scale system, we also need to use geo indexing (check the geohash chapter). Here we just want to pratice the use of PubSub. So, let us assume we only track nearby friends for a small city.
  
### Leader Boards for an online game
A leaderboard is a dynamic ranking system that tracks and displays the performance of players in real time. It updates scores frequently and efficiently retrieves the top performers or a specific player's rank, ensuring minimal latency. Required operations:
- get the top 10 players
- get the rank of a specific user


## How to Use?

1. in one terminal tab, enter the current directory, start Redis container
```
$ docker compose up
```

2. in another terminal tab, start vritual environment and execute the code.
```
$ bash start_venv.sh
$ python3 challenge_nearby_friends.py
```

## Redis Client API

### List
- `lpush(name, *values)` and `rpush(name, *values)`: Push values onto the head/tail of the list name
- `lpop(name, count=None)` and `rpop(name, count=None)`: Removes and returns the first/last elements of the list name
- `blpop(keys, timeout=0)` and `brpop(keys, timeout=0)`: blocking call to remove and return the first/last elements of the list name

### Hash
- `hset(name, key=None, value=None, mapping=None, items=None)`: Set key to value within hash name, mapping accepts a dict of key/value pairs that will be added to hash name. items accepts a list of key/value pairs that will be added to hash name. Returns the number of fields that were added.
- `hgetall(name)`: Return a Python dict of the hash’s name/value pairs


### Sorted Set


### PubSub
[official documentation](https://redis-py.readthedocs.io/en/stable/advanced_features.html#publish-subscribe)

Example of subscriber
```
def my_handler(message):
    # example message: {'pattern': None, 'type': 'subscribe', 'channel': b'my-channel', 'data': 1}
    print('MY HANDLER: ', message['data'])

r = redis.Redis(...)
p = r.pubsub()
p.subscribe(**{'my-channel-1': my_handler, 'my-channel-2': my_handler})
# run the subscriber handler in a thread; otherwise, the handler won't have a chance to run when a message comes in
p.run_in_thread(sleep_time=0.001)
```

Example of publisher:
```
r = redis.Redis(...)
r.publish('my-channel-1', 'some data')
```
