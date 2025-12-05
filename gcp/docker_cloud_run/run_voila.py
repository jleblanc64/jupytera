import logging
import os
import sys

from ipystream.voila import patched_generator, auth_wall_limit, patch_voila
from ipystream.voila.patch_voila import POOL_SIZE
from ipystream.voila.utils import create_ipynb


def patch():
    # patch voila app
    from voila.app import Voila
    from voila.static_file_handler import AllowListFileHandler

    def patched_get_absolute_path(self, root, path):
        return super(AllowListFileHandler, self).get_absolute_path(root, path)

    AllowListFileHandler.get_absolute_path = patched_get_absolute_path
    return Voila()

def run(disable_logging):
    # patched_generator.patch_voila_get_generator(enforce_PARAM_KEY_TOKEN=False)
    # auth_wall_limit.patch(log_user_fun=None, token_to_user_fun=None)

    NOTEBOOK = "jupyter.ipynb"

    os.environ["VOILA_APP"] = "1"
    extra_args = [
        "--port=8866",
        "--no-browser",
        "--Voila.ip=0.0.0.0",
        "--base_url=/",
        "--ServerApp.log_level=DEBUG",
        "--show_tracebacks=True",
        "--preheat_kernel=True",
        f"--pool_size={POOL_SIZE}",
    ]

    create_ipynb(NOTEBOOK)
    sys.argv = ["voila", NOTEBOOK] + extra_args

    # start Voila
    voila_app = patch()
    voila_app.initialize()
    print("VOILA: http://localhost:8866")

    # if disable_logging:
    #     logging.disable(logging.CRITICAL)
    voila_app.start()

run(disable_logging=False)
