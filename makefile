IMAGE=sheepit-golem
CONTAINER=sheepit-golem

.PHONY: build default open stop clean deep-clean

build: Dockerfile 
	sudo docker build -t $(IMAGE) .

default: build
	sudo docker run -dit --name $(CONTAINER) -v $(pwd)/sheepit:/golem/work $(IMAGE)

open: default
	sudo docker exec -ti sheepit-golem "/bin/bash"

stop:
	sudo docker stop $(CONTAINER)

clean: stop
	sudo docker rm $(CONTAINER)

deep-clean: clean
	sudo docker image rm $(IMAGE)