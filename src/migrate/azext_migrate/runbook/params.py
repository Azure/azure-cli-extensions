# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Argument declarations for the ``migrate runbook`` command group."""

from azure.cli.core.commands.parameters import (
    resource_group_name_type,
    get_enum_type,
)
from azext_migrate.runbook.constants import (
    RUNBOOK_STATUS_VALUES,
    STEP_TYPE_VALUES,
)
from azext_migrate.runbook.validators import (
    validate_generate,
)


def load_runbook_arguments(self, _):
    with self.argument_context('migrate runbook') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument(
            'project_name',
            options_list=['--project-name', '-p'],
            help='Name of the Azure Migrate project.')
        c.argument(
            'runbook_name',
            options_list=['--name', '-n', '--runbook-name'],
            help='Name of the runbook.')

    with self.argument_context('migrate runbook generate') as c:
        c.argument(
            'wave_name',
            options_list=['--wave-name'],
            validator=validate_generate,
            help='Name of the wave to generate the runbook from '
                 '(required).')

    with self.argument_context('migrate runbook update') as c:
        c.argument(
            'description',
            options_list=['--description'],
            help='Updated description for the runbook.')

    with self.argument_context('migrate runbook list') as c:
        c.argument(
            'wave_name',
            options_list=['--wave-name'],
            help='Filter runbooks by wave name.')
        c.argument(
            'status',
            options_list=['--status'],
            arg_type=get_enum_type(RUNBOOK_STATUS_VALUES),
            help='Filter runbooks by lifecycle status.')

    with self.argument_context('migrate runbook definition show') as c:
        c.argument(
            'workstream_id',
            options_list=['--workstream-id'],
            help='Limit the output to a single workstream.')
        c.argument(
            'step_id',
            options_list=['--step-id'],
            help='Limit the output to a single step.')

    with self.argument_context('migrate runbook definition download') as c:
        c.argument(
            'destination',
            options_list=['--destination'],
            help='Directory to save the downloaded files to '
                 '(default: current directory).')

    with self.argument_context(
            'migrate runbook definition step add') as c:
        c.argument(
            'step_type', options_list=['--step-type'], required=True,
            arg_type=get_enum_type(STEP_TYPE_VALUES),
            help='Kind of step to add.')
        c.argument(
            'step_name', options_list=['--step-name'], required=True,
            help='Display name for the step.')
        c.argument(
            'workstream_id', options_list=['--workstream-id'],
            required=True,
            help='Id of the workstream to add the step to.')
        c.argument(
            'step_description', options_list=['--step-description'],
            help='Optional description for the step.')
        c.argument(
            'depends_on', options_list=['--depends-on'], nargs='*',
            help='Space-separated step ids this step depends on.')
        c.argument(
            'migration_entity_ids',
            options_list=['--migration-entity-ids'], nargs='*',
            help='Space-separated migration entity ids to associate '
                 'with the step.')

    with self.argument_context(
            'migrate runbook definition step update') as c:
        c.argument(
            'step_id', options_list=['--step-id'], required=True,
            help='Id of the step to update.')
        c.argument(
            'step_name', options_list=['--step-name'],
            help='Updated display name for the step.')
        c.argument(
            'step_description', options_list=['--step-description'],
            help='Updated description for the step.')
        c.argument(
            'depends_on', options_list=['--depends-on'], nargs='*',
            help='Space-separated step ids this step depends on.')

    with self.argument_context(
            'migrate runbook definition step remove') as c:
        c.argument(
            'step_id', options_list=['--step-id'], required=True,
            help='Id of the step to remove.')

    with self.argument_context(
            'migrate runbook definition workstream split') as c:
        c.argument(
            'source_workstream_id',
            options_list=['--source-workstream-id'], required=True,
            help='Id of the workstream to split.')
        c.argument(
            'new_workstream_name',
            options_list=['--new-workstream-name'], required=True,
            help='Display name for the new workstream.')
        c.argument(
            'step_ids', options_list=['--step-ids'],
            nargs='+', required=True,
            help='Space-separated step ids to move into the new '
                 'workstream.')

    with self.argument_context(
            'migrate runbook definition workstream merge') as c:
        c.argument(
            'source_workstream_ids',
            options_list=['--source-workstream-ids'], nargs='+',
            required=True,
            help='Space-separated ids of the workstreams to merge.')
        c.argument(
            'new_workstream_name',
            options_list=['--new-workstream-name'], required=False,
            help='Display name for the merged workstream. Defaults to the '
                 'first workstream name if not provided.')

    with self.argument_context(
            'migrate runbook execution show') as c:
        c.argument(
            'execution_id', options_list=['--execution-id'], required=True,
            help='Id of the runbook execution.')
        c.argument(
            'step_id', options_list=['--step-id'],
            help='Limit the output to a single step.')
        c.argument(
            'watch', options_list=['--watch'], action='store_true',
            help='Re-render the status table on an interval until the '
                 'execution reaches a terminal state.')
        c.argument(
            'interval', options_list=['--interval'], type=int,
            help='Refresh interval in seconds for --watch (default: 5).')

    with self.argument_context(
            'migrate runbook execution pause') as c:
        c.argument(
            'execution_id', options_list=['--execution-id'], required=True,
            help='Id of the runbook execution.')

    with self.argument_context(
            'migrate runbook execution resume') as c:
        c.argument(
            'execution_id', options_list=['--execution-id'], required=True,
            help='Id of the runbook execution.')

    with self.argument_context(
            'migrate runbook execution cancel') as c:
        c.argument(
            'execution_id', options_list=['--execution-id'], required=True,
            help='Id of the runbook execution.')

    with self.argument_context('migrate runbook wait') as c:
        c.argument(
            'created', options_list=['--created'], action='store_true',
            help='Wait until provisioningState reaches Succeeded.')
        c.argument(
            'updated', options_list=['--updated'], action='store_true',
            help='Wait until provisioningState reaches Succeeded after '
                 'an update.')
        c.argument(
            'deleted', options_list=['--deleted'], action='store_true',
            help='Wait until the runbook no longer exists.')
        c.argument(
            'exists', options_list=['--exists'], action='store_true',
            help='Wait until the runbook exists.')
        c.argument(
            'custom', options_list=['--custom'],
            help="Wait until a JMESPath condition is met, e.g. "
                 "\"properties.state=='ExecutionSucceeded'\".")
        c.argument(
            'interval', options_list=['--interval'], type=int,
            help='Polling interval in seconds (default: 30).')
        c.argument(
            'timeout', options_list=['--timeout'], type=int,
            help='Maximum wait time in seconds (default: 3600).')
