import json


def handler(event, context):
    body = {
        "message": "upload_link_generator.handler",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
