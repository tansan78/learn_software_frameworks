
import flask
import socket
import logging

app = flask.Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route("/")
def index():
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    return flask.render_template('index.html', host_name=host_name, host_ip=host_ip)

@app.route("/echo")
def list_ip():
    return 'hello world'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
