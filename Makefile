IMAGE_NAME:=alexvolha/search_service

build:
	docker build -f docker/Dockerfile -t $(IMAGE_NAME):base .

build_prod:
	docker build -f docker/Dockerfile.prod -t $(IMAGE_NAME):latest .

test:
	docker-compose -f docker/test-compose.yml rm -f && docker-compose -f docker/test-compose.yml up --abort-on-container-exit

push:
	docker push alexvolha/search_service:latest
