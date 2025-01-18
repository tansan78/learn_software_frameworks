
## What is Apache ZooKeeper?

[Apache ZooKeeper](https://zookeeper.apache.org/) runs Paxos algorithm, which has high consistency (by sacrificing some availability).

It is a popular tool for name lookup, lead/master election, membership management, etc.

Two code challenges:
- lead/master node election: `challenge_leader_election.py`
- [consistent hashing](https://en.wikipedia.org/wiki/Consistent_hashing): `challenge_consistent_hashing.py`

Keep code as simple as possible, instead of being perfect.

The code uses [Kazoo](https://kazoo.readthedocs.io/en/latest/index.html#) which is a Python client for ZooKeeper.


## How to Run Code
Before you start, please make sure that you have docker installed.

Open 2 terminal tabs
- in the first tab, (in the zookeeper directory) start the container of Apache Zookeeper
```
$ docker compose up
```
- in the second tab, (in the zookeeper directory) start the virtual envionment, and run the example code
```
$ bash start_venv.sh
$ python3 challenge_leader_election.py
$ python3 challenge_consistent_hashing.py
```
