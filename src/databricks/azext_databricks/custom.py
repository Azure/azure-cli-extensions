# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument
from .aaz.latest.databricks.workspace.vnet_peering._create import Create as _WorkspaceVnetPeeringCreate
from .aaz.latest.databricks.workspace import Create as _DatabricksWorkspaceCreate, Update as _DatabricksWorkspaceUpdate

import random
import string

from azure.cli.core.aaz import has_value


def id_generator(size=13, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class DatabricksWorkspaceCreate(_DatabricksWorkspaceCreate):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.managed_resource_group._required = False
        args_schema.vnet._fmt = AAZResourceIdArgFormat(
            template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network/virtualNetworks/{}"
        )
        args_schema.disk_key_source._registered = False
        args_schema.managed_services_key_source._registered = False
        return args_schema

    def pre_operations(self):
        from msrestazure.tools import is_valid_resource_id, resource_id
        """Parse managed resource_group which can be either resource group name or id, generate a randomized name if not provided"""
        args = self.ctx.args
        subscription_id = self.ctx.subscription_id
        workspace_name = args.name.to_serialized_data()
        if has_value(args.managed_resource_group):
            managed_resource_group = args.managed_resource_group.to_serialized_data()

        if not has_value(args.managed_resource_group):
            args.managed_resource_group = resource_id(
                subscription=subscription_id,
                resource_group='databricks-rg-' + workspace_name + '-' + id_generator())
        elif not is_valid_resource_id(managed_resource_group):
            args.managed_resource_group = resource_id(
                subscription=subscription_id,
                resource_group=managed_resource_group)

        if has_value(args.disk_key_name):
            args.disk_key_source = 'Microsoft.Keyvault'
        if has_value(args.managed_services_key_name):
            args.managed_services_key_source = 'Microsoft.Keyvault'


class DatabricksWorkspaceUpdate(_DatabricksWorkspaceUpdate):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.disk_key_source._registered = False
        args_schema.managed_services_key_source._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.disk_key_name):
            args.disk_key_source = 'Microsoft.Keyvault'
        if has_value(args.managed_services_key_name):
            args.managed_services_key_source = 'Microsoft.Keyvault'


class WorkspaceVnetPeeringCreate(_WorkspaceVnetPeeringCreate):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.remote_vnet._fmt = AAZResourceIdArgFormat(
            template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network/virtualNetworks/{}"
        )
        return args_schema
