MAIN_PKG := rsshub
DOCKER_HUB := registry.cn-shenzhen.aliyuncs.com
GIT_TAG := $(shell git describe --abbrev=0 --tags 2>/dev/null || echo 0.0.0)
GIT_COMMIT_SEQ := $(shell git rev-parse --short HEAD 2>/dev/null || echo 000000)
GIT_COMMIT_CNT := $(shell git rev-list --all --count 2>/dev/null || echo 0)
VERSION := $(GIT_TAG).$(GIT_COMMIT_CNT).$(GIT_COMMIT_SEQ)
BUILD_TIME := $(shell TZ=UTC-8 date +"%Y-%m-%d %H:%m:%S")
FULL_VERSION := $(MAIN_PKG):$(GIT_TAG).$(GIT_COMMIT_CNT).$(GIT_COMMIT_SEQ)

docker:
	docker build . -t $(DOCKER_HUB)/$(FULL_VERSION)

docker-save: docker
	docker save $(DOCKER_HUB)/$(FULL_VERSION) | gzip > $(MAIN_PKG).$(VERSION).tar.gz

docker-push:
	docker push $(DOCKER_HUB)/$(FULL_VERSION)

docker-clean:
	docker images | grep $(MAIN_PKG) | awk '{print $$3}' | xargs docker rmi -f
	echo "y" | docker image prune

.PHONY: docker