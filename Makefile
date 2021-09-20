.PHONY: venv build-image

VENV_NAME=venv
BRANCH_NAME_SANITIZED=$(subst /,-,$(BRANCH_NAME))
WORKSPACE_DIR=$(subst @,-,$(notdir ${PWD}))
DOCKER_PROJECT_NAME=poap-scan-v2-etl
IMAGE_TAG=ethereum-etl:latest
AWS_REGION=us-west-2

build:
	docker build -t $(IMAGE_TAG) . -f Dockerfile

venv:
	virtualenv -p python3.7 $(VENV_NAME) && \
	. $(VENV_NAME)/bin/activate && \
	pip install -r requirements.txt

build-image:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin 744082184901.dkr.ecr.us-west-2.amazonaws.com && \
	docker build -t $(IMAGE_TAG) . -f Dockerfile && \
  docker tag $(IMAGE_TAG) 744082184901.dkr.ecr.us-west-2.amazonaws.com/$(IMAGE_TAG)

# Push image to ECR
push: build-image
	docker push 744082184901.dkr.ecr.us-west-2.amazonaws.com/$(IMAGE_TAG)