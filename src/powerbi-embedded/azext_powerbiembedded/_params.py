# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_location_type,
    get_enum_type
)

from azure.cli.core.commands.validators import get_default_location_from_resource_group


def load_arguments(self, _):

    with self.argument_context('powerbi-embedded workspace-collection') as c:
        c.argument('name', options_list=['--name', '-n'], id_part='name', help='Power BI Embedded Workspace Collection name')
        c.argument('tags', tags_type)
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)

    with self.argument_context('powerbi-embedded workspace-collection regenerate-key') as c:
        c.argument('key_name', arg_type=get_enum_type(['key1', 'key2']), help='Name of the key which will be regenerated.')

    with self.argument_context('powerbi-embedded workspace-collection workspace list') as c:
        c.argument('workspace_collection_name', help='Power BI Embedded Workspace Collection name')
