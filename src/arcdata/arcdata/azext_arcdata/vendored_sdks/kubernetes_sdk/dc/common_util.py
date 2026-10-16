# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import json
import re
from azure.cli.core.azclierror import ArgumentUsageError
from azext_arcdata.core.util import display
from azext_arcdata.vendored_sdks.kubernetes_sdk.dc import constants as dc_constants
from azext_arcdata.vendored_sdks.kubernetes_sdk.dc.constants import (
    CONNECTIVITY_TYPES,
    GUID_REGEX,
    INFRASTRUCTURE_CR_ALLOWED_VALUES,
    INFRASTRUCTURE_CR_INVALID_VALUE_MSG,
    INFRASTRUCTURE_PARAMETER_ALLOWED_VALUES,
    INFRASTRUCTURE_PARAMETER_INVALID_VALUE_MSG,
    SUPPORTED_EUAP_REGIONS,
    SUPPORTED_REGIONS,
)

################################################################################
# -- Helper functions to validate data controller parameters
################################################################################


def validate_dc_create_params(
    name,
    namespace,
    subscription,
    location,
    resource_group,
    # connectivity_mode,
    infrastructure,
    # profile_name=None,
    # path=None,
    logs_ui_public_key_file,
    logs_ui_private_key_file,
    metrics_ui_public_key_file,
    metrics_ui_private_key_file,
):
    """
    Validates the supplied arguments for 'arc dc create' command
    """
    # _validate_config(profile_name, path)
    _validate_namespace(namespace)
    _validate_data_controller_name(name)
    _validate_azure_subscription_id(subscription)
    # _validate_connectivity_type(connectivity_mode)
    _validate_resource_group(resource_group)
    _validate_azure_resource_location(location)
    _validate_infrastructure_parameter(infrastructure)
    _validate_monitoring_certificate_params(
        logs_ui_public_key_file,
        logs_ui_private_key_file,
        metrics_ui_public_key_file,
        metrics_ui_private_key_file,
    )


def _validate_azure_subscription_id(sid):
    msg = "Please input a valid Azure subscription ID."
    if not sid:
        raise ValueError(msg)
    if sid and not re.match(GUID_REGEX, sid):
        msg = "{} is invalid. ".format(sid) + msg
        raise ValueError(msg)


def _validate_azure_resource_location(loc):
    msg = (
        "Please input a valid Azure location. Supported regions are: "
        + ", ".join(SUPPORTED_REGIONS)
        + "."
    )
    # If location was not provided or an invalid location was provided
    if not loc or not (
        loc.lower() in SUPPORTED_REGIONS
        or loc.lower() in SUPPORTED_EUAP_REGIONS
    ):
        raise ValueError(msg)


def _validate_infrastructure_parameter(infrastructure):
    """
    Validate the infrastructure parameter. A valid parameter is either None,
    or one of dc_constants.INFRASTRUCTURE_PARAMETER_ALLOWED_VALUES
    """
    msg = INFRASTRUCTURE_PARAMETER_INVALID_VALUE_MSG

    if infrastructure is None:
        return

    if infrastructure not in INFRASTRUCTURE_PARAMETER_ALLOWED_VALUES:
        raise ValueError(msg)


def validate_infrastructure_value(infrastructure):
    """
    Validate the infrastructure CR value. A valid value is one of
    dc_constants.INFRASTRUCTURE_CR_ALLOWED_VALUES.
    """

    msg = (
        "infrastructure set to '{infrastructure}'. "
        "{INFRASTRUCTURE_CR_INVALID_VALUE_MSG}".format(
            infrastructure=infrastructure,
            INFRASTRUCTURE_CR_INVALID_VALUE_MSG=INFRASTRUCTURE_CR_INVALID_VALUE_MSG,
        )
    )

    if not infrastructure:
        raise ValueError(INFRASTRUCTURE_CR_INVALID_VALUE_MSG)

    if infrastructure not in INFRASTRUCTURE_CR_ALLOWED_VALUES:
        raise ValueError(msg)


def _validate_resource_group(rg):
    msg = "Please input a valid Azure resource group"
    if not rg:
        raise ValueError(msg)


def _validate_namespace(ns):
    msg = "Please enter a valid name for the Kubernetes namespace"
    if not ns:
        raise ValueError(msg)


def _validate_connectivity_type(cn):
    msg = "Please enter a valid connectivity type. Options are: {}".format(
        CONNECTIVITY_TYPES
    )
    # If conn_type was not provided or an invalid conn_type was provided
    if not cn or cn.lower() not in CONNECTIVITY_TYPES:
        raise ValueError(msg)


def _validate_data_controller_name(name):
    msg = "Please enter a valid name for the Data Controller"
    if not name:
        raise ValueError(msg)


def _validate_monitoring_certificate_params(
    logs_ui_public_key_file=None,
    logs_ui_private_key_file=None,
    metrics_ui_public_key_file=None,
    metrics_ui_private_key_file=None,
):
    if bool(logs_ui_public_key_file) ^ bool(logs_ui_private_key_file):
        if logs_ui_public_key_file:
            raise ArgumentUsageError(
                "Logsui certificate private key file path must be provided "
                "when public key file is provided."
            )

        if logs_ui_private_key_file:
            raise ArgumentUsageError(
                "Logsui certificate public key file path must be provided "
                "when private key file is provided."
            )

    if bool(metrics_ui_public_key_file) ^ bool(metrics_ui_private_key_file):
        if metrics_ui_public_key_file:
            raise ArgumentUsageError(
                "Metricsui certificate private key file path must be provided "
                "when public key file is provided."
            )

        if metrics_ui_private_key_file:
            raise ArgumentUsageError(
                "Metricsui certificate public key file path must be provided "
                "when private key file is provided."
            )


"""
def _validate_config(profile_name=None, path=None):
    # -- Error if both profile_name and config_profile are specified --
    if profile_name and path:
        raise ValueError(
            "Cannot specify both 'profile-name' and 'path'. "
            "Please specify only one."
        )
"""

################################################################################
# File I/O
################################################################################


def get_valid_dc_infrastructures():
    """
    Get the valid sql license types
    """
    return INFRASTRUCTURE_PARAMETER_ALLOWED_VALUES


def get_kubernetes_infra(nodes):
    """
    Get the kubernetes infrastructure.
    """
    try:
        # nodes = client.apis.kubernetes.list_node()
        if nodes.items:
            provider_id = str(nodes.items[0].spec.provider_id)
            infra = provider_id.split(":")[0]
            if infra == "k3s" or infra == "kind":
                return dc_constants.INFRASTRUCTURE_OTHER
            if infra == "azure":
                return dc_constants.INFRASTRUCTURE_AZURE
            if infra == "gce":
                return dc_constants.INFRASTRUCTURE_GCP
            if infra == "aws":
                return dc_constants.INFRASTRUCTURE_AWS
            if infra == "moc":
                return dc_constants.INFRASTRUCTURE_OTHER
    except Exception as e:
        raise ValueError(
            "Unable to determine Kubernetes infrastructure. Unexpected error."
        ) from e

    raise ValueError(
        "Unable to determine Kubernetes infrastructure. Node's provider_id "
        "unknown."
    )


def write_file(file_path, data, export_type, data_timestamp=None):
    result = {
        "exportType": export_type,
        "dataTimestamp": data_timestamp,
        "data": data,
    }
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(result, json_file, indent=4)

    output_type = export_type
    display(
        "\t\t{} are exported to {}.".format(output_type.capitalize(), file_path)
    )


def write_output_file(file_path, content):
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(content, json_file, indent=4)
