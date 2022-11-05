# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import ClientRequestError
from azure.cli.core.util import sdk_no_wait
from .vendored_sdks.appplatform.v2022_11_01_preview import models

DEFAULT_NAME = "default"

def predefined_accelerator_list(cmd, client, resource_group, service):
    return client.predefined_accelerators.list(resource_group, service, DEFAULT_NAME)


def predefined_accelerator_show(cmd, client, resource_group, service, name):
    return client.predefined_accelerators.get(resource_group, service, DEFAULT_NAME, name)


def predefined_accelerator_disable(cmd, client, resource_group, service, name, no_wait=False):
    return sdk_no_wait(no_wait, client.predefined_accelerators.begin_disable, resource_group, service, DEFAULT_NAME, name)


def predefined_accelerator_enable(cmd, client, resource_group, service, name, no_wait=False):
    return sdk_no_wait(no_wait, client.predefined_accelerators.begin_enable, resource_group, service, DEFAULT_NAME, name)