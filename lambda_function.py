import asyncio
import sys
import traceback

import app
import log


def lambda_handler(event, context):
    """Lambda handler function to trigger the main function."""
    try:
       asyncio.run(app.main())
    except Exception as e:
        log.log("lambda_handler", f"Error: {e}")
        tb_str = traceback.format_exception(*sys.exc_info())
        traceback_str = "".join(tb_str)
        log.log("lambda_handler", f"{traceback_str}")

