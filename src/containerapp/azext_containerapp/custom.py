# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import (ResourceNotFoundError)
from knack.util import CLIError

from ._client_factory import handle_raw_exception
from ._clients import KubeEnvironmentClient


def create_containerapp(cmd, resource_group_name, containerapp_name, location=None, tags=None):
    raise CLIError('TODO: Implement `containerapp create`')


def show_kube_environment(cmd, name, resource_group_name):
    try:
        return KubeEnvironmentClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except CLIError as e:
        handle_raw_exception(e)
