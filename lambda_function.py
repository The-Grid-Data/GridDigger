import asyncio
from http import HTTPStatus
import app
import json


def lambda_handler(event, context):
    """Lambda handler function."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.handle_update(event, context))

    return {
        "statusCode": HTTPStatus.OK,
        "body": json.dumps({"message": "Update processed"}),
    }
