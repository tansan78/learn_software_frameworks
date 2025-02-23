
import flask
from flask import request

import logging
import time
from flask_socketio import SocketIO, send, join_room, leave_room


logging.basicConfig(level=logging.DEBUG)


app = flask.Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
socketio = SocketIO(app)
last_updated_ts = time.time()

room_name = 'my_chatroom'


@app.route("/")
def index():
    logging.info('received root request')
    return flask.render_template('index.html', host_name='hostname', host_ip='host_ip')


@socketio.on('join')
def on_join(data):
    # ******* WRITE YOUR CODE *********
    # Join the chat room; check the index.html file for the client action
    # the data is a dictionary, like {'username': 'thomas'}
    # Read https://flask-socketio.readthedocs.io/en/latest/getting_started.html#rooms before you start
    pass


@socketio.on('echo')
def send_msg(msg):
    global last_updated_ts
    last_updated_ts = time.time()

    # ******* WRITE YOUR CODE *********
    # A client send a message; broadcast the message to other clients


def bg_worker():
    global last_updated_ts

    for i in range(20):
        time.sleep(5)

        delta = int(time.time() - last_updated_ts)
        logging.info(f'background worker checking {delta}....')

        if delta > 5:
            socketio.send(f'You have not sent message for {delta} second; we miss you', to=room_name)
            last_updated_ts = time.time()
    
    socketio.send('This is my last message', to=room_name)


if __name__ == '__main__':
   logging.info('Starting server')
   socketio.start_background_task(bg_worker)
   socketio.run(app, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)
   # app.run(host='0.0.0.0', port=8080)