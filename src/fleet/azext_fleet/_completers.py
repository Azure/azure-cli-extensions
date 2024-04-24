# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


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
        warn(f'Warning: {err.message}')

    return None
