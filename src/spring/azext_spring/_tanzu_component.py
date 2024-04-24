# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods, unused-argument, redefined-builtin

from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from msrestazure.tools import resource_id
from .application_live_view import create as application_live_view_create
from .dev_tool_portal import create_or_update as dev_tool_portal_create
from .vendored_sdks.appplatform.v2024_05_01_preview.models._app_platform_management_client_enums import ConfigurationServiceGeneration
from .vendored_sdks.appplatform.v2024_05_01_preview import models

GATEWAY_RESOURCE_TYPE = "gateways"
DEFAULT_NAME = "default"
logger = get_logger(__name__)


def create_dev_tool_portal(cmd, client, resource_group, service, enable_application_live_view, enable_application_accelerator, **_):
    if any([enable_application_live_view, enable_application_accelerator]):
        logger.warning('- Creating Dev Tool Portal ..')
        return dev_tool_portal_create(cmd, client, service, resource_group,
                                      enable_application_live_view=enable_application_live_view,
                                      enable_application_accelerator=enable_application_accelerator)


def create_application_live_view(cmd, client, resource_group, service, enable_application_live_view, **_):
    if enable_application_live_view:
        logger.warning('- Creating Application Live View ..')
        return application_live_view_create(cmd, client, service, resource_group)


def create_application_configuration_service(cmd, client, resource_group, service, enable_application_configuration_service, application_configuration_service_generation, **_):
    if enable_application_configuration_service:
        logger.warning(" - Creating Application Configuration Service ..")
        acs_resource = models.ConfigurationServiceResource()
        acs_resource.properties = models.ConfigurationServiceProperties()
        if application_configuration_service_generation:
            acs_resource.properties.generation = application_configuration_service_generation
            logger.warning("Create with generation {}".format(application_configuration_service_generation))
        else:
            acs_resource.properties.generation = ConfigurationServiceGeneration.GEN2
            logger.warning("Default generation will be Gen2")

        return client.configuration_services.begin_create_or_update(resource_group, service, DEFAULT_NAME, acs_resource)


def create_service_registry(cmd, client, resource_group, service, enable_service_registry, **_):
    if enable_service_registry:
        logger.warning(" - Creating Service Registry ..")
        return client.service_registries.begin_create_or_update(resource_group, service, DEFAULT_NAME)


def create_gateway(cmd, client, resource_group, service, enable_gateway, gateway_instance_count=None, sku=None, **_):
    if enable_gateway:
        logger.warning(" - Creating Spring Cloud Gateway ..")
        gateway_resource = models.GatewayResource()
        if gateway_instance_count and sku:
            gateway_resource.sku = models.Sku(name=sku.name, tier=sku.tier,
                                              capacity=gateway_instance_count)
        return client.gateways.begin_create_or_update(resource_group, service, DEFAULT_NAME, gateway_resource)


def create_api_portal(cmd, client, resource_group, service, enable_api_portal, api_portal_instance_count=None, sku=None, **_):
    if enable_api_portal:
        logger.warning(" - Creating API portal ..")
        gateway_id = resource_id(
            subscription=get_subscription_id(cmd.cli_ctx),
            resource_group=resource_group,
            namespace='Microsoft.AppPlatform',
            type='Spring',
            name=service,
            child_type_1=GATEWAY_RESOURCE_TYPE,
            child_name_1=DEFAULT_NAME
        )

        api_portal_resource = models.ApiPortalResource(
            properties=models.ApiPortalProperties(
                gateway_ids=[gateway_id]
            )
        )
        if api_portal_instance_count and sku:
            api_portal_resource.sku = models.Sku(name=sku.name, tier=sku.tier,
                                                 capacity=api_portal_instance_count)
        return client.api_portals.begin_create_or_update(resource_group, service, DEFAULT_NAME, api_portal_resource)


def create_application_accelerator(cmd, client, resource_group, service, enable_application_accelerator, **_):
    if enable_application_accelerator:
        logger.warning(" - Creating Application Accelerator ..")
        application_accelerator_resource = models.ApplicationAcceleratorResource(
            properties=models.ApplicationAcceleratorProperties(
            )
        )
        return client.application_accelerators.begin_create_or_update(resource_group, service, DEFAULT_NAME, application_accelerator_resource)
