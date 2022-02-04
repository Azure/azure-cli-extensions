# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import (ResourceNotFoundError, ValidationError)
from azure.cli.core.commands.client_factory import get_subscription_id

from ._client_factory import providers_client_factory, cf_resource_groups


def _get_location_from_resource_group(cli_ctx, resource_group_name):
    client = cf_resource_groups(cli_ctx)
    group = client.get(resource_group_name)
    return group.location


def _validate_subscription_registered(cmd, resource_provider):
    providers_client = None
    try:
        providers_client = providers_client_factory(cmd.cli_ctx, get_subscription_id(cmd.cli_ctx))
        registration_state = getattr(providers_client.get(resource_provider), 'registration_state', "NotRegistered")

        if not (registration_state and registration_state.lower() == 'registered'):
            raise ValidationError('Subscription is not registered for the {} resource provider. Please run \"az provider register -n {} --wait\" to register your subscription.'.format(
                resource_provider, resource_provider))
    except ValidationError as ex:
        raise ex
    except Exception:
        pass


def _ensure_location_allowed(cmd, location, resource_provider):
    providers_client = None
    try:
        providers_client = providers_client_factory(cmd.cli_ctx, get_subscription_id(cmd.cli_ctx))

        if providers_client is not None:
            resource_types = getattr(providers_client.get(resource_provider), 'resource_types', [])
            res_locations = []
            for res in resource_types:
                if res and getattr(res, 'resource_type', "") == 'containerApps':
                    res_locations = getattr(res, 'locations', [])

            res_locations = [res_loc.lower().replace(" ", "") for res_loc in res_locations if res_loc.strip()]

            location_formatted = location.lower().replace(" ", "")
            if location_formatted not in res_locations:
                raise ValidationError("Location '{}' is not currently supported. To get list of supported locations, run `az provider show -n {} --query 'resourceTypes[?resourceType=='containerApps'].locations'`".format(
                    location, resource_provider))
    except ValidationError as ex:
        raise ex
    except Exception:
        pass
