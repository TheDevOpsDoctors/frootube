include ../config/variables.make.$(ENV)

.PHONY: deploy

output/package.zip: convert.py job.json
	rm -f '$@'
	zip -u '$@' $^

output/packaged-template.yaml: template.yaml output/package.zip
	aws cloudformation package \
		--profile $(AWS_PROFILE) \
		--region $(AWS_REGION) \
		--template-file '$<' \
		--output-template-file '$@' \
		--s3-bucket a1b1-$(APP)-$(ENV)-deployment \
		--s3-prefix packaged-functions

deploy: output/packaged-template.yaml
	aws cloudformation deploy \
		--profile $(AWS_PROFILE) \
		--region $(AWS_REGION) \
		--template-file '$<' \
		--capabilities CAPABILITY_IAM \
		--stack-name dev-encoder-job-creator-function
