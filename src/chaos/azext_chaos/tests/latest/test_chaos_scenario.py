# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Integration tests for the ``az chaos scenario`` command group (E5-T2).

Covers the scenario lifecycle:
  create scenario → list scenarios → show scenario → delete scenario

Re-record when: playback fails OR a spec change merges to
``azure-rest-api-specs[-pr]`` under ``Microsoft.Chaos`` that touches a
covered scenario operation.
"""

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer


class TestChaosScenarioLifecycle(ScenarioTest):
    """E5-T2: scenario lifecycle — create → list → show → delete."""

    @ResourceGroupPreparer(name_prefix='cli_test_chaos_sc', location='eastus')
    def test_scenario_lifecycle(self, resource_group):
        self.kwargs.update({
            'ws': self.create_random_name('ws', 15),
            'scenario': self.create_random_name('sc', 15),
            'loc': 'eastus',
        })

        # ── prerequisite: create workspace ──────────────────────────────
        self.cmd(
            'chaos workspace create -n {ws} -g {rg} -l {loc} '
            '--identity-type SystemAssigned '
            '--scopes /subscriptions/{sub}/resourceGroups/{rg}',
        )

        # ── scenario create ─────────────────────────────────────────────
        self.cmd(
            'chaos scenario create -w {ws} -g {rg} -n {scenario}',
            checks=[
                self.check('name', '{scenario}'),
            ],
        )

        # ── scenario list ───────────────────────────────────────────────
        list_result = self.cmd(
            'chaos scenario list -w {ws} -g {rg}',
            checks=[
                self.greater_than('length(@)', 0),
            ],
        ).get_output_in_json()
        self.assertTrue(
            any(s['name'] == self.kwargs['scenario'] for s in list_result),
            'Created scenario not found in list output',
        )

        # ── scenario show ───────────────────────────────────────────────
        self.cmd(
            'chaos scenario show -w {ws} -g {rg} -n {scenario}',
            checks=[
                self.check('name', '{scenario}'),
            ],
        )

        # ── scenario delete ─────────────────────────────────────────────
        self.cmd(
            'chaos scenario delete -w {ws} -g {rg} -n {scenario} --yes',
        )

        # Verify deletion
        list_after = self.cmd(
            'chaos scenario list -w {ws} -g {rg}',
        ).get_output_in_json()
        self.assertFalse(
            any(s['name'] == self.kwargs['scenario'] for s in list_after),
            'Scenario should not appear after deletion',
        )

        # ── cleanup: delete workspace ───────────────────────────────────
        self.cmd('chaos workspace delete -n {ws} -g {rg} --yes')
