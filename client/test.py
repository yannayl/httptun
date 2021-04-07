import requests
from pytun import TunTapDevice

def main():
  tun = TunTapDevice(name="http_tun")
  tun.addr = '10.8.0.2'
  tun.dstaddr = '10.8.0.1'
  tun.netmask = '255.255.255.0'
  tun.mtu = 1500
  tun.up()
  while True:
    buf = tun.read(tun.mtu)
    rv = requests.post("http://127.0.0.1:8080/", data=buf)
    if rv.content:
      tun.write(rv.content)

if __name__ == "__main__":
  exit(main())
