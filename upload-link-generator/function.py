#!/usr/bin/env python3

import json
import os
import uuid

import boto3


def handler(event, _context):
    if os.environ.get('DEBUG') == 'true':
        print(json.dumps(event))

    media_id = str(uuid.uuid4())
    bucket = os.environ['UPLOAD_BUCKET']
    filename = 'upload/' + media_id
    status_code = 200
    body = {}

    try:
        s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
        url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': bucket,
                'Key': filename,
                'Metadata': {'id': media_id},
            }
        )

        body = {
            'url': url,
            'media_id': media_id,
            'filename': filename
        }

    except Exception as e:
        print('Exception: %s' % e)
        status_code = 500
        raise

    finally:
        return {
            'statusCode': status_code,
            'body': json.dumps(body),
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
        }
