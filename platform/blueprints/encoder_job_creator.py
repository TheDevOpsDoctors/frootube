from __future__ import print_function

from stacker.blueprints.base import Blueprint
from troposphere import iam, GetAtt

from blueprints.exporter import Exporter


class Roles(Blueprint, Exporter):
    VARIABLES = {
        'tags': {
            'type': dict,
        },
        'exports': {
            'type': dict,
            'default': {}
        }
    }

    def create_media_convert_role(self):
        t = self.template

        trust_policy = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Effect': 'Allow',
                    'Principal': {'Service': 'mediaconvert.amazonaws.com'},
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
                        's3:*',
                    ],
                    'Resource': '*'
                }
            ]
        }

        role_policy = iam.Policy('MediaConvertRolePolicy',
                                 PolicyName='mediaConvertRolePolicy',
                                 PolicyDocument=role_policy_document)

        role = iam.Role('MediaConvertRole',
                        AssumeRolePolicyDocument=trust_policy,
                        Policies=[role_policy])
        t.add_resource(role)

        return role

    def create_lambda_role(self, media_convert_role):
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
                        'logs:PutLogEvents',
                        'mediaconvert:*',
                    ],
                    'Resource': '*'
                },
                {
                    'Effect': 'Allow',
                    'Action': 'iam:PassRole',
                    'Resource': GetAtt(media_convert_role, 'Arn'),
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
        media_convert_role = self.create_media_convert_role()
        self.create_lambda_role(media_convert_role)
        self.create_exports()
