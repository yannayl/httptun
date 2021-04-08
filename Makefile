all: run-local-server

DOCKER = docker --config .docker
HTTPTUN_KEY=$(shell base64 < .keyfile)

.PHONY: build-server
build-server: server/Dockerfile server/app.py server/run.sh
	$(DOCKER) build -t http_tunner:server server
	
.PHONY: run-local-server
run-local-server: build-server
	$(DOCKER) run -e HTTPTUN_KEY=$(HTTPTUN_KEY) --rm -it  -p 8080:80 --cap-add net_admin --sysctl net.ipv4.ip_forward=1 http_tunner:server

.PHONY: run-client
run-client:
	HTTPTUN_KEY=$(HTTPTUN_KEY) sudo -E python3 client/test.py