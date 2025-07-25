# This module is main to spawn an http server.
#
# In this module, we connect all elements together, in order to make the
# server runnable.
import logging
import sys
import uvicorn

from lumapps_poc.infrastructure import http_server


def serve() -> None:
    # Configure logging
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    app = http_server.create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    serve()