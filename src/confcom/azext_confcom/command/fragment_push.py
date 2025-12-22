# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import subprocess
import tempfile
from typing import BinaryIO


def oras_push(
    signed_fragment: BinaryIO,
    manifest_tag: str,
) -> None:
    subprocess.run(
        [
            "oras",
            "push",
            "--artifact-type", "application/x-ms-ccepolicy-frag",
            manifest_tag,
            os.path.relpath(signed_fragment.name, start=os.getcwd()),
        ],
        check=True,
        timeout=120,
    )


def fragment_push(
    signed_fragment: BinaryIO,
    manifest_tag: str,
) -> None:

    if signed_fragment.name == "<stdin>":
        with tempfile.NamedTemporaryFile(delete=True) as temp_signed_fragment:
            temp_signed_fragment.write(signed_fragment.read())
            temp_signed_fragment.flush()
            oras_push(
                signed_fragment=temp_signed_fragment,
                manifest_tag=manifest_tag,
            )
    else:
        oras_push(
            signed_fragment=signed_fragment,
            manifest_tag=manifest_tag,
        )
