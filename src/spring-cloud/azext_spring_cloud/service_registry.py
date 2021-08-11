# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument, logging-format-interpolation, protected-access, wrong-import-order, too-many-lines
from ._enterprise import app_get_enterprise
from ._util_enterprise import (is_enterprise_tier, get_client)
from .vendored_sdks.appplatform.v2022_05_01_preview import models as models
from azure.cli.core.commands import cached_put
from azure.cli.core.util import sdk_no_wait
from knack.log import get_logger
from knack.util import CLIError

SERVICE_REGISTRY_NAME = "ServiceRegistry"

logger = get_logger(__name__)

def service_registry_show(cmd, client, service, resource_group):
    return client.service_registries.get(resource_group, service)


def service_registry_bind(cmd, client, service, resource_group, app):
    _service_registry_bind_or_unbind_app(cmd, client, service, resource_group, app, True)


def service_registry_unbind(cmd, client, service, resource_group, app):
    _service_registry_bind_or_unbind_app(cmd, client, service, resource_group, app, False)


def _service_registry_bind_or_unbind_app(cmd, client, service, resource_group, app_name, enabled):
    app = client.apps.get(resource_group, service, app_name)
    app.properties.addon_configs = {
        SERVICE_REGISTRY_NAME: models.AddonProfile()
    } if app.properties.addon_configs is None else app.properties.addon_configs

    if app.properties.addon_configs[SERVICE_REGISTRY_NAME].enabled == enabled:
        logger.warning('App "{}" has been {}binded'.format(app_name, '' if enabled else 'un'))
        return

    app.properties.addon_configs[SERVICE_REGISTRY_NAME].enabled = enabled
    return client.apps.begin_update(resource_group, service, app_name, app)
