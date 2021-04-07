all: run

.PHONY: build
build: Dockerfile app.py run.sh
	docker build . -t http_tunner:server
	
.PHONY: run
run: build
	docker run --rm -it  -p 8080:80 --cap-add net_admin --sysctl net.ipv4.ip_forward=1 http_tunner:server
