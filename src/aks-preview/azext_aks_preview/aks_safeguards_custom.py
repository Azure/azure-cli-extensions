# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Custom classes for AKS Safeguards commands to support -g/-n argument pattern
"""

from azure.cli.core.aaz import AAZResourceGroupNameArg, AAZStrArg, has_value
from azure.cli.core.azclierror import ArgumentUsageError, CLIError, HTTPError
from azure.cli.core.util import send_raw_request

from azext_aks_preview.aaz.latest.aks.safeguards._create import Create
from azext_aks_preview.aaz.latest.aks.safeguards._delete import Delete
from azext_aks_preview.aaz.latest.aks.safeguards._list import List
from azext_aks_preview.aaz.latest.aks.safeguards._show import Show
from azext_aks_preview.aaz.latest.aks.safeguards._update import Update
from azext_aks_preview.aaz.latest.aks.safeguards._wait import Wait


def _validate_and_set_managed_cluster_argument(ctx):
    """
    Validates that either managed_cluster OR (resource_group AND cluster_name) are provided,
    but not both. Then constructs the managed_cluster resource ID from -g and -n if needed.
    """
    args = ctx.args
    has_managed_cluster = has_value(args.managed_cluster)
    has_rg_and_cluster = has_value(args.resource_group) and has_value(args.cluster_name)

    # Ensure exactly one of the two conditions is true
    if has_managed_cluster == has_rg_and_cluster:
        raise ArgumentUsageError(
            "You must provide either 'managed_cluster' or both 'resource_group' and 'cluster_name', but not both."
        )

    if not has_managed_cluster:
        # Construct the managed cluster resource ID from resource group and cluster name
        args.managed_cluster = (
            f"/subscriptions/{ctx.subscription_id}/resourceGroups/{args.resource_group}/"
            f"providers/Microsoft.ContainerService/managedClusters/{args.cluster_name}"
        )
    else:
        # If managed_cluster is provided, normalize it (add leading slash if missing)
        managed_cluster_value = args.managed_cluster.to_serialized_data()

        # Normalize resource ID: add leading slash if missing for backward compatibility
        if managed_cluster_value and not managed_cluster_value.startswith('/'):
            managed_cluster_value = f"/{managed_cluster_value}"

        args.managed_cluster = managed_cluster_value


def _add_resource_group_cluster_name_args(_args_schema):
    """
    Adds -g/--resource-group and -n/--name arguments to the schema and makes
    managed_cluster optional (so users can choose either pattern).
    """
    _args_schema.resource_group = AAZResourceGroupNameArg(
        options=["-g", "--resource-group"],
        help=r"The name of the resource group. You can configure the default group using "
             r"`az configure --defaults group=`<name>``. You may provide either --managed-cluster "
             r"or both --resource-group and --name, but not both.",
        required=False,
    )
    _args_schema.cluster_name = AAZStrArg(
        options=["--name", "-n"],
        help="The name of the Managed Cluster. You may provide either --managed-cluster "
             "or both --resource-group and --name, but not both.",
        required=False,
    )
    _args_schema.managed_cluster._required = False  # pylint: disable=protected-access
    return _args_schema


class AKSSafeguardsShowCustom(Show):
    """Custom Show command for AKS Safeguards with -g/-n support"""

    def pre_operations(self):
        _validate_and_set_managed_cluster_argument(self.ctx)

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        _args_schema = super()._build_arguments_schema(*args, **kwargs)
        return _add_resource_group_cluster_name_args(_args_schema)


class AKSSafeguardsDeleteCustom(Delete):
    """Custom Delete command for AKS Safeguards with -g/-n support"""

    def pre_operations(self):
        _validate_and_set_managed_cluster_argument(self.ctx)

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        _args_schema = super()._build_arguments_schema(*args, **kwargs)
        return _add_resource_group_cluster_name_args(_args_schema)


class AKSSafeguardsUpdateCustom(Update):
    """Custom Update command for AKS Safeguards with -g/-n support"""

    def pre_operations(self):
        _validate_and_set_managed_cluster_argument(self.ctx)

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        _args_schema = super()._build_arguments_schema(*args, **kwargs)
        return _add_resource_group_cluster_name_args(_args_schema)


class AKSSafeguardsCreateCustom(Create):
    """Custom Create command for AKS Safeguards with -g/-n support and idempotency check"""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        _args_schema = super()._build_arguments_schema(*args, **kwargs)
        return _add_resource_group_cluster_name_args(_args_schema)

    def pre_operations(self):
        # Validate and set managed cluster argument
        _validate_and_set_managed_cluster_argument(self.ctx)

        # Check if Deployment Safeguards already exists before attempting create
        resource_uri = self.ctx.args.managed_cluster.to_serialized_data()

        # Validate resource_uri format to prevent URL injection
        if not resource_uri.startswith('/subscriptions/'):
            raise CLIError(f"Invalid managed cluster resource ID format: {resource_uri}")

        # Construct the GET URL to check if resource already exists
        api_version = self._aaz_info['version']
        safeguards_url = (
            f"https://management.azure.com{resource_uri}/providers/"
            f"Microsoft.ContainerService/deploymentSafeguards/default?api-version={api_version}"
        )

        # Check if resource already exists
        resource_exists = False
        try:
            response = send_raw_request(self.ctx.cli_ctx, "GET", safeguards_url)
            if response.status_code == 200:
                resource_exists = True
        except HTTPError as ex:
            # 404 means resource doesn't exist, which is expected for create
            if ex.response.status_code != 404:
                # Re-raise if it's not a 404 - could be auth issue, network problem, etc.
                raise

        # If resource exists, block the create
        if resource_exists:
            raise CLIError(
                "Deployment Safeguards instance already exists for this cluster. "
                "Please use 'az aks safeguards update' to modify the configuration, "
                "or 'az aks safeguards delete' to remove it before creating a new one."
            )


class AKSSafeguardsListCustom(List):
    """Custom List command for AKS Safeguards with -g/-n support"""

    def pre_operations(self):
        _validate_and_set_managed_cluster_argument(self.ctx)

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        _args_schema = super()._build_arguments_schema(*args, **kwargs)
        return _add_resource_group_cluster_name_args(_args_schema)


class AKSSafeguardsWaitCustom(Wait):
    """Custom Wait command for AKS Safeguards with -g/-n support"""

    def pre_operations(self):
        _validate_and_set_managed_cluster_argument(self.ctx)

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        _args_schema = super()._build_arguments_schema(*args, **kwargs)
        return _add_resource_group_cluster_name_args(_args_schema)
