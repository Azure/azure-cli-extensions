# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument, logging-format-interpolation, protected-access, wrong-import-order, too-many-lines
from knack.log import get_logger

from azure.cli.core.util import sdk_no_wait
from .vendored_sdks.appplatform.v2024_05_01_preview import models

DEFAULT_NAME = "default"

logger = get_logger(__name__)


def show(cmd, client, service, resource_group):
    return client.dev_tool_portals.get(resource_group, service, DEFAULT_NAME)


def create(cmd, client, service, resource_group,
           assign_endpoint=False,
           client_id=None,
           client_secret=None,
           metadata_url=None,
           scopes=None,
           no_wait=False):
    return create_or_update(cmd, client, service, resource_group,
                            assign_endpoint=assign_endpoint,
                            client_id=client_id,
                            client_secret=client_secret,
                            metadata_url=metadata_url,
                            scopes=scopes,
                            no_wait=no_wait)


def update(cmd, client, service, resource_group,
           assign_endpoint=None,
           client_id=None,
           client_secret=None,
           metadata_url=None,
           scopes=None,
           no_wait=False):
    dev_tool_portal = show(cmd, client, service, resource_group)
    return create_or_update(cmd, client, service, resource_group, dev_tool_portal,
                            assign_endpoint=assign_endpoint,
                            client_id=client_id,
                            client_secret=client_secret,
                            metadata_url=metadata_url,
                            scopes=scopes,
                            no_wait=no_wait)


def create_or_update(cmd, client, service, resource_group,
                     dev_tool_portal=models.DevToolPortalResource(properties=models.DevToolPortalProperties()),
                     assign_endpoint=None,
                     client_id=None,
                     client_secret=None,
                     metadata_url=None,
                     scopes=None,
                     enable_application_live_view=None,
                     enable_application_accelerator=None,
                     no_wait=False):
    if assign_endpoint is not None:
        dev_tool_portal.properties.public = assign_endpoint
    if client_id and client_secret and metadata_url and scopes:
        dev_tool_portal.properties.sso_properties = models.DevToolPortalSsoProperties(
            client_id=client_id,
            client_secret=client_secret,
            metadata_url=metadata_url,
            scopes=scopes
        )
    dev_tool_portal.properties.features = dev_tool_portal.properties.features or models.DevToolPortalFeatureSettings(
        application_live_view=models.DevToolPortalFeatureDetail(),
        application_accelerator=models.DevToolPortalFeatureDetail()
    )
    if enable_application_live_view is not None:
        dev_tool_portal.properties.features.application_live_view.state = \
            _get_desired_state(enable_application_live_view)
    if enable_application_accelerator is not None:
        dev_tool_portal.properties.features.application_accelerator.state = \
            _get_desired_state(enable_application_accelerator)
    return sdk_no_wait(no_wait, client.dev_tool_portals.begin_create_or_update, resource_group,
                       service, DEFAULT_NAME, dev_tool_portal)


def delete(cmd, client, service, resource_group, no_wait=False):
    return sdk_no_wait(no_wait, client.dev_tool_portals.begin_delete, resource_group, service, DEFAULT_NAME)


def is_updatable(resource):
    return resource and resource.properties.provisioning_state in [
        models.DevToolPortalProvisioningState.SUCCEEDED,
        models.DevToolPortalProvisioningState.FAILED,
        models.DevToolPortalProvisioningState.CANCELED
    ]


def try_get(cmd, client, service, resource_group):
    try:
        return show(cmd, client, service, resource_group)
    except:
        return None


def _get_desired_state(enable):
    return models.DevToolPortalFeatureState.ENABLED if enable else models.DevToolPortalFeatureState.DISABLED
