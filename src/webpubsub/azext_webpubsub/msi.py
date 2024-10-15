# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from .vendored_sdks.azure_mgmt_webpubsub.models import (
    ManagedIdentity,
    WebPubSubResource
)

from .vendored_sdks.azure_mgmt_webpubsub.operations import (
    WebPubSubOperations,
)


SYSTEM_ASSIGNED_IDENTITY_ALIAS = '[system]'


def webpubsub_msi_assign(client: WebPubSubOperations, resource_group_name, webpubsub_name, identity):
    msiType, user_identity = _analyze_identity(identity)

    identity = ManagedIdentity(type=msiType, user_assigned_identities={user_identity: {}} if user_identity else None)
    parameter = WebPubSubResource(location=None, identity=identity)
    return client.begin_update(resource_group_name, webpubsub_name, parameter)


def webpubsub_msi_remove(client: WebPubSubOperations, resource_group_name, webpubsub_name):
    identity = ManagedIdentity(type="None")
    parameter = WebPubSubResource(location=None, identity=identity)
    return client.begin_update(resource_group_name, webpubsub_name, parameter)


def webpubsub_msi_show(client: WebPubSubOperations, resource_group_name, webpubsub_name):
    res = client.get(resource_group_name, webpubsub_name)
    return res.identity


def _analyze_identity(identity):
    if identity == SYSTEM_ASSIGNED_IDENTITY_ALIAS:
        return "SystemAssigned", None
    return "UserAssigned", identity
