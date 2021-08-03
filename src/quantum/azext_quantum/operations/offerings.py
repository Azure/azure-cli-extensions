# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,redefined-builtin

from knack.util import CLIError
from .._client_factory import cf_offerings, cf_vm_image_term
import time

PUBLISHER_NOT_AVAILABLE = "N/A"
OFFER_NOT_AVAILABLE = "N/A"


def _show_info(msg):
    import colorama
    colorama.init()
    print(f"\033[1m{colorama.Fore.GREEN}{msg}{colorama.Style.RESET_ALL}")


def _get_terms_from_marketplace(cmd, publisher_id, offer_id, sku):
    from azure.mgmt.marketplaceordering.models import OfferType
    return cf_vm_image_term(cmd.cli_ctx).get(offer_type=OfferType.VIRTUALMACHINE, publisher_id=publisher_id, offer_id=offer_id, plan_id=sku)


def _set_terms_from_marketplace(cmd, publisher_id, offer_id, sku, term):
    from azure.mgmt.marketplaceordering.models import OfferType
    return cf_vm_image_term(cmd.cli_ctx).create(offer_type=OfferType.VIRTUALMACHINE, publisher_id=publisher_id, offer_id=offer_id, plan_id=sku, parameters=term)


def _get_publisher_and_offer_from_provider_id(providers, provider_id):
    publisher_id = None
    offer_id = None
    for p in providers:
        if (p.id.lower() == provider_id.lower()):
            offer_id = p.properties.managed_application.offer_id
            publisher_id = p.properties.managed_application.publisher_id
            break
    return (publisher_id, offer_id)


def _valid_publisher_and_offer(provider, publisher, offer):
    if (offer is None or publisher is None):
        raise CLIError(f"Provider '{provider}' not found.")
    if (offer == OFFER_NOT_AVAILABLE or publisher == PUBLISHER_NOT_AVAILABLE):
        # We show this information to the user to prevent a confusion when term commands take no effect.
        _show_info(f"No terms require to be accepted for provider '{provider}'.")
        return False
    return True


def list_offerings(cmd, location=None):
    """
    Get the list of all provider offerings available on the given location.
    """
    if (not location):
        raise CLIError("A location is required to list offerings available.")
    client = cf_offerings(cmd.cli_ctx)
    return client.list(location_name=location)


def show_terms(cmd, provider_id=None, sku=None, location=None):
    """
    Show the terms of a provider and SKU combination including license URL and acceptance status.
    """
    # This command is a wrapper for `az vm image terms show`, but it takes care of finding the Publisher and Offer on behalf of the user.
    client = cf_offerings(cmd.cli_ctx)
    (publisher_id, offer_id) = _get_publisher_and_offer_from_provider_id(client.list(location_name=location), provider_id)
    if not _valid_publisher_and_offer(provider_id, publisher_id, offer_id):
        return None
    return _get_terms_from_marketplace(cmd, publisher_id, offer_id, sku)


def accept_terms(cmd, provider_id=None, sku=None, location=None):
    """
    Accept the terms of a provider and SKU combination to enable it for workspace creation.
    """
    # This command is a wrapper for `az vm image terms accept`, but it takes care of finding the Publisher and Offer on behalf of the user.
    client = cf_offerings(cmd.cli_ctx)
    (publisher_id, offer_id) = _get_publisher_and_offer_from_provider_id(client.list(location_name=location), provider_id)
    if not _valid_publisher_and_offer(provider_id, publisher_id, offer_id):
        return None
    term = _get_terms_from_marketplace(cmd, publisher_id, offer_id, sku)
    term.accepted = True
    return _set_terms_from_marketplace(cmd, publisher_id, offer_id, sku, term)
