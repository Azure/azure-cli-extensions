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
        operations_tmpl='azext_blueprint.vendored_sdks.blueprint.operations._blueprints_operations#BlueprintsOperations'
                        '.{}',
        client_factory=cf_blueprints)
    with self.command_group('blueprint', blueprint_blueprints, client_factory=cf_blueprints, is_experimental=True) as g:
        from azext_blueprint.custom import BlueprintCreate, BlueprintDelete, BlueprintShow, BlueprintList, BlueprintUpdate
        self.command_table["blueprint create"] = BlueprintCreate(loader=self)
        self.command_table["blueprint delete"] = BlueprintDelete(loader=self)
        self.command_table["blueprint show"] = BlueprintShow(loader=self)
        self.command_table["blueprint list"] = BlueprintList(loader=self)
        self.command_table["blueprint update"] = BlueprintUpdate(loader=self)
        g.custom_command('import', 'import_blueprint_with_artifacts',
                         confirmation="This operation will overwrite any unpublished changes"
                                      " if the blueprint already exists.")
        g.custom_command('export', 'export_blueprint_with_artifacts')

    with self.command_group('blueprint resource-group') as g:
        g.custom_command('add', 'add_blueprint_resource_group')
        g.custom_command('update', 'update_blueprint_resource_group')
        g.custom_command('remove', 'remove_blueprint_resource_group', confirmation=True)
        g.custom_show_command('show', 'get_blueprint_resource_group')
        g.custom_command('list', 'list_blueprint_resource_group')

    from ._client_factory import cf_artifacts
    blueprint_artifacts = CliCommandType(
        operations_tmpl='azext_blueprint.vendored_sdks.blueprint.operations._artifacts_operations#ArtifactsOperations'
                        '.{}',
        client_factory=cf_artifacts)
    with self.command_group('blueprint artifact'):
        from azext_blueprint.custom import BlueprintArtifactDelete, BlueprintArtifactShow, BlueprintArtifactList
        self.command_table["blueprint artifact delete"] = BlueprintArtifactDelete(loader=self)
        self.command_table["blueprint artifact show"] = BlueprintArtifactShow(loader=self)
        self.command_table["blueprint artifact list"] = BlueprintArtifactList(loader=self)

    with self.command_group('blueprint artifact policy', blueprint_artifacts, client_factory=cf_artifacts) as g:
        g.custom_command('create', 'create_blueprint_artifact_policy')
        g.custom_command('update', 'update_blueprint_artifact_policy')

    with self.command_group('blueprint artifact role', blueprint_artifacts, client_factory=cf_artifacts) as g:
        g.custom_command('create', 'create_blueprint_artifact_role')
        g.custom_command('update', 'update_blueprint_artifact_role')

    with self.command_group('blueprint artifact template', blueprint_artifacts, client_factory=cf_artifacts) as g:
        g.custom_command('create', 'create_blueprint_artifact_template')
        g.custom_command('update', 'update_blueprint_artifact_template')

    with self.command_group('blueprint'):
        from azext_blueprint.custom import BlueprintPublish, BlueprintVersionDelete, BlueprintVersionShow, \
            BlueprintVersionList
        self.command_table["blueprint publish"] = BlueprintPublish(loader=self)
        self.command_table["blueprint version delete"] = BlueprintVersionDelete(loader=self)
        self.command_table["blueprint version show"] = BlueprintVersionShow(loader=self)
        self.command_table["blueprint version list"] = BlueprintVersionList(loader=self)

    with self.command_group('blueprint version artifact'):
        from azext_blueprint.custom import BlueprintVersionArtifactShow, BlueprintVersionArtifactList
        self.command_table["blueprint version artifact show"] = BlueprintVersionArtifactShow(loader=self)
        self.command_table["blueprint version artifact list"] = BlueprintVersionArtifactList(loader=self)

    from ._client_factory import cf_assignments
    blueprint_assignments = CliCommandType(
        operations_tmpl='azext_blueprint.vendored_sdks.blueprint.operations'
                        '._assignments_operations#AssignmentsOperations.{}',
        client_factory=cf_assignments)
    with self.command_group('blueprint assignment', blueprint_assignments, client_factory=cf_assignments) as g:
        g.custom_command('create', 'create_blueprint_assignment')
        g.custom_command('update', 'update_blueprint_assignment')
        g.custom_wait_command('wait', 'get_blueprint_assignment')
        from azext_blueprint.custom import BlueprintAssignmentDelete, BlueprintAssignmentShow, BlueprintAssignmentList, \
            BlueprintAssignmentWho
        self.command_table["blueprint assignment delete"] = BlueprintAssignmentDelete(loader=self)
        self.command_table["blueprint assignment show"] = BlueprintAssignmentShow(loader=self)
        self.command_table["blueprint assignment list"] = BlueprintAssignmentList(loader=self)
        self.command_table["blueprint assignment who"] = BlueprintAssignmentWho(loader=self)
