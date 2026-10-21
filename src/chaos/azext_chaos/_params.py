# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import (
    get_location_type,
    tags_type,
)
from azext_chaos._validators import (
    validate_scope,
    validate_parameters_json,
    validate_user_assigned,
)


def load_arguments(self, _):
    # ── chaos setup (composite / porcelain) ──────────────────────────
    with self.argument_context('chaos setup') as c:
        c.argument(
            'workspace_name',
            options_list=['--name', '-n'],
            help='Name of the Chaos Studio workspace to create.',
        )
        c.argument(
            'location',
            arg_type=get_location_type(self.cli_ctx),
            help='Location for the workspace. Optional only when the '
                 'resource group already exists (defaults to the resource '
                 "group's location). Required when the resource group does "
                 'not exist, because setup creates it and has no region to '
                 'default to.',
        )
        c.argument(
            'scopes',
            nargs='+',
            validator=validate_scope,
            help='Space-separated list of ARM resource IDs that the workspace '
                 'is allowed to target: a resource group, subscription, or '
                 'service group. Required — there is no default scope. '
                 'Examples: '
                 '`/subscriptions/<sub-id>/resourceGroups/<rg-name>` or '
                 '`/providers/Microsoft.Management/serviceGroups/<name>`',
        )
        c.argument(
            'user_assigned',
            options_list=['--user-assigned', '--mi-user-assigned'],
            nargs='+',
            validator=validate_user_assigned,
            help='Space-separated ARM resource ID(s) of user-assigned managed '
                 'identities to use as the workspace identity. When omitted, '
                 'the workspace uses a system-assigned identity. Example: '
                 '`/subscriptions/<sub-id>/resourceGroups/<rg-name>/providers/'
                 'Microsoft.ManagedIdentity/userAssignedIdentities/<name>`',
        )
        c.argument(
            'skip_permissions',
            options_list=['--skip-permissions'],
            action='store_true',
            default=False,
            help='Skip granting the workspace identity the Reader role on the '
                 'target scopes. Use when you manage RBAC out of band. '
                 'Evaluation still runs, but can only discover resources if the '
                 'identity already holds Reader on the scopes.',
        )
        c.argument(
            'skip_evaluation_wait',
            options_list=['--skip-evaluation-wait'],
            action='store_true',
            default=False,
            help='Do not wait/retry for Azure Resource Graph propagation after '
                 'a new Reader role assignment; run a single evaluation attempt '
                 'and report a rerun hint if it has not propagated yet. Useful '
                 'for non-interactive/CI runs.',
        )
        c.argument(
            'tags',
            arg_type=tags_type,
            help='Space-separated tags in KEY=VALUE form for the workspace.',
        )

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
        # ``--scenario-id`` is auto-derived from --workspace-name/--scenario-name
        # by the ScenarioConfigCreate subclass (custom.py); hide it so users are
        # not asked for a redundant full ARM ID.
        c.ignore('scenario_id')
        c.argument(
            'parameters',
            options_list=['--parameters'],
            validator=validate_parameters_json,
            help='Action parameters as a JSON array of {key,value} objects '
                 '(or @file.json containing that array). '
                 'Example: --parameters "[{key:duration,value:PT10M}]" '
                 'or --parameters @params.json',
        )

    with self.argument_context('chaos scenario config update') as c:
        c.argument(
            'parameters',
            options_list=['--parameters'],
            validator=validate_parameters_json,
            help='Action parameters as a JSON array of {key,value} objects '
                 '(or @file.json containing that array). '
                 'Example: --parameters "[{key:duration,value:PT10M}]" '
                 'or --parameters @params.json',
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
        # Consistent with 'run cancel' and 'run wait': --run-id is canonical,
        # with -n/--name as aliases.
        c.argument(
            'run_id',
            options_list=['--run-id', '--name', '-n'],
            help='GUID of the scenario run.',
        )

    with self.argument_context('chaos scenario run cancel') as c:
        c.argument(
            'run_id',
            options_list=['--run-id', '--name', '-n'],
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
