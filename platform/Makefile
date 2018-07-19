include ../config/variables.make.$(ENV)

SHELL=/bin/bash

default: build

build:
	stacker diff --region $(AWS_REGION) --profile $(AWS_PROFILE) --interactive config/$(ENV).env config/config.yaml
	@echo -n "Press enter to continue, CTRL-C to abort"
	@read i
	stacker build --region $(AWS_REGION) --profile $(AWS_PROFILE) --interactive --tail config/$(ENV).env config/config.yaml

.PHONY: build
