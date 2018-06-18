include ../config/variables.make.$(ENV)

STACK_NAME=$(ENV)-upload-link-generator-function

.PHONY: deploy invoke

output/package.zip: function.py
	rm -f '$@'
	zip -u '$@' $^

output/packaged-template.yaml: template.yaml output/package.zip
	aws cloudformation package \
		--profile $(AWS_PROFILE) \
		--region $(AWS_DEFAULT_REGION) \
		--template-file '$<' \
		--output-template-file '$@' \
		--s3-bucket a1b1-$(APP)-$(ENV)-deployment \
		--s3-prefix packaged-functions

deploy: output/packaged-template.yaml
	aws cloudformation deploy \
		--profile $(AWS_PROFILE) \
		--region $(AWS_DEFAULT_REGION) \
		--template-file '$<' \
		--capabilities CAPABILITY_IAM \
		--stack-name $(STACK_NAME)

invoke:
	FID=$(shell AWS_PROFILE="$(AWS_PROFILE)" AWS_DEFAULT_REGION="$(AWS_DEFAULT_REGION)" \
	            aws cloudformation list-stack-resources --stack-name $(STACK_NAME) \
	            | jq -r '.StackResourceSummaries[] | select(.LogicalResourceId=="Function").PhysicalResourceId'); \
	aws lambda invoke --function-name "$${FID}" --region '$(AWS_DEFAULT_REGION)' --profile '$(AWS_PROFILE)' \
	                  --qualifier '$(ENV)' 'output/$(ENV)-invoke.out'
	cat 'output/$(ENV)-invoke.out'
