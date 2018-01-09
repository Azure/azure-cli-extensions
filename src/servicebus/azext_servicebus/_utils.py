# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_servicebus.servicebus.models.service_bus_management_client_enums import AccessRights


def accessrights_converter(accessrights):
    accessrights_new = []
    if accessrights == 'Send':
        accessrights_new.append(AccessRights.send)
    if accessrights == 'Manage':
        accessrights_new.append(AccessRights.manage)
    if accessrights == 'Listen':
        accessrights_new.append(AccessRights.listen)

    return accessrights_new
