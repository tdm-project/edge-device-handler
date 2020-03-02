GIT_BRANCH=$(shell git rev-parse --abbrev-ref HEAD | sed -e 's/master/latest/')
DOCKER_IMAGE_VERSION=1.0.1
DOCKER_IMAGE_NAME=tdmproject/edge-device-handler
DOCKER_IMAGE_TAGNAME=$(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_VERSION)
DOCKER_IMAGE_TESTING=$(DOCKER_IMAGE_NAME):testing-$(DOCKER_IMAGE_VERSION)

default: build-final

build-final:
	docker build --target=final -f docker/Dockerfile -t $(DOCKER_IMAGE_TAGNAME) .
	docker tag $(DOCKER_IMAGE_TAGNAME) $(DOCKER_IMAGE_NAME):$(GIT_BRANCH)

push:
	docker push $(DOCKER_IMAGE_TAGNAME)
	docker push $(DOCKER_IMAGE_NAME)
	docker push $(DOCKER_IMAGE_NAME):$(GIT_BRANCH)

test:
	docker build --target=testing -f docker/Dockerfile -t $(DOCKER_IMAGE_TESTING) .
	docker run --rm --entrypoint=tests/entrypoint.sh $(DOCKER_IMAGE_TESTING)
