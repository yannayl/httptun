#!/bin/bash -e

iptables-legacy --table nat --append POSTROUTING --jump MASQUERADE

mkdir -p /dev/net && mknod /dev/net/tun c 10 200

python3 app.py
