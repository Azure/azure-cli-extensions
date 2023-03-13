# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import json
import re
from datetime import timedelta
from typing import Tuple
from azure.cli.core.azclierror import (
    MutuallyExclusiveArgumentError,
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
)
from . import consts


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


def get_data_from_key_or_file(key, filepath, strip_newline=False):
    if key and filepath:
        raise MutuallyExclusiveArgumentError(
            consts.KEY_AND_FILE_TOGETHER_ERROR, consts.KEY_AND_FILE_TOGETHER_HELP
        )
    data = None
    if filepath:
        data = read_key_file(filepath, strip_newline)
    elif key:
        data = key
    return data


def read_config_settings_file(file_path):
    try:
        with open(file_path, "r") as f:
            settings = json.load(f)
            if len(settings) == 0:
                raise Exception("File {} is empty".format(file_path))
            return settings
    except ValueError as ex:
        raise Exception("File {} is not a valid JSON file".format(file_path)) from ex


def read_key_file(path, strip_newline=False):
    try:
        with open(path, "r") as myfile:  # user passed in filename
            data_list = myfile.readlines()  # keeps newline characters intact
            data_list_len = len(data_list)
            if (data_list_len) <= 0:
                raise Exception("File provided does not contain any data")
            raw_data = "".join(data_list)
        if strip_newline:
            raw_data = raw_data.strip()
        return to_base64(raw_data)
    except Exception as ex:
        raise InvalidArgumentValueError(
            consts.KEY_FILE_READ_ERROR.format(ex), consts.KEY_FILE_READ_HELP
        ) from ex


def parse_dependencies(depends_on):
    if not depends_on:
        return None
    depends_on = depends_on.strip()
    if depends_on[0] == "[":
        depends_on = depends_on[1:-1]
    return depends_on.split(",")


def parse_duration(duration):
    if not duration:
        return duration
    regex = re.compile(r"((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?")
    parts = regex.match(duration)
    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)
    return int(timedelta(**time_params).total_seconds())


def format_duration(seconds):
    if seconds is None:
        return None
    seconds = int(seconds)
    hours = seconds // 3600
    seconds -= hours * 3600
    minutes = seconds // 60
    seconds -= minutes * 60
    res = ""
    if hours > 0:
        res += "{}h".format(hours)
    if minutes > 0:
        res += "{}m".format(minutes)
    if seconds > 0:
        res += "{}s".format(seconds)
    return res


def from_base64(base64_str):
    return base64.b64decode(base64_str)


def to_base64(raw_data):
    bytes_data = raw_data.encode("utf-8")
    return base64.b64encode(bytes_data).decode("utf-8")


def fix_compliance_state(config):
    # If we get Compliant/NonCompliant as compliance_sate, change them before returning
    if config.compliance_status.compliance_state.lower() == "noncompliant":
        config.compliance_status.compliance_state = "Failed"
    elif config.compliance_status.compliance_state.lower() == "compliant":
        config.compliance_status.compliance_state = "Installed"

    return config


def is_dogfood_cluster(cmd):
    return cmd.cli_ctx.cloud.endpoints.resource_manager == consts.DF_RM_ENDPOINT


def has_prune_enabled(config):
    if config.kustomizations:
        for kustomization in config.kustomizations.values():
            if kustomization.prune:
                return True
    return False
