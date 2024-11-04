# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    test2_name_type = CLIArgumentType(options_list='--test2-name-name', help='Name of the Test2.', id_part='name')

    with self.argument_context('test2') as c:
        c.argument('api_version')
        c.argument('model_format')
        c.argument('model_name')
        c.argument('model_version')
        #c.argument('tags', tags_type)
        #c.argument('location', validator=get_default_location_from_resource_group)
        #c.argument('test2_name', test2_name_type, options_list=['--name', '-n'])

    with self.argument_context('test2 list') as c:
        c.argument('test2_name', test2_name_type, id_part=None)
