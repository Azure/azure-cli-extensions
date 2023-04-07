# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument, logging-format-interpolation, protected-access, wrong-import-order, too-many-lines
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from msrestazure.tools import resource_id

SERVICE_REGISTRY_NAME = "serviceRegistry"
RESOURCE_ID = "resourceId"

RESOURCE_TYPE = "serviceRegistries"
DEFAULT_NAME = "default"

logger = get_logger(__name__)


def service_registry_create(cmd, client, service, resource_group):
    return client.service_registries.begin_create_or_update(resource_group, service, DEFAULT_NAME)


def service_registry_delete(cmd, client, service, resource_group):
    return client.service_registries.begin_delete(resource_group, service, DEFAULT_NAME)


def service_registry_show(cmd, client, service, resource_group):
    return client.service_registries.get(resource_group, service, DEFAULT_NAME)


def service_registry_bind(cmd, client, service, resource_group, app):
    return _service_registry_bind_or_unbind_app(cmd, client, service, resource_group, app, True)


def service_registry_unbind(cmd, client, service, resource_group, app):
    return _service_registry_bind_or_unbind_app(cmd, client, service, resource_group, app, False)


def _service_registry_bind_or_unbind_app(cmd, client, service, resource_group, app_name, enabled):
    app = client.apps.get(resource_group, service, app_name)
    app.properties.addon_configs = _get_app_addon_configs_with_service_registry(app.properties.addon_configs)

    if (app.properties.addon_configs[SERVICE_REGISTRY_NAME][RESOURCE_ID] != "") == enabled:
        logger.warning('App "{}" has been {}binded'.format(app_name, '' if enabled else 'un'))
        return app

    service_registry_id = resource_id(
        subscription=get_subscription_id(cmd.cli_ctx),
        resource_group=resource_group,
        namespace='Microsoft.AppPlatform',
        type='Spring',
        name=service,
        child_type_1=RESOURCE_TYPE,
        child_name_1=DEFAULT_NAME
    )

    if enabled:
        app.properties.addon_configs[SERVICE_REGISTRY_NAME][RESOURCE_ID] = service_registry_id
    else:
        app.properties.addon_configs[SERVICE_REGISTRY_NAME][RESOURCE_ID] = ""
    return client.apps.begin_update(resource_group, service, app_name, app)


def _get_app_addon_configs_with_service_registry(addon_configs):
    if addon_configs is None:
        addon_configs = {}
    if addon_configs.get(SERVICE_REGISTRY_NAME) is None:
        addon_configs[SERVICE_REGISTRY_NAME] = {}
    if addon_configs[SERVICE_REGISTRY_NAME].get(RESOURCE_ID) is None:
        addon_configs[SERVICE_REGISTRY_NAME][RESOURCE_ID] = ""
    return addon_configs
