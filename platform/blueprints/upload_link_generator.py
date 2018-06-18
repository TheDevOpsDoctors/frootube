from __future__ import print_function

from stacker.blueprints.base import Blueprint
from troposphere import iam, GetAtt

from blueprints.exporter import Exporter


class Role(Blueprint, Exporter):
    VARIABLES = {
        'tags': {
            'type': dict,
        },
        'UploadBucket': {
            'type': str,
        },
        'exports': {
            'type': dict,
            'default': {},
        },
    }

    def create_lambda_role(self, upload_bucket_name):
        t = self.template

        trust_policy = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Effect': 'Allow',
                    'Principal': {'Service': 'lambda.amazonaws.com'},
                    'Action': 'sts:AssumeRole',
                }
            ]
        }

        role_policy_document = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Effect': 'Allow',
                    'Action': [
                        'logs:CreateLogGroup',
                        'logs:CreateLogStream',
                        'logs:PutLogEvents'
                    ],
                    'Resource': '*'
                },
                {
                    'Effect': 'Allow',
                    'Action': [
                        's3:putObject',
                    ],
                    'Resource': 'arn:aws:s3:::{}/*'.format(upload_bucket_name)
                },
            ]
        }

        role_policy = iam.Policy('LambdaRolePolicy',
                                 PolicyName='LambdaRolePolicy',
                                 PolicyDocument=role_policy_document)

        role = iam.Role('LambdaRole',
                        AssumeRolePolicyDocument=trust_policy,
                        Policies=[role_policy])
        t.add_resource(role)

        return role

    def create_template(self):
        variables = self.get_variables()
        self.create_lambda_role(variables['UploadBucket'])
        self.create_exports()
