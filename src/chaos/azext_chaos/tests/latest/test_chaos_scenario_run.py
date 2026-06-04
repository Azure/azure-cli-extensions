# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Integration tests for the ``az chaos scenario run`` command group.

Test classes:
  - TestScenarioRunStartDefault (E5-T3a-a): default mode validates then executes
  - TestScenarioRunStartSkipValidation (E5-T3a-b): --skip-validation skips validate
  - TestScenarioRunStartValidationFailure (E5-T3a-c): failed validation → non-zero exit
  - TestScenarioRunStartNoWait (E5-T3a-d): --no-wait applies only to execute LRO
  - TestScenarioRunStartFireAndForget (E5-T3a-e): --skip-validation --no-wait
  - TestCatalogScenarioEvalGate (E5-T3b): catalog scenario first-run eval-gate recovery
  - TestScenarioRunOperations (E5-T4): list → show → cancel

Re-record when: playback fails OR a spec change merges to
``azure-rest-api-specs[-pr]`` under ``Microsoft.Chaos`` that touches a
covered scenario-run operation.
"""

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer


# ── Shared mixin for workspace + scenario + config setup ────────────────

class _ChaosRunTestBase(ScenarioTest):
    """Base class that provisions a workspace, scenario, and config for run tests."""

    def _setup_workspace_and_config(self, resource_group, *,
                                    refresh_recommendations=True):
        """Create workspace → scenario → config.  Optionally run
        refresh-recommendations (skipped for the eval-gate negative test)."""
        self.kwargs.update({
            'ws': self.create_random_name('ws', 15),
            'scenario': self.create_random_name('sc', 15),
            'config': self.create_random_name('cfg', 15),
            'loc': 'eastus',
        })

        self.cmd(
            'chaos workspace create -n {ws} -g {rg} -l {loc} '
            '--identity-type SystemAssigned '
            '--scopes /subscriptions/{sub}/resourceGroups/{rg}',
        )
        self.cmd(
            'chaos scenario create -w {ws} -g {rg} -n {scenario}',
        )
        if refresh_recommendations:
            self.cmd(
                'chaos workspace refresh-recommendations -n {ws} -g {rg}',
            )
        self.cmd(
            "chaos scenario config create -w {ws} -g {rg} "
            "--scenario-name {scenario} -n {config} "
            "--parameters '{{}}'",
        )

    def _cleanup(self):
        """Delete config → scenario → workspace."""
        self.cmd(
            'chaos scenario config delete -w {ws} -g {rg} '
            '--scenario-name {scenario} -n {config} --yes',
        )
        self.cmd('chaos scenario delete -w {ws} -g {rg} -n {scenario} --yes')
        self.cmd('chaos workspace delete -n {ws} -g {rg} --yes')


# ═══════════════════════════════════════════════════════════════════════
# E5-T3a: scenario run start mode matrix
# ═══════════════════════════════════════════════════════════════════════


class TestScenarioRunStartDefault(_ChaosRunTestBase):
    """E5-T3a (a): ``run start`` (default) → validate issued → execute →
    run ID returned."""

    @ResourceGroupPreparer(name_prefix='cli_test_chaos_run_def', location='eastus')
    def test_run_start_default(self, resource_group):
        self._setup_workspace_and_config(resource_group)

        # Default mode: validate + execute
        result = self.cmd(
            'chaos scenario run start -w {ws} -g {rg} '
            '--scenario-name {scenario} --config-name {config}',
            checks=[
                self.exists('name'),
                self.exists('properties.status'),
            ],
        ).get_output_in_json()

        # The returned resource is a ScenarioRun with a run ID
        self.assertTrue(
            result.get('name'),
            'run start should return a ScenarioRun with a name (run ID)',
        )

        self._cleanup()


class TestScenarioRunStartSkipValidation(_ChaosRunTestBase):
    """E5-T3a (b): ``run start --skip-validation`` → no validate →
    execute issued directly."""

    @ResourceGroupPreparer(name_prefix='cli_test_chaos_run_skip', location='eastus')
    def test_run_start_skip_validation(self, resource_group):
        self._setup_workspace_and_config(resource_group)

        result = self.cmd(
            'chaos scenario run start -w {ws} -g {rg} '
            '--scenario-name {scenario} --config-name {config} '
            '--skip-validation',
            checks=[
                self.exists('name'),
            ],
        ).get_output_in_json()

        self.assertTrue(
            result.get('name'),
            'run start --skip-validation should return a run ID',
        )

        self._cleanup()


class TestScenarioRunStartValidationFailure(_ChaosRunTestBase):
    """E5-T3a (c): negative test — ``run start`` against a config that
    fails validation → non-zero exit and no execute issued.

    Uses an intentionally malformed parameters body (an invalid JSON structure
    with unrecognised properties) so the server-side validation rejects the
    config.  The base-class ``_setup_workspace_and_config`` creates a *valid*
    config; this test creates a second, invalid one for the negative path.
    """

    @ResourceGroupPreparer(name_prefix='cli_test_chaos_run_fail', location='eastus')
    def test_run_start_validation_failure(self, resource_group):
        self._setup_workspace_and_config(resource_group)

        # Create a deliberately invalid config with malformed parameters.
        # The invalid parameters contain an unknown property that the service
        # validation will reject, ensuring a non-Succeeded status.
        self.kwargs['bad_config'] = self.create_random_name('bad', 15)
        self.cmd(
            "chaos scenario config create -w {ws} -g {rg} "
            "--scenario-name {scenario} -n {bad_config} "
            "--parameters '{{\"__invalid_property__\": true, "
            "\"__force_validation_failure__\": 1}}'",
        )

        # run start should fail because validation fails
        self.cmd(
            'chaos scenario run start -w {ws} -g {rg} '
            '--scenario-name {scenario} --config-name {bad_config}',
            expect_failure=True,
        )

        # cleanup extra config
        self.cmd(
            'chaos scenario config delete -w {ws} -g {rg} '
            '--scenario-name {scenario} -n {bad_config} --yes',
        )
        self._cleanup()


class TestScenarioRunStartNoWait(_ChaosRunTestBase):
    """E5-T3a (d): ``run start --no-wait`` → validate polled to completion →
    execute kicked off → command returns with run ID before execute completes
    (demonstrating --no-wait applies only to execute LRO)."""

    @ResourceGroupPreparer(name_prefix='cli_test_chaos_run_nw', location='eastus')
    def test_run_start_no_wait(self, resource_group):
        self._setup_workspace_and_config(resource_group)

        result = self.cmd(
            'chaos scenario run start -w {ws} -g {rg} '
            '--scenario-name {scenario} --config-name {config} '
            '--no-wait',
            checks=[
                self.exists('runId'),
            ],
        ).get_output_in_json()

        # With --no-wait, the run ID is parsed from the Location header
        run_id = result.get('runId')
        self.assertTrue(run_id, '--no-wait should return a runId')

        # Verify the run exists via show (it may still be running)
        self.kwargs['run_id'] = run_id
        self.cmd(
            'chaos scenario run show -w {ws} -g {rg} '
            '--scenario-name {scenario} --run-id {run_id}',
            checks=[
                self.check('name', run_id),
                self.exists('properties.status'),
            ],
        )

        self._cleanup()


class TestScenarioRunStartFireAndForget(_ChaosRunTestBase):
    """E5-T3a (e): ``run start --skip-validation --no-wait`` →
    no validate → execute kicked off → returns before execute completes."""

    @ResourceGroupPreparer(name_prefix='cli_test_chaos_run_ff', location='eastus')
    def test_run_start_fire_and_forget(self, resource_group):
        self._setup_workspace_and_config(resource_group)

        result = self.cmd(
            'chaos scenario run start -w {ws} -g {rg} '
            '--scenario-name {scenario} --config-name {config} '
            '--skip-validation --no-wait',
            checks=[
                self.exists('runId'),
            ],
        ).get_output_in_json()

        run_id = result.get('runId')
        self.assertTrue(run_id, '--skip-validation --no-wait should return a runId')

        self._cleanup()


# ═══════════════════════════════════════════════════════════════════════
# E5-T3b: catalog-scenario eval-gate recovery
# ═══════════════════════════════════════════════════════════════════════


class TestCatalogScenarioEvalGate(_ChaosRunTestBase):
    """E5-T3b: from a clean workspace (no prior refresh-recommendations),
    ``run start`` fails with eval-gate error → refresh-recommendations →
    retry succeeds.  This is the objective check for G6."""

    @ResourceGroupPreparer(name_prefix='cli_test_chaos_eval', location='eastus')
    def test_catalog_scenario_eval_gate_recovery(self, resource_group):
        # Setup WITHOUT refresh-recommendations
        self._setup_workspace_and_config(resource_group,
                                         refresh_recommendations=False)

        # Attempt run start → should fail with eval-gate error
        result = self.cmd(
            'chaos scenario run start -w {ws} -g {rg} '
            '--scenario-name {scenario} --config-name {config}',
            expect_failure=True,
        )
        # Verify the error message contains the friendly guidance
        stderr = result.output if hasattr(result, 'output') else str(result)
        self.assertIn('refresh-recommendations', stderr,
                      'eval-gate error should reference refresh-recommendations command')

        # Run refresh-recommendations to satisfy the eval gate
        self.cmd(
            'chaos workspace refresh-recommendations -n {ws} -g {rg}',
        )

        # Retry run start → should now succeed
        retry_result = self.cmd(
            'chaos scenario run start -w {ws} -g {rg} '
            '--scenario-name {scenario} --config-name {config}',
        ).get_output_in_json()

        self.assertTrue(
            retry_result.get('name'),
            'run start should succeed after refresh-recommendations',
        )

        self._cleanup()


# ═══════════════════════════════════════════════════════════════════════
# E5-T4: scenario run list → show → cancel
# ═══════════════════════════════════════════════════════════════════════


class TestScenarioRunOperations(_ChaosRunTestBase):
    """E5-T4: run list → show → cancel lifecycle."""

    @ResourceGroupPreparer(name_prefix='cli_test_chaos_run_ops', location='eastus')
    def test_run_list_show_cancel(self, resource_group):
        self._setup_workspace_and_config(resource_group)

        # Start a run (--skip-validation for speed)
        start_result = self.cmd(
            'chaos scenario run start -w {ws} -g {rg} '
            '--scenario-name {scenario} --config-name {config} '
            '--skip-validation --no-wait',
            checks=[
                self.exists('runId'),
            ],
        ).get_output_in_json()

        run_id = start_result.get('runId')
        self.assertTrue(run_id, 'Expected a run ID from run start')
        self.kwargs['run_id'] = run_id

        # ── run list ────────────────────────────────────────────────────
        list_result = self.cmd(
            'chaos scenario run list -w {ws} -g {rg} '
            '--scenario-name {scenario}',
            checks=[
                self.greater_than('length(@)', 0),
            ],
        ).get_output_in_json()
        self.assertTrue(
            any(r['name'] == run_id for r in list_result),
            'Started run not found in list output',
        )

        # ── run show ────────────────────────────────────────────────────
        self.cmd(
            'chaos scenario run show -w {ws} -g {rg} '
            '--scenario-name {scenario} --run-id {run_id}',
            checks=[
                self.check('name', run_id),
                self.exists('properties.status'),
            ],
        )

        # ── run cancel ──────────────────────────────────────────────────
        self.cmd(
            'chaos scenario run cancel -w {ws} -g {rg} '
            '--scenario-name {scenario} --run-id {run_id}',
        )

        # Verify cancelled status
        show_after = self.cmd(
            'chaos scenario run show -w {ws} -g {rg} '
            '--scenario-name {scenario} --run-id {run_id}',
        ).get_output_in_json()
        status = (show_after.get('properties') or {}).get('status', '')
        self.assertIn(
            status, ('Cancelled', 'Cancelling', 'Failed'),
            f'Run status should reflect cancellation, got: {status}',
        )

        self._cleanup()
