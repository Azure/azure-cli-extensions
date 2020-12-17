# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

import json
from distutils import log as logger
from collections import OrderedDict
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


def print_keyvault_policy_output(keyvault_secret_uri, user_assigned_identity_resource_id, raw_result):
    '''Prints warning to user about adding pipeline to KV Access Policy.'''

    keyvault_name = keyvault_secret_uri.split("https://")[1].split('.')[0]

    if user_assigned_identity_resource_id is not None:
        # if user ended resource id with a '/', remove it
        if user_assigned_identity_resource_id[-1] == '/':
            user_assigned_identity_resource_id = user_assigned_identity_resource_id[:-1]

        # account for ARM bug where the identity user assigned identities dict key resource id has lowercase resourcegroup rather than resourceGroup
        user_assigned_identity_resource_id_list = user_assigned_identity_resource_id.split("/")
        user_assigned_identity_resource_id_list[3] = "resourcegroups"
        user_assigned_identity_resource_id = '/'.join(user_assigned_identity_resource_id_list)

    identity_object_id = raw_result.identity.principal_id if user_assigned_identity_resource_id is None else raw_result.identity.user_assigned_identities[user_assigned_identity_resource_id].principal_id

    logger.warn("***YOU MUST RUN THE FOLLOWING COMMAND PRIOR TO ATTEMPTING A PIPELINERUN OR EXPECTING SOURCETRIGGER TO SUCCESSFULLY IMPORT IMAGES***")
    logger.warn(f'az keyvault set-policy --name {keyvault_name} --secret-permissions get --object-id {identity_object_id}')
