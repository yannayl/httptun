import binascii
import os
import requests
from pytun import TunTapDevice
from Cryptodome.Cipher import AES

KEY = binascii.a2b_base64(os.getenv('HTTPTUN_KEY'))
URL = "http://127.0.0.1:8080/"

def decrypt(ciphertext, nonce, tag):
    cipher = AES.new(KEY, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    cipher.verify(tag)
    return plaintext

def encrypt(plaintext):
    cipher = AES.new(KEY, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return ciphertext, cipher.nonce, tag

def main():
  tun = TunTapDevice(name="http_tun")
  tun.addr = '10.8.0.2'
  tun.dstaddr = '10.8.0.1'
  tun.netmask = '255.255.255.0'
  tun.mtu = 1500
  tun.up()
  session = requests.Session()
  while True:
    buf = tun.read(tun.mtu)
    ciphertext, nonce, tag = encrypt(buf)
    postdata = {
        'ciphertext': binascii.b2a_base64(ciphertext),
        'nonce': binascii.b2a_base64(nonce),
        'tag': binascii.b2a_base64(tag),
    }
    rv = session.post(URL, json=postdata)
    try:
      for attr in ['nonce', 'ciphertext', 'tag']:
        if attr not in rv.json():
          continue
  
      ciphertext = binascii.a2b_base64(rv.json()['ciphertext'])
      nonce = binascii.a2b_base64(rv.json()['nonce'])
      tag = binascii.a2b_base64(rv.json()['tag'])
      tun.write(decrypt(ciphertext, nonce, tag))
    except:
      pass

if __name__ == "__main__":
  exit(main())
