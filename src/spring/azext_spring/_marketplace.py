# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
# pylint: disable=unused-argument, logging-format-interpolation, protected-access, wrong-import-order, too-many-lines
from knack.log import get_logger
from ._constant import (MARKETPLACE_OFFER_ID, MARKETPLACE_PUBLISHER_ID)

logger = get_logger(__name__)


def _spring_list_marketplace_plan(cmd, client):
    # return get_mgmt_service_client(cli_ctx, AppPlatformManagementClient_20220501preview)
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.marketplace.v2018_08_01_beta import MarketplaceRPService
    from .vendored_sdks.marketplace.v2018_08_01_beta.models import Offer

    logger.warning('To view the Azure Spring Apps Enterprise tier offering and read a detailed description, see https://aka.ms/ascmpoffer')
    client = get_mgmt_service_client(cmd.cli_ctx, MarketplaceRPService)
    offer = client.offer.get('{}.{}'.format(MARKETPLACE_PUBLISHER_ID, MARKETPLACE_OFFER_ID))
    offer.plans = [x for x in offer.plans if _is_valid_plan(x)]
    return Offer.deserialize(offer).serialize(offer)


def _is_valid_plan(plan):
    return plan.availabilities


def transform_marketplace_plan_output(result):
    def _table_item_view(plan):
        return {
            'publisher id': result['properties']['publisherId'],
            'product id': result['properties']['offerId'],
            'plan id': plan['planId'],
            'plan display name': plan['displayName']
        }

    plans = result['properties']['plans']
    return [_table_item_view(plan) for plan in plans]
