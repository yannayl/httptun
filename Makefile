all: run-local-server

DOCKER = docker --config .docker
HTTPTUN_KEY = $(shell base64 < .keyfile)
GCLOUD_CONFIG = .gcloudconfig
GCLOUD = CLOUDSDK_CONFIG=.gcloudconfig gcloud
GCLOUD_PROJECT = $(shell $(GCLOUD) config get-value project)
SERVER_IMAGE_TAG = gcr.io/$(GCLOUD_PROJECT)/server
SERVER_NAME = server
SERVER_ZONE = northamerica-northeast1-a

.PHONY: build-server
build-server: server/Dockerfile server/app.py server/run.sh
	$(DOCKER) build -t http_tunner:server server
	
.PHONY: run-local-server
run-local-server: build-server
	$(DOCKER) run -e HTTPTUN_KEY=$(HTTPTUN_KEY) --rm -it  -p 8080:80 --cap-add net_admin --sysctl net.ipv4.ip_forward=1 http_tunner:server

.PHONY: run-client
run-client:
	HTTPTUN_URL=http://127.0.0.1:8080 \
		HTTPTUN_KEY=$(HTTPTUN_KEY) sudo -E python3 client/test.py

.PHONY: run-client-remote
run-client-remote:
	HTTPTUN_URL=http://$(shell $(GCLOUD) compute instances describe $(SERVER_NAME) --zone $(SERVER_ZONE) --format='get(networkInterfaces[0].networkIP)') \
		HTTPTUN_KEY=$(HTTPTUN_KEY) sudo -E python3 client/test.py

.PHONY: push-server
push-server: build-server
	$(DOCKER) tag http_tunner:server $(SERVER_IMAGE_TAG)
	CLOUDSDK_CONFIG=.gcloudconfig $(DOCKER) push $(SERVER_IMAGE_TAG)

.PHONY: create-remote-server
create-remote-server:
	$(GCLOUD) compute instances create-with-container $(SERVER_NAME) \
		--container-env HTTPTUN_KEY=$(HTTPTUN_KEY) \
		--container-image $(SERVER_IMAGE_TAG) \
		--container-privileged \
		--machine-type f1-micro \
		--restart-on-failure \
		--tags http-server \
		--zone $(SERVER_ZONE)

.PHONY: delete-remote-server
delete-remote-serve:
	$(GCLOUD) compute instances delete $(SERVER_NAME)