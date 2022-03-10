# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azure.cli.core.commands.validators import (
    get_default_location_from_resource_group,
    validate_file_or_dict
)
from azext_fidalgo.action import (
    AddParameters,
    AddGitHub,
    AddImageReference
)

def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type

    with self.argument_context('fidalgo dev project list') as c:
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')
        c.argument('filter_', options_list=['--filter'], type=str, help='An OData $filter clause to apply to the '
                   'operation.')
        c.argument('dev_center', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo dev pool list') as c:
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')
        c.argument('filter_', options_list=['--filter'], type=str, help='An OData $filter clause to apply to the '
                   'operation.')
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('dev_center', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo dev pool show') as c:
        c.argument('pool_name', options_list=['--name', '-n', '--pool-name'], type=str, help='The name of a pool of '
                   'virtual machines.')
        c.argument('project_name', options_list=['--project-name', '--project'], type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('dev_center', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo dev virtual-machine list') as c:
        c.argument('filter_', options_list=['--filter'], type=str, help='An OData $filter clause to apply to the '
                   'operation.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('user_id', type=str, help='The id of the user. If value is \'me\', the identity is taken from the '
                   'authentication context')
        c.argument('dev_center', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo dev virtual-machine show') as c:
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('user_id', type=str, help='The id of the user. If value is \'me\', the identity is taken from the '
                   'authentication context')
        c.argument('virtual_machine_name', options_list=['--name', '-n', '--virtual-machine-name'], type=str,
                   help='The name of a virtual machine.')
        c.argument('dev_center', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo dev virtual-machine create') as c:
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('user_id', type=str, help='The id of the user. If value is \'me\', the identity is taken from the '
                   'authentication context')
        c.argument('virtual_machine_name', options_list=['--name', '-n', '--virtual-machine-name'], type=str,
                   help='The name of a virtual machine.')
        c.argument('pool_name', type=str, help='The name of the virtual machine pool this machine belongs to.')
        c.argument('dev_center', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo dev virtual-machine delete') as c:
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('user_id', type=str, help='The id of the user. If value is \'me\', the identity is taken from the '
                   'authentication context')
        c.argument('virtual_machine_name', options_list=['--name', '-n', '--virtual-machine-name'], type=str,
                   help='The name of a virtual machine.')
        c.argument('dev_center', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo dev virtual-machine assign') as c:
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('user_id', type=str, help='The id of the user. If value is \'me\', the identity is taken from the '
                   'authentication context')
        c.argument('virtual_machine_name', options_list=['--name', '-n', '--virtual-machine-name'], type=str,
                   help='The name of a virtual machine.')
        c.argument('new_owner', type=str, help='Identifier of new owner')
        c.argument('dev_center', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo dev virtual-machine get-rdp-file-content') as c:
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('user_id', type=str, help='The id of the user. If value is \'me\', the identity is taken from the '
                   'authentication context')
        c.argument('virtual_machine_name', options_list=['--name', '-n', '--virtual-machine-name'], type=str,
                   help='The name of a virtual machine.')
        c.argument('dev_center', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo dev virtual-machine start') as c:
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('user_id', type=str, help='The id of the user. If value is \'me\', the identity is taken from the '
                   'authentication context')
        c.argument('virtual_machine_name', options_list=['--name', '-n', '--virtual-machine-name'], type=str,
                   help='The name of a virtual machine.')
        c.argument('dev_center', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo dev virtual-machine stop') as c:
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('user_id', type=str, help='The id of the user. If value is \'me\', the identity is taken from the '
                   'authentication context')
        c.argument('virtual_machine_name', options_list=['--name', '-n', '--virtual-machine-name'], type=str,
                   help='The name of a virtual machine.')
        c.argument('dev_center', type=str, help='The Fidalgo DevCenter.')
        c.argument('fidalgo_dns_suffix', type=str, help='Optional DevCenter DNS suffix')

    with self.argument_context('fidalgo dev environment list') as c:
        c.argument('dev_center', type=str, help='The DevCenter to operate on.')
        c.argument('fidalgo_dns_suffix', type=str, help='The DNS suffix used as the base for all fidalgo requests.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('filter_', options_list=['--filter'], type=str, help='An OData $filter clause to apply to the '
                   'operation.')

    with self.argument_context('fidalgo dev environment show') as c:
        c.argument('dev_center', type=str, help='The DevCenter to operate on.')
        c.argument('fidalgo_dns_suffix', type=str, help='The DNS suffix used as the base for all fidalgo requests.')
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='The name '
                   'of the environment.')

    with self.argument_context('fidalgo dev environment create') as c:
        c.argument('dev_center', type=str, help='The DevCenter to operate on.')
        c.argument('fidalgo_dns_suffix', type=str, help='The DNS suffix used as the base for all fidalgo requests.')
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='The name '
                   'of the environment.')
        c.argument('description', type=str, help='Description of the Environment.')
        c.argument('catalog_item_name', type=str, help='Name of the catalog item.')
        c.argument('deployment_parameters', type=validate_file_or_dict, help='Deployment parameters passed to catalog '
                   'item. Expected value: json-string/json-file/@json-file.')
        c.argument('environment_type', type=str, help='Environment type.')
        c.argument('owner', type=str, help='Identifier of the owner of this Environment.')
        c.argument('tags', tags_type)

    with self.argument_context('fidalgo dev environment update') as c:
        c.argument('dev_center', type=str, help='The DevCenter to operate on.')
        c.argument('fidalgo_dns_suffix', type=str, help='The DNS suffix used as the base for all fidalgo requests.')
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='The name '
                   'of the environment.')
        c.argument('description', type=str, help='Description of the Environment.')
        c.argument('catalog_item_name', type=str, help='Name of the catalog item.')
        c.argument('deployment_parameters', type=validate_file_or_dict, help='Deployment parameters passed to catalog '
                   'item. Expected value: json-string/json-file/@json-file.')

    with self.argument_context('fidalgo dev environment delete') as c:
        c.argument('dev_center', type=str, help='The DevCenter to operate on.')
        c.argument('fidalgo_dns_suffix', type=str, help='The DNS suffix used as the base for all fidalgo requests.')
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='The name '
                   'of the environment.')

    with self.argument_context('fidalgo dev environment deploy') as c:
        c.argument('dev_center', type=str, help='The DevCenter to operate on.')
        c.argument('fidalgo_dns_suffix', type=str, help='The DNS suffix used as the base for all fidalgo requests.')
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='The name '
                   'of the environment.')
        c.argument('parameters', type=validate_file_or_dict, help='Deployment parameters. Expected value: '
                   'json-string/json-file/@json-file.')

    with self.argument_context('fidalgo dev deployment list') as c:
        c.argument('dev_center', type=str, help='The DevCenter to operate on.')
        c.argument('fidalgo_dns_suffix', type=str, help='The DNS suffix used as the base for all fidalgo requests.')
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('environment_name', type=str, help='The name of the environment.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')
        c.argument('filter_', options_list=['--filter'], type=str, help='An OData $filter clause to apply to the '
                   'operation.')

    with self.argument_context('fidalgo dev catalog-item list') as c:
        c.argument('dev_center', type=str, help='The DevCenter to operate on.')
        c.argument('fidalgo_dns_suffix', type=str, help='The DNS suffix used as the base for all fidalgo requests.')
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')
        c.argument('filter_', options_list=['--filter'], type=str, help='An OData $filter clause to apply to the '
                   'operation.')

    with self.argument_context('fidalgo dev environment-type list') as c:
        c.argument('dev_center', type=str, help='The DevCenter to operate on.')
        c.argument('fidalgo_dns_suffix', type=str, help='The DNS suffix used as the base for all fidalgo requests.')
        c.argument('project_name', type=str, help='The Fidalgo Project upon which to execute operations.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')

    #control plane
    with self.argument_context('fidalgo admin dev-center list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')

    with self.argument_context('fidalgo admin dev-center show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', options_list=['--name', '-n', '--dev-center-name'], type=str, help='The name of '
                   'the devcenter.', id_part='name')

    with self.argument_context('fidalgo admin dev-center create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', options_list=['--name', '-n', '--dev-center-name'], type=str, help='The name of '
                   'the devcenter.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('identity_type', arg_type=get_enum_type(['SystemAssigned', 'UserAssigned',
                                                                             'SystemAssigned, UserAssigned', 'None']),
                   help='The type of identity used for the resource. The type \'SystemAssigned, UserAssigned\' '
                   'includes both an implicitly created identity and a user assigned identity. The type \'None\' will '
                   'remove any identities from the resource.', required=False, arg_group='Identity')
        c.argument('user_assigned_identity', type=str, help='The user identity '
                   'associated with the resource. The user identity references will be an ARM resource id '
                   'in the form: \'/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microso'
                   'ft.ManagedIdentity/userAssignedIdentities/{identityName}\'. ', arg_group='Identity')

    with self.argument_context('fidalgo admin dev-center update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', options_list=['--name', '-n', '--dev-center-name'], type=str, help='The name of '
                   'the devcenter.', id_part='name')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('identity_type', arg_type=get_enum_type(['SystemAssigned', 'UserAssigned',
                                                                             'SystemAssigned, UserAssigned', 'None']),
                   help='The type of identity used for the resource. The type \'SystemAssigned, UserAssigned\' '
                   'includes both an implicitly created identity and a user assigned identity. The type \'None\' will '
                   'remove any identities from the resource.', required=False, arg_group='Identity')
        c.argument('user_assigned_identities', type=validate_file_or_dict, help='The list of user identities '
                   'associated with the resource. The user identity dictionary key references will be ARM resource ids '
                   'in the form: \'/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microso'
                   'ft.ManagedIdentity/userAssignedIdentities/{identityName}\'. Expected value: '
                   'json-string/json-file/@json-file.', arg_group='Identity')

    with self.argument_context('fidalgo admin dev-center delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', options_list=['--name', '-n', '--dev-center-name'], type=str, help='The name of '
                   'the devcenter.', id_part='name')

    with self.argument_context('fidalgo admin dev-center attach-network') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', options_list=['--name', '-n', '--dev-center-name'], type=str, help='The name of '
                   'the devcenter.', id_part='name')
        c.argument('network_connection_id', type=str, help='Resource id of a Network Settings resource')

    with self.argument_context('fidalgo admin dev-center detach-network') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', options_list=['--name', '-n', '--dev-center-name'], type=str, help='The name of '
                   'the devcenter.', id_part='name')
        c.argument('network_connection_id', type=str, help='Resource id of a Network Settings resource')

    with self.argument_context('fidalgo admin dev-center wait') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', options_list=['--name', '-n', '--dev-center-name'], type=str, help='The name of '
                   'the devcenter.', id_part='name')

    with self.argument_context('fidalgo admin project list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')

    with self.argument_context('fidalgo admin project show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', options_list=['--name', '-n', '--project-name'], type=str, help='The name of the '
                   'project.', id_part='name')

    with self.argument_context('fidalgo admin project create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', options_list=['--name', '-n', '--project-name'], type=str, help='The name of the '
                   'project.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('dev_center_id', type=str, help='Resource Id of an associated DevCenter')
        c.argument('description', type=str, help='Description of the project.')

    with self.argument_context('fidalgo admin project update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', options_list=['--name', '-n', '--project-name'], type=str, help='The name of the '
                   'project.', id_part='name')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('dev_center_id', type=str, help='Resource Id of an associated DevCenter')
        c.argument('description', type=str, help='Description of the project.')

    with self.argument_context('fidalgo admin project delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', options_list=['--name', '-n', '--project-name'], type=str, help='The name of the '
                   'project.', id_part='name')

    with self.argument_context('fidalgo admin project wait') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', options_list=['--name', '-n', '--project-name'], type=str, help='The name of the '
                   'project.', id_part='name')

    with self.argument_context('fidalgo attached-network list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')
        c.argument('dev_center_name', type=str, help='The name of the devcenter.')

    with self.argument_context('fidalgo attached-network show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.', id_part='name')
        c.argument('attached_network_connection_name', options_list=['--name', '-n', '--attached-network-connection-name'], type=str, help='The name of the attached NetworkConnection.',
                   id_part='child_name_1')
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')

    with self.argument_context('fidalgo attached-network create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.')
        c.argument('attached_network_connection_name', options_list=['--name', '-n', '--attached-network-connection-name'], type=str, help='The name of the attached NetworkConnection.')
        c.argument('network_connection_resource_id', type=str, help='The resource ID of the NetworkConnection you want '
                   'to attach.')

    with self.argument_context('fidalgo attached-network update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('attached_network_connection_name', options_list=['--name', '-n', '--attached-network-connection-name'], type=str, help='The name of the attached NetworkConnection.',
                   id_part='child_name_1')
        c.argument('network_connection_resource_id', type=str, help='The resource ID of the NetworkConnection you want '
                   'to attach.')

    with self.argument_context('fidalgo attached-network delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('attached_network_connection_name', options_list=['--name', '-n', '--attached-network-connection-name'], type=str, help='The name of the attached NetworkConnection.',
                   id_part='child_name_1')

    with self.argument_context('fidalgo attached-network wait') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.', id_part='name')
        c.argument('attached_network_connection_name', type=str, help='The name of the attached NetworkConnection.',
                   id_part='child_name_1')
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')

    with self.argument_context('fidalgo admin environment list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')

    with self.argument_context('fidalgo admin environment show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.', id_part='name')
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='The name '
                   'of the environment.', id_part='child_name_1')

    with self.argument_context('fidalgo admin environment create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.')
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='The name '
                   'of the environment.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('description', type=str, help='Description of the Environment.')
        c.argument('catalog_item_name', type=str, help='Name of the catalog item.')
        c.argument('template_uri', type=str, help='Uri of a template used to deploy resources to the environment.')
        c.argument('deployment_parameters', type=validate_file_or_dict, help='Deployment parameters passed to catalog '
                   'item. Expected value: json-string/json-file/@json-file.')
        c.argument('environment_type', type=str, help='Environment type.')

    with self.argument_context('fidalgo admin environment update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.', id_part='name')
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='The name '
                   'of the environment.', id_part='child_name_1')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('description', type=str, help='Description of the Environment.')
        c.argument('catalog_item_name', type=str, help='Name of the catalog item.')
        c.argument('template_uri', type=str, help='Uri of a template used to deploy resources to the environment.')
        c.argument('deployment_parameters', type=validate_file_or_dict, help='Deployment parameters passed to catalog '
                   'item. Expected value: json-string/json-file/@json-file.')

    with self.argument_context('fidalgo admin environment delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.', id_part='name')
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='The name '
                   'of the environment.', id_part='child_name_1')

    with self.argument_context('fidalgo admin environment deploy') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.', id_part='name')
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='The name '
                   'of the environment.', id_part='child_name_1')
        c.argument('parameters', type=validate_file_or_dict, help='Deployment parameters passed to catalog item. '
                   'Expected value: json-string/json-file/@json-file.')

    with self.argument_context('fidalgo admin environment wait') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.', id_part='name')
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='The name '
                   'of the environment.', id_part='child_name_1')

    with self.argument_context('fidalgo admin deployment list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.')
        c.argument('environment_name', type=str, help='The name of the environment.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')

    with self.argument_context('fidalgo admin environment-type list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')
        c.argument('dev_center_name', type=str, help='The name of the devcenter.')

    with self.argument_context('fidalgo admin environment-type show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('environment_type_name', options_list=['--name', '-n', '--environment-type-name'], type=str,
                   help='The name of the environment type.', id_part='child_name_1')

    with self.argument_context('fidalgo admin environment-type create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.')
        c.argument('environment_type_name', options_list=['--name', '-n', '--environment-type-name'], type=str,
                   help='The name of the environment type.')
        c.argument('tags', tags_type)
        c.argument('description', type=str, help='Description of the environment type.')

    with self.argument_context('fidalgo admin environment-type update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('environment_type_name', options_list=['--name', '-n', '--environment-type-name'], type=str,
                   help='The name of the environment type.', id_part='child_name_1')
        c.argument('tags', tags_type)
        c.argument('description', type=str, help='Description of the environment type.')

    with self.argument_context('fidalgo admin environment-type delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('environment_type_name', options_list=['--name', '-n', '--environment-type-name'], type=str,
                   help='The name of the environment type.', id_part='child_name_1')

    with self.argument_context('fidalgo admin environment-type wait') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('environment_type_name', options_list=['--name', '-n', '--environment-type-name'], type=str,
                   help='The name of the environment type.', id_part='child_name_1')

    with self.argument_context('fidalgo admin catalog-item list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.')
        c.argument('catalog_name', type=str, help='The name of the Catalog.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')
        c.argument('project_name', type=str, help='The name of the project.')

    with self.argument_context('fidalgo admin catalog-item show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('catalog_name', type=str, help='The name of the Catalog.', id_part='child_name_1')
        c.argument('catalog_item_name', options_list=['--name', '-n', '--catalog-item-name'], type=str, help='The name '
                   'of the catalog item.', id_part='child_name_2')

    with self.argument_context('fidalgo admin catalog-item create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.')
        c.argument('catalog_name', type=str, help='The name of the Catalog.')
        c.argument('catalog_item_name', options_list=['--name', '-n', '--catalog-item-name'], type=str, help='The name '
                   'of the catalog item.')
        c.argument('description', type=str, help='Description of the catalog item.')
        c.argument('template_path', type=str, help='Path to the catalog item entrypoint file.', arg_group='Engine')
        c.argument('parameters', action=AddParameters, nargs='+', help='Parameters that can be provided to the catalog '
                   'item.', arg_group='Engine')

    with self.argument_context('fidalgo admin catalog-item update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('catalog_name', type=str, help='The name of the Catalog.', id_part='child_name_1')
        c.argument('catalog_item_name', options_list=['--name', '-n', '--catalog-item-name'], type=str, help='The name '
                   'of the catalog item.', id_part='child_name_2')
        c.argument('tags', tags_type)
        c.argument('description', type=str, help='Description of the catalog item.')

    with self.argument_context('fidalgo admin catalog-item delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('catalog_name', type=str, help='The name of the Catalog.', id_part='child_name_1')
        c.argument('catalog_item_name', options_list=['--name', '-n', '--catalog-item-name'], type=str, help='The name '
                   'of the catalog item.', id_part='child_name_2')

    with self.argument_context('fidalgo admin gallery list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')

    with self.argument_context('fidalgo admin gallery show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('gallery_name', options_list=['--name', '-n', '--gallery-name'], type=str, help='The name of the '
                   'gallery.', id_part='child_name_1')

    with self.argument_context('fidalgo admin gallery create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.')
        c.argument('gallery_name', options_list=['--name', '-n', '--gallery-name'], type=str, help='The name of the '
                   'gallery.')
        c.argument('gallery_resource_id', type=str, help='The resource ID of the backing Azure Compute Gallery.')

    with self.argument_context('fidalgo admin gallery update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('gallery_name', options_list=['--name', '-n', '--gallery-name'], type=str, help='The name of the '
                   'gallery.', id_part='child_name_1')
        c.argument('gallery_resource_id', type=str, help='The resource ID of the backing Azure Compute Gallery.')
        c.ignore('body')

    with self.argument_context('fidalgo admin gallery delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('gallery_name', options_list=['--name', '-n', '--gallery-name'], type=str, help='The name of the '
                   'gallery.', id_part='child_name_1')

    with self.argument_context('fidalgo admin gallery wait') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('gallery_name', options_list=['--name', '-n', '--gallery-name'], type=str, help='The name of the '
                   'gallery.', id_part='child_name_1')
                   
    with self.argument_context('fidalgo admin image list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.')
        c.argument('gallery_name', type=str, help='The name of the gallery.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')

    with self.argument_context('fidalgo admin image show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('gallery_name', type=str, help='The name of the gallery.', id_part='child_name_1')
        c.argument('image_name', options_list=['--name', '-n', '--image-name'], type=str,
                   help='The name of the image.', id_part='child_name_2')

    with self.argument_context('fidalgo admin image-version list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.')
        c.argument('gallery_name', type=str, help='The name of the gallery.')
        c.argument('image_name', type=str, help='The name of the image.')

    with self.argument_context('fidalgo admin image-version show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('gallery_name', type=str, help='The name of the gallery.', id_part='child_name_1')
        c.argument('image_name', type=str, help='The name of the image.', id_part='child_name_2')
        c.argument('version_name', type=str, help='The version of the image.', id_part='child_name_3')

    with self.argument_context('fidalgo admin catalog list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')

    with self.argument_context('fidalgo admin catalog show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('catalog_name', options_list=['--name', '-n', '--catalog-name'], type=str, help='The name of the '
                   'Catalog.', id_part='child_name_1')

    with self.argument_context('fidalgo admin catalog create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.')
        c.argument('catalog_name', options_list=['--name', '-n', '--catalog-name'], type=str, help='The name of the '
                   'Catalog.')
        c.argument('git_hub', action=AddGitHub, nargs='+', help='Properties for a GitHub catalog type.')
        c.argument('ado_git', action=AddGitHub, nargs='+', help='Properties for an Azure DevOps catalog type.')

    with self.argument_context('fidalgo admin catalog update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('catalog_name', options_list=['--name', '-n', '--catalog-name'], type=str, help='The name of the '
                   'Catalog.', id_part='child_name_1')
        c.argument('tags', tags_type)
        c.argument('git_hub', action=AddGitHub, nargs='+', help='Properties for a GitHub catalog type.')
        c.argument('ado_git', action=AddGitHub, nargs='+', help='Properties for an Azure DevOps catalog type.')

    with self.argument_context('fidalgo admin catalog delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('catalog_name', options_list=['--name', '-n', '--catalog-name'], type=str, help='The name of the '
                   'Catalog.', id_part='child_name_1')

    with self.argument_context('fidalgo admin catalog sync') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('catalog_name', options_list=['--name', '-n', '--catalog-name'], type=str, help='The name of the '
                   'Catalog.', id_part='child_name_1')

    with self.argument_context('fidalgo admin catalog wait') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('catalog_name', options_list=['--name', '-n', '--catalog-name'], type=str, help='The name of the '
                   'Catalog.', id_part='child_name_1')

    with self.argument_context('fidalgo admin mapping list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')

    with self.argument_context('fidalgo admin mapping show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('mapping_name', options_list=['--name', '-n', '--mapping-name'], type=str, help='Mapping name.',
                   id_part='child_name_1')

    with self.argument_context('fidalgo admin mapping create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.')
        c.argument('mapping_name', options_list=['--name', '-n', '--mapping-name'], type=str, help='Mapping name.')
        c.argument('mapped_subscription_id', type=str, help='Id of a subscription that the environment type will be '
                   'mapped to. The environment\'s resources will be deployed into this subscription.')
        c.argument('environment_type', type=str, help='Environment type (e.g. Dev/Test)')
        c.argument('project_id', type=str, help='Resource Id of a project that this mapping is associated with.')

    with self.argument_context('fidalgo admin mapping update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('mapping_name', options_list=['--name', '-n', '--mapping-name'], type=str, help='Mapping name.',
                   id_part='child_name_1')
        c.argument('mapped_subscription_id', type=str, help='Id of a subscription that the environment type will be '
                   'mapped to. The environment\'s resources will be deployed into this subscription.')

    with self.argument_context('fidalgo admin devbox-definition list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')

    with self.argument_context('fidalgo admin devbox-definition show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('dev_box_definition_name', options_list=['--name', '-n', '--dev-box-definition-name'], type=str,
                   help='The name of the Dev Box definition.', id_part='child_name_1')

    with self.argument_context('fidalgo admin devbox-definition create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.')
        c.argument('dev_box_definition_name', options_list=['--name', '-n', '--dev-box-definition-name'], type=str, help='The name of the Dev Box definition.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                    validator=get_default_location_from_resource_group)
        c.argument('image_reference', action=AddImageReference, nargs='+', help='Image reference information.')
        c.argument('sku_name', type=str, help='The name of the SKU.', arg_group='Sku')

    with self.argument_context('fidalgo admin devbox-definition update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('dev_box_definition_name', options_list=['--name', '-n', '--dev-box-definition-name'], type=str, help='The name of the Dev Box definition.',
                   id_part='child_name_1')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('image_reference', action=AddImageReference, nargs='+', help='Image reference information.')
        c.argument('sku_name', type=str, help='The name of the SKU.', arg_group='Sku')

    with self.argument_context('fidalgo admin devbox-definition delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('dev_box_definition_name', options_list=['--name', '-n', '--dev-box-definition-name'], type=str,
                   help='The name of the Dev Box definition.', id_part='child_name_1')

    with self.argument_context('fidalgo admin devbox-definition wait') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('dev_box_definition_name', options_list=['--name', '-n', '--dev-box-definition-name'], type=str,
                   help='The name of the Dev Box definition.', id_part='child_name_1')

    with self.argument_context('fidalgo admin mapping delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('dev_center_name', type=str, help='The name of the devcenter.', id_part='name')
        c.argument('mapping_name', options_list=['--name', '-n', '--mapping-name'], type=str, help='Mapping name.',
                   id_part='child_name_1')

    with self.argument_context('fidalgo admin operation-statuses show') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('operation_id', type=str, help='The ID of an ongoing async operation')

    with self.argument_context('fidalgo admin sku list') as c:
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')

    with self.argument_context('fidalgo admin pool list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.')
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')

    with self.argument_context('fidalgo admin pool show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.', id_part='name')
        c.argument('pool_name', options_list=['--name', '-n', '--pool-name'], type=str, help='Name of the pool.',
                   id_part='child_name_1')

    with self.argument_context('fidalgo admin pool create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.')
        c.argument('pool_name', options_list=['--name', '-n', '--pool-name'], type=str, help='Name of the pool.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('machine_definition_id', type=str, required=True, help='Resource Id of a Machine Definition')
        c.argument('dev_box_definition_name', type=str, help='Name of a Dev Box definition in parent Project of this Pool')
        c.argument('network_settings_id', type=str, required=True, help='Resource Id of a Network Settings resource')
        c.argument('network_connection_name', type=str, help='Name of a Network Connection in parent Project of this Pool')
        c.argument('sku_name', type=str, required=True, help='The name of the SKU.', arg_group='Sku')

    with self.argument_context('fidalgo admin pool update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.', id_part='name')
        c.argument('pool_name', options_list=['--name', '-n', '--pool-name'], type=str, help='Name of the pool.',
                   id_part='child_name_1')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('machine_definition_id', type=str, help='Resource Id of a Machine Definition')
        c.argument('dev_box_definition_name', type=str, help='Name of a Dev Box definition in parent Project of this Pool')
        c.argument('network_settings_id', type=str, required=True, help='Resource Id of a Network Settings resource')
        c.argument('network_connection_name', type=str, help='Name of a Network Connection in parent Project of this Pool')
        c.argument('sku_name', type=str, help='The name of the SKU.', arg_group='Sku')

    with self.argument_context('fidalgo admin pool delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.', id_part='name')
        c.argument('pool_name', options_list=['--name', '-n', '--pool-name'], type=str, help='Name of the pool.',
                   id_part='child_name_1')

    with self.argument_context('fidalgo admin pool wait') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('project_name', type=str, help='The name of the project.', id_part='name')
        c.argument('pool_name', options_list=['--name', '-n', '--pool-name'], type=str, help='Name of the pool.',
                   id_part='child_name_1')

    with self.argument_context('fidalgo admin machine-definition list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')

    with self.argument_context('fidalgo admin machine-definition show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('machine_definition_name', options_list=['--name', '-n', '--machine-definition-name'], type=str,
                   help='The name of the machine definition.', id_part='name')

    with self.argument_context('fidalgo admin machine-definition create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('machine_definition_name', options_list=['--name', '-n', '--machine-definition-name'], type=str,
                   help='The name of the machine definition.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('image_reference', action=AddImageReference, nargs='+', help='Image reference information.')

    with self.argument_context('fidalgo admin machine-definition update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('machine_definition_name', options_list=['--name', '-n', '--machine-definition-name'], type=str,
                   help='The name of the machine definition.', id_part='name')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('image_reference', action=AddImageReference, nargs='+', help='Image reference information.')

    with self.argument_context('fidalgo admin machine-definition delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('machine_definition_name', options_list=['--name', '-n', '--machine-definition-name'], type=str,
                   help='The name of the machine definition.', id_part='name')

    with self.argument_context('fidalgo admin machine-definition wait') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('machine_definition_name', options_list=['--name', '-n', '--machine-definition-name'], type=str,
                   help='The name of the machine definition.', id_part='name')

    with self.argument_context('fidalgo admin network-setting list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('top', type=int, help='The maximum number of resources to return from the operation. Example: '
                   '\'$top=10\'.')

    with self.argument_context('fidalgo admin network-setting show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('network_setting_name', options_list=['--name', '-n', '--network-setting-name'], type=str,
                   help='Name of the Network Settings that can be applied to a Pool.', id_part='name')

    with self.argument_context('fidalgo admin network-setting create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('network_setting_name', options_list=['--name', '-n', '--network-setting-name'], type=str,
                   help='Name of the Network Settings that can be applied to a Pool.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('subnet_id', type=str, help='The subnet to attach Virtual Machines to')
        c.argument('networking_resource_group_id', type=str, help='Target resource group id for NICs to be placed. '
                   'Required format: \'/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}\'')
        c.argument('domain_name', type=str, help='Active Directory domain name')
        c.argument('organization_unit', type=str, help='Active Directory domain Organization Unit (OU)')
        c.argument('domain_username', type=str, help='The username of an Active Directory account (user or service '
                   'account) that has permissions to create computer objects in Active Directory. Required format: '
                   'admin@contoso.com.')
        c.argument('domain_password', type=str, help='The password for the account used to join domain')
        c.argument('networking_resource_group_name', type=str, help='The name for the managed resource group where NICs will be '
                   'placed.')
        c.argument('domain_join_type', arg_type=get_enum_type(['HybridAzureADJoin', 'AzureADJoin']), help='AAD Join '
                   'type.')

    with self.argument_context('fidalgo admin network-setting update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('network_setting_name', options_list=['--name', '-n', '--network-setting-name'], type=str,
                   help='Name of the Network Settings that can be applied to a Pool.', id_part='name')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('subnet_id', type=str, help='The subnet to attach Virtual Machines to')
        c.argument('networking_resource_group_id', type=str, help='Target resource group id for NICs to be placed. '
                   'Required format: \'/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}\'')
        c.argument('domain_name', type=str, help='Active Directory domain name')
        c.argument('organization_unit', type=str, help='Active Directory domain Organization Unit (OU)')
        c.argument('domain_username', type=str, help='The username of an Active Directory account (user or service '
                   'account) that has permissions to create computer objects in Active Directory. Required format: '
                   'admin@contoso.com.')
        c.argument('domain_password', type=str, help='The password for the account used to join domain')

    with self.argument_context('fidalgo admin network-setting delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('network_setting_name', options_list=['--name', '-n', '--network-setting-name'], type=str,
                   help='Name of the Network Settings that can be applied to a Pool.', id_part='name')

    with self.argument_context('fidalgo admin network-setting show-health-detail') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('network_setting_name', options_list=['--name', '-n', '--network-setting-name'], type=str,
                   help='Name of the Network Settings that can be applied to a Pool.', id_part='name')

    with self.argument_context('fidalgo admin network-setting wait') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('network_setting_name', options_list=['--name', '-n', '--network-setting-name'], type=str,
                   help='Name of the Network Settings that can be applied to a Pool.', id_part='name')
