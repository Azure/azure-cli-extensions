# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Integration tests for the ``az chaos workspace`` command group (E5-T1).

Covers the full workspace lifecycle:
  create → show → list → update → refresh-recommendation →
  evaluate-scenarios (alias) → show-discovery → show-evaluation → delete

Re-record when: playback fails OR a spec change merges to
``azure-rest-api-specs[-pr]`` under ``Microsoft.Chaos`` that touches a
covered workspace operation.
"""

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer, live_only


@live_only()
class TestChaosWorkspaceLifecycle(ScenarioTest):
    """E5-T1: workspace lifecycle — create → show → list → update →
    refresh-recommendation → evaluate-scenarios → show-discovery →
    show-evaluation → delete."""

    @ResourceGroupPreparer(name_prefix='cli_test_chaos_ws', location='westus2')
    def test_workspace_lifecycle(self, resource_group):
        self.kwargs.update({
            'sub': self.get_subscription_id(),
            'ws': self.create_random_name('ws', 15),
            'loc': 'westus2',
        })

        # ── create ──────────────────────────────────────────────────────
        self.cmd(
            'chaos workspace create -n {ws} -g {rg} -l {loc} '
            '--mi-system-assigned '
            '--scopes /subscriptions/{sub}/resourceGroups/{rg}',
            checks=[
                self.check('name', '{ws}'),
                self.check('location', '{loc}'),
                self.check('properties.provisioningState', 'Succeeded'),
                self.exists('identity'),
                self.check('identity.type', 'SystemAssigned'),
            ],
        )

        # ── show ────────────────────────────────────────────────────────
        self.cmd(
            'chaos workspace show -n {ws} -g {rg}',
            checks=[
                self.check('name', '{ws}'),
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        )

        # ── list (by resource group) ────────────────────────────────────
        list_result = self.cmd(
            'chaos workspace list -g {rg}',
            checks=[
                self.greater_than('length(@)', 0),
            ],
        ).get_output_in_json()
        self.assertTrue(
            any(w['name'] == self.kwargs['ws'] for w in list_result),
            'Created workspace not found in list output',
        )

        # ── update (add tags) ───────────────────────────────────────────
        self.cmd(
            'chaos workspace update -n {ws} -g {rg} '
            '--tags env=test purpose=e5',
            checks=[
                self.check('name', '{ws}'),
                self.check('tags.env', 'test'),
                self.check('tags.purpose', 'e5'),
            ],
        )

        # ── refresh-recommendation ─────────────────────────────────────
        self.cmd(
            'chaos workspace refresh-recommendation -n {ws} -g {rg}',
        )

        # ── evaluate-scenarios (alias — same handler) ───────────────────
        self.cmd(
            'chaos workspace evaluate-scenarios -n {ws} -g {rg}',
        )

        # ── show-discovery ──────────────────────────────────────────────
        self.cmd(
            'chaos workspace show-discovery -n {ws} -g {rg}',
            checks=[
                self.exists('properties.status'),
            ],
        )

        # ── show-evaluation ─────────────────────────────────────────────
        self.cmd(
            'chaos workspace show-evaluation -n {ws} -g {rg}',
            checks=[
                self.exists('properties.status'),
            ],
        )

        # ── delete ──────────────────────────────────────────────────────
        self.cmd(
            'chaos workspace delete -n {ws} -g {rg} --yes',
        )

        # Verify deletion
        list_after = self.cmd(
            'chaos workspace list -g {rg}',
        ).get_output_in_json()
        self.assertFalse(
            any(w['name'] == self.kwargs['ws'] for w in list_after),
            'Workspace should not appear after deletion',
        )
