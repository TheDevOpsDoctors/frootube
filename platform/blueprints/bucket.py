from stacker.blueprints.base import Blueprint
from stacker.blueprints.variables.types import (
    TroposphereType,
    CFNString,
)
from troposphere import (
    s3,
    Ref,
    Tags,
)

class Bucket(Blueprint):
    VARIABLES = {
        'BucketName': {
            'type': CFNString,
            'description': 'S3 bucket Name',
        },
        'tags': {
            'type': dict,
        }
    }
    def create_template(self):
        t = self.template
        variables = self.get_variables()
        t.add_resource(s3.Bucket('Bucket',
                                 BucketName=Ref('BucketName'),
                                 Tags=Tags(variables['tags'])))
