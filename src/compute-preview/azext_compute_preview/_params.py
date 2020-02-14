# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    # compute-preview_name_type = CLIArgumentType(options_list='--compute-preview-name-name', help='Name of the Compute-preview.', id_part='name')
    #
    # with self.argument_context('compute-preview') as c:
    #     c.argument('tags', tags_type)
    #     c.argument('location', validator=get_default_location_from_resource_group)
    #     c.argument('compute-preview_name', compute-preview_name_type, options_list=['--name', '-n'])
    #
    # with self.argument_context('compute-preview list') as c:
    #     c.argument('compute-preview_name', compute-preview_name_type, id_part=None)

    name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')

    shared_vm_extension_name = CLIArgumentType(overrides=name_arg_type, help='Name of shared vm extension.',
                                               id_part='name')

    with self.argument_context('vm extension publish') as c:
        c.argument('shared_vm_extension_name', shared_vm_extension_name)
        c.argument('company_name', help='The company name of this Shared VM Extension.')
        c.argument('description', help='The description of this Shared VM Extension.')
        c.argument('eula', help='The privacy statement uri.')
        c.argument('homepage', help='The homepage uri.')
        c.argument('label', help='The label of this Shared VM Extension.')
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('privacy', help='The privacy statement uri.')
        c.argument('tags', tags_type)
