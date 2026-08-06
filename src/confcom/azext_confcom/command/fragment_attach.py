# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import subprocess
import sys
import tempfile
from typing import Optional

from azext_confcom import oras_proxy
from azext_confcom.errors import eprint


def oras_attach(
    signed_fragment_path: str,
    manifest_tag: str,
    platform: Optional[str] = None,
) -> None:
    cmd = [
        "oras",
        "attach",
        "--artifact-type", "application/x-ms-ccepolicy-frag",
    ]

    if platform:
        cmd.extend(["--platform", platform])
    else:
        # Try to detect platform from the image itself
        image_platforms = oras_proxy.get_image_platforms(manifest_tag)
        if len(image_platforms) > 1:
            platforms_str = ", ".join(image_platforms)
            eprint(
                f"Multi-platform image detected ({platforms_str}). "
                "Please specify the platform to attach the fragment to using the --platform parameter.",
                exit_code=1
            )
        elif len(image_platforms) == 1:
            cmd.extend(["--platform", image_platforms[0]])
        else:
            # Platform detection failed (empty list)
            eprint(
                f"Failed to detect platform of image {manifest_tag}. Does it exist in the registry?",
                exit_code=1
            )

    cmd.extend([
        manifest_tag,
        os.path.relpath(signed_fragment_path, start=os.getcwd()) + ":application/cose-x509+rego",
    ])

    subprocess.run(
        cmd,
        check=True,
        timeout=120,
    )


def fragment_attach(
    signed_fragment: Optional[str],
    manifest_tag: str,
    platform: Optional[str] = None,
) -> None:

    if signed_fragment is None:
        with tempfile.NamedTemporaryFile(delete=True) as temp_signed_fragment:
            temp_signed_fragment.write(sys.stdin.buffer.read())
            temp_signed_fragment.flush()
            oras_attach(
                signed_fragment_path=temp_signed_fragment.name,
                manifest_tag=manifest_tag,
                platform=platform,
            )
    else:
        if not os.path.isfile(signed_fragment):
            eprint(f"Signed fragment file not found: {signed_fragment}")
        oras_attach(
            signed_fragment_path=signed_fragment,
            manifest_tag=manifest_tag,
            platform=platform,
        )
