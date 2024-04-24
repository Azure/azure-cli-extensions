# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument, logging-format-interpolation, protected-access, wrong-import-order, too-many-lines
from knack.log import get_logger

from .vendored_sdks.appplatform.v2024_05_01_preview import models
from .dev_tool_portal import (is_updatable as is_dev_tool_portal_updatable,
                              try_get as get_dev_tool_portal,
                              create_or_update as create_or_update_dev_tool_portal,
                              _get_desired_state as get_dev_tool_portal_desired_state)
from ._utils import (wait_till_end)

DEFAULT_NAME = "default"

logger = get_logger(__name__)


def show(cmd, client, service, resource_group):
    return client.application_live_views.get(resource_group, service, DEFAULT_NAME)


def create(cmd, client, service, resource_group, no_wait=False):
    poller = client.application_live_views.begin_create_or_update(resource_group, service, DEFAULT_NAME,
                                                                  models.ApplicationLiveViewResource())
    dev_tool_portal_poller = _get_enable_dev_tool_portal_poller(cmd, client, service, resource_group)
    pollers = [x for x in [poller, dev_tool_portal_poller] if x is not None]
    if not no_wait:
        wait_till_end(cmd, *pollers)
    return poller


def delete(cmd, client, service, resource_group, no_wait=False):
    poller = client.application_live_views.begin_delete(resource_group, service, DEFAULT_NAME)
    dev_tool_portal_poller = _get_disable_dev_tool_portal_poller(cmd, client, service, resource_group)
    pollers = [x for x in [poller, dev_tool_portal_poller] if x is not None]
    if not no_wait:
        wait_till_end(cmd, *pollers)
    return poller


def _get_enable_dev_tool_portal_poller(cmd, client, service, resource_group):
    dev_tool_portal = get_dev_tool_portal(cmd, client, service, resource_group)
    if not dev_tool_portal:
        logger.warning('- View Application Live View through Dev Tool portal. '
                       'Create Dev Tool Portal by running '
                       '"az spring dev-tool create --service {} --resource-group {} --assign-endpoint"'
                       .format(service, resource_group))
        return None
    if not is_dev_tool_portal_updatable(dev_tool_portal):
        return None
    return _get_update_dev_tool_portal_poller(cmd, client, service, resource_group,
                                              dev_tool_portal, True)


def _get_disable_dev_tool_portal_poller(cmd, client, service, resource_group):
    dev_tool_portal = get_dev_tool_portal(cmd, client, service, resource_group)
    if not dev_tool_portal or not is_dev_tool_portal_updatable(dev_tool_portal):
        return None
    return _get_update_dev_tool_portal_poller(cmd, client, service, resource_group,
                                              dev_tool_portal, False)


def _get_update_dev_tool_portal_poller(cmd, client, service, resource_group, dev_tool_portal,
                                       enable_application_live_view):
    desired_state = get_dev_tool_portal_desired_state(enable_application_live_view)
    if dev_tool_portal.properties.features.application_live_view.state == desired_state:
        return None
    return create_or_update_dev_tool_portal(cmd, client, service, resource_group, dev_tool_portal,
                                            enable_application_live_view=enable_application_live_view)
