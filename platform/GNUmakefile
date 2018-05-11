include .make.env

default: build

build:
	stacker build --region $(REGION) --profile $(PROFILE) --interactive --tail config/$(ENV).env config/config.yaml

.PHONY: build
