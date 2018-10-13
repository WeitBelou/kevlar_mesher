USERNAME = strangeducttape
APPLICATION = kevlar_mesher
TAG=$(shell git rev-parse HEAD)

IMAGE = $(USERNAME)/$(APPLICATION):$(TAG)

DOCKER_UID = 501
DOCKER_USER = appuser

.PHONY: build
build:
	docker build \
	--build-arg NB_UID=$(DOCKER_UID) \
	--build-arg NB_USER=$(DOCKER_USER) \
	-t $(IMAGE) .

.PHONY: run
run: build
	docker -v $(PWD)/out:/home/$(DOCKER_USER)/out:rw $(IMAGE)
