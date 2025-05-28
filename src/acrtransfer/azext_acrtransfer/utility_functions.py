# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import IdentityProperties, UserIdentityProperties


def create_identity_properties(user_assigned_identity_resource_id):
    '''Returns IdentityProperties object.'''

    if user_assigned_identity_resource_id is None:
        resource_identity_type = "SystemAssigned"
        user_assigned_identities = None

    else:
        resource_identity_type = "UserAssigned"
        user_identity_properties = UserIdentityProperties()
        user_assigned_identities = {user_assigned_identity_resource_id: user_identity_properties}

    return IdentityProperties(type=resource_identity_type, user_assigned_identities=user_assigned_identities)
