# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument, logging-format-interpolation, protected-access, wrong-import-order, too-many-lines
from knack.log import get_logger

from .vendored_sdks.appplatform.v2022_11_01_preview import models

DEFAULT_NAME = "default"

logger = get_logger(__name__)


def show(cmd, client, service, resource_group):
    return client.dev_tool_portals.get(resource_group, service, DEFAULT_NAME)


def create(cmd, client, service, resource_group,
           assign_endpoint=False,
           client_id=None,
           client_secret=None,
           metadata_url=None,
           scopes=None):
    dev_tool_portal = models.DevToolPortalResource(properties=models.DevToolPortalProperties())
    return _update(cmd, client, service, resource_group, dev_tool_portal,
                   assign_endpoint=assign_endpoint,
                   client_id=client_id,
                   client_secret=client_secret,
                   metadata_url=metadata_url,
                   scopes=scopes)


def update(cmd, client, service, resource_group,
           assign_endpoint=None,
           client_id=None,
           client_secret=None,
           metadata_url=None,
           scopes=None):
    dev_tool_portal = show(cmd, client, service, resource_group)
    return _update(cmd, client, service, resource_group, dev_tool_portal,
                   assign_endpoint=assign_endpoint,
                   client_id=client_id,
                   client_secret=client_secret,
                   metadata_url=metadata_url,
                   scopes=scopes)


def _update(cmd, client, service, resource_group, dev_tool_portal,
           assign_endpoint=None,
           client_id=None,
           client_secret=None,
           metadata_url=None,
           scopes=None):
    if assign_endpoint is not None:
        dev_tool_portal.properties.public = assign_endpoint
    if client_id and client_secret and metadata_url and scopes:
        dev_tool_portal.properties.sso_properties = models.DevToolPortalSsoProperties(
            client_id=client_id,
            client_secret=client_secret,
            metadata_url=metadata_url,
            scopes=scopes
        )
    return client.dev_tool_portals.begin_create_or_update(resource_group, service, DEFAULT_NAME, dev_tool_portal)


def delete(cmd, client, service, resource_group):
    return client.dev_tool_portals.begin_delete(resource_group, service, DEFAULT_NAME)
