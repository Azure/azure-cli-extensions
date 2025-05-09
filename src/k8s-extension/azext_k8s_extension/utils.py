# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from typing import Tuple
from urllib.parse import urlparse
from . import consts
from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError


def get_cluster_rp_api_version(cluster_type, cluster_rp=None) -> Tuple[str, str]:
    if cluster_type.lower() == consts.PROVISIONED_CLUSTER_TYPE:
        if cluster_rp is None or cluster_rp.strip() == "":
            raise RequiredArgumentMissingError(
                "Error! Cluster Resource Provider value is required for Cluster Type '{}'".format(cluster_type)
            )
        if cluster_rp.lower() == consts.HYBRIDCONTAINERSERVICE_RP:
            return (
                consts.HYBRIDCONTAINERSERVICE_RP,
                consts.HYBRIDCONTAINERSERVICE_API_VERSION,
            )
        raise InvalidArgumentValueError(
            "Error! Cluster type '{}' and Cluster Resource Provider '{}' combination is not supported".format(cluster_type, cluster_rp)
        )
    if cluster_type.lower() == consts.CONNECTED_CLUSTER_TYPE:
        return consts.CONNECTED_CLUSTER_RP, consts.CONNECTED_CLUSTER_API_VERSION
    if cluster_type.lower() == consts.APPLIANCE_TYPE:
        return consts.APPLIANCE_RP, consts.APPLIANCE_API_VERSION
    if (
        cluster_type.lower() == ""
        or cluster_type.lower() == consts.MANAGED_CLUSTER_TYPE
    ):
        return consts.MANAGED_CLUSTER_RP, consts.MANAGED_CLUSTER_API_VERSION
    raise InvalidArgumentValueError(
        "Error! Cluster type '{}' is not supported".format(cluster_type)
    )


def read_config_settings_file(file_path):
    try:
        with open(file_path, "r") as f:
            settings = json.load(f)
            if len(settings) == 0:
                raise Exception("File {} is empty".format(file_path))
            return settings
    except ValueError as ex:
        raise Exception("File {} is not a valid JSON file".format(file_path)) from ex


def is_dogfood_cluster(cmd):
    return (
        urlparse(cmd.cli_ctx.cloud.endpoints.resource_manager).hostname
        == consts.DF_RM_HOSTNAME
    )


def is_skip_prerequisites_specified(configuration_settings):
    # Determine if provisioning to prerequisites should be skipped by a configuration setting named skipPrerequisites.
    SKIP_PREQUISITES = 'skipPrerequisites'

    has_skip_prerequisites_set = False

    if SKIP_PREQUISITES in configuration_settings:
        skip_prerequisites_configuration_setting = configuration_settings[SKIP_PREQUISITES]
        if (isinstance(skip_prerequisites_configuration_setting, str) and str(skip_prerequisites_configuration_setting).lower() == "true") or (isinstance(skip_prerequisites_configuration_setting, bool) and skip_prerequisites_configuration_setting):
            has_skip_prerequisites_set = True

    return has_skip_prerequisites_set
