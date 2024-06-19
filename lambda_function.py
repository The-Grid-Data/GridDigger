import asyncio

import app


def lambda_handler(event, context):
    """Lambda handler function to trigger the main function."""
    asyncio.run(app.main())