# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_chaos._table_format import (
    discovered_resource_list_table_format,
    discovered_resource_show_table_format,
    permission_fix_show_table_format,
    scenario_config_list_table_format,
    scenario_config_show_table_format,
    scenario_list_table_format,
    scenario_run_list_table_format,
    scenario_run_show_table_format,
    scenario_show_table_format,
    validation_show_table_format,
    workspace_discovery_show_table_format,
    workspace_evaluation_show_table_format,
    workspace_list_table_format,
    workspace_show_table_format,
)


def load_command_table(self, _):
    # ── Table transformers for aaz-generated commands ────────────────
    # These commands are already registered by load_aaz_command_table()
    # before this function is called.  We set table_transformer on each
    # result-bearing command so --output table renders useful columns.
    _aaz_transformers = {
        'chaos workspace show': workspace_show_table_format,
        'chaos workspace list': workspace_list_table_format,
        'chaos workspace show-discovery': workspace_discovery_show_table_format,
        'chaos workspace show-evaluation': workspace_evaluation_show_table_format,
        'chaos scenario show': scenario_show_table_format,
        'chaos scenario list': scenario_list_table_format,
        'chaos scenario config show': scenario_config_show_table_format,
        'chaos scenario config list': scenario_config_list_table_format,
        'chaos scenario config show-validation': validation_show_table_format,
        'chaos scenario config show-permission-fix': permission_fix_show_table_format,
        'chaos scenario run show': scenario_run_show_table_format,
        'chaos scenario run list': scenario_run_list_table_format,
        'chaos discovered-resource show': discovered_resource_show_table_format,
        'chaos discovered-resource list': discovered_resource_list_table_format,
    }
    for cmd_name, transformer in _aaz_transformers.items():
        if cmd_name in self.command_table:
            self.command_table[cmd_name].table_transformer = transformer

    # ── Custom command overrides──────────────────────────────────────
    with self.command_group(
        'chaos workspace',
        operations_tmpl='azext_chaos.custom#{}',
    ) as g:
        g.custom_show_command(
            'show-discovery',
            'workspace_show_discovery',
            table_transformer=workspace_discovery_show_table_format,
        )
        g.custom_show_command(
            'show-evaluation',
            'workspace_show_evaluation',
            table_transformer=workspace_evaluation_show_table_format,
        )

    with self.command_group(
        'chaos scenario config',
        operations_tmpl='azext_chaos.custom#{}',
    ) as g:
        g.custom_command(
            'validate',
            'scenario_config_validate',
            supports_no_wait=True,
            table_transformer=validation_show_table_format,
        )
        g.custom_command(
            'fix-permissions',
            'scenario_config_fix_permissions',
            supports_no_wait=True,
            table_transformer=permission_fix_show_table_format,
        )
        g.custom_show_command(
            'show-validation',
            'scenario_config_show_validation',
            table_transformer=validation_show_table_format,
        )
        g.custom_show_command(
            'show-permission-fix',
            'scenario_config_show_permission_fix',
            table_transformer=permission_fix_show_table_format,
        )

    with self.command_group(
        'chaos scenario run',
        operations_tmpl='azext_chaos.custom#{}',
    ) as g:
        g.custom_command(
            'start',
            'scenario_run_start',
            supports_no_wait=True,
            table_transformer=scenario_run_show_table_format,
        )
        g.custom_command(
            'cancel',
            'scenario_run_cancel',
            supports_no_wait=True,
        )

    _register_aaz_subclass_overrides(self)


def _register_aaz_subclass_overrides(loader):
    """Register AAZCommand subclass overrides via direct command_table writes.

    These supersede the AAZ-generated commands of the same name.  Pattern
    reference: Azure/azure-cli-extensions:src/connectedmachine/azext_connectedmachine
    /commands.py — subclass + manual ``command_table[name] = cls(loader=self)``.

    Because instantiating an ``AAZCommand`` requires a real ``AzCommandsLoader``
    (Knack rejects non-CLI ``cli_ctx``), unit tests that drive ``load_command_table``
    with a ``MagicMock`` loader should ``@patch`` this helper out.
    """
    from azext_chaos.custom import (
        ScenarioConfigCreate,
        ScenarioConfigExecute,
        WorkspaceRefreshRecommendation,
        WorkspaceEvaluateScenarios,
    )
    from azext_chaos.custom_wait import ScenarioRunWait
    loader.command_table['chaos scenario config create'] = ScenarioConfigCreate(loader=loader)
    loader.command_table['chaos scenario run wait'] = ScenarioRunWait(loader=loader)
    # Override ``chaos scenario config execute`` to fix the NoneType crash on
    # successful LRO completion (AAZ codegen passes None as the LRO success
    # deserializer; subclass injects a no-op via _handler override).
    loader.command_table['chaos scenario config execute'] = ScenarioConfigExecute(loader=loader)
    # Override the AAZ-generated ``chaos workspace refresh-recommendation``
    # to add inner-LRO failure detection (see WorkspaceRefreshRecommendation
    # docstring for why this is functionally necessary, not stylistic).
    loader.command_table['chaos workspace refresh-recommendation'] = WorkspaceRefreshRecommendation(loader=loader)
    # Register ``chaos workspace evaluate-scenarios`` as a porcelain alias
    # at a NAME the spec does not define. The subclass instance bears the
    # alias name; AAZCommand inherits everything from the parent class.
    loader.command_table['chaos workspace evaluate-scenarios'] = WorkspaceEvaluateScenarios(loader=loader)
