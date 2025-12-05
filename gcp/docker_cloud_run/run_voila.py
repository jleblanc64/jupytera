import os
import sys
from pathlib import Path

from ipystream.voila.patch_voila import POOL_SIZE
from voila.app import Voila
from voila.static_file_handler import AllowListFileHandler

def create_ipynb(path: str) -> Path:
    content = """{"cells": [{
      "cell_type": "code", "execution_count": null, "id": "run-cell", "metadata": {},"outputs": [],
      "source": [
        "from python.notebook import run\\n",
        "run()"
      ]}],
      "metadata": {}, "nbformat": 4, "nbformat_minor": 5}"""

    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return file_path

def run():
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

    def patched_get_absolute_path(self, root, path):
        return super(AllowListFileHandler, self).get_absolute_path(root, path)

    AllowListFileHandler.get_absolute_path = patched_get_absolute_path
    voila_app = Voila()
    voila_app.initialize()
    voila_app.start()

run()
