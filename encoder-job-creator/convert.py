#!/usr/bin/env python3

import boto3
import json
import os
import uuid


def handler(event, _context):
    if os.environ.get('DEBUG') == 'true':
        print(json.dumps(event))

    event = json.loads(event['Records'][0]['Sns']['Message'])

    if os.environ.get('DEBUG') == 'true':
        print(json.dumps(event))

    asset_id = str(uuid.uuid4())
    source_s3_bucket = event['Records'][0]['s3']['bucket']['name']
    source_s3_key = event['Records'][0]['s3']['object']['key']
    source_s3 = 's3://' + source_s3_bucket + '/' + source_s3_key
    source_s3_basename = os.path.splitext(os.path.basename(source_s3))[0]
    destination_s3 = 's3://' + os.environ['DESTINATION_BUCKET']
    media_convert_role = os.environ['MEDIA_CONVERT_ROLE']
    region = os.environ['AWS_DEFAULT_REGION']
    status_code = 200
    body = {}

    # Use MediaConvert SDK UserMetadata to tag jobs with the assetID
    # Events from MediaConvert will have the assetID in UserMedata
    job_metadata = {'assetID': asset_id}

    try:
        # Job settings are in the lambda zip file in the current working directory
        with open('job.json') as json_data:
            job_settings = json.load(json_data)
            print(job_settings)

        # get the account-specific mediaconvert endpoint for this region
        mc_client = boto3.client('mediaconvert', region_name=region)
        endpoints = mc_client.describe_endpoints()

        # add the account-specific endpoint to the client session
        client = boto3.client('mediaconvert', region_name=region, endpoint_url=endpoints['Endpoints'][0]['Url'],
                              verify=False)

        # Update the job settings with the source video from the S3 event and destination
        # paths for converted videos
        job_settings['Inputs'][0]['FileInput'] = source_s3

        s3_key_hls = 'assets/' + asset_id + '/HLS/' + source_s3_basename
        job_settings['OutputGroups'][0]['OutputGroupSettings']['HlsGroupSettings']['Destination'] \
            = destination_s3 + '/' + s3_key_hls

        s3_key_watermark = 'assets/' + asset_id + '/MP4/' + source_s3_basename
        job_settings['OutputGroups'][1]['OutputGroupSettings']['FileGroupSettings']['Destination'] \
            = destination_s3 + '/' + s3_key_watermark

        s3_key_thumbnails = 'assets/' + asset_id + '/Thumbnails/' + source_s3_basename
        job_settings['OutputGroups'][2]['OutputGroupSettings']['FileGroupSettings']['Destination'] \
            = destination_s3 + '/' + s3_key_thumbnails

        print('jobSettings:')
        print(json.dumps(job_settings))

        # Convert the video using AWS Elemental MediaConvert
        job = client.create_job(Role=media_convert_role, UserMetadata=job_metadata, Settings=job_settings)
        print(json.dumps(job, default=str))

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
