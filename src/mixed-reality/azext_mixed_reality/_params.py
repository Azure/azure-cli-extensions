# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import get_enum_type

def load_arguments(self, _):
    with self.argument_context('spatial_anchors_account create') as c:
        c.argument('resource_group_name', help='Name of an Azure resource group.')
        c.argument('spatial_anchors_account_name', options_list=('--name'), help='Name of an Mixed Reality Spatial Anchors Account.')
        c.argument('location', help='The geo-location where the resource lives.')
        c.argument('tags', help='Resource tags.')
