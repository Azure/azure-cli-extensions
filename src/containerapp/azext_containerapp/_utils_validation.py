# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re

from azure.cli.core.azclierror import ValidationError

_VALID_IMAGE_NAME_RE = re.compile(r'^[a-zA-Z0-9._:/@-]+$')


def validate_image_name(name):
    """Validate that a container image name does not contain shell metacharacters."""
    if not name or not _VALID_IMAGE_NAME_RE.match(name):
        raise ValidationError(
            f"Invalid container image name: {name!r}. "
            "Image names may only contain alphanumeric characters, '.', '_', ':', '/', '@', and '-'."
        )
