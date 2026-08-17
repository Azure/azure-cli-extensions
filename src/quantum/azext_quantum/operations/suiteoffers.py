# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.cli.core.azclierror import InvalidArgumentValueError
from .._client_factory import cf_suite_offers, cf_suite_offer_status


def list_targets(cmd, provider_id):
    """
    Get the list of targets and their status available through a suite offer,
    without requiring an Azure Quantum workspace.
    """
    from azure.cli.core.commands.client_factory import get_subscription_id

    subscription = get_subscription_id(cmd.cli_ctx)
    location = _get_suite_offer_location(cmd, provider_id)

    status = cf_suite_offer_status(cmd.cli_ctx, subscription, location, provider_id)

    # Suite offers that failed provisioning are omitted by the data-plane listing, so no
    # additional filtering is required here. Normalize the response into a list of providers.
    if isinstance(status, dict):
        return status.get('value', [status])
    return status


def _get_suite_offer_location(cmd, provider_id):
    """
    Resolve the region for a suite offer from its subscription-level listing.
    """
    for offer in cf_suite_offers(cmd.cli_ctx).list_by_subscription():
        if offer.properties.provider_id.lower() == provider_id.lower():
            return offer.properties.location
    raise InvalidArgumentValueError(f"Suite offer '{provider_id}' not found in the current subscription.")
