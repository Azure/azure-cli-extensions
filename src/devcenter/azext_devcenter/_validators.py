# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import re
from azure.cli.core.azclierror import (
    RequiredArgumentMissingError,
    InvalidArgumentValueError,
)
from azure.cli.core.aaz import has_value


# Control plane
def validate_attached_network_or_dev_box_def(dev_center_name, project_name):
    if not has_value(dev_center_name) and not has_value(project_name):
        error_message = """Either project (--project --project-name) \
or dev center (--dev-center --dev-center-name -d) should be set."""
        raise RequiredArgumentMissingError(error_message)


# Data plane


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
