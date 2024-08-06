# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods, unused-argument, redefined-builtin

import json
from azure.cli.core.util import sdk_no_wait
from .vendored_sdks.appplatform.v2024_05_01_preview import models
from ._buildservices_factory import BuildService
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger

logger = get_logger(__name__)

DEFAULT_BUILD_SERVICE_NAME = "default"
DEFAULT_BUILD_AGENT_POOL_NAME = "default"
DEFAULT_CONTAINER_REGISTRY_NAME = "default"
DEFAULT_CONTAINER_REGISTRY_TYPE = "BasicAuth"


def _update_default_build_agent_pool(cmd, client, resource_group, name, build_pool_size=None):
    if build_pool_size is not None:
        build_properties = models.BuildServiceAgentPoolProperties(
            pool_size=models.BuildServiceAgentPoolSizeProperties(
                name=build_pool_size))
        agent_pool_resource = models.BuildServiceAgentPoolResource(
            properties=build_properties)
        return client.build_service_agent_pool.begin_update_put(
            resource_group, name, DEFAULT_BUILD_SERVICE_NAME, DEFAULT_BUILD_AGENT_POOL_NAME, agent_pool_resource)


def create_build_service(cmd, client, resource_group, service, disable_build_service=False,
                         registry_server=None, registry_username=None, registry_password=None):
    if disable_build_service:
        return

    if registry_server:
        container_registry_properties = models.ContainerRegistryProperties(
            credentials=models.ContainerRegistryBasicCredentials(
                type=DEFAULT_CONTAINER_REGISTRY_TYPE,
                server=registry_server,
                username=registry_username,
                password=registry_password))
        container_registry_resource = models.ContainerRegistryResource(
            properties=container_registry_properties)
        poller = client.container_registries.begin_create_or_update(
            resource_group, service, DEFAULT_CONTAINER_REGISTRY_NAME, container_registry_resource)
        LongRunningOperation(cmd.cli_ctx)(poller)

        subscription = get_subscription_id(cmd.cli_ctx)
        service_resource_id = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}'.format(subscription, resource_group, service)
        build_service_properties = models.BuildServiceProperties(
            container_registry='{}/containerregistries/{}'.format(service_resource_id, DEFAULT_CONTAINER_REGISTRY_NAME))
        build_service_resource = models.BuildService(
            properties=build_service_properties)
        return client.build_service.begin_create_or_update(resource_group, service, DEFAULT_BUILD_SERVICE_NAME, build_service_resource)
    else:
        build_service_properties = models.BuildServiceProperties(
            container_registry=None)
        build_service_resource = models.BuildService(
            properties=build_service_properties)
        return client.build_service.begin_create_or_update(resource_group, service, DEFAULT_BUILD_SERVICE_NAME, build_service_resource)


def create_or_update_builder(cmd, client, resource_group, service, name, builder_json=None, builder_file=None, no_wait=False):
    logger.warning('Editing builder will regenerate images for all app deployments using this builder. These new images will ' +
                   'be used after app restart either manually by yourself or automatically by Azure Spring Apps in regular maintenance tasks. ' +
                   'Use CLI command --"az spring build-service builder show-deployments" to view the app deployment list of the builder.')
    builder = _update_builder(builder_file, builder_json)
    builder_resource = models.BuilderResource(
        properties=builder
    )
    return sdk_no_wait(no_wait, client.build_service_builder.begin_create_or_update,
                       resource_group, service, DEFAULT_BUILD_SERVICE_NAME, name, builder_resource)


def builder_show(cmd, client, resource_group, service, name):
    return client.build_service_builder.get(resource_group, service, DEFAULT_BUILD_SERVICE_NAME, name)


def builder_show_deployments(cmd, client, resource_group, service, name):
    return client.build_service_builder.list_deployments(resource_group, service, DEFAULT_BUILD_SERVICE_NAME, name)


def builder_delete(cmd, client, resource_group, service, name, no_wait=False):
    return sdk_no_wait(no_wait, client.build_service_builder.begin_delete, resource_group, service, DEFAULT_BUILD_SERVICE_NAME, name)


def create_or_update_container_registry(cmd, client, resource_group, service, name=None, server=None, username=None, password=None):
    container_registry_properties = models.ContainerRegistryProperties(
        credentials=models.ContainerRegistryBasicCredentials(
            server=server,
            username=username,
            password=password))
    container_registry_resource = models.ContainerRegistryResource(
        properties=container_registry_properties)
    return sdk_no_wait(False, client.container_registries.begin_create_or_update,
                       resource_group, service, name, container_registry_resource)


def container_registry_show(cmd, client, resource_group, service, name=None):
    return client.container_registries.get(resource_group, service, name)


def container_registry_delete(cmd, client, resource_group, service, name, no_wait=False):
    return sdk_no_wait(no_wait, client.container_registries.begin_delete, resource_group, service, name)


def container_registry_list(cmd, client, resource_group, service):
    return client.container_registries.list(resource_group, service)


def create_or_update_build(cmd, client, resource_group, service, name=None, builder=None, build_env=None,
                           build_cpu=None, build_memory=None, source_path=None, artifact_path=None,
                           apms=None, certificates=None, disable_validation=None):
    build_service = BuildService(cmd, client, resource_group, service)
    kwargs = {
        'build_name': name,
        'build_cpu': build_cpu,
        'build_memory': build_memory,
        'build_env': build_env,
        'builder': builder,
        'source_path': source_path,
        'artifact_path': artifact_path,
        'apms': apms,
        'certificates': certificates,
        'disable_validation': disable_validation
    }
    build_service.build_and_get_result(4, **kwargs)


def build_show(cmd, client, resource_group, service, name=None):
    return client.build_service.get_build(resource_group, service, DEFAULT_BUILD_SERVICE_NAME, name)


def build_list(cmd, client, resource_group, service):
    return client.build_service.list_builds(resource_group, service, DEFAULT_BUILD_SERVICE_NAME)


def build_delete(cmd, client, resource_group, service, name, no_wait=False):
    return sdk_no_wait(no_wait, client.build_service.begin_delete_build, resource_group, service, DEFAULT_BUILD_SERVICE_NAME, name)


def build_result_show(cmd, client, resource_group, service, build_name=None, name=None):
    return client.build_service.get_build_result(resource_group, service, DEFAULT_BUILD_SERVICE_NAME, build_name, name)


def build_result_list(cmd, client, resource_group, service, build_name=None):
    return client.build_service.list_build_results(resource_group, service, DEFAULT_BUILD_SERVICE_NAME, build_name)


def update_build_service(cmd, client, resource_group, service, registry_name=None, no_wait=False):
    subscription = get_subscription_id(cmd.cli_ctx)
    service_resource_id = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}'.format(subscription, resource_group, service)
    build_service_properties = models.BuildServiceProperties(
        container_registry='{}/containerregistries/{}'.format(service_resource_id, registry_name) if registry_name else None)
    build_service_resource = models.BuildService(
        properties=build_service_properties)
    return sdk_no_wait(no_wait, client.build_service.begin_create_or_update, resource_group, service, DEFAULT_BUILD_SERVICE_NAME, build_service_resource)


def build_service_show(cmd, client, resource_group, service):
    return client.build_service.get_build_service(resource_group, service, DEFAULT_BUILD_SERVICE_NAME)


def _update_builder(builder_file, builder_json):
    if builder_file is not None:
        with open(builder_file, 'r') as json_file:
            builder = json.load(json_file)

    if builder_json is not None:
        builder = json.loads(builder_json)

    return builder
