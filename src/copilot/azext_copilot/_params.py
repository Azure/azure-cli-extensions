# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    copilot_name_type = CLIArgumentType(options_list='--copilot-name-name', help='Name of the Copilot.', id_part='name')

    with self.argument_context('copilot') as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('copilot_name', copilot_name_type, options_list=['--name', '-n'])
        c.argument('prompt', options_list=['--prompt', '-p'], help='Let CLI Copilot do your job for you.')

    with self.argument_context('copilot list') as c:
        c.argument('copilot_name', copilot_name_type, id_part=None)
