# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_three_state_flag,
    get_enum_type,
    get_location_type
)

# from azext_databricks.action import (
#     PeeringAddAuthorizations
# )


def load_arguments(self, _):

    with self.argument_context('databricks workspace create') as c:
        c.argument('workspace_name', options_list=['--name', '-n'], help='The name of the workspace.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('managed_resource_group', help='The managed resource group to create. It can be either a name or a resource id.')
        c.argument('aml_workspace_id', help='Azure Machine Learning workspace id.')
        c.argument('custom_virtual_network_id', options_list=['--virtual-network-id'], help='Virtual network id.')
        c.argument('custom_public_subnet_name', options_list=['--public-subnet-name'], help='Public subnet name.')
        c.argument('custom_private_subnet_name', options_list=['--private-subnet-name'], help='Private subnet name.')
        c.argument('enable_no_public_ip', arg_type=get_three_state_flag(), options_list=['--no-public-ip'], help='Set true to disallow public IP. Default is false')
        c.argument('load_balancer_backend_pool_name', help='The name of load balancer backend pool name.')
        c.argument('load_balancer_id', help='Load balancer id.')
        c.argument('relay_namespace_name', help='The name of relay namespace. Default value is "dbrelay" as prefix, followed by random digits and letters.')
        c.argument('storage_account_name', help='Storage account name. Default value is "dbstorage" as prefix, followed by random digits and letters.')
        c.argument('storage_account_sku_name', help='Storage account SKU. Default value is "Standard_GRS".')
        c.argument('vnet_address_prefix', help='The vnet address prefix. Default value is "10.139".')
        c.argument('sku_name', options_list=['--sku'], arg_type=get_enum_type(['standard', 'premium', 'trial']), help='The SKU tier name.')

    with self.argument_context('databricks workspace update') as c:
        c.argument('workspace_name', options_list=['--name', '-n'], id_part='name', help='The name of the workspace.')
        c.argument('tags', tags_type)

    with self.argument_context('databricks workspace delete') as c:
        c.argument('workspace_name', options_list=['--name', '-n'], id_part='name', help='The name of the workspace.')

    with self.argument_context('databricks workspace show') as c:
        c.argument('workspace_name', options_list=['--name', '-n'], id_part='name', help='The name of the workspace.')

    with self.argument_context('databricks workspace list') as c:
        c.argument('list_all', options_list=['--all'], action='store_true', help='List all workspace under subscription.')

    with self.argument_context('databricks workspace wait') as c:
        c.argument('workspace_name', options_list=['--name', '-n'], id_part='name', help='The name of the workspace.')
