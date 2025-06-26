# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import PathLike

from azure.ai.ml.constants._common import REGISTRY_URI_FORMAT


def _set_path_type(path):
    """
    Used to determine if the path is local, remote, or jobs during
    the model creation scenario and set the telemetry tracking accordingly
    """
    path_type = None
    if path:
        if isinstance(path, PathLike):
            path_type = "local"
        elif path.startswith("azureml://jobs/"):
            path_type = "jobs"
        elif path.startswith("runs:/"):
            path_type = "runs"
        elif path.startswith("azureml://datastores/"):
            path_type = "datastores"
        else:
            path_type = "remote"
    return path_type


def _set_instance_type(deployment):
    """
    Used to determine the instance type when deployment type is Managed
    """
    if deployment and deployment.type and deployment.type == "Managed":
        return deployment.instance_type


def _set_egress_public_network_access(deployment):
    """
    Used to determine the value of egress public network access when
    deployment type is Managed
    """
    if deployment and deployment.type and deployment.type == "Managed":
        return deployment.egress_public_network_access


def _set_asset_reference_type(deployment_asset, asset_type):
    """
    Used to determine the type of the asset reference:
    version, label, inline, registry
    """
    if isinstance(deployment_asset, str) and deployment_asset.startswith(REGISTRY_URI_FORMAT):
        return "registry"
    elif isinstance(deployment_asset, str) and ":" in deployment_asset:
        return "version"
    elif isinstance(deployment_asset, str) and "@" in deployment_asset:
        return "label"
    elif isinstance(deployment_asset, asset_type):
        if deployment_asset._auto_increment_version:
            return "inline_next_version"
        elif deployment_asset._is_anonymous:
            return "inline_anonymous"
        return "inline"
    return


def _set_code_reference_type(deployment_code):
    if deployment_code.code and deployment_code.code.startswith(REGISTRY_URI_FORMAT):
        return "registry"
    elif deployment_code.code and deployment_code.code.startswith("azureml:/subscriptions"):
        return "id"
    elif deployment_code.code and ":" in deployment_code.code:
        return "name:version"
    return "inline"
