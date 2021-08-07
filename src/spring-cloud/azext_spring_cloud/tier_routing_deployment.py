# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
from ._util_enterprise import is_enterprise_tier, get_client
from .custom import (deployment_get)
from knack.log import get_logger

logger = get_logger(__name__)


def deployment_get_routing(cmd, client,
            resource_group,
            service, app, name):
    client = get_client(cmd) if is_enterprise_tier(cmd, resource_group, service) else client
    return deployment_get(cmd, client, resource_group, service, app, name)
