# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,redefined-builtin

from knack.util import CLIError
from .._client_factory import cf_offerings
import time


def _get_publisher_and_offer_from_provider_id(providers, provider_id):
    publisher_id = None
    offer_id = None
    for p in providers:
        if (p.id.lower() == provider_id.lower()):
            offer_id = p.properties.managed_application.offer_id
            publisher_id = p.properties.managed_application.publisher_id
            break
    if (offer_id == None or publisher_id == None):
        raise CLIError("Provider not found")
    return (publisher_id, offer_id)


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
    client = cf_offerings(cmd.cli_ctx)
    (publisher_id, offer_id) = _get_publisher_and_offer_from_provider_id(client.list(location_name=location), provider_id)
    print(f"az vm image terms show -p {publisher_id} -f {offer_id} --plan {sku}")
    return None


def accept_terms(cmd, provider_id=None, sku=None, location=None):
    """
    Accept the terms of a provider and SKU combination to enable it for workspace creation.
    """
    client = cf_offerings(cmd.cli_ctx)
    (publisher_id, offer_id) = _get_publisher_and_offer_from_provider_id(client.list(location_name=location), provider_id)
    print(f"az vm image terms accept -p {publisher_id} -f {offer_id} --plan {sku}")
    return None
