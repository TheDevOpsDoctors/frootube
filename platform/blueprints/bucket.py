from __future__ import print_function

from stacker.blueprints.base import Blueprint
from stacker.blueprints.variables.types import (
    CFNString,
)
from troposphere import (
    s3,
    Ref,
    Tags,
    Output,
    Export,
    Sub,
    sns
)

from blueprints.exporter import Exporter


class Bucket(Blueprint, Exporter):
    VARIABLES = {
        'BucketName': {
            'type': CFNString,
            'description': 'S3 bucket Name',
        },
        'public': {
            'type': bool,
            'default': False,
        },
        'public_post': {
            'type': bool,
            'default': False,
        },
        'tags': {
            'type': dict,
        },
        'exports': {
            'type': dict,
            'default': {},
        }
    }

    def create_bucket(self, t, more_props=None):
        variables = self.get_variables()
        bucket_properties = {
            'BucketName': Ref('BucketName'),
            'Tags': Tags(variables['tags']),
        }
        if more_props is not None:
            bucket_properties.update(more_props)

        if variables['public']:
            bucket_properties['CorsConfiguration'] = {
                'CorsRules': [
                    {
                        'AllowedHeaders': ['Authorization', 'Content-*', 'Host'],
                        'AllowedMethods': ['GET'],
                        'AllowedOrigins': ['*'],
                        'MaxAge': 3000,
                    }
                ]
            }

        if variables['public_post']:
            bucket_properties['CorsConfiguration'] = {
                'CorsRules': [
                    {
                        'AllowedHeaders': ['Authorization', 'Content-*', 'Host'],
                        'AllowedMethods': ['POST'],
                        'AllowedOrigins': ['*'],
                        'MaxAge': 3000,
                    }
                ]
            }

        bucket = s3.Bucket.from_dict('Bucket', bucket_properties)
        t.add_resource(bucket)

        if variables['public']:
            policy_document = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": [
                            "s3:GetObject"
                        ],
                        "Effect": "Allow",
                        "Resource": Sub("arn:aws:s3:::${BucketName}/*"),
                        "Principal": '*',
                    }
                ]
            }

            bucket_policy = s3.BucketPolicy('BucketPolicy',
                                            Bucket=Ref('BucketName'),
                                            PolicyDocument=policy_document)
            t.add_resource(bucket_policy)

        return bucket

    def create_template(self):
        t = self.template
        self.create_bucket(t)
        self.create_exports()


class BucketWithSns(Bucket):
    def defined_variables(self):
        variables = super(BucketWithSns, self).defined_variables()

        additional = {
            'InternalBucketName': {
                'type': CFNString,
                'description': 'Internal bucket name'
            },
        }

        variables.update(additional)
        return variables

    def create_template(self):
        t = self.template

        topic_name = Sub("${InternalBucketName}CreateObjectTopic")
        topic = sns.Topic('Topic',
                          DisplayName=topic_name)
        t.add_resource(topic)

        policy = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Effect': 'Allow',
                    'Principal': {'AWS': '*'},
                    'Action': 'sns:Publish',
                    'Resource': Ref(topic),
                    'Condition': {
                        'ArnLike': {
                            'aws:SourceArn': Sub('arn:aws:s3:::${BucketName}')
                        }
                    }
                }
            ]
        }
        t.add_resource(sns.TopicPolicy('TopicPolicy',
                                       PolicyDocument=policy,
                                       Topics=[Ref(topic)]))

        more_bucket_props = {
            'NotificationConfiguration': {
                'TopicConfigurations': [
                    {'Event': 's3:ObjectCreated:*', 'Topic': Ref(topic)}
                ]
            },
        }

        bucket = self.create_bucket(t, more_props=more_bucket_props)
        bucket.DependsOn = ['Topic', 'TopicPolicy']

        super(BucketWithSns, self).create_exports()

        t.add_output(Output('CreateObjectTopicArn',
                            Value=Ref(topic), Export=Export(Sub('${InternalBucketName}CreateObjectTopicArn'))))
