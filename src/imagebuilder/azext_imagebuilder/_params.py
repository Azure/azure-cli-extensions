# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')
    image_template_name = CLIArgumentType(overrides=name_arg_type,
                                          help='The name of the image Template', id_part='name')

    with self.argument_context('imagebuilder create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('image_template_name', image_template_name)
        c.argument('location', arg_type=get_location_type(self.cli_ctx),
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('customize', id_part=None, help='Specify the properties used to describe the customization steps of the image, like Image source etc')
        c.argument('build_timeout_in_minutes', id_part=None, help='Maximum duration to wait while building the image template. Omit or specify 0 to use the default (4 hours).')
        c.argument('vm_size', id_part=None, help='Size of the virtual machine used to build, customize and capture images. Omit or specify empty string to use the default (Standard_D1_v2).')
        c.argument('_type', options_list=['--type'], arg_type=get_enum_type(['UserAssigned', 'None']), id_part=None, help='The type of identity used for the image template. The type \'None\' will remove any identities from the image template.')
        c.argument('user_assigned_identities', id_part=None, help='The list of user identities associated with the image template. The user identity dictionary key references will be ARM resource ids in the form: \'/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}\'.')

    with self.argument_context('imagebuilder create', arg_group='Source') as c:
        c.argument('source_type',
                   arg_type=get_enum_type(['ISO', 'PlatformImage', 'ManagedImage', 'SharedImageVersion']),
                   help='The type of source image you want to start with')
        c.argument('source_image',
                   help='Name or ID of managed image or ID of image version in the shared image gallery')
        c.argument('source_uri',
                   help='URI to get the ISO image. This URI has to be accessible to the resource provider '
                        'at the time of the image template creation.')
        c.argument('source_checksum', help='SHA256 Checksum of the ISO image')
        c.argument('source_urn', help='URN of PlatformImage. Format: publisher:offer:sku:version')

    with self.argument_context('imagebuilder create', arg_group='Distribute') as c:
        c.argument('distribute_type', arg_type=get_enum_type(['ManagedImage', 'SharedImage', 'VHD']),
                   help='Type of distribution')
        c.argument('distribute_location', nargs='+',
                   help='Location of managed image or locations of Shared Image Gallery image')
        c.argument('distribute_image', help='Name or ID of managed image or ID of Shared Image Gallery image')
        c.argument('run_output_name', help='The name to be used for the associated RunOutput')
        c.argument('artifact_tag', tags_type,
                   help='Tags that will be applied to the artifact once it has been created/updated by the distributor')

    with self.argument_context('imagebuilder update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('image_template_name', image_template_name)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('build_timeout_in_minutes', id_part=None, help='Maximum duration to wait while building the image template. Omit or specify 0 to use the default (4 hours).')
        c.argument('vm_profile_vm_size', id_part=None, help='Size of the virtual machine used to build, customize and capture images. Omit or specify empty string to use the default (Standard_D1_v2).')
        c.argument('_type', options_list=['--type'], arg_type=get_enum_type(['UserAssigned', 'None']), id_part=None, help='The type of identity used for the image template. The type \'None\' will remove any identities from the image template.')
        c.argument('user_assigned_identities', id_part=None, help='The list of user identities associated with the image template. The user identity dictionary key references will be ARM resource ids in the form: \'/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}\'.')

    with self.argument_context('imagebuilder delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('image_template_name', image_template_name)

    with self.argument_context('imagebuilder show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('image_template_name', image_template_name)

    with self.argument_context('imagebuilder list') as c:
        c.argument('resource_group', resource_group_name_type)

    with self.argument_context('imagebuilder run') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('image_template_name', image_template_name)

    with self.argument_context('imagebuilder list_run_outputs') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('image_template_name', image_template_name)

    with self.argument_context('imagebuilder get_run_output') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('image_template_name', id_part=None, help='The name of the image Template')
        c.argument('name', id_part=None, help='The name of the run output')
