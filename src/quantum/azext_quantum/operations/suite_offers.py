# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from collections import OrderedDict

from azure.cli.core.azclierror import InvalidArgumentValueError, ResourceNotFoundError
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.core.exceptions import ResourceNotFoundError as AzureResourceNotFoundError

from .._client_factory import cf_suite_offers, cf_suite_offers_data_plane, base_url_v2

# Suite offer quota allocations are always reported at the per-target scope.
_SUITE_OFFER_QUOTA_SCOPE = "SubscriptionTarget"


def list_suite_offers(cmd):
    """
    List the Azure Quantum suite offers available to the current subscription.
    """
    client = cf_suite_offers(cmd.cli_ctx)
    return client.list_by_subscription()


def suite_offer_quotas(cmd, provider_id):
    """
    Return the v2 quota allocations, merged with their consumed usages, for a suite offer
    provider account in the current subscription.
    """
    subscription_id = get_subscription_id(cmd.cli_ctx)

    # 1. Control-plane: locate the suite offer for the requested provider account.
    offers = cf_suite_offers(cmd.cli_ctx).list_by_subscription()
    offer = next(
        (o for o in offers
         if o.properties is not None
         and o.properties.provider_id is not None
         and o.properties.provider_id.lower() == provider_id.lower()),
        None,
    )
    if offer is None:
        raise InvalidArgumentValueError(
            f"No suite offer was found for provider account '{provider_id}' in subscription '{subscription_id}'."
        )

    # 2. Data-plane (v2): fetch the consumed quota usages for that provider account.
    endpoint = base_url_v2(offer.properties.location)
    client = cf_suite_offers_data_plane(cmd.cli_ctx, subscription_id, endpoint)
    try:
        usages = client.list_quota_usages(subscription_id, provider_id)
    except AzureResourceNotFoundError as ex:
        raise ResourceNotFoundError(
            f"No quota usages were found for provider account '{provider_id}'."
        ) from ex

    # 3. Merge allocations (limits) with usages (consumed).
    return _merge_suite_offer_quotas(offer, usages, provider_id)


def suite_offer_targets(cmd, provider_id):
    """
    List the targets and their status available through a suite offer provider account,
    without requiring an Azure Quantum workspace.
    """
    subscription_id = get_subscription_id(cmd.cli_ctx)

    # 1. Control-plane: locate the suite offer to resolve its region.
    offers = cf_suite_offers(cmd.cli_ctx).list_by_subscription()
    offer = next(
        (o for o in offers
         if o.properties is not None
         and o.properties.provider_id is not None
         and o.properties.provider_id.lower() == provider_id.lower()),
        None,
    )
    if offer is None:
        raise InvalidArgumentValueError(
            f"No suite offer was found for provider account '{provider_id}' in subscription '{subscription_id}'."
        )

    # 2. Data-plane (v2): fetch the provider/target status for that provider account.
    endpoint = base_url_v2(offer.properties.location)
    client = cf_suite_offers_data_plane(cmd.cli_ctx, subscription_id, endpoint)
    try:
        status = client.get_provider_status(subscription_id, provider_id)
    except AzureResourceNotFoundError as ex:
        raise ResourceNotFoundError(
            f"No target status was found for provider account '{provider_id}'."
        ) from ex

    # The endpoint returns a single provider; wrap it so the table transformer shared with
    # 'az quantum target list' can iterate provider rows.
    return [status]


def _minutes(standard, high):
    """Build a {standardMinutesLifetime, highMinutesLifetime} block."""
    return OrderedDict([
        ("standardMinutesLifetime", standard),
        ("highMinutesLifetime", high),
    ])


def _merge_suite_offer_quotas(offer, usages, provider_id):
    """
    Build one row per target quota allocation, attaching its matching data-plane usage.
    Suite offer quotas are reported at the SubscriptionTarget scope only.
    """
    # Data-plane usages keyed by target id.
    usage_by_target = {
        usage.target_id: usage for usage in (usages or []) if usage.target_id is not None
    }

    rows = []
    for target_quota in sorted(offer.properties.target_quotas or [], key=lambda q: q.target_id or ""):
        usage = usage_by_target.get(target_quota.target_id)
        usage_values = usage.usage if usage is not None else None

        row = OrderedDict()
        row["providerId"] = provider_id
        row["scope"] = _SUITE_OFFER_QUOTA_SCOPE
        row["targetId"] = target_quota.target_id
        row["allocation"] = _minutes(
            target_quota.standard_minutes_lifetime,
            target_quota.high_minutes_lifetime,
        )
        row["usage"] = _minutes(
            usage_values.standard_minutes_lifetime if usage_values is not None else None,
            usage_values.high_minutes_lifetime if usage_values is not None else None,
        )
        rows.append(row)

    return rows
