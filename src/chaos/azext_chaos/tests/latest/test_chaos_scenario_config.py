# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Integration tests for the ``az chaos scenario config`` command group (E5-T3).

Covers the scenario configuration lifecycle:
  create → show → list → validate → show-validation →
  fix-permissions → show-permission-fix → delete

Re-record when: playback fails OR a spec change merges to
``azure-rest-api-specs[-pr]`` under ``Microsoft.Chaos`` that touches a
covered scenario-configuration operation.
"""

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer


class TestChaosScenarioConfigLifecycle(ScenarioTest):
    """E5-T3: scenario config lifecycle — create → show → list → validate →
    show-validation → fix-permissions → show-permission-fix → delete."""

    @ResourceGroupPreparer(name_prefix='cli_test_chaos_cfg', location='eastus')
    def test_scenario_config_lifecycle(self, resource_group):
        self.kwargs.update({
            'ws': self.create_random_name('ws', 15),
            'scenario': self.create_random_name('sc', 15),
            'config': self.create_random_name('cfg', 15),
            'loc': 'eastus',
        })

        # ── prerequisite: workspace + scenario + refresh-recommendations
        self.cmd(
            'chaos workspace create -n {ws} -g {rg} -l {loc} '
            '--identity-type SystemAssigned '
            '--scopes /subscriptions/{sub}/resourceGroups/{rg}',
        )
        self.cmd(
            'chaos scenario create -w {ws} -g {rg} -n {scenario}',
        )
        # Ensure workspace evaluation is complete (required for validate)
        self.cmd(
            'chaos workspace refresh-recommendations -n {ws} -g {rg}',
        )

        # ── scenario config create ──────────────────────────────────────
        self.cmd(
            "chaos scenario config create -w {ws} -g {rg} "
            "--scenario-name {scenario} -n {config} "
            "--parameters '{{}}'",
            checks=[
                self.check('name', '{config}'),
            ],
        )

        # ── scenario config show ────────────────────────────────────────
        self.cmd(
            'chaos scenario config show -w {ws} -g {rg} '
            '--scenario-name {scenario} -n {config}',
            checks=[
                self.check('name', '{config}'),
            ],
        )

        # ── scenario config list ────────────────────────────────────────
        list_result = self.cmd(
            'chaos scenario config list -w {ws} -g {rg} '
            '--scenario-name {scenario}',
            checks=[
                self.greater_than('length(@)', 0),
            ],
        ).get_output_in_json()
        self.assertTrue(
            any(c['name'] == self.kwargs['config'] for c in list_result),
            'Created config not found in list output',
        )

        # ── scenario config validate (default — polls to completion) ────
        self.cmd(
            'chaos scenario config validate -w {ws} -g {rg} '
            '--scenario-name {scenario} -n {config}',
            checks=[
                self.exists('properties.status'),
            ],
        )

        # ── scenario config show-validation ─────────────────────────────
        self.cmd(
            'chaos scenario config show-validation -w {ws} -g {rg} '
            '--scenario-name {scenario} -n {config}',
            checks=[
                self.exists('properties.status'),
            ],
        )

        # ── scenario config fix-permissions ─────────────────────────────
        self.cmd(
            'chaos scenario config fix-permissions -w {ws} -g {rg} '
            '--scenario-name {scenario} -n {config}',
        )

        # ── scenario config show-permission-fix ─────────────────────────
        self.cmd(
            'chaos scenario config show-permission-fix -w {ws} -g {rg} '
            '--scenario-name {scenario} -n {config}',
            checks=[
                self.exists('properties.state'),
            ],
        )

        # ── scenario config delete ──────────────────────────────────────
        self.cmd(
            'chaos scenario config delete -w {ws} -g {rg} '
            '--scenario-name {scenario} -n {config} --yes',
        )

        # Verify deletion
        list_after = self.cmd(
            'chaos scenario config list -w {ws} -g {rg} '
            '--scenario-name {scenario}',
        ).get_output_in_json()
        self.assertFalse(
            any(c['name'] == self.kwargs['config'] for c in list_after),
            'Config should not appear after deletion',
        )

        # ── cleanup ─────────────────────────────────────────────────────
        self.cmd('chaos scenario delete -w {ws} -g {rg} -n {scenario} --yes')
        self.cmd('chaos workspace delete -n {ws} -g {rg} --yes')
