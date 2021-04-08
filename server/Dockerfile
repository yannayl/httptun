FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y \
  iptables \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app.py .
COPY run.sh .

EXPOSE 80/tcp

CMD ["bash", "run.sh"]