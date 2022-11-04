# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import ClientRequestError
from azure.cli.core.util import sdk_no_wait
from .vendored_sdks.appplatform.v2022_11_01_preview import models

DEFAULT_NAME = "default"


def application_accelerator_show(cmd, client, resource_group, service):
    return client.application_accelerators.get(resource_group, service, DEFAULT_NAME)


def application_accelerator_create(cmd, client, resource_group, service):
    properties = models.ApplicationAcceleratorProperties(
    )
    application_accelerator_resource = models.ApplicationAcceleratorResource(properties=properties)
    return client.application_accelerators.begin_create_or_update(resource_group, service, DEFAULT_NAME, application_accelerator_resource)


def application_accelerator_delete(cmd, client, resource_group, service, no_wait=False):
    return sdk_no_wait(no_wait, client.application_accelerators.begin_delete, resource_group, service, DEFAULT_NAME)