
## WebSocket Introduction
WebSocket is a full-duplex communication protocol that enables real-time, bidirectional data exchange between a client and a server over a single, persistent TCP connection. Unlike HTTP, WebSocket eliminates the need for repeated request-response cycles, reducing latency and overhead. It is commonly used for live data streaming, chat applications, online gaming, and other interactive web applications.


## Challenge

Please read [How to Use](#how-to-use) and [API Introduction](#api-introduction) before you start.

### Build a chat room
Implement a chat room, such that all joined users can send message to each other instantly.

You should code in the [app/app.py](./app/app.py) file. 
- A template is already implemented;
- take a look at the client code at [app/templates/index.html](./app/templates/index.html)
- The solution can be found in [app/solution/app.py](./app/solution/app.py)



## How to Use

1. In terminal, enter the current directory, then start the Flask container by running:
```
$ docker compose up
```
2. in browser tab, type http://localhost:8080/ to access the main page; type username to join a chat room (hard-coded in server side)
3. in another browser tab, type http://localhost:8080/ to access the main page; type username to join the chat room
4. type message in any tab, you should see message in the other tab. Also, server will send some message if no one type any message.


## API Introduction

We use **Flask-SocketIO**, please read the [Getting Started](https://flask-socketio.readthedocs.io/en/latest/getting_started.html) to get a idea.

To implement a chat room, we use the [Rooms](https://flask-socketio.readthedocs.io/en/latest/getting_started.html#rooms) provided by Flask-SocketIO.