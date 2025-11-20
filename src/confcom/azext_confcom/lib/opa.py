# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
from typing import Iterable

import requests

from azext_confcom.lib.binaries import get_binaries_dir

_opa_path = os.path.abspath(os.path.join(get_binaries_dir(), "opa"))
_opa_url = {
    "Linux": "https://github.com/open-policy-agent/opa/releases/download/v1.10.1/opa_linux_amd64",
    "Windows": "https://github.com/open-policy-agent/opa/releases/download/v1.10.1/opa_windows_amd64.exe",
}
_expected_sha256 = {
    "Linux": "fe8e191d44fec33db2a3d0ca788b9f83f866d980c5371063620c3c6822792877",
    "Windows": "4c932053350eabca47681208924046fbf3ad9de922d6853fb12cddf59aef15ce",
}


def opa_get():

    if not all(platform.system() in mapping for mapping in [_opa_url, _expected_sha256]):
        raise RuntimeError(f"OPA is not supported on platform: {platform.system()}")

    opa_fetch_resp = requests.get(_opa_url[platform.system()], verify=True)
    opa_fetch_resp.raise_for_status()

    assert hashlib.sha256(opa_fetch_resp.content).hexdigest() == _expected_sha256[platform.system()]

    with open(_opa_path, "wb") as f:
        f.write(opa_fetch_resp.content)

    os.chmod(_opa_path, 0o755)
    return _opa_path


def opa_run(args: Iterable[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [_opa_path, *args],
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
