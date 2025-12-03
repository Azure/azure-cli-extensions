# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import tempfile

from pathlib import Path

from azext_confcom.lib.images import sanitize_image_reference
from azext_confcom.lib.oras import get_artifact_references, pull


def get_fragments_from_image(image_reference: str):

    for reference in get_artifact_references(image_reference):

        fragment_path = Path(tempfile.gettempdir()) / sanitize_image_reference(reference)
        pull(reference, fragment_path)

        for fragment_file in fragment_path.glob("*.rego.cose"):
            yield fragment_file
