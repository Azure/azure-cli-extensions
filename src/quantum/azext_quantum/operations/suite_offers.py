# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from collections import OrderedDict

from azure.cli.core.azclierror import InvalidArgumentValueError, ResourceNotFoundError
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.core.exceptions import ResourceNotFoundError as AzureResourceNotFoundError

from .._client_factory import cf_suite_offers, cf_suite_offer_quota_usages, base_url_v2


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
    client = cf_suite_offer_quota_usages(cmd.cli_ctx, subscription_id, endpoint)
    try:
        usages = client.list_quota_usages(subscription_id, provider_id)
    except AzureResourceNotFoundError as ex:
        raise ResourceNotFoundError(
            f"No quota usages were found for provider account '{provider_id}'."
        ) from ex

    # 3. Merge allocations (limits) with usages (consumed).
    return _merge_suite_offer_quotas(offer, usages, provider_id)


def _minutes_row(allocated, used):
    """Build the per-priority {allocated, used, remaining} entry, or None if nothing is known."""
    if allocated is None and used is None:
        return None
    remaining = None
    if allocated is not None and used is not None:
        remaining = allocated - used
    return OrderedDict([("allocated", allocated), ("used", used), ("remaining", remaining)])


def _merge_suite_offer_quotas(offer, usages, provider_id):
    """
    Combine the ARM quota allocations (limits) with the data-plane quota usages (consumed),
    keyed by target id (None represents the subscription-level allocation).
    """
    props = offer.properties

    # Allocations keyed by target id (None => subscription-level).
    allocations = {}
    if props.quotas is not None:
        allocations[None] = props.quotas
    for target_quota in props.target_quotas or []:
        allocations[target_quota.target_id] = target_quota

    # Usages keyed by target id (None => subscription-level).
    usage_by_key = {}
    for usage in usages or []:
        usage_by_key[usage.target_id] = usage

    rows = []
    # Emit the subscription-level row first, then target rows sorted by target id.
    keys = list(allocations.keys()) + [k for k in usage_by_key if k not in allocations]
    ordered_keys = [None] if (None in allocations or None in usage_by_key) else []
    ordered_keys += sorted(k for k in keys if k is not None)

    for key in ordered_keys:
        allocation = allocations.get(key)
        usage = usage_by_key.get(key)

        std_allocated = allocation.standard_minutes_lifetime if allocation is not None else None
        high_allocated = allocation.high_minutes_lifetime if allocation is not None else None

        usage_values = usage.usage if usage is not None else None
        std_used = usage_values.standard_minutes_lifetime if usage_values is not None else None
        high_used = usage_values.high_minutes_lifetime if usage_values is not None else None

        row = OrderedDict()
        row["providerId"] = provider_id
        row["scope"] = "Subscription" if key is None else "SubscriptionTarget"
        if key is not None:
            row["targetId"] = key

        std = _minutes_row(std_allocated, std_used)
        if std is not None:
            row["standardMinutesLifetime"] = std
        high = _minutes_row(high_allocated, high_used)
        if high is not None:
            row["highMinutesLifetime"] = high

        if usage is not None and usage.last_modified_time is not None:
            row["lastModifiedTime"] = usage.last_modified_time

        rows.append(row)

    return rows
