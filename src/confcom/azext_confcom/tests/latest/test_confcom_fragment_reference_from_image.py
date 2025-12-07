# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import subprocess

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from azext_confcom.command.fragment_references_from_image import fragment_references_from_image


CONFCOM_DIR = Path(__file__).parent.parent.parent.parent
SAMPLES_DIR = CONFCOM_DIR / "samples"


def test_fragment_reference_from_image(docker_image):

    image_ref, spec_file_path = docker_image
    signed_fragment_path = SAMPLES_DIR / "fragments" / "fragment.rego.cose"

    # Attach a signed fragment to the image
    subprocess.run(
        [
            "oras",
            "attach",
            "--artifact-type",
            "application/x-ms-ccepolicy-frag",
            image_ref,
            signed_fragment_path.name,
        ],
        check=True,
        timeout=120,
        cwd=signed_fragment_path.parent.as_posix(),
    )

    # Generate the fragment reference
    buffer = StringIO()
    with redirect_stdout(buffer):
        fragment_references_from_image(
            image=image_ref,
            minimum_svn=None,
        )

    fragment_references = json.loads(buffer.getvalue())

    # Check the reference looks as expected
    assert fragment_references == [
        {
            'feed': '',
            'includes': ['containers'],
            'issuer': 'did:x509:0:sha256:q2YUkwrO2Ufcq66-CXKS9CA-XZMqFMbFom99GjaR2eI::subject:CN:Contoso',
            'minimum_svn': '1'
        }
    ]
