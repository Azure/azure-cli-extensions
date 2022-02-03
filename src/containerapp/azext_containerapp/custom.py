# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import (ResourceNotFoundError)
from knack.util import CLIError

from ._client_factory import handle_raw_exception
from ._clients import KubeEnvironmentClient, ManagedEnvironmentClient


def create_containerapp(cmd, resource_group_name, containerapp_name, location=None, tags=None):
    raise CLIError('TODO: Implement `containerapp create`')


def show_kube_environment(cmd, name, resource_group_name):
    try:
        return KubeEnvironmentClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except CLIError as e:
        handle_raw_exception(e)


def list_kube_environments(cmd, resource_group_name=None):
    try:
        kube_envs = []
        if resource_group_name is None:
            kube_envs = KubeEnvironmentClient.list_by_subscription(cmd=cmd)
        else:
            kube_envs = KubeEnvironmentClient.list_by_resource_group(cmd=cmd, resource_group_name=resource_group_name)

        return [e for e in kube_envs if "properties" in e and
            "environmentType" in e["properties"] and
            e["properties"]["environmentType"] and
            e["properties"]["environmentType"].lower() == "managed"]
    except CLIError as e:
        handle_raw_exception(e)


def show_managed_environment(cmd, name, resource_group_name):
    try:
        return ManagedEnvironmentClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except CLIError as e:
        handle_raw_exception(e)


def list_managed_environments(cmd, resource_group_name=None):
    try:
        managed_envs = []
        if resource_group_name is None:
            managed_envs = ManagedEnvironmentClient.list_by_subscription(cmd=cmd)
        else:
            managed_envs = ManagedEnvironmentClient.list_by_resource_Group(cmd=cmd, resource_group_name=resource_group_name)

        return [e for e in managed_envs if "properties" in e and
            "environmentType" in e["properties"] and
            e["properties"]["environmentType"] and
            e["properties"]["environmentType"].lower() == "managed"]
    except CLIError as e:
        handle_raw_exception(e)
