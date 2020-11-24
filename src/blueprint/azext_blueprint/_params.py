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
    get_location_type,
    file_type
)
from azure.cli.core.commands.validators import validate_file_or_dict
from knack.arguments import CLIArgumentType
from argcomplete.completers import FilesCompleter

from ._validators import blueprint_validator, blueprint_assignment_validator

from .vendored_sdks.blueprint.models._blueprint_management_client_enums import (
    BlueprintTargetScope,
    ManagedServiceIdentityType,
    AssignmentLockMode
)


parameter_type = CLIArgumentType(
    type=validate_file_or_dict,
    options_list=['--parameters', '-p'],
    help='Parameters in JSON string or path to JSON file.',
    completer=FilesCompleter()
)

template_type = CLIArgumentType(
    type=validate_file_or_dict,
    options_list=['--template', '-t'],
    help='ARM template in JSON string or path to JSON file.',
    completer=FilesCompleter()
)

subscription_type = CLIArgumentType(
    arg_group='Scope',
    options_list=['--subscription', '-s'],
    help='Use subscription for the scope of the blueprint. If --management-group is not specified, --subscription value or the default subscription will be used as the scope.'
)

management_group_type = CLIArgumentType(
    arg_group='Scope',
    options_list=['--management-group', '-m'],
    help='Use management group for the scope of the blueprint.'
)


def load_arguments(self, _):

    with self.argument_context('blueprint', validator=blueprint_validator) as c:
        c.ignore('scope')  # scope is divided into management_group and subscription
        c.ignore('_subscription')  # ignore the global subscription param
        c.argument('subscription', arg_type=subscription_type)
        c.argument('management_group', arg_type=management_group_type)

    with self.argument_context('blueprint create') as c:
        c.argument('blueprint_name', options_list=['--name', '-n'], help='Name of the blueprint definition.')
        c.argument('display_name', help='One-liner string explain this resource.')
        c.argument('description', help='Multi-line explain this resource.')
        c.argument('target_scope', arg_type=get_enum_type(BlueprintTargetScope), default='subscription', help='The scope where this blueprint definition can be assigned.')
        c.argument('parameters', arg_type=parameter_type, help='Parameters required by this blueprint definition. It can be a JSON string or JSON file path.')

    with self.argument_context('blueprint import') as c:
        c.argument('blueprint_name', options_list=['--name', '-n'], help='Name of the blueprint definition.')
        c.argument('input_path', type=file_type, help='The directory path for json definitions of the blueprint and artifacts. The blueprint definition file should be named blueprint.json. Artifacts json files should be in a subdirectory named artifacts.', completer=FilesCompleter())

    with self.argument_context('blueprint update') as c:
        c.argument('blueprint_name', options_list=['--name', '-n'], help='Name of the blueprint definition.')
        c.argument('description', help='Multi-line explain this resource.')
        c.argument('parameters', arg_type=parameter_type, help='Parameters required by this blueprint definition. It can be a JSON string or JSON file path.')

    with self.argument_context('blueprint delete') as c:
        c.argument('blueprint_name', options_list=['--name', '-n'], help='Name of the blueprint definition.')

    with self.argument_context('blueprint show') as c:
        c.argument('blueprint_name', options_list=['--name', '-n'], help='Name of the blueprint definition.')

    with self.argument_context('blueprint list') as c:
        pass

    with self.argument_context('blueprint artifact delete') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', options_list=['--name', '-n'], help='Name of the blueprint artifact.')

    with self.argument_context('blueprint artifact show') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', options_list=['--name', '-n'], help='Name of the blueprint artifact.')

    with self.argument_context('blueprint artifact list') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')

    with self.argument_context('blueprint resource-group add') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('rg_name', help='Name of this resource group. Leave empty if the resource group name will be specified during the blueprint assignment.')
        c.argument('rg_location', help='Location of this resource group. Leave empty if the resource group location will be specified during the blueprint assignment.')
        c.argument('artifact_name', help='A unique name of this resource group artifact.')
        c.argument('display_name', help='Display name of this resource group artifact.')
        c.argument('description', help='Description of the blueprint artifact.')
        c.argument('depends_on', nargs='+', help='Artifacts which need to be deployed before the specified artifact.')
        c.argument('tags', tags_type, help='Tags to be assigned to this resource group.')

    with self.argument_context('blueprint resource-group update') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('rg_name', help='Name of this resource group. Leave empty if the resource group name will be specified during the blueprint assignment.')
        c.argument('rg_location', help='Location of this resource group. Leave empty if the resource group location will be specified during the blueprint assignment.')
        c.argument('artifact_name', help='A unique name of this resource group artifact.')
        c.argument('display_name', help='Display name of this resource group artifact.')
        c.argument('description', help='Description of the blueprint artifact.')
        c.argument('depends_on', nargs='*', help="Artifacts which need to be deployed before the specified artifact. Use '--depends-on' with no values to remove dependencies.")
        c.argument('tags', tags_type, arg_group='Resource Group', help='Tags to be assigned to this resource group.')

    with self.argument_context('blueprint resource-group remove') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='A unique name of this resource group artifact.')

    with self.argument_context('blueprint resource-group show') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='A unique name of this resource group artifact.')

    with self.argument_context('blueprint resource-group list') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')

    with self.argument_context('blueprint artifact policy create') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='Name of the blueprint artifact.')
        c.argument('display_name', help='DisplayName of this artifact.')
        c.argument('description', help='Description of the blueprint artifact.')
        c.argument('depends_on', nargs='+', help='Artifacts which need to be deployed before the specified artifact.')
        c.argument('policy_definition_id', help='The full policy definition id.')
        c.argument('resource_group_art', help='Name of the resource group artifact to which the policy will be assigned.')
        c.argument('parameters', arg_type=parameter_type, help='Parameters for policy assignment artifact. It can be a JSON string or JSON file path.')

    with self.argument_context('blueprint artifact policy update') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='Name of the blueprint artifact.')
        c.argument('display_name', help='DisplayName of this artifact.')
        c.argument('description', help='Description of the blueprint artifact.')
        c.argument('depends_on', nargs='*', help="Artifacts which need to be deployed before the specified artifact. Use '--depends-on' with no values to remove dependencies.")
        c.argument('resource_group_art', help='Name of the resource group artifact to which the policy will be assigned.')
        c.argument('parameters', arg_type=parameter_type, help='Parameters for policy assignment artifact. It can be a JSON string or JSON file path.')

    with self.argument_context('blueprint artifact role create') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='Name of the blueprint artifact.')
        c.argument('display_name', help='DisplayName of this artifact.')
        c.argument('description', help='Description of the blueprint artifact.')
        c.argument('depends_on', nargs='+', help='Artifacts which need to be deployed before the specified artifact.')
        c.argument('role_definition_id', help='The full role definition id. Only built-in roles are supported.')
        c.argument('resource_group_art', help='Name of the resource group artifact to which the policy will be assigned.')
        c.argument('principal_ids', nargs='+', help='Array of user or group identities in Azure Active Directory or a reference to the corresponding parameter in blueprint definiton. The roleDefinition will apply to each identity.')

    with self.argument_context('blueprint artifact role update') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='Name of the blueprint artifact.')
        c.argument('display_name', help='DisplayName of this artifact.')
        c.argument('description', help='Description of the blueprint artifact.')
        c.argument('depends_on', nargs='*', help="Artifacts which need to be deployed before the specified artifact. Use '--depends-on' with no values to remove dependencies.")
        c.argument('resource_group_art', help='Name of the resource group artifact to which the policy will be assigned.')

    with self.argument_context('blueprint artifact template create') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='Name of the blueprint artifact.')
        c.argument('display_name', help='DisplayName of this artifact.')
        c.argument('description', help='Description of the blueprint artifact.')
        c.argument('depends_on', nargs='+', help='Artifacts which need to be deployed before the specified artifact.')
        c.argument('resource_group_art', help='Name of the resource group artifact to which the policy will be assigned.')
        c.argument('parameters', arg_type=parameter_type, help='Parameters for ARM template artifact. It can be a JSON string or JSON file path.')
        c.argument('template', arg_type=template_type)

    with self.argument_context('blueprint artifact template update') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='Name of the blueprint artifact.')
        c.argument('display_name', help='DisplayName of this artifact.')
        c.argument('description', help='Description of the blueprint artifact.')
        c.argument('depends_on', nargs='*', help="Artifacts which need to be deployed before the specified artifact. Use '--depends-on' with no values to remove dependencies.")
        c.argument('resource_group_art', help='Name of the resource group artifact to which the policy will be assigned.')
        c.argument('parameters', arg_type=parameter_type, help='Parameters for ARM template artifact. It can be a JSON string or JSON file path.')
        c.argument('template', arg_type=template_type)

    with self.argument_context('blueprint publish') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('version_id', options_list=['--version'], help='Version of the published blueprint definition.')
        c.argument('change_notes', help='Version-specific change notes.')

    with self.argument_context('blueprint version delete') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('version_id', options_list=['--version'], help='Version of the published blueprint definition.')

    with self.argument_context('blueprint version show') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('version_id', options_list=['--version'], help='Version of the published blueprint definition.')

    with self.argument_context('blueprint version list') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')

    with self.argument_context('blueprint version artifact show') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('version_id', options_list=['--version'], help='Version of the published blueprint definition.')
        c.argument('artifact_name', help='Name of the blueprint artifact.')

    with self.argument_context('blueprint version artifact list') as c:
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('version_id', options_list=['--version'], help='Version of the published blueprint definition.')

    with self.argument_context('blueprint assignment', validator=blueprint_assignment_validator) as c:
        # override help
        c.argument('subscription', help='Use subscription for the target scope of the blueprint assignment. Default susbcription will be used if option not specified.')
        c.argument('management_group', help='Use management group for the target scope of the blueprint assignment. It is reserved for future use. Use --subscription instead.')

    for scope in ['create', 'update']:
        with self.argument_context('blueprint assignment ' + scope) as c:
            from .action import ResourceGroupAssignAddAction
            c.argument('assignment_name', options_list=['--name', '-n'], help='Name of the blueprint assignment.')
            c.argument('location', arg_type=get_location_type(self.cli_ctx))
            c.argument('user_assigned_identity', arg_group='Identity', help='The user-assigned managed identity associated with the resource.')
            c.argument('display_name', help='One-liner string explain this resource.')
            c.argument('description', help='Multi-line explain this resource.')
            c.argument('blueprint_id', options_list=['--blueprint-version'], help='Resource ID of the published version of a blueprint definition.')
            c.argument('parameters', arg_type=parameter_type, help='Blueprint assignment parameter values. It can be a JSON string or JSON file path.')
            c.argument('resource_groups', options_list=['--resource-group-value'], action=ResourceGroupAssignAddAction, nargs='+', help="Key=Value pairs for a resource group. Keys include 'artifact_name'(required), 'name', 'location'.")
            c.argument('locks_mode', arg_type=get_enum_type(AssignmentLockMode), help='Lock mode.')
            c.argument('locks_excluded_principals', help='List of AAD principals excluded from blueprint locks. Up to 5 principals are permitted.', nargs='+')

    with self.argument_context('blueprint assignment create') as c:
        c.argument('identity_type', arg_type=get_enum_type(ManagedServiceIdentityType), default='SystemAssigned', arg_group='Identity', help='Type of the managed identity.')

    with self.argument_context('blueprint assignment update') as c:
        c.argument('identity_type', arg_type=get_enum_type(ManagedServiceIdentityType), arg_group='Identity', help='Type of the managed identity.')

    with self.argument_context('blueprint assignment delete') as c:
        c.argument('assignment_name', options_list=['--name', '-n'], help='Name of the blueprint assignment.')

    with self.argument_context('blueprint assignment show') as c:
        c.argument('assignment_name', options_list=['--name', '-n'], help='Name of the blueprint assignment.')

    with self.argument_context('blueprint assignment list') as c:
        pass

    with self.argument_context('blueprint assignment wait') as c:
        # extra argument cannot be registered to a group-level scope, have to redefine
        # management_group and subscription as extra at command level here
        # for a non-custom command.
        c.extra('subscription', arg_type=subscription_type, help='Use subscription for the target scope of the blueprint assignment. Default susbcription will be used if option not specified.')
        c.extra('management_group', arg_type=management_group_type, help='Use management group for the target scope of the blueprint assignment. It is reserved for future use. Use --subscription instead.')
        c.argument('assignment_name', options_list=['--name', '-n'], help='Name of the blueprint assignment.')

    with self.argument_context('blueprint assignment who') as c:
        c.argument('assignment_name', options_list=['--name', '-n'], help='Name of the blueprint assignment.')
