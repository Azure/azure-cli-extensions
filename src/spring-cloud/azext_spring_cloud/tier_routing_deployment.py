# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
from ._util_enterprise import is_enterprise_tier, get_client
from ._enterprise import (deployment_delete_enterprise)
from .custom import (deployment_get as deployment_get_standard, deployment_list as deployment_list_standard,
                     deployment_delete as deployment_delete_standard)
from knack.log import get_logger

logger = get_logger(__name__)


def deployment_get(cmd, client,
                   resource_group,
                   service, app, name):
    client = get_client(cmd) if is_enterprise_tier(cmd, resource_group, service) else client
    return deployment_get_standard(cmd, client, resource_group, service, app, name)


def deployment_list(cmd, client,
                    resource_group,
                    service, app):
    client = get_client(cmd) if is_enterprise_tier(cmd, resource_group, service) else client
    return deployment_list_standard(cmd, client, resource_group, service, app)


def deployment_delete(cmd, client, resource_group, service, app, name):
    if is_enterprise_tier(cmd, resource_group, service):
        return deployment_delete_enterprise(cmd, get_client(cmd), resource_group, service, app, name)
    else:
        return deployment_delete_standard(cmd, client, resource_group, service, app, name)