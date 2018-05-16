include ../config/variables.make.$(ENV)

default: diff

diff:
	stacker diff --region $(AWS_REGION) --profile $(AWS_PROFILE) --interactive config/$(ENV).env config/config.yaml

build:
	stacker build --region $(AWS_REGION) --profile $(AWS_PROFILE) --interactive --tail config/$(ENV).env config/config.yaml

.PHONY: build
