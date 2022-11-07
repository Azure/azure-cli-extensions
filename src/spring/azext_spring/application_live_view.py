# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument, logging-format-interpolation, protected-access, wrong-import-order, too-many-lines
from knack.log import get_logger

from .vendored_sdks.appplatform.v2022_11_01_preview import models
from .dev_tool_portal import (try_get as get_dev_tool_portal,
                              create_or_update as create_or_update_dev_tool_portal)
from ._utils import (wait_till_end)

DEFAULT_NAME = "default"

logger = get_logger(__name__)


def show(cmd, client, service, resource_group):
    return client.application_live_views.get(resource_group, service, DEFAULT_NAME)


def create(cmd, client, service, resource_group, no_wait=False):
    poller = client.application_live_views.begin_create_or_update(resource_group, service, DEFAULT_NAME,
                                                                  models.ApplicationLiveViewResource())
    dev_tool_portal_poller = _get_update_dev_tool_portal_poller(cmd, client, service, resource_group,
                                                                enable_application_live_view=True)
    pollers = [x for x in [poller, dev_tool_portal_poller] if x is not None]
    if not no_wait:
        wait_till_end(cmd, *pollers)
    return poller


def delete(cmd, client, service, resource_group, no_wait=False):
    poller = client.application_live_views.begin_delete(resource_group, service, DEFAULT_NAME)
    dev_tool_portal_poller = _get_update_dev_tool_portal_poller(cmd, client, service, resource_group,
                                                                enable_application_live_view=False)
    pollers = [x for x in [poller, dev_tool_portal_poller] if x is not None]
    if not no_wait:
        wait_till_end(cmd, *pollers)
    return poller


def _get_update_dev_tool_portal_poller(cmd, client, service, resource_group,
                                       enable_application_live_view):
    dev_tool_portal = get_dev_tool_portal(cmd, client, service, resource_group)
    if not dev_tool_portal:
        return None
    desired_state = models.DevToolPortalFeatureState.ENABLED if enable_application_live_view \
                    else models.DevToolPortalFeatureState.DISABLED
    if dev_tool_portal.properties.features.application_live_view.state == desired_state:
        return None
    return create_or_update_dev_tool_portal(cmd, client, service, resource_group, dev_tool_portal,
                                            enable_application_live_view=enable_application_live_view)