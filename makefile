IMAGE=sheepit-golem
CONTAINER=sheepit-golem

.PHONY: build default open stop clean deep-clean gvmi-push image

build: Dockerfile 
	sudo docker build -t $(IMAGE) .

sheepit.gvmi: build
	sudo gvmkit-build $(IMAGE):latest -o sheepit.gvmi

image: sheepit.gvmi

gvmi-push: sheepit.gvmi
	sudo gvmkit-build $(IMAGE):latest -o sheepit.gvmi --push
	

default: build
	sudo docker run -dit --name $(CONTAINER) -v $(pwd)/sheepit:/golem/work $(IMAGE)

open: default
	sudo docker exec -ti sheepit-golem "/bin/bash"

stop:
	sudo docker stop $(CONTAINER)

clean: stop
	sudo docker rm $(CONTAINER)

deep-clean:
	sudo docker image rm $(IMAGE)