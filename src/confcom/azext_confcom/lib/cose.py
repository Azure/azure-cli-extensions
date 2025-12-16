# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import hashlib
import platform
import re
import requests
import subprocess

from typing import Iterable
from pathlib import Path

from azext_confcom.lib.paths import get_binaries_dir


_binaries_dir = get_binaries_dir()
_cosesign1_binaries = {
    "Linux": {
        "path": _binaries_dir / "sign1util",
        "url": "https://github.com/microsoft/cosesign1go/releases/download/v1.4.0/sign1util",
        "sha256": "526b54aeb6293fc160e8fa1f81be6857300aba9641d45955f402f8b082a4d4a5",
    },
    "Windows": {
        "path": _binaries_dir / "sign1util.exe",
        "url": "https://github.com/microsoft/cosesign1go/releases/download/v1.4.0/sign1util.exe",
        "sha256": "f33cccf2b1bb8c3a495c730984b47d0f0715678981dbfe712248a2452dd53303",
    },
}


def cose_get():
    for binary_info in _cosesign1_binaries.values():
        cosesign1_fetch_resp = requests.get(binary_info["url"], verify=True)
        cosesign1_fetch_resp.raise_for_status()

        assert hashlib.sha256(cosesign1_fetch_resp.content).hexdigest() == binary_info["sha256"]

        with open(binary_info["path"], "wb") as f:
            f.write(cosesign1_fetch_resp.content)


def cose_run(args: Iterable[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [_cosesign1_binaries[platform.system()]["path"], *args],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )


def cose_print(file_path: Path):
    return cose_run([
        "print",
        "--in", file_path.as_posix(),
    ]).stdout.strip()


def cose_get_properties(file_path: Path):
    cose_print_output = cose_print(file_path)
    return {
        "iss": re.search(r"^iss:\s*(.*)$", cose_print_output, re.MULTILINE).group(1),
        "feed": re.search(r"^feed:[ \t]*([^\r\n]*)", cose_print_output, re.MULTILINE).group(1),
        "payload": re.search(r"^payload:\s*(.*)", cose_print_output, re.MULTILINE | re.DOTALL).group(1),
    }
