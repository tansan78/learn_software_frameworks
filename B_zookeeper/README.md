
## What is Apache ZooKeeper?

[Apache ZooKeeper](https://zookeeper.apache.org/) is a centralized service designed for maintaining configuration information, naming, synchronization, and providing group services in distributed systems. It runs Paxos algorithm, and gurantees consistency as long as the client can reach the majority of nodes.

It employs a hierarchical namespace similar to a file system, where each node (or znode) can store small amounts of data. Key features include:
- **Ephemeral Nodes**: Automatically deleted when a client disconnects, useful for representing temporary states.
- **Sequential Nodes**: Automatically assigned a unique, incrementing suffix, ideal for ordering tasks such as leader election.


## Code Challenges

### [Consistent Hashing](https://en.wikipedia.org/wiki/Consistent_hashing)
Consistent hashing is a distributed algorithm designed to minimize key remapping when nodes are added or removed in a system. By mapping both keys and nodes onto a circular hash space, it assigns each key to the nearest node in the clockwise direction. This approach ensures that only a small fraction of keys need to be redistributed during changes, providing scalability and fault tolerance. Consistent hashing is widely used in distributed caching, load balancing, and data partitioning scenarios where maintaining a balanced load and minimal disruption is critical.

### Lead Election
Leader election in distributed systems is the process of selecting a single node (the leader) from among a group of nodes to coordinate and manage tasks within the system. This process ensures that despite the decentralized nature of the system, one node can be designated to handle specific responsibilities—such as managing shared resources, coordinating tasks, or ensuring consistency across the network. Effective leader election algorithms are designed to handle node failures, network partitions, and dynamic membership changes, maintaining system stability and performance even in challenging environments.


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

## Client API
The code uses [Kazoo](https://kazoo.readthedocs.io/en/latest/basic_usage.html) which is a Python client for ZooKeeper.

Some important concepts from [Zookeeper Overview](https://zookeeper.apache.org/doc/current/zookeeperOver.html):


> **Data model and the hierarchical namespace**
> 
> The namespace provided by ZooKeeper is much like that of a standard file system. A name is a sequence of path elements separated by a slash (/). Every node in ZooKeeper's namespace is identified by a path.
> 
> **Nodes and ephemeral nodes**
> 
> Unlike standard file systems, each node in a ZooKeeper namespace can have data associated with it as well as children. It is like having a file-system that allows a file to also be a directory. (ZooKeeper was designed to store coordination data: status information, configuration, location information, etc., so the data stored at each node is usually small, in the byte to kilobyte range.) We use the term znode to make it clear that we are talking about ZooKeeper data nodes.
> 
> Znodes maintain a stat structure that includes version numbers for data changes, ACL changes, and timestamps, to allow cache validations and coordinated updates. Each time a znode's data changes, the version number increases. For instance, whenever a client retrieves data it also receives the version of the data.
> 
> The data stored at each znode in a namespace is read and written atomically. Reads get all the data bytes associated with a znode and a write replaces all the data. Each node has an Access Control List (ACL) that restricts who can do what.
> 
> ZooKeeper also has the notion of ephemeral nodes. These znodes exists as long as the session that created the znode is active. When the session ends the znode is deleted.
> 
> 
> **Conditional updates and watches**
> 
> ZooKeeper supports the concept of watches. Clients can set a watch on a znode. A watch will be triggered and removed when the znode changes. When a watch is triggered, the client receives a packet saying that the znode has changed. If the connection between the client and one of the ZooKeeper servers is broken, the client will receive a local notification.
