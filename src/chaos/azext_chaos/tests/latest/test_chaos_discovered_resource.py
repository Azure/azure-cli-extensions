# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Integration tests for the ``az chaos discovered-resource`` command group (E5-T5).

Covers discovered-resource browsing:
  list discovered resources → show discovered resource

Re-record when: playback fails OR a spec change merges to
``azure-rest-api-specs[-pr]`` under ``Microsoft.Chaos`` that touches a
covered discovered-resource operation.
"""

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer, live_only


@live_only()
class TestChaosDiscoveredResourceBrowsing(ScenarioTest):
    """E5-T5: discovered-resource list → show."""

    @ResourceGroupPreparer(name_prefix='cli_test_chaos_dr', location='westus2')
    def test_discovered_resource_list_and_show(self, resource_group):
        self.kwargs.update({
            'sub': self.get_subscription_id(),
            'ws': self.create_random_name('ws', 15),
            'loc': 'westus2',
        })

        # ── prerequisite: create workspace + refresh-recommendation ────
        # Scoping the workspace to the test resource group so that
        # discovery will find at least the resource group itself.
        self.cmd(
            'chaos workspace create -n {ws} -g {rg} -l {loc} '
            '--mi-system-assigned '
            '--scopes /subscriptions/{sub}/resourceGroups/{rg}',
        )
        self.cmd(
            'chaos workspace refresh-recommendation -n {ws} -g {rg}',
        )

        # ── discovered-resource list ────────────────────────────────────
        list_result = self.cmd(
            'chaos discovered-resource list --workspace-name {ws} -g {rg}',
            checks=[
                self.greater_than('length(@)', 0),
            ],
        ).get_output_in_json()

        # Pick the first discovered resource for show
        first_name = list_result[0]['name']
        self.kwargs['dr_name'] = first_name

        # ── discovered-resource show ────────────────────────────────────
        self.cmd(
            'chaos discovered-resource show --workspace-name {ws} -g {rg} -n {dr_name}',
            checks=[
                self.check('name', first_name),
                self.exists('properties'),
            ],
        )

        # ── cleanup ─────────────────────────────────────────────────────
        self.cmd('chaos workspace delete -n {ws} -g {rg} --yes')
