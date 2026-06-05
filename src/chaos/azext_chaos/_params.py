# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import (
    get_location_type,
)
from azext_chaos._validators import validate_scope, validate_parameters_json


def load_arguments(self, _):
    # ── chaos workspace ──────────────────────────────────────────────
    with self.argument_context('chaos workspace') as c:
        # Spec pattern: ^[^<>%&:?#/\\]+$  (minLength: 1)
        c.argument(
            'workspace_name',
            options_list=['--name', '-n'],
            help='Name of the Chaos Studio workspace.',
        )

    with self.argument_context('chaos workspace create') as c:
        c.argument(
            'location',
            arg_type=get_location_type(self.cli_ctx),
        )
        c.argument(
            'scopes',
            nargs='+',
            validator=validate_scope,
            help='Space-separated list of ARM resource IDs defining the '
                 'scope of this workspace.',
        )

    with self.argument_context('chaos workspace update') as c:
        c.argument(
            'tags',
            help='Space-separated tags in KEY=VALUE form. Use "" to clear '
                 'existing tags.',
        )

    with self.argument_context('chaos workspace delete') as c:
        c.argument(
            'yes',
            options_list=['--yes', '-y'],
            action='store_true',
            help='Do not prompt for confirmation.',
        )

    # evaluate-scenarios alias inherits all args from refresh-recommendation;
    # register the same overrides so short flags resolve correctly.
    for ctx_name in ('chaos workspace refresh-recommendation',
                     'chaos workspace evaluate-scenarios'):
        with self.argument_context(ctx_name) as c:
            c.argument(
                'workspace_name',
                options_list=['--name', '-n'],
                help='Name of the Chaos Studio workspace.',
            )

    # ── chaos scenario ───────────────────────────────────────────────
    with self.argument_context('chaos scenario') as c:
        c.argument(
            'workspace_name',
            options_list=['--workspace-name'],
            help='Name of the parent Chaos Studio workspace.',
        )
        c.argument(
            'scenario_name',
            options_list=['--name', '-n'],
            help='Name of the scenario.',
        )

    with self.argument_context('chaos scenario delete') as c:
        c.argument(
            'yes',
            options_list=['--yes', '-y'],
            action='store_true',
            help='Do not prompt for confirmation.',
        )

    # ── chaos scenario config ────────────────────────────────────────
    with self.argument_context('chaos scenario config') as c:
        c.argument(
            'workspace_name',
            options_list=['--workspace-name'],
            help='Name of the parent Chaos Studio workspace.',
        )
        c.argument(
            'scenario_name',
            options_list=['--scenario-name'],
            help='Name of the parent scenario.',
        )
        c.argument(
            'scenario_configuration_name',
            options_list=['--name', '-n'],
            help='Name of the scenario configuration.',
        )

    with self.argument_context('chaos scenario config create') as c:
        c.argument(
            'parameters',
            options_list=['--parameters'],
            validator=validate_parameters_json,
            help='Action parameters as a JSON string or @file.json reference.',
        )

    with self.argument_context('chaos scenario config delete') as c:
        c.argument(
            'yes',
            options_list=['--yes', '-y'],
            action='store_true',
            help='Do not prompt for confirmation.',
        )

    # ── chaos scenario run ───────────────────────────────────────────
    with self.argument_context('chaos scenario run') as c:
        c.argument(
            'workspace_name',
            options_list=['--workspace-name'],
            help='Name of the parent Chaos Studio workspace.',
        )
        c.argument(
            'scenario_name',
            options_list=['--scenario-name'],
            help='Name of the parent scenario.',
        )

    with self.argument_context('chaos scenario run start') as c:
        c.argument(
            'scenario_configuration_name',
            options_list=['--config-name'],
            help='Name of the scenario configuration to execute.',
        )
        c.argument(
            'skip_validation',
            options_list=['--skip-validation'],
            action='store_true',
            default=False,
            help='Skip pre-flight validation and proceed directly to execute. '
                 'Use for CI re-runs of an already-validated configuration.',
        )

    with self.argument_context('chaos scenario run show') as c:
        # Spec pattern: ^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$
        c.argument(
            'run_id',
            options_list=['--run-id'],
            help='GUID of the scenario run.',
        )

    with self.argument_context('chaos scenario run cancel') as c:
        c.argument(
            'run_id',
            options_list=['--run-id'],
            help='GUID of the scenario run to cancel.',
        )

    # ── chaos scenario config fix-permissions (custom override) ──────
    # The custom handler accepts an optional --what-if Body bool for
    # server-side dry-run.
    with self.argument_context('chaos scenario config fix-permissions') as c:
        c.argument(
            'what_if',
            options_list=['--what-if'],
            action='store_true',
            default=False,
            help='Submit a server-side dry run that reports the role '
                 'assignments that would be made, without actually '
                 'creating them.',
        )

    # ── chaos discovered-resource ────────────────────────────────────
    with self.argument_context('chaos discovered-resource') as c:
        c.argument(
            'workspace_name',
            options_list=['--workspace-name'],
            help='Name of the parent Chaos Studio workspace.',
        )

    with self.argument_context('chaos discovered-resource show') as c:
        c.argument(
            'discovered_resource_name',
            options_list=['--name', '-n'],
            help='Name of the discovered resource.',
        )
