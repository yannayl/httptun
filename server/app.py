from gevent.pywsgi import WSGIServer
from gevent.queue import Empty, Queue
from gevent.select import select
from gevent import spawn
from flask import Flask, request, make_response
from pytun import TunTapDevice
import logging

logger = logging.getLogger()

tun = TunTapDevice(name="http_tun")
tun.addr = '10.8.0.1'
tun.dstaddr = '10.8.0.2'
tun.netmask = '255.255.255.0'
tun.mtu = 1500
tun.up()

tun2http_queue = Queue()

def read_tun():
    while True:
        select([tun.fileno()], [], [])
        buf = tun.read(tun.mtu)
        tun2http_queue.put(buf)

app = Flask(__name__)
@app.route('/', methods=['POST'])
def index():
    select([], [tun.fileno()], [])
    tun.write(request.data)
    try:
        ret = tun2http_queue.get_nowait()
        return make_response(ret)
    except Empty:
        return make_response(b'')

spawn(read_tun)
http_server = WSGIServer(('', 80), app)
http_server.serve_forever()