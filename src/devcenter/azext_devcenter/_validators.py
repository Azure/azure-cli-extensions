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
from knack.log import get_logger

logger = get_logger(__name__)


# Control plane
def validate_attached_network_or_dev_box_def(dev_center_name, project_name):
    if has_value(dev_center_name) and has_value(project_name):
        warning_message = """Both the dev-center and project parameters were provided. \
Only the dev-center parameter will be used and the command will only reference the child \
resource(s) under the dev center. To reference the child resource(s) under the project, \
remove the dev-center parameter and set the project parameter. """
        logger.warning(warning_message)
    if not has_value(dev_center_name) and not has_value(project_name):
        error_message = """Either project (--project --project-name) \
or dev center (--dev-center --dev-center-name -d) should be set."""
        raise RequiredArgumentMissingError(error_message)


def validate_repo_git(ado_git, git_hub):
    if not has_value(ado_git) and not has_value(git_hub):
        error_message = """Either an AdoGit (--ado-git) \
or GitHub source control definition (--git-hub) should be set."""
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


def validate_endpoint(endpoint, dev_center):
    if endpoint is not None and dev_center is not None:
        logger.warning(
            "Both the endpoint and dev-center parameters were provided. Only the endpoint parameter will be used."
        )
    if endpoint is not None:
        check_valid_uri = re.match(
            r"(https)://.+.*\.(devcenter.azure-test.net|devcenter.azure.com)$", endpoint
        )
        if check_valid_uri is None:
            raise InvalidArgumentValueError("The endpoint is invalid.")
    if endpoint is None and dev_center is None:
        error_message = """Either an endpoint (--endpoint) \
or dev-center (--dev-center) should be set."""
        raise RequiredArgumentMissingError(error_message)
