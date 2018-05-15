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
)


class Bucket(Blueprint):
    VARIABLES = {
        'BucketName': {
            'type': CFNString,
            'description': 'S3 bucket Name',
        },
        'tags': {
            'type': dict,
        },
        'exports': {
            'type': dict,
            'default': {}
        }
    }

    def create_template(self):
        t = self.template
        variables = self.get_variables()
        t.add_resource(s3.Bucket('Bucket',
                                 BucketName=Ref('BucketName'),
                                 Tags=Tags(variables['tags'])))
        for k, v in variables['exports'].iteritems():
            v = v.replace('$\{', '${')
            t.add_output(Output(k, Value=Sub(v), Export=Export(k)))
