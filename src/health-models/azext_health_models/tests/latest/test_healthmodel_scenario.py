# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import *


class HealthModelScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_healthmodel_crud', location='centralus')
    def test_healthmodel_crud_cycle(self, resource_group):
        self.kwargs.update({
            'rg': resource_group,
            'model': self.create_random_name('clihm', 24),
            'entity': self.create_random_name('client', 24),
            'location': 'centralus',
        })

        self.cmd('monitor health-models create -g {rg} -n {model} -l {location}', checks=[
            self.check('name', '{model}'),
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('location', '{location}')
        ])
        self.cmd('monitor health-models show -g {rg} -n {model}', checks=[
            self.check('name', '{model}')
        ])
        self.cmd('monitor health-models update -g {rg} -n {model} --tags env=test owner=cli', checks=[
            self.check('tags.env', 'test'),
            self.check('tags.owner', 'cli')
        ])
        self.cmd('monitor health-models list -g {rg}', checks=[
            self.check('length(@)', 1),
            self.check('[0].name', '{model}')
        ])

        self.cmd('monitor health-models entity create -g {rg} --health-model-name {model} -n {entity} '
                 '--display-name "CLI Test Entity" --impact Standard', checks=[
            self.check('name', '{entity}'),
            self.check('properties.displayName', 'CLI Test Entity'),
            self.check('properties.impact', 'Standard')
        ])
        self.cmd('monitor health-models entity show -g {rg} --health-model-name {model} -n {entity}', checks=[
            self.check('name', '{entity}')
        ])
        self.cmd('monitor health-models entity list -g {rg} --health-model-name {model}', checks=[
            self.greater_than('length(@)', 0)
        ])
        self.cmd('monitor health-models entity delete -g {rg} --health-model-name {model} -n {entity} --yes')

        self.cmd('monitor health-models delete -g {rg} -n {model} --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_healthmodel_arrange', location='centralus')
    def test_healthmodel_arrange_persists_canvas_position(self, resource_group):
        self.kwargs.update({
            'rg': resource_group,
            'model': self.create_random_name('clihm', 24),
            'root': self.create_random_name('root', 24),
            'mid': self.create_random_name('mid', 24),
            'leaf': self.create_random_name('leaf', 24),
            'location': 'centralus',
        })

        self.cmd('monitor health-models create -g {rg} -n {model} -l {location}')

        for entity in ('root', 'mid', 'leaf'):
            self.cmd('monitor health-models entity create -g {rg} --health-model-name {model} '
                     '-n {%s} --display-name "CLI Test Entity" --impact Standard' % entity)

        self.cmd('monitor health-models relationship create -g {rg} --health-model-name {model} '
                 '-n rel-root-mid --parent-entity-name {root} --child-entity-name {mid}')
        self.cmd('monitor health-models relationship create -g {rg} --health-model-name {model} '
                 '-n rel-mid-leaf --parent-entity-name {mid} --child-entity-name {leaf}')

        # `--yes` skips the affected-entity confirmation prompt, which cannot be answered
        # without a tty under test; it changes no request the cassette recorded.
        self.cmd('monitor health-models arrange -g {rg} --health-model-name {model} --yes')

        root_position = self.cmd('monitor health-models entity show -g {rg} --health-model-name {model} '
                                 '-n {root}').get_output_in_json()['properties']['canvasPosition']
        mid_position = self.cmd('monitor health-models entity show -g {rg} --health-model-name {model} '
                                '-n {mid}').get_output_in_json()['properties']['canvasPosition']
        leaf_position = self.cmd('monitor health-models entity show -g {rg} --health-model-name {model} '
                                 '-n {leaf}').get_output_in_json()['properties']['canvasPosition']

        # Strict rank hierarchy top-to-bottom: root -> mid -> leaf, each in its own rank.
        self.assertLess(root_position['y'], mid_position['y'])
        self.assertLess(mid_position['y'], leaf_position['y'])
        # A single-child chain has one node per rank, so the rank separation (in canvas units)
        # is exactly ranksep(100, portal default) plus the assumed node height. Human-adjudicated
        # correction: "Use Portal seed 200x81 (Recommended)" - `ModelActionsSlice.ts` seeds
        # `measured: { width: 200, height: 81 }` onto every V2/V3 entity - so the CLI default
        # height is now 81 (was 36), giving a rank gap of 181 (was 136).
        self.assertAlmostEqual(mid_position['y'] - root_position['y'], 181.0)
        self.assertAlmostEqual(leaf_position['y'] - mid_position['y'], 181.0)
        # The health model itself auto-creates an unrelated "self" entity (zero edges), which
        # shares rank 0 with root and is placed leftmost per the isolated-node rule; root is
        # then pushed right by nodesep(50) + the assumed node width. With the new 200-wide
        # default that gap is 250 (was 222 under the prior 172 approximation) - live-verified
        # (see blueprint Evidence collected). The shared-centerline behavior then pulls
        # mid/leaf (root's only real descendants, one per rank) onto that same x.
        self.assertAlmostEqual(root_position['x'], 250.0)
        self.assertAlmostEqual(mid_position['x'], root_position['x'])
        self.assertAlmostEqual(leaf_position['x'], root_position['x'])

        self.cmd('monitor health-models delete -g {rg} -n {model} --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_healthmodel_arrange_subtree', location='centralus')
    def test_healthmodel_arrange_entity_name_scopes_to_subtree(self, resource_group):
        """`--entity-name` end-to-end (CLI-boundary) proof: a full-model arrange establishes
        every entity's baseline `canvasPosition`; a subsequent `--entity-name mid` arrange must
        then leave the selected root (`mid`) at that exact same pre-existing position, recompute
        `leaf` (its only descendant) relative to it, and leave `root` - mid's own parent, and so
        outside the mid-rooted subtree - completely untouched.

        `root -> mid -> leaf` is the smallest chain that covers all three roles at once: an
        entity above the selection, the selection's anchor, and a descendant below it.
        """
        self.kwargs.update({
            'rg': resource_group,
            'model': self.create_random_name('clihm', 24),
            'root': self.create_random_name('root', 24),
            'mid': self.create_random_name('mid', 24),
            'leaf': self.create_random_name('leaf', 24),
            'location': 'centralus',
        })

        self.cmd('monitor health-models create -g {rg} -n {model} -l {location}')

        for entity in ('root', 'mid', 'leaf'):
            self.cmd('monitor health-models entity create -g {rg} --health-model-name {model} '
                     '-n {%s} --display-name "CLI Test Entity" --impact Standard' % entity)

        self.cmd('monitor health-models relationship create -g {rg} --health-model-name {model} '
                 '-n rel-root-mid --parent-entity-name {root} --child-entity-name {mid}')
        self.cmd('monitor health-models relationship create -g {rg} --health-model-name {model} '
                 '-n rel-mid-leaf --parent-entity-name {mid} --child-entity-name {leaf}')

        # Baseline: a full-model arrange positions every entity.
        self.cmd('monitor health-models arrange -g {rg} --health-model-name {model} --yes')

        def _position(entity_key):
            return self.cmd('monitor health-models entity show -g {rg} --health-model-name {model} '
                            '-n {%s}' % entity_key).get_output_in_json()['properties']['canvasPosition']

        root_before = _position('root')
        mid_before = _position('mid')

        # Scope the second arrange to `mid`'s own subtree (mid + leaf only).
        self.cmd('monitor health-models arrange -g {rg} --health-model-name {model} --entity-name {mid} --yes')

        root_after = _position('root')
        mid_after = _position('mid')
        leaf_after = _position('leaf')

        # Selected root (`mid`) is anchored to its own pre-existing position EXACTLY.
        self.assertEqual(mid_after, mid_before)
        # `root` is outside the `mid`-rooted subtree, so it is byte-for-byte untouched.
        self.assertEqual(root_after, root_before)
        # `leaf` (mid's only descendant) is laid out strictly below the anchored root, using
        # the exact same rank-gap formula (height + ranksep) as the full-model case above,
        # and centered on the same x (a single-child chain has nothing to skew it off-center).
        self.assertAlmostEqual(leaf_after['y'] - mid_after['y'], 181.0)
        self.assertAlmostEqual(leaf_after['x'], mid_after['x'])

        self.cmd('monitor health-models delete -g {rg} -n {model} --yes')

    def test_healthmodel_list_recorded(self):
        self.cmd('monitor health-models list', checks=[self.check('type(@)', 'array')])
