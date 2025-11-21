# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import platform
import requests
import hashlib
import json
import os
import subprocess

from typing import Iterable
from pathlib import Path
from azext_confcom.lib.paths import get_binaries_dir


_binaries_dir = get_binaries_dir()
_opa_binaries = {
    "Linux": {
        "path": _binaries_dir / "opa",
        "url": "https://github.com/open-policy-agent/opa/releases/download/v1.10.1/opa_linux_amd64",
        "sha256": "fe8e191d44fec33db2a3d0ca788b9f83f866d980c5371063620c3c6822792877",
    },
    "Windows": {
        "path": _binaries_dir / "opa.exe",
        "url": "https://github.com/open-policy-agent/opa/releases/download/v1.10.1/opa_windows_amd64.exe",
        "sha256": "4c932053350eabca47681208924046fbf3ad9de922d6853fb12cddf59aef15ce",
    },
}


def opa_get():

    for binary_info in _opa_binaries.values():
        opa_fetch_resp = requests.get(binary_info["url"], verify=True)
        opa_fetch_resp.raise_for_status()

        assert hashlib.sha256(opa_fetch_resp.content).hexdigest() == binary_info["sha256"]

        with open(binary_info["path"], "wb") as f:
            f.write(opa_fetch_resp.content)

        os.chmod(binary_info["path"], 0o755)


def opa_run(args: Iterable[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [_opa_binaries[platform.system()]["path"], *args],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )


def opa_eval(data_path: Path, query: str):
    return json.loads(opa_run([
        "eval",
        "--format", "json",
        "--data", str(data_path),
        query,
    ]).stdout.strip())
