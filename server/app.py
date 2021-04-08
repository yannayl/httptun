from gevent.pywsgi import WSGIServer
from gevent.queue import Empty, Queue
from gevent.select import select
from gevent import spawn
from flask import Flask, abort, request, jsonify
from pytun import TunTapDevice
from Cryptodome.Cipher import AES
import binascii
import logging
import json
import os

KEY = binascii.a2b_base64(os.getenv('HTTPTUN_KEY'))

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

def decrypt(ciphertext, nonce, tag):
    cipher = AES.new(KEY, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    cipher.verify(tag)
    return plaintext

def encrypt(plaintext):
    cipher = AES.new(KEY, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return ciphertext, cipher.nonce, tag

app = Flask(__name__)
@app.route('/', methods=['POST'])
def index():
    for attr in ['nonce', 'ciphertext', 'tag']:
        if attr not in request.json:
            abort(400)

    ciphertext = binascii.a2b_base64(request.json['ciphertext'])
    nonce = binascii.a2b_base64(request.json['nonce'])
    tag = binascii.a2b_base64(request.json['tag'])

    cipher = AES.new(KEY, AES.MODE_EAX, nonce=nonce)
    try:
        plaintext = decrypt(ciphertext, nonce, tag)
    except ValueError:
        abort(403)

    select([], [tun.fileno()], [])
    tun.write(plaintext)
    try:
        ret = tun2http_queue.get_nowait()
        ciphertext, nonce, tag = encrypt(ret)
    except:
        return ''
    
    return jsonify({
        'ciphertext': binascii.b2a_base64(ciphertext).decode('utf-8'),
        'nonce': binascii.b2a_base64(nonce).decode('utf-8'),
        'tag': binascii.b2a_base64(tag).decode('utf-8'),
    })

spawn(read_tun)
http_server = WSGIServer(('', 80), app)
http_server.serve_forever()