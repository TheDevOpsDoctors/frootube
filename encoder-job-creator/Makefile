include ../config/variables.make.$(ENV)

.PHONY: deploy

output/package.zip: convert.py job.json
	rm -f output/package.zip
	zip -u output/package.zip convert.py job.json

output/packaged-template.yaml: output/package.zip template.yaml
	aws cloudformation package \
		--profile $(AWS_PROFILE) \
		--region $(AWS_REGION) \
		--template-file template.yaml \
		--output-template-file output/packaged-template.yaml \
		--s3-bucket a1b1-$(APP)-$(ENV)-deployment \
		--s3-prefix packaged-functions

deploy: output/packaged-template.yaml
	aws cloudformation deploy \
		--profile $(AWS_PROFILE) \
		--region $(AWS_REGION) \
		--template-file '$<' \
		--capabilities CAPABILITY_IAM \
		--stack-name dev-encoder-job-creator
