# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods, unused-argument, redefined-builtin

import json
from azure.cli.core.util import sdk_no_wait
from .vendored_sdks.appplatform.v2022_01_01_preview import models

DEFAULT_BUILD_SERVICE_NAME = "default"
DEFAULT_BUILD_AGENT_POOL_NAME = "default"


def _update_default_build_agent_pool(cmd, client, resource_group, name, build_pool_size=None):
    if build_pool_size is not None:
        build_properties = models.BuildServiceAgentPoolProperties(
            pool_size=models.BuildServiceAgentPoolSizeProperties(
                name=build_pool_size))
        agent_pool_resource = models.BuildServiceAgentPoolResource(
            properties=build_properties)
        return client.build_service_agent_pool.begin_update_put(
            resource_group, name, DEFAULT_BUILD_SERVICE_NAME, DEFAULT_BUILD_AGENT_POOL_NAME, agent_pool_resource)


def create_or_update_builder(cmd, client, resource_group, service, name, builder_json=None, builder_file=None, no_wait=False):
    builder = _update_builder(builder_file, builder_json)
    builder_resource = models.BuilderResource(
        properties=builder
    )
    return sdk_no_wait(no_wait, client.build_service_builder.begin_create_or_update,
                       resource_group, service, DEFAULT_BUILD_SERVICE_NAME, name, builder_resource)


def builder_show(cmd, client, resource_group, service, name):
    return client.build_service_builder.get(resource_group, service, DEFAULT_BUILD_SERVICE_NAME, name)


def builder_delete(cmd, client, resource_group, service, name, no_wait=False):
    return sdk_no_wait(no_wait, client.build_service_builder.begin_delete, resource_group, service, DEFAULT_BUILD_SERVICE_NAME, name)


def _update_builder(builder_file, builder_json):
    if builder_file is not None:
        with open(builder_file, 'r') as json_file:
            builder = json.load(json_file)

    if builder_json is not None:
        builder = json.loads(builder_json)

    return builder
