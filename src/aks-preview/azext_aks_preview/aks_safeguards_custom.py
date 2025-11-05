# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Custom classes for AKS Safeguards commands to support -g/-n argument pattern
"""

from azure.cli.core.aaz import AAZResourceGroupNameArg, AAZStrArg, has_value
from azure.cli.core.azclierror import ArgumentUsageError

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
            f"subscriptions/{ctx.subscription_id}/resourceGroups/{args.resource_group}/"
            f"providers/Microsoft.ContainerService/managedClusters/{args.cluster_name}"
        )


def _add_resource_group_cluster_name_args(_args_schema):
    """
    Adds -g/--resource-group and -n/--name arguments to the schema and makes
    managed_cluster optional (so users can choose either pattern).
    """
    _args_schema.resource_group = AAZResourceGroupNameArg(
        options=["-g", "--resource-group"],
        help="The name of the resource group. You can configure the default group using "
             "az configure --defaults group=<name>. You may provide either 'managed_cluster' "
             "or both 'resource_group' and 'name', but not both.",
        required=False,
    )
    _args_schema.cluster_name = AAZStrArg(
        options=["--name", "-n"],
        help="The name of the Managed Cluster. You may provide either 'managed_cluster' "
             "or both 'resource_group' and 'name', but not both.",
        required=False,
    )
    _args_schema.managed_cluster.required = False
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
    """Custom Create command for AKS Safeguards with -g/-n support"""

    def pre_operations(self):
        _validate_and_set_managed_cluster_argument(self.ctx)

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        _args_schema = super()._build_arguments_schema(*args, **kwargs)
        return _add_resource_group_cluster_name_args(_args_schema)


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
