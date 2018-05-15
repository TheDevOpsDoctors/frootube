include ../config/variables.make.$(ENV)

default: build

build:
	stacker build --region $(AWS_REGION) --profile $(AWS_PROFILE) --interactive --tail config/$(ENV).env config/config.yaml

.PHONY: build
