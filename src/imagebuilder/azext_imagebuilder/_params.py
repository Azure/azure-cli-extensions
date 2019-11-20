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


def load_arguments(self, _):

    with self.argument_context('imagebuilder create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('image_template_name', id_part=None, help='The name of the image Template')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('customize_name', id_part=None, help='Specifies the properties used to describe the customization steps of the image, like Image source etc', nargs='+')
        c.argument('distribute_run_output_name', id_part=None, help='The distribution targets where the image output needs to go to.', nargs='+')
        c.argument('distribute_artifact_tags', id_part=None, help='The distribution targets where the image output needs to go to.', nargs='+')
        c.argument('build_timeout_in_minutes', id_part=None, help='Maximum duration to wait while building the image template. Omit or specify 0 to use the default (4 hours).')
        c.argument('vm_profile_vm_size', id_part=None, help='Size of the virtual machine used to build, customize and capture images. Omit or specify empty string to use the default (Standard_D1_v2).')
        c.argument('_type', options_list=['--type'], arg_type=get_enum_type(['UserAssigned', 'None']), id_part=None, help='The type of identity used for the image template. The type \'None\' will remove any identities from the image template.')
        c.argument('user_assigned_identities', id_part=None, help='The list of user identities associated with the image template. The user identity dictionary key references will be ARM resource ids in the form: \'/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}\'.')

    with self.argument_context('imagebuilder update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('image_template_name', id_part=None, help='The name of the image Template')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('customize_name', id_part=None, help='Specifies the properties used to describe the customization steps of the image, like Image source etc', nargs='+')
        c.argument('distribute_run_output_name', id_part=None, help='The distribution targets where the image output needs to go to.', nargs='+')
        c.argument('distribute_artifact_tags', id_part=None, help='The distribution targets where the image output needs to go to.', nargs='+')
        c.argument('build_timeout_in_minutes', id_part=None, help='Maximum duration to wait while building the image template. Omit or specify 0 to use the default (4 hours).')
        c.argument('vm_profile_vm_size', id_part=None, help='Size of the virtual machine used to build, customize and capture images. Omit or specify empty string to use the default (Standard_D1_v2).')
        c.argument('_type', options_list=['--type'], arg_type=get_enum_type(['UserAssigned', 'None']), id_part=None, help='The type of identity used for the image template. The type \'None\' will remove any identities from the image template.')
        c.argument('user_assigned_identities', id_part=None, help='The list of user identities associated with the image template. The user identity dictionary key references will be ARM resource ids in the form: \'/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}\'.')

    with self.argument_context('imagebuilder delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('image_template_name', id_part=None, help='The name of the image Template')

    with self.argument_context('imagebuilder list') as c:
        c.argument('resource_group', resource_group_name_type)

    with self.argument_context('imagebuilder show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('image_template_name', id_part=None, help='The name of the image Template')

    with self.argument_context('imagebuilder run') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('image_template_name', id_part=None, help='The name of the image Template')

    with self.argument_context('imagebuilder list_run_outputs') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('image_template_name', id_part=None, help='The name of the image Template')

    with self.argument_context('imagebuilder get_run_output') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('image_template_name', id_part=None, help='The name of the image Template')
        c.argument('name', id_part=None, help='The name of the run output')

    with self.argument_context('imagebuilder list') as c:
        pass
