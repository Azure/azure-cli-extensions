# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import subprocess
import sys
import tempfile
from typing import Optional

from azext_confcom.errors import eprint


def oras_push(
    signed_fragment_path: str,
    manifest_tag: str,
) -> None:
    subprocess.run(
        [
            "oras",
            "push",
            "--artifact-type", "application/x-ms-ccepolicy-frag",
            manifest_tag,
            os.path.relpath(signed_fragment_path, start=os.getcwd()),
        ],
        check=True,
        timeout=120,
    )


def fragment_push(
    signed_fragment: Optional[str],
    manifest_tag: str,
) -> None:

    if signed_fragment is None:
        with tempfile.NamedTemporaryFile(delete=True) as temp_signed_fragment:
            temp_signed_fragment.write(sys.stdin.buffer.read())
            temp_signed_fragment.flush()
            oras_push(
                signed_fragment_path=temp_signed_fragment.name,
                manifest_tag=manifest_tag,
            )
    else:
        if not os.path.isfile(signed_fragment):
            eprint(f"Signed fragment file not found: {signed_fragment}")
        oras_push(
            signed_fragment_path=signed_fragment,
            manifest_tag=manifest_tag,
        )
