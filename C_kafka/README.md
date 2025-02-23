
## Kafka

Apache Kafka plays an important role for data processing.

It is recommended to read [the instrudction section of Apache Kafka official web site](https://kafka.apache.org/documentation/#introduction)

Important concepts include:
- topics
- partition
- producer group and consumer group


## Challenge

[kafka-python](https://kafka-python.readthedocs.io/) is used as the access client.



## Comparison between Kafka, Task Queue (like RabbitMQ and SQS), and Redis Pubsub


| Example Case | choice | reasoning |
| :----------  | :--:   | :-----    |
| chat room for messengers | Redis PubSub | each user needs 1 connection; both Kafka and queue system are design for tens of thousands of consumers, and frequent subscriptions and unsubscriptions; Redis PubSub, on the other hand, is lightweight and support thousands. Missing a few messages is not a big issue, as we still need database for durability |
| machine metrics | kafka | Kafka is designed to process massive amount of data with durability. Queue system is not designed for massive volume of data, and Redis PubSub does not support durability well |
| crawl web page | Queue system | Kafka does not support multiple consumers per partitions; Redis PubSub does not support durability; further, queue system support priority queue, retry queue, deadletter queue out of box, which is convenient for crawling web pages|
