
## What is Apache ZooKeeper?

[Apache ZooKeeper](https://zookeeper.apache.org/) runs Paxos algorithm, which has high consistency (by sacrificing some availability).

It is a popular tool for name lookup, lead/master node election, membership management, etc.

Here we provide two examples:
- lead/master node election: `leader_election.py`
- [consistent hashing](https://en.wikipedia.org/wiki/Consistent_hashing): `consistent_hashing.py`

The code means to be as simple as possible, instead of being perfect.

The code uses [Kazoo](https://kazoo.readthedocs.io/en/latest/index.html#) which is a Python client for ZooKeeper.

## How to Run Code
Before you start, please make sure that you have docker installed.


Open 2 terminal tabs
- in the first tab, start the container of Apache Zookeeper
```
$ docker compose up
```
- in the second tab, start the virtual envionment, and run the example code
```
$ bash start_venv.sh
$ python3 consistent_hashing.py
$ python3 leader_election.py
```
