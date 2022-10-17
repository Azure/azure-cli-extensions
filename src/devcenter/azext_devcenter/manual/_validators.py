# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.azclierror import RequiredArgumentMissingError


def validate_attached_network_or_dev_box_def(namespace):
    if not namespace.project_name and not namespace.dev_center_name:
        error_message = """Either project (--project --project-name) \
or dev center (--dev-center --dev-center-name -dc) should be set."""
        raise RequiredArgumentMissingError(error_message)


def validate_dev_box_list(namespace):
    if namespace.project_name is not None and namespace.user_id is None:
        raise RequiredArgumentMissingError(
            "--user-id is required when using --project-name/--project."
        )
