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

    shared_vm_extension_name = CLIArgumentType(overrides=name_arg_type, help='Name of Shared VM Extension.',
                                               id_part='name')

    with self.argument_context('vm extension publish') as c:
        c.argument('shared_vm_extension_name', shared_vm_extension_name, help='The name of the Shared VM Extension. The allowed characters are alphabets and numbers with dots and periods allowed in the middle. The maximum length is 80 characters.')
        c.argument('company_name', help='The company name of this Shared VM Extension.')
        c.argument('description', help='The description of this Shared VM Extension.')
        c.argument('eula', help='The privacy statement uri.')
        c.argument('homepage', help='The homepage uri.')
        c.argument('label', help='The label of this Shared VM Extension.')
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('privacy', help='The privacy statement uri.')
        c.argument('tags', tags_type)

    with self.argument_context('vm extension publish-version') as c:
        c.argument('shared_vm_extension_name', shared_vm_extension_name, help='The name of the shared VM Extension definition in which the Extension Version is to be created.')
        c.argument('shared_vm_extension_version_name', help='The name of the shared VM Extension Version to be created. Needs to follow semantic version name pattern: The allowed characters are digit and period. Digits must be within the range of a 32-bit integer. Format: <MajorVersion>.<MinorVersion>.<Patch>')
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)

