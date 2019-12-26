# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from ._client_factory import cf_blueprints
    blueprint_blueprints = CliCommandType(
        operations_tmpl='azext_blueprint.vendored_sdks.blueprint.operations._blueprints_operations#BlueprintsOperations.{}',
        client_factory=cf_blueprints)
    with self.command_group('blueprint', blueprint_blueprints, client_factory=cf_blueprints) as g:
        g.custom_command('create', 'create_blueprint')
        g.custom_command('update', 'update_blueprint')
        g.custom_command('delete', 'delete_blueprint')
        g.custom_command('show', 'get_blueprint')
        g.custom_command('list', 'list_blueprint')

    from ._client_factory import cf_artifacts
    blueprint_artifacts = CliCommandType(
        operations_tmpl='azext_blueprint.vendored_sdks.blueprint.operations._artifacts_operations#ArtifactsOperations.{}',
        client_factory=cf_artifacts)
    with self.command_group('blueprint artifact', blueprint_artifacts, client_factory=cf_artifacts) as g:
        g.custom_command('create', 'create_blueprint_artifact')
        g.custom_command('update', 'update_blueprint_artifact')
        g.custom_command('delete', 'delete_blueprint_artifact')
        g.custom_command('show', 'get_blueprint_artifact')
        g.custom_command('list', 'list_blueprint_artifact')

    from ._client_factory import cf_published_blueprints
    blueprint_published_blueprints = CliCommandType(
        operations_tmpl='azext_blueprint.vendored_sdks.blueprint.operations._published_blueprints_operations#PublishedBlueprintsOperations.{}',
        client_factory=cf_published_blueprints)
    with self.command_group('blueprint published', blueprint_published_blueprints, client_factory=cf_published_blueprints) as g:
        g.custom_command('create', 'create_blueprint_published')
        g.custom_command('update', 'update_blueprint_published')
        g.custom_command('delete', 'delete_blueprint_published')
        g.custom_command('show', 'get_blueprint_published')
        g.custom_command('list', 'list_blueprint_published')

    from ._client_factory import cf_published_artifacts
    blueprint_published_artifacts = CliCommandType(
        operations_tmpl='azext_blueprint.vendored_sdks.blueprint.operations._published_artifacts_operations#PublishedArtifactsOperations.{}',
        client_factory=cf_published_artifacts)
    with self.command_group('blueprint published artifact', blueprint_published_artifacts, client_factory=cf_published_artifacts) as g:
        g.custom_command('get', 'get_blueprint_published_artifact')
        g.custom_command('list', 'list_blueprint_published_artifact')

    from ._client_factory import cf_assignments
    blueprint_assignments = CliCommandType(
        operations_tmpl='azext_blueprint.vendored_sdks.blueprint.operations._assignments_operations#AssignmentsOperations.{}',
        client_factory=cf_assignments)
    with self.command_group('blueprint assignment', blueprint_assignments, client_factory=cf_assignments) as g:
        g.custom_command('create', 'create_blueprint_assignment')
        g.custom_command('update', 'update_blueprint_assignment')
        g.custom_command('delete', 'delete_blueprint_assignment')
        g.custom_command('show', 'get_blueprint_assignment')
        g.custom_command('list', 'list_blueprint_assignment')
        g.custom_command('who_is_blueprint', 'who_is_blueprint_blueprint_assignment')
