# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import shutil
import json
import subprocess

from pathlib import Path
from typing import Iterable

from azext_confcom.errors import eprint


def oras_run(args: Iterable[str]) -> subprocess.CompletedProcess:

    # Maintain existing behaviour of requiring the user to install ORAS themselves
    if not shutil.which("oras"):
        eprint("ORAS CLI not installed. Please install ORAS CLI: https://oras.land/docs/installation")

    return subprocess.run(
        ["oras", *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def discover(reference: str):
    return json.loads(oras_run([
        "discover",
        "--format",
        "json",
        reference,
    ]).stdout.strip())


def pull(reference: str, destination: Path):
    return oras_run([
        "pull",
        "--output",
        destination.as_posix(),
        reference,
    ])


def get_artifact_references(reference: str):

    def get_references(discover_result):
        if "artifactType" in discover_result:
            yield discover_result["reference"]
        for field in discover_result.values():
            if isinstance(field, list):
                for item in field:
                    yield from get_references(item)
            if isinstance(field, dict):
                yield from get_references(field)

    return list(get_references(discover(reference)))
