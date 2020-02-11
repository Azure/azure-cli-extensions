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
    get_location_type
)
from knack.arguments import CLIArgumentType
from argcomplete.completers import FilesCompleter


parameter_type = CLIArgumentType(
    options_list=['--parameters'],
    help='Parameters in JSON format or file path to Json file with "@" prefix.'
)

template_type = CLIArgumentType(
    options_list=['--template'],
    help='ARM template in JSON format or file path to Json file with "@" prefix.'
)


def load_arguments(self, _):

    with self.argument_context('blueprint create') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', options_list=['--name', '-n'], help='Name of the blueprint definition.')
        c.argument('display_name', help='One-liner string explain this resource.')
        c.argument('description', help='Multi-line explain this resource.')
        c.argument('target_scope', arg_type=get_enum_type(['subscription', 'managementGroup']), help='The scope where this blueprint definition can be assigned.')
        c.argument('parameters', arg_type=parameter_type, help='Parameters required by this blueprint definition.')

    with self.argument_context('blueprint import') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', options_list=['--name', '-n'], help='Name of the blueprint definition.')
        c.argument('input_path', help='The directory path for json definitions of blueprint and artifacts. Artifacts json files should be in input-path/artifacts/.', completer=FilesCompleter())

    with self.argument_context('blueprint update') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', options_list=['--name', '-n'], help='Name of the blueprint definition.')
        c.argument('description', help='Multi-line explain this resource.')
        c.argument('parameters', arg_type=parameter_type, help='Parameters required by this blueprint definition.')

    with self.argument_context('blueprint delete') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', options_list=['--name', '-n'], help='Name of the blueprint definition.')

    with self.argument_context('blueprint show') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', options_list=['--name', '-n'], help='Name of the blueprint definition.')

    with self.argument_context('blueprint list') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')

    with self.argument_context('blueprint artifact delete') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='Name of the blueprint artifact.')

    with self.argument_context('blueprint artifact show') as c:
        c.argument('name_place_holder', id_part='name')
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='Name of the blueprint artifact.')

    with self.argument_context('blueprint artifact list') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')

    with self.argument_context('blueprint resource-group create') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('rg_name', help='Name of this resource group. Leave empty if the resource group name will be specified during the blueprint assignment.')
        c.argument('rg_location', help='Location of this resource group. Leave empty if the resource group location will be specified during the blueprint assignment.')
        c.argument('artifact_name', help='A unique name of this resource group artifact.')
        c.argument('display_name', help='Display name of this resource group artifact.')
        c.argument('description', help='Description of the blueprint artifact.')
        c.argument('depends_on', nargs='+', help='Artifacts which need to be deployed before the specified artifact.')
        c.argument('tags', tags_type, help='Tags to be assigned to this resource group.')

    with self.argument_context('blueprint resource-group update') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('rg_name', help='Name of this resource group. Leave empty if the resource group name will be specified during the blueprint assignment.')
        c.argument('rg_location', help='Location of this resource group. Leave empty if the resource group location will be specified during the blueprint assignment.')
        c.argument('artifact_name', help='A unique name of this resource group artifact.')
        c.argument('display_name', help='Display name of this resource group artifact.')
        c.argument('description', help='Description of the blueprint artifact.')
        c.argument('depends_on', nargs='+', help='Artifacts which need to be deployed before the specified artifact.')
        c.argument('tags', tags_type, arg_group='Resource Group', help='Tags to be assigned to this resource group.')

    with self.argument_context('blueprint resource-group delete') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='A unique name of this resource group artifact.')

    with self.argument_context('blueprint resource-group show') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='A unique name of this resource group artifact.')

    with self.argument_context('blueprint resource-group list') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')

    with self.argument_context('blueprint artifact policy create') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='Name of the blueprint artifact.')
        c.argument('display_name', help='DisplayName of this artifact.')
        c.argument('description', help='Description of the blueprint artifact.')
        c.argument('depends_on', nargs='+', help='Artifacts which need to be deployed before the specified artifact.')
        c.argument('policy_definition_id', help='Azure resource ID of the policy definition.')
        c.argument('resource_group_art', help='Name of the resource group artifact to which the policy will be assigned.')
        c.argument('parameters', arg_type=parameter_type)

    with self.argument_context('blueprint artifact policy update') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='Name of the blueprint artifact.')
        c.argument('display_name', help='DisplayName of this artifact.')
        c.argument('description', help='Description of the blueprint artifact.')
        c.argument('depends_on', nargs='+', help='Artifacts which need to be deployed before the specified artifact.')
        c.argument('resource_group_art', help='Name of the resource group artifact to which the policy will be assigned.')
        c.argument('parameters', arg_type=parameter_type)

    with self.argument_context('blueprint artifact role create') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='Name of the blueprint artifact.')
        c.argument('display_name', help='DisplayName of this artifact.')
        c.argument('description', help='Description of the blueprint artifact.')
        c.argument('depends_on', nargs='+', help='Artifacts which need to be deployed before the specified artifact.')
        c.argument('role_definition_id', help='Azure resource ID of the RoleDefinition.')
        c.argument('resource_group_art', help='Name of the resource group artifact to which the policy will be assigned.')
        c.argument('principal_ids', help='Array of user or group identities in Azure Active Directory. The roleDefinition will apply to each identity.')

    with self.argument_context('blueprint artifact role update') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='Name of the blueprint artifact.')
        c.argument('display_name', help='DisplayName of this artifact.')
        c.argument('description', help='Description of the blueprint artifact.')
        c.argument('depends_on', nargs='+', help='Artifacts which need to be deployed before the specified artifact.')
        c.argument('resource_group_art', help='Name of the resource group artifact to which the policy will be assigned.')

    with self.argument_context('blueprint artifact template create') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='Name of the blueprint artifact.')
        c.argument('display_name', help='DisplayName of this artifact.')
        c.argument('description', help='Description of the blueprint artifact.')
        c.argument('depends_on', nargs='+', help='Artifacts which need to be deployed before the specified artifact.')
        c.argument('resource_group_art', help='Name of the resource group artifact to which the policy will be assigned.')
        c.argument('parameters', arg_type=parameter_type)
        c.argument('template', arg_type=template_type)

    with self.argument_context('blueprint artifact template update') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('artifact_name', help='Name of the blueprint artifact.')
        c.argument('display_name', help='DisplayName of this artifact.')
        c.argument('description', help='Description of the blueprint artifact.')
        c.argument('depends_on', nargs='+', help='Artifacts which need to be deployed before the specified artifact.')
        c.argument('resource_group_art', help='Name of the resource group artifact to which the policy will be assigned.')
        c.argument('parameters', arg_type=parameter_type)
        c.argument('template', arg_type=template_type)

    with self.argument_context('blueprint published create') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('version_id', options_list=['--version'], help='Version of the published blueprint definition.')
        c.argument('change_notes', help='Version-specific change notes.')

    with self.argument_context('blueprint published delete') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('version_id', options_list=['--version'], help='Version of the published blueprint definition.')

    with self.argument_context('blueprint published show') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('version_id', options_list=['--version'], help='Version of the published blueprint definition.')

    with self.argument_context('blueprint published list') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')

    with self.argument_context('blueprint published artifact show') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('version_id', options_list=['--version'], help='Version of the published blueprint definition.')
        c.argument('artifact_name', help='Name of the blueprint artifact.')

    with self.argument_context('blueprint published artifact list') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('blueprint_name', help='Name of the blueprint definition.')
        c.argument('version_id', options_list=['--version'], help='Version of the published blueprint definition.')

    for scope in ['blueprint assignment create', 'blueprint assignment update']:
        with self.argument_context(scope) as c:
            c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
            c.argument('assignment_name', help='Name of the blueprint assignment.')
            c.argument('location', arg_type=get_location_type(self.cli_ctx))
            c.argument('identity_type', arg_type=get_enum_type(['None', 'SystemAssigned', 'UserAssigned']), help='Type of the managed identity.')
            c.argument('identity_principal_id', help='Azure Active Directory principal ID associated with this Identity.')
            c.argument('identity_tenant_id', help='ID of the Azure Active Directory.')
            c.argument('identity_user_assigned_identities', help='The list of user-assigned managed identities associated with the resource. Key is the Azure resource Id of the managed identity.')
            c.argument('display_name', help='One-liner string explain this resource.')
            c.argument('description', help='Multi-line explain this resource.')
            c.argument('blueprint_id', help='ID of the published version of a blueprint definition.')
            c.argument('parameters', arg_type=parameter_type, help='Blueprint assignment parameter values.')
            c.argument('resource_groups', help='Names and locations of resource group placeholders.')
            c.argument('locks_mode', arg_type=get_enum_type(['None', 'AllResourcesReadOnly', 'AllResourcesDoNotDelete']), help='Lock mode.')
            c.argument('locks_excluded_principals', help='List of AAD principals excluded from blueprint locks. Up to 5 principals are permitted.', nargs='+')

    with self.argument_context('blueprint assignment delete') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('assignment_name', help='Name of the blueprint assignment.')

    with self.argument_context('blueprint assignment show') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('assignment_name', help='Name of the blueprint assignment.')

    with self.argument_context('blueprint assignment list') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')

    with self.argument_context('blueprint assignment wait') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('assignment_name', help='Name of the blueprint assignment.')

    with self.argument_context('blueprint assignment who-is-blueprint') as c:
        c.argument('scope', help='The scope of the resource. Valid scopes are: management group (format: \'/providers/Microsoft.Management/managementGroups/{managementGroup}\'), subscription (format: \'/subscriptions/{subscriptionId}\'). For blueprint assignments management group scope is reserved for future use.')
        c.argument('assignment_name', help='Name of the blueprint assignment.')
