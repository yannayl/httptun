FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y \
  iptables \
  inetutils-ping \
  tcpdump \
  net-tools \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY app.py .
COPY run.sh .

CMD ["bash", "run.sh"]