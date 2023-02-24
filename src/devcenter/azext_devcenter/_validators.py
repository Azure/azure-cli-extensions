# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import re
from azure.cli.core.azclierror import (
    RequiredArgumentMissingError,
    InvalidArgumentValueError,
)


def validate_dev_box_list(namespace):
    if namespace.project_name is not None and namespace.user_id is None:
        raise RequiredArgumentMissingError(
            "--user-id is required when using --project-name/--project."
        )


def validate_time(namespace):
    regex = "([01]?[0-9]|2[0-3]):[0-5][0-9]"
    pattern = re.compile(regex)
    validation = pattern.match(namespace.delay_time)
    if validation is None:
        raise InvalidArgumentValueError("--delay-time should be in the format HH:MM")
