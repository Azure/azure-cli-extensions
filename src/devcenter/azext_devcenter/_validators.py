# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from datetime import datetime
import locale
import re
from azure.cli.core.azclierror import (
    RequiredArgumentMissingError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
)
from azure.cli.core.aaz import has_value


locale.setlocale(locale.LC_ALL, "")


# Control plane
def validate_attached_network_or_dev_box_def(dev_center_name, project_name):
    if has_value(dev_center_name) and has_value(project_name):
        error_message = """Only dev-center (--dev-center --dev-center-name -d). \
or project (--project --project-name) should be set."""
        raise MutuallyExclusiveArgumentError(error_message)
    if not has_value(dev_center_name) and not has_value(project_name):
        error_message = """Either project (--project --project-name) \
or dev center (--dev-center --dev-center-name -d) should be set."""
        raise RequiredArgumentMissingError(error_message)


def validate_repo_git(ado_git, git_hub):
    if not has_value(ado_git) and not has_value(git_hub):
        error_message = """Either an AdoGit (--ado-git) \
or GitHub source control definition (--git-hub) should be set."""
        raise RequiredArgumentMissingError(error_message)


def validate_pool_create(
    virtual_network_type, network_connection_name, managed_virtual_network_regions
):
    if (
        not has_value(managed_virtual_network_regions)
        and virtual_network_type == "Managed"
    ):
        error_message = """When virtual-network-type is set to "Managed", \
managed virtual network regions (--managed-virtual-network-regions) should be set."""
        raise RequiredArgumentMissingError(error_message)
    if not has_value(network_connection_name) and (
        virtual_network_type == "Unmanaged" or not has_value(virtual_network_type)
    ):
        error_message = """When virtual-network-type is not used or set to "Unmanaged", \
a network connection name (--network-connection) should be set."""
        raise RequiredArgumentMissingError(error_message)
    if has_value(managed_virtual_network_regions) and (
        virtual_network_type == "Unmanaged" or not has_value(virtual_network_type)
    ):
        error_message = """When virtual-network-type is not used or set to "Unmanaged", \
managed virtual network regions (--managed-virtual-network-regions) should not be set."""
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
        error_message = """Only dev-center (--dev-center --dev-center-name -d) \
or endpoint (--endpoint) parameter should be set."""
        raise MutuallyExclusiveArgumentError(error_message)
    if endpoint is not None:
        check_valid_uri = re.match(
            r"(https)://.+.*\.(devcenter.azure-test.net|devcenter.azure.com)[/]?$",
            endpoint,
        )
        if check_valid_uri is None:
            raise InvalidArgumentValueError(
                f"""The endpoint '{endpoint}' is invalid. Please ensure that the \
endpoint starts with 'https' and is properly formatted. Run \
'az devcenter admin project show' to view the endpoint of a specific project. \
Run 'az devcenter admin project list' to view the \
list of available projects. Contact your admin for further assistance."""
            )
    if endpoint is None and dev_center is None:
        error_message = """Either an endpoint (--endpoint) \
or dev-center (--dev-center --dev-center-name -d) should be set."""
        raise RequiredArgumentMissingError(error_message)


def validate_env_name_already_exists(env_iterator, name, user_id, project):
    for env in env_iterator:
        if env["name"].casefold() == name.casefold():
            if user_id == "me":
                user_id = env["user"]
            error_message = f"""An environment with the name '{name}' \
already exists for the user-id '{user_id}' in this project '{project}'."""
            raise InvalidArgumentValueError(error_message)


def is_iso8601(namespace):
    if namespace.expiration_date is None:
        return
    try:
        datetime.fromisoformat(namespace.expiration_date)
        return
    except ValueError as exception:
        error_message = f"""The expiration date is invalid '{namespace.expiration_date}' \
it must be in ISO 8601 format. For example: 2023-12-30T22:35:00+00:00"""
        raise InvalidArgumentValueError(error_message) from exception
