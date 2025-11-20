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

_opa_pathh = os.path.abspath(os.path.join(get_binaries_dir(), "opa"))
_expected_sha256 = "fe8e191d44fec33db2a3d0ca788b9f83f866d980c5371063620c3c6822792877"


def opa_get():

    opa_fetch_resp = requests.get(
        f"https://openpolicyagent.org/downloads/latest/opa_{platform.system().lower()}_amd64")
    opa_fetch_resp.raise_for_status()

    assert hashlib.sha256(opa_fetch_resp.content).hexdigest() == _expected_sha256

    with open(_opa_pathh, "wb") as f:
        f.write(opa_fetch_resp.content)

    os.chmod(_opa_pathh, 0o755)
    return _opa_pathh


def opa_run(args: Iterable[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [_opa_pathh, *args],
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
