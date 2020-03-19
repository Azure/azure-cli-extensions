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
        g.generic_update_command('update', custom_func_name='update_blueprint',
                                 setter_arg_name='blueprint',
                                 setter_name='create_or_update')
        g.custom_command('delete', 'delete_blueprint', confirmation=True)
        g.custom_show_command('show', 'get_blueprint')
        g.custom_command('list', 'list_blueprint')
        g.custom_command('import', 'import_blueprint_with_artifacts', confirmation="This operation will overwrite any unpublished changes if the blueprint already exists.")

    with self.command_group('blueprint resource-group', blueprint_blueprints, client_factory=cf_blueprints) as g:
        g.custom_command('add', 'add_blueprint_resource_group')
        g.custom_command('update', 'update_blueprint_resource_group')
        g.custom_command('remove', 'remove_blueprint_resource_group', confirmation=True)
        g.custom_show_command('show', 'get_blueprint_resource_group')
        g.custom_command('list', 'list_blueprint_resource_group')

    from ._client_factory import cf_artifacts
    blueprint_artifacts = CliCommandType(
        operations_tmpl='azext_blueprint.vendored_sdks.blueprint.operations._artifacts_operations#ArtifactsOperations.{}',
        client_factory=cf_artifacts)
    with self.command_group('blueprint artifact', blueprint_artifacts, client_factory=cf_artifacts) as g:
        g.custom_command('delete', 'delete_blueprint_artifact', confirmation=True)
        g.custom_show_command('show', 'get_blueprint_artifact')
        g.custom_command('list', 'list_blueprint_artifact')

    with self.command_group('blueprint artifact policy', blueprint_artifacts, client_factory=cf_artifacts) as g:
        g.custom_command('create', 'create_blueprint_artifact_policy')
        g.custom_command('update', 'update_blueprint_artifact_policy')

    with self.command_group('blueprint artifact role', blueprint_artifacts, client_factory=cf_artifacts) as g:
        g.custom_command('create', 'create_blueprint_artifact_role')
        g.custom_command('update', 'update_blueprint_artifact_role')

    with self.command_group('blueprint artifact template', blueprint_artifacts, client_factory=cf_artifacts) as g:
        g.custom_command('create', 'create_blueprint_artifact_template')
        g.custom_command('update', 'update_blueprint_artifact_template')

    from ._client_factory import cf_published_blueprints
    blueprint_published_blueprints = CliCommandType(
        operations_tmpl='azext_blueprint.vendored_sdks.blueprint.operations._published_blueprints_operations#PublishedBlueprintsOperations.{}',
        client_factory=cf_published_blueprints)
    with self.command_group('blueprint', blueprint_published_blueprints, client_factory=cf_published_blueprints) as g:
        g.custom_command('publish', 'publish_blueprint')
        g.custom_command('version delete', 'delete_blueprint_version', confirmation=True)
        g.custom_command('version show', 'get_blueprint_version')
        g.custom_command('version list', 'list_blueprint_version')

    from ._client_factory import cf_published_artifacts
    blueprint_published_artifacts = CliCommandType(
        operations_tmpl='azext_blueprint.vendored_sdks.blueprint.operations._published_artifacts_operations#PublishedArtifactsOperations.{}',
        client_factory=cf_published_artifacts)
    with self.command_group('blueprint version artifact', blueprint_published_artifacts, client_factory=cf_published_artifacts) as g:
        g.custom_show_command('show', 'get_blueprint_version_artifact')
        g.custom_command('list', 'list_blueprint_version_artifact')

    from ._client_factory import cf_assignments
    blueprint_assignments = CliCommandType(
        operations_tmpl='azext_blueprint.vendored_sdks.blueprint.operations._assignments_operations#AssignmentsOperations.{}',
        client_factory=cf_assignments)
    with self.command_group('blueprint assignment', blueprint_assignments, client_factory=cf_assignments) as g:
        g.custom_command('create', 'create_blueprint_assignment')
        g.custom_command('update', 'update_blueprint_assignment')
        g.custom_command('delete', 'delete_blueprint_assignment', confirmation=True)
        g.custom_show_command('show', 'get_blueprint_assignment')
        g.custom_command('list', 'list_blueprint_assignment')
        g.wait_command('wait')
        g.custom_command('who', 'who_is_blueprint_blueprint_assignment')
