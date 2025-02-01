
## Redis

Redis is a popular in memory NoSQL database.


## Challenges

- Use Redis as a pubsub
- Use Redis to build [a leaderboard for online games](https://redis.io/solutions/leaderboards/)


## How to Use?

- In one terminal tab, start Redis container
```
$ docker compose up
```

- in another terminal tab, start vritual environment
```
$ bash start_venv.sh
$ python3 pubsub.py
```