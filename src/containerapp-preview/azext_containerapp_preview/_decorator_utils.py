# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.azclierror import ValidationError
from azure.cli.core.commands.client_factory import get_subscription_id

from ._client_factory import providers_client_factory, handle_raw_exception


def _ensure_location_allowed(cmd, location, resource_provider, resource_type):
    providers_client = None
    try:
        providers_client = providers_client_factory(cmd.cli_ctx, get_subscription_id(cmd.cli_ctx))
    except Exception as ex:
        handle_raw_exception(ex)

    resource_types = []
    if providers_client is not None:
        try:
            resource_types = getattr(providers_client.get(resource_provider), 'resource_types', [])
        except Exception as ex:
            handle_raw_exception(ex)

        res_locations = []
        for res in resource_types:
            if res and getattr(res, 'resource_type', "") == resource_type:
                res_locations = getattr(res, 'locations', [])

        res_locations = [res_loc.lower().replace(" ", "").replace("(", "").replace(")", "") for res_loc in res_locations if res_loc.strip()]

        location_formatted = location.lower().replace(" ", "")
        if location_formatted not in res_locations:
            raise ValidationError(f"Location '{location}' is not currently supported. To get list of supported locations, run `az provider show -n {resource_provider} --query \"resourceTypes[?resourceType=='{resource_type}'].locations\"`")
