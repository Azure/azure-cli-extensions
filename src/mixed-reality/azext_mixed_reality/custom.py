# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from knack.util import CLIError
from azext_subscription.subscription.models import (SubscriptionCreationParameters, AdPrincipal)

logger = get_logger(__name__)

def cli_spatial_anchors_account_create(cmd, client, resource_group_name, spatial_anchors_account_name, location, tags=None):
    return client.create(resource_group_name, spatial_anchors_account_name, location, tags)
