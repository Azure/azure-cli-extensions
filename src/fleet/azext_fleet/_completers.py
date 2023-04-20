# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import get_one_of_subscription_locations
from azure.cli.core.decorators import Completer


@Completer
def get_k8s_versions_completion_list(cmd, prefix, namespace, **kwargs):  # pylint: disable=unused-argument
    """Return Kubernetes versions available for provisioning a new cluster."""
    location = _get_location(cmd.cli_ctx, namespace)
    return get_k8s_versions(cmd.cli_ctx, location) if location else None


def get_k8s_versions(cli_ctx, location):
    """Return a list of Kubernetes versions available for a new cluster."""
    # TODO: Add cf_container_services in client_factory
    from azext_fleet._client_factory import cf_container_services
    from jmespath import search  # pylint: disable=import-error

    results = cf_container_services(cli_ctx).list_orchestrators(location, resource_type='managedClusters').as_dict()
    # Flatten all the "orchestrator_version" fields into one array
    return search('orchestrators[*].orchestrator_version', results)


def _get_location(cli_ctx, namespace):
    """
    Return an Azure location by using an explicit `--location` argument, then by `--resource-group`, and
    finally by the subscription if neither argument was provided.
    """
    location = None
    if getattr(namespace, 'location', None):
        location = namespace.location
    elif getattr(namespace, 'resource_group_name', None):
        location = _get_location_from_resource_group(cli_ctx, namespace.resource_group_name)
    if not location:
        location = get_one_of_subscription_locations(cli_ctx)
    return location


def _get_location_from_resource_group(cli_ctx, resource_group_name):
    from azext_fleet._client_factory import get_resource_groups_client
    from msrestazure.azure_exceptions import CloudError

    try:
        rg = get_resource_groups_client(cli_ctx).get(resource_group_name)
        return rg.location
    except CloudError as err:
        # Print a warning if the user hit [TAB] but the `--resource-group` argument was incorrect.
        # For example: "Warning: Resource group 'bogus' could not be found."
        from argcomplete import warn
        warn('Warning: {}'.format(err.message))
