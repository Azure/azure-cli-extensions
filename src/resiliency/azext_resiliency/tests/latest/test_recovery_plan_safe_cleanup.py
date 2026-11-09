# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Maintained OFFLINE regressions for PO-001 and PO-002; no Azure calls."""

import copy
import json
import unittest

from .recovery_plan_safe_cleanup import OwnedScenarioLedger


class OwnedScenarioCleanupTests(unittest.TestCase):
    PLAN = '/providers/Microsoft.Management/serviceGroups/fake/providers/Microsoft.AzureResilienceManagement/recoveryPlans/owned'
    GRANT = '/subscriptions/fake/resourceGroups/fake/providers/Microsoft.Authorization/roleAssignments/owned-guid'

    def setUp(self):
        self.saved = []
        self.ledger = OwnedScenarioLedger(self.PLAN, lambda state: self.saved.append(copy.deepcopy(state)))
        self.ledger.state['creationConfirmed'] = True
        self.mutations = []

    def snapshot(self, status=None):
        jobs = [] if status is None else [{
            'id': self.PLAN + '/recoveryJobs/exact-job',
            'properties': {'resourceId': self.PLAN, 'status': status},
        }]
        return {'provisioningState': 'Succeeded', 'jobs': jobs}

    def cleanup(self, snapshot):
        return self.ledger.cleanup(
            lambda: snapshot, lambda grant: self.mutations.append(('role', grant)),
            lambda: self.mutations.append(('plan', self.PLAN)))

    def grant(self):
        scope = self.GRANT.rsplit('/providers/', 1)[0]
        self.ledger.assignment_intent(self.GRANT, 'exact-principal', scope, 'reader-guid')
        return {
            'id': self.GRANT, 'principalId': 'exact-principal', 'scope': scope,
            'roleDefinitionId': '/providers/Microsoft.Authorization/roleDefinitions/reader-guid',
        }

    def test_pending_action_retains_plan_and_confirmed_grants(self):
        self.ledger.assignment_confirmed(self.GRANT, self.grant())
        self.ledger.action_started('failover')
        self.assertFalse(self.cleanup(self.snapshot('Completed')))
        self.assertEqual(self.mutations, [])
        self.assertEqual(self.ledger.state['assignments'][self.GRANT]['status'], 'Confirmed')

    def test_paused_inprogress_and_unknown_jobs_never_trigger_mutation(self):
        for status in ('Paused', 'InProgress', 'NewUnknownState', None):
            with self.subTest(status=status):
                snapshot = self.snapshot('Completed')
                snapshot['jobs'][0]['properties']['status'] = status
                self.assertFalse(self.cleanup(snapshot))
                self.assertEqual(self.mutations, [])

    def test_missing_authoritative_inventory_fails_closed(self):
        for snapshot in (None, {}, {'provisioningState': 'Succeeded'}):
            self.assertFalse(self.cleanup(snapshot))
            self.assertEqual(self.mutations, [])

    def test_job_owner_mismatch_fails_closed(self):
        snapshot = self.snapshot('Completed')
        snapshot['jobs'][0]['properties']['resourceId'] = '/some-other-plan'
        self.assertFalse(self.cleanup(snapshot))
        self.assertEqual(self.mutations, [])

    def test_foreign_job_id_with_matching_resource_metadata_fails_closed(self):
        snapshot = self.snapshot('Completed')
        snapshot['jobs'][0]['id'] = '/someone-elses-plan/recoveryJobs/exact-job'
        self.assertFalse(self.cleanup(snapshot))
        self.assertEqual(self.mutations, [])

    def test_nonlist_authoritative_inventory_fails_closed(self):
        for inventory in ({}, 'unexpected', None):
            self.assertFalse(self.cleanup({**self.snapshot(), 'jobs': inventory}))
            self.assertEqual(self.mutations, [])

    def test_changed_group_nonce_with_same_plan_and_identity_fails_closed(self):
        self.ledger.state.update(identityPrincipal='same-principal', groupUniqueId='owned-group')
        snapshot = {**self.snapshot(), 'identityPrincipal': 'same-principal', 'groupUniqueId': 'another-group'}
        self.assertFalse(self.cleanup(snapshot))
        self.assertEqual(self.mutations, [])

    def test_pre_put_intent_is_durable_and_blocks_cleanup(self):
        self.grant()
        self.assertEqual(self.saved[-1]['assignments'][self.GRANT]['status'], 'Intended')
        self.assertFalse(self.cleanup(self.snapshot()))
        self.assertEqual(self.mutations, [])

    def test_response_mismatch_retains_ambiguous_intent(self):
        response = self.grant()
        response['principalId'] = 'someone-else'
        with self.assertRaisesRegex(AssertionError, 'ownership'):
            self.ledger.assignment_confirmed(self.GRANT, response)
        self.assertEqual(self.saved[-1]['assignments'][self.GRANT]['status'], 'Ambiguous')
        self.assertFalse(self.cleanup(self.snapshot()))
        self.assertEqual(self.mutations, [])

    def test_exception_after_possible_put_retains_assignment(self):
        self.grant()
        self.ledger.assignment_ambiguous(self.GRANT)
        self.assertFalse(self.cleanup(self.snapshot()))
        self.assertEqual(self.mutations, [])

    def test_terminal_jobs_delete_only_confirmed_owned_grant_then_plan(self):
        self.ledger.assignment_confirmed(self.GRANT, self.grant())
        self.assertTrue(self.cleanup(self.snapshot('Failed')))
        self.assertEqual(self.mutations, [('role', self.GRANT), ('plan', self.PLAN)])
        self.assertEqual(self.ledger.state['cleanup'], 'VerifiedDeleted')

    def test_grant_delete_failure_prevents_plan_delete(self):
        self.ledger.assignment_confirmed(self.GRANT, self.grant())

        def fail(grant):
            self.mutations.append(('role-attempt', grant))
            raise RuntimeError('ambiguous role delete')

        self.assertFalse(self.ledger.cleanup(
            lambda: self.snapshot('Completed'), fail,
            lambda: self.mutations.append(('plan', self.PLAN))))
        self.assertEqual(self.mutations, [('role-attempt', self.GRANT)])
        self.assertEqual(self.ledger.state['cleanup'], 'Retained')

    def test_new_active_job_before_plan_delete_retains_plan(self):
        snapshots = iter((self.snapshot('Completed'), self.snapshot('Paused')))
        self.assertFalse(self.ledger.cleanup(
            lambda: next(snapshots), lambda grant: self.mutations.append(('role', grant)),
            lambda: self.mutations.append(('plan', self.PLAN))))
        self.assertEqual(self.mutations, [])

    def test_failed_job_inventory_query_never_revokes_role(self):
        self.ledger.assignment_confirmed(self.GRANT, self.grant())

        def fail():
            raise RuntimeError('native GET failed')

        self.assertFalse(self.ledger.cleanup(
            fail, lambda grant: self.mutations.append(('role', grant)),
            lambda: self.mutations.append(('plan', self.PLAN))))
        self.assertEqual(self.mutations, [])
        self.assertIn('native GET failed', self.ledger.state['cleanupReasons'])

    def test_new_scenarios_never_register_legacy_deletion_callbacks(self):
        from .recovery_plan_safe import ResiliencySafeRecoveryPlanScenario
        scenario = ResiliencySafeRecoveryPlanScenario.__new__(ResiliencySafeRecoveryPlanScenario)
        scenario._cleanups = []
        scenario.addCleanup(scenario._delete)
        scenario.addCleanup(scenario._delete_role, self.GRANT)
        self.assertEqual(scenario._cleanups, [])

        def safe():
            return None

        scenario.addCleanup(safe)
        self.assertEqual(scenario._cleanups, [(safe, (), {})])

    def test_helper_scenarios_are_not_collected(self):
        from .recovery_plan_safe import ResiliencySafeRecoveryPlanScenario
        names = unittest.TestLoader().getTestCaseNames(ResiliencySafeRecoveryPlanScenario)
        self.assertEqual(names, [])

    def test_terminal_monitor_resolves_nonworkflow_cleanup_only(self):
        key = 'update --plan-description fixed:'
        self.ledger.action_started(key)
        monitor = {'id': '/exact-monitor', 'resourceId': self.PLAN, 'status': 'Succeeded'}
        self.assertTrue(self.ledger.resolve_nonworkflow_terminal(key, monitor, '/exact-monitor'))
        self.assertFalse(self.cleanup(self.snapshot('InProgress')))
        self.assertEqual(self.mutations, [])

    def test_wrong_nonterminal_or_other_monitor_cannot_resolve_pending(self):
        key = 'update --plan-description fixed:'
        self.ledger.action_started(key)
        for overrides in ({'status': 'Accepted'}, {'resourceId': '/other-plan'}, {'id': '/other-monitor'}):
            monitor = {'id': '/exact-monitor', 'resourceId': self.PLAN, 'status': 'Succeeded', **overrides}
            self.assertFalse(self.ledger.resolve_nonworkflow_terminal(key, monitor, '/exact-monitor'))
        self.assertEqual(self.ledger.state['actions'][key], 'Pending')

    def test_workflow_receipt_without_native_job_id_is_never_resolved_by_monitor(self):
        key = 'failover --operation-id owned:'
        self.ledger.action_started(key)
        monitor = {'id': '/exact-monitor', 'resourceId': self.PLAN, 'status': 'Succeeded'}
        self.assertFalse(self.ledger.resolve_nonworkflow_terminal(key, monitor, '/exact-monitor'))
        self.assertFalse(self.cleanup(self.snapshot()))
        self.assertEqual(self.mutations, [])

    def test_same_plan_name_with_changed_identity_is_not_owned(self):
        self.ledger.state['identityPrincipal'] = 'original-principal'
        snapshot = {**self.snapshot(), 'identityPrincipal': 'someone-else'}
        self.assertFalse(self.cleanup(snapshot))
        self.assertEqual(self.mutations, [])

    def test_confirmed_failed_plan_is_deleted_only_with_terminal_job_inventory(self):
        resource = {
            'id': self.PLAN, 'identity': {'type': 'SystemAssigned', 'principalId': 'owned-principal'},
            'properties': {'recoveryGroupsSetting': {'defaultGroup': {'properties': {'groupUniqueId': 'owned-group'}}}},
        }
        self.assertTrue(self.ledger.confirm_creation_from_native(resource, 'owned-group'))
        snapshot = {**self.snapshot('Completed'), 'provisioningState': 'Failed',
                    'identityPrincipal': 'owned-principal', 'groupUniqueId': 'owned-group'}
        self.assertTrue(self.cleanup(snapshot))
        self.assertEqual(self.mutations, [('plan', self.PLAN)])

    def test_accepted_inprogress_and_deleting_plan_are_always_retained(self):
        for state in ('Accepted', 'InProgress', 'Deleting'):
            self.assertFalse(self.cleanup({**self.snapshot(), 'provisioningState': state}))
            self.assertEqual(self.mutations, [])

    def test_unproved_creation_response_does_not_confirm_ownership(self):
        self.ledger.state['creationConfirmed'] = False
        resource = {'id': '/someone-elses-plan', 'identity': {'type': 'SystemAssigned', 'principalId': 'other'}}
        self.assertFalse(self.ledger.confirm_creation_from_native(resource, 'owned-group'))
        self.assertFalse(self.cleanup(self.snapshot()))
        self.assertEqual(self.mutations, [])

    def test_permission_setup_precedes_update_resource(self):
        from .recovery_plan_safe import ResiliencySafeRecoveryPlanScenario
        fake = unittest.TestCase()
        events = []
        resource = {
            'id': 'exact-rr',
            'properties': {'recoveryResourceUniqueId': 'exact-unique', 'inclusionState': 'Included'},
        }
        fake.kwargs = {'group_id': 'exact-group'}
        fake.runbook_id = '/fixture/runbooks/ro-validation-noop'
        fake._runbook_for_configuration = lambda failure: fake.runbook_id
        fake._create = lambda **kwargs: {'identity': {'principalId': 'exact-principal'}}
        fake._storage = lambda: ([resource], resource)
        fake._authorize_runbooks = lambda principal: events.append(('authorize', principal))
        fake.create_guid = lambda: 'exact-operation'
        fake.check = lambda *args: None

        class Result:
            def __init__(self, output):
                self.output = output

            def get_output_in_json(self):
                return self.output

        def command(text, **kwargs):
            if text.startswith('update-resource'):
                events.append(('update', json.loads(fake.kwargs['changes'])))
                return Result({'failedResources': []})
            return Result([resource])

        fake._plan = command
        created, selected = ResiliencySafeRecoveryPlanScenario._configure_runbook(fake)
        self.assertEqual(events[0], ('authorize', 'exact-principal'))
        self.assertEqual(events[1][0], 'update')
        self.assertEqual(events[1][1][0]['selected-protection-solution-type'], 'CustomRunbook')
        setting = events[1][1][0]['selected-protection-solution-setting']
        self.assertEqual(setting, {'custom-runbook': {
            'failover-action': {'resource-id': fake.runbook_id},
            'reprotect-action': {'resource-id': fake.runbook_id},
        }})
        self.assertEqual(selected['id'], 'exact-rr')
        self.assertEqual(created['identity']['principalId'], 'exact-principal')

    @staticmethod
    def independent_finalize_fixture(native_output, before_state='Warning', wait_output=None, wait_exit=0):
        fake = unittest.TestCase()
        fake.recording_processors = []
        calls = []
        fake.kwargs = {'plan_name': 'owned-finalize'}
        fake.plan_id = 'exact-owned-finalize-id'
        fake.successful_scenario = False
        fake._create = lambda: {'identity': {'principalId': 'owned-principal'}}
        resource = {
            'id': 'native-member', 'properties': {
                'resourceId': '/subscriptions/scope-sub/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/member',
                'recoveryResourceUniqueId': 'native-unique', 'inclusionState': 'NewlyDiscovered',
            },
        }
        fake._storage = lambda: ([resource], {})
        fake.create_guid = lambda: 'finalize-operation'
        fake._authorize_grants = lambda principal, grants: calls.append(('reader-grants', principal, grants))
        fake._evidence = lambda *args: None

        def forbidden_setup(**kwargs):
            raise AssertionError('Finalize must not require runbook/Readiness setup.')

        fake._configured = forbidden_setup
        fake._readiness = forbidden_setup

        def valid_configuration(bounded):
            fake.assertTrue(bounded)
            calls.append('valid-custom-runbook-configuration')
            return fake._create(), resource

        fake._configure_runbook = valid_configuration

        class Result:
            def __init__(self, value, exit_code=0):
                self.value = value
                self.output = json.dumps(value) if value is not None else ''
                self.exit_code = exit_code

            def get_output_in_json(self):
                return self.value

        def command(text):
            calls.append(text)
            if text == 'show':
                return Result({
                    'id': fake.plan_id, 'name': 'owned-finalize',
                    'properties': {'planState': before_state, 'provisioningState': 'Succeeded', 'planType': 'Zonal'},
                    'identity': {'principalId': 'owned-principal'},
                })
            if text.startswith('finalize'):
                return Result(native_output)
            if text.startswith('wait'):
                return Result(wait_output, wait_exit)
            raise AssertionError('Unexpected native command: ' + text)

        fake._plan = command
        return fake, calls

    def test_finalize_is_independent_accepts_error_free_or_void_and_requires_native_completion(self):
        from .recovery_plan_safe import ResiliencySafeRecoveryPlanScenario
        for output in ({}, None):
            with self.subTest(output=output):
                fake, calls = self.independent_finalize_fixture(output)
                ResiliencySafeRecoveryPlanScenario._scenario_finalize(fake)
                self.assertTrue(fake.successful_scenario)
                self.assertEqual(calls, [
                    'valid-custom-runbook-configuration', 'show', 'finalize --operation-id {operation_id}',
                    'wait --custom "properties.planState == \'Ready\' && properties.provisioningState == \'Succeeded\' '
                    '&& properties.planType == \'Zonal\' && identity.principalId == \'{finalize_principal}\'" '
                    '--interval 5 --timeout 300',
                ])
                self.assertEqual(fake.kwargs['operation_id'], 'finalize-operation')
                self.assertEqual(fake.kwargs['finalize_principal'], 'owned-principal')

    def test_finalize_native_errors_or_plan_output_are_not_replaced_by_wait(self):
        from .recovery_plan_safe import ResiliencySafeRecoveryPlanScenario
        for output in ({'error': {'code': 'Denied', 'message': 'Permission failure'}},
                       {'name': 'owned-finalize', 'properties': {'planState': 'Ready'}}):
            with self.subTest(output=output):
                fake, calls = self.independent_finalize_fixture(output)
                with self.assertRaises(AssertionError):
                    ResiliencySafeRecoveryPlanScenario._scenario_finalize(fake)
                self.assertFalse(fake.successful_scenario)
                self.assertEqual(calls[-1], 'finalize --operation-id {operation_id}')

    def test_finalize_already_ready_fixture_does_not_count_as_transition_or_invoke_action(self):
        from .recovery_plan_safe import ResiliencySafeRecoveryPlanScenario
        fake, calls = self.independent_finalize_fixture({}, before_state='Ready')
        with self.assertRaisesRegex(AssertionError, 'Warning-to-Ready'):
            ResiliencySafeRecoveryPlanScenario._scenario_finalize(fake)
        self.assertFalse(fake.successful_scenario)
        self.assertEqual(calls, ['valid-custom-runbook-configuration', 'show'])

    def test_finalize_failed_or_nonempty_native_wait_never_marks_success(self):
        from .recovery_plan_safe import ResiliencySafeRecoveryPlanScenario
        for value, exit_code in ((None, 1), ({'error': 'Wait operation timed-out after 300 seconds'}, 0)):
            with self.subTest(value=value, exit_code=exit_code):
                fake, calls = self.independent_finalize_fixture({}, wait_output=value, wait_exit=exit_code)
                with self.assertRaises(AssertionError):
                    ResiliencySafeRecoveryPlanScenario._scenario_finalize(fake)
                self.assertFalse(fake.successful_scenario)
                self.assertTrue(calls[-1].startswith('wait --custom'))

    def native_grant_fixture(self, timeout=False):
        fake = unittest.TestCase()
        fake.kwargs = {}
        fake.ledger = self.ledger
        fake.create_guid = lambda: 'owned-guid'
        fake._evidence = lambda *args: None
        scope = self.GRANT.rsplit('/providers/', 1)[0]

        class Result:
            def __init__(self, output):
                self.output = output

            def get_output_in_json(self):
                return self.output

        def command(text):
            if text.startswith('az role assignment list'):
                return Result([])
            self.assertTrue(text.startswith('az role assignment create'))
            intent = self.saved[-1]['assignments'][self.GRANT]
            self.assertEqual(intent['status'], 'Intended')
            self.assertEqual(intent['principalId'], 'exact-principal')
            self.assertEqual(intent['scope'], scope)
            self.mutations.append(('put', self.GRANT))
            if timeout:
                raise TimeoutError('simulated ambiguous PUT')
            return Result({
                'id': self.GRANT, 'principalId': 'exact-principal', 'scope': scope,
                'roleDefinitionId': '/providers/Microsoft.Authorization/roleDefinitions/reader-guid',
            })

        fake._role_cmd = command
        return fake, scope

    def test_native_grant_wrapper_persists_intent_before_put(self):
        from .recovery_plan_safe import ResiliencySafeRecoveryPlanScenario
        fake, scope = self.native_grant_fixture()
        ResiliencySafeRecoveryPlanScenario._authorize_grants(fake, 'exact-principal', [(scope, 'reader-guid')])
        self.assertEqual(self.mutations, [('put', self.GRANT)])
        self.assertEqual(self.ledger.state['assignments'][self.GRANT]['status'], 'Confirmed')
        self.assertEqual(fake.kwargs['assignment_subscription'], 'fake')

    def test_native_grant_wrapper_timeout_retains_ambiguity_without_cleanup(self):
        from .recovery_plan_safe import ResiliencySafeRecoveryPlanScenario
        fake, scope = self.native_grant_fixture(timeout=True)
        with self.assertRaisesRegex(TimeoutError, 'ambiguous PUT'):
            ResiliencySafeRecoveryPlanScenario._authorize_grants(fake, 'exact-principal', [(scope, 'reader-guid')])
        self.assertEqual(self.ledger.state['assignments'][self.GRANT]['status'], 'Ambiguous')
        self.assertFalse(self.cleanup(self.snapshot('Completed')))
        self.assertEqual(self.mutations, [('put', self.GRANT)])

    @staticmethod
    def input_scenario(same=True):
        from azure.cli.testsdk.scenario_tests.recording_processors import GeneralNameReplacer
        from .recovery_plan_native import (
            ResiliencyNativeRecoveryPlanScenario, RecoveryPlanSubscriptionScrubber)
        from .recovery_plan_safe import ResiliencySafeRecoveryPlanScenario
        cls = ResiliencySafeRecoveryPlanScenario if same else ResiliencyNativeRecoveryPlanScenario
        scenario = cls.__new__(cls)
        scenario.subscription_scrubber = RecoveryPlanSubscriptionScrubber()
        scenario.name_replacer = GeneralNameReplacer()
        primary = '11111111-1111-4111-8111-111111111111'
        subscription = primary if same else '22222222-2222-4222-8222-222222222222'
        aa = '/subscriptions/' + subscription + '/resourceGroups/CanaryRG/providers/Microsoft.Automation/automationAccounts/CustomerAA'
        actual = {
            'subscriptionId': subscription, 'tenantId': '33333333-3333-4333-8333-333333333333',
            'resourceGroup': 'CanaryRG', 'automationAccount': 'CustomerAA', 'automationAccountId': aa,
            'noOpRunbookId': aa + '/runbooks/CustomerRunbook',
        }
        return scenario, actual, primary

    def test_same_subscription_fixture_preserves_primary_alias_and_customer_runbook_name(self):
        from azure.cli.testsdk.scenario_tests.const import MOCKED_SUBSCRIPTION_ID
        scenario, actual, primary = self.input_scenario()
        configured = scenario._prepare_live_fixture(actual, primary, 'ApprovedSG')
        self.assertEqual(configured['noOpRunbookId'], actual['noOpRunbookId'])
        self.assertNotEqual(scenario.subscription_scrubber.secondary_actual, primary)
        wire = scenario.subscription_scrubber._replace_subscription_id(json.dumps({
            'runbook': actual['noOpRunbookId'], 'storage': '/subscriptions/' + primary + '/resourceGroups/CanaryRG/storage',
        }))
        response = {'headers': {'content-type': ['application/json']}, 'body': {'string': wire}}
        scenario.name_replacer.process_response(response)
        sanitized = json.loads(response['body']['string'])
        expected = scenario._playback_fixture()
        self.assertIsNone(expected['intentionalFailureRunbookId'])
        self.assertEqual(sanitized['runbook'], expected['noOpRunbookId'])
        self.assertIn('/subscriptions/' + MOCKED_SUBSCRIPTION_ID + '/', sanitized['storage'])
        self.assertNotIn(scenario.subscription_scrubber.secondary, response['body']['string'])

    def test_legacy_cross_subscription_fixture_keeps_original_fake_ids_and_failure_default(self):
        from azure.cli.testsdk.scenario_tests.const import MOCKED_SUBSCRIPTION_ID
        scenario, actual, primary = self.input_scenario(same=False)
        scenario._prepare_live_fixture(actual, primary, 'ApprovedSG')
        fake = scenario._playback_fixture()
        self.assertEqual(fake['subscriptionId'], '00000000-0000-0000-0000-000000000003')
        self.assertEqual(fake['noOpRunbookId'],
                         '/subscriptions/00000000-0000-0000-0000-000000000003/resourceGroups/ro-cli-custom-fixture'
                         '/providers/Microsoft.Automation/automationAccounts/ro-cli-validation-aa/runbooks/ro-validation-noop')
        self.assertEqual(fake['intentionalFailureRunbookId'],
                         fake['noOpRunbookId'].removesuffix('ro-validation-noop') + 'ro-validation-failure')
        self.assertEqual(scenario.subscription_scrubber._replace_subscription_id('/subscriptions/' + primary + '/'),
                         '/subscriptions/' + MOCKED_SUBSCRIPTION_ID + '/')
        self.assertEqual(scenario.subscription_scrubber._replace_subscription_id(actual['noOpRunbookId']),
                         actual['noOpRunbookId'].replace(actual['subscriptionId'], fake['subscriptionId']))

    def test_fixture_rejects_mode_mismatch_and_foreign_noop_before_registering_aliases(self):
        for invalid in ('mode', 'foreign', 'missing', 'aa', 'empty', 'path', 'query', 'fragment', 'encoded', 'backslash'):
            with self.subTest(invalid=invalid):
                scenario, actual, primary = self.input_scenario()
                if invalid == 'mode':
                    actual['subscriptionId'] = '22222222-2222-4222-8222-222222222222'
                    actual['automationAccountId'] = actual['automationAccountId'].replace(primary, actual['subscriptionId'])
                    actual['noOpRunbookId'] = actual['noOpRunbookId'].replace(primary, actual['subscriptionId'])
                elif invalid == 'foreign':
                    actual['noOpRunbookId'] = actual['noOpRunbookId'].replace('/CustomerAA/', '/OtherAA/')
                elif invalid == 'missing':
                    actual.pop('noOpRunbookId')
                elif invalid == 'aa':
                    actual['automationAccountId'] += '-different'
                else:
                    child = {'empty': '', 'path': 'CustomerRunbook/child', 'query': 'CustomerRunbook?sig=value',
                             'fragment': 'CustomerRunbook#part', 'encoded': 'CustomerRunbook%2Fchild',
                             'backslash': 'CustomerRunbook\\child'}[invalid]
                    actual['noOpRunbookId'] = actual['automationAccountId'] + '/runbooks/' + child
                with self.assertRaises(ValueError):
                    scenario._prepare_live_fixture(actual, primary, 'ApprovedSG')
                self.assertEqual(scenario.name_replacer.names_name, [])

    def test_missing_foreign_or_noop_failure_id_aborts_both_helpers_before_create_or_grants(self):
        from unittest.mock import Mock
        from .recovery_plan_native import ResiliencyNativeRecoveryPlanScenario
        from .recovery_plan_safe import ResiliencySafeRecoveryPlanScenario
        for cls in (ResiliencyNativeRecoveryPlanScenario, ResiliencySafeRecoveryPlanScenario):
            for invalid in (None, '/other-aa/runbooks/failure', '/owned-aa/runbooks/customer'):
                with self.subTest(cls=cls.__name__, invalid=invalid):
                    scenario = cls.__new__(cls)
                    scenario.automation_id = '/owned-aa'
                    scenario.runbook_id = '/owned-aa/runbooks/customer'
                    scenario.failure_runbook_id = invalid
                    scenario._create = Mock()
                    scenario._authorize_runbooks = Mock()
                    with self.assertRaises(ValueError):
                        scenario._configure_runbook(failure=True)
                    scenario._create.assert_not_called()
                    scenario._authorize_runbooks.assert_not_called()

    def test_explicit_valid_failure_id_is_not_derived_from_customer_name(self):
        scenario, actual, primary = self.input_scenario()
        actual['intentionalFailureRunbookId'] = actual['automationAccountId'] + '/runbooks/DeliberateFailure'
        prepared = scenario._prepare_live_fixture(actual, primary, 'ApprovedSG')
        scenario.runbook_id = prepared['noOpRunbookId']
        scenario.failure_runbook_id = prepared['intentionalFailureRunbookId']
        scenario.automation_id = prepared['automationAccountId']
        self.assertEqual(scenario._runbook_for_configuration(True), actual['intentionalFailureRunbookId'])
        self.assertEqual(scenario._runbook_for_configuration(False), actual['noOpRunbookId'])
        self.assertIn(('DeliberateFailure', 'ro-validation-failure'), scenario.name_replacer.names_name)

    def test_selected_scope_requires_empty_source_array_and_exact_owned_protected_native_id(self):
        from unittest.mock import Mock
        from .recovery_plan_safe import ResiliencySafeRecoveryPlanScenario
        current = {
            'id': self.PLAN + '/recoveryResources/exact-native',
            'properties': {'resourceId': '/subscriptions/fake/providers/Microsoft.Storage/storageAccounts/member',
                           'inclusionState': 'Included',
                           'protectionStatus': 'Protected', 'selectedProtectionSolutionType': 'CustomRunbook'},
        }
        fake = unittest.TestCase()
        fake.plan_type, fake.plan_id = 'Zonal', self.PLAN
        fake.storage_id = current['properties']['resourceId']
        fake.kwargs = {}
        fake._evidence = Mock()
        result = Mock()
        result.get_output_in_json.return_value = current
        fake._plan = Mock(return_value=result)
        command = ResiliencySafeRecoveryPlanScenario._selected_request(fake, current, consent='Unspecified')
        request = json.loads(fake.kwargs['action_request'])
        self.assertEqual(request['selected-resource-ids'], [current['id']])
        self.assertEqual(request['source-locations'], [])
        self.assertEqual(request, {
            'source-locations': [],
            'selected-resource-ids': [current['id']],
            'execution-configurations': {'user-consent': 'Unspecified'},
        })
        self.assertEqual(request['execution-configurations']['user-consent'], 'Unspecified')
        self.assertIn('--failover-direction FromSpecificLocations', command)
        fake._evidence.assert_called_once()
        for overrides in ({'protectionStatus': 'NotProtected'}, {'inclusionState': 'Excluded'},
                          {'resourceId': '/another/storage'}, {'selectedProtectionSolutionType': 'None'}):
            with self.subTest(overrides=overrides):
                result.get_output_in_json.return_value = {**current, 'properties': {**current['properties'], **overrides}}
                with self.assertRaises(AssertionError):
                    ResiliencySafeRecoveryPlanScenario._selected_request(fake, current)

        result.get_output_in_json.return_value = {**current, 'id': self.PLAN + '/recoveryResources/other'}
        with self.assertRaises(AssertionError):
            ResiliencySafeRecoveryPlanScenario._selected_request(fake, current)
        foreign = {**current, 'id': self.PLAN + '-different/recoveryResources/exact-native'}
        result.get_output_in_json.return_value = foreign
        with self.assertRaises(AssertionError):
            ResiliencySafeRecoveryPlanScenario._selected_request(fake, foreign)
        empty_id = {**current, 'id': ''}
        result.get_output_in_json.return_value = empty_id
        with self.assertRaises(AssertionError):
            ResiliencySafeRecoveryPlanScenario._selected_request(fake, empty_id)
        nonstorage = {**current, 'properties': {**current['properties'], 'resourceId': '/providers/Microsoft.Compute/vm'}}
        fake.storage_id = nonstorage['properties']['resourceId']
        result.get_output_in_json.return_value = nonstorage
        with self.assertRaises(AssertionError):
            ResiliencySafeRecoveryPlanScenario._selected_request(fake, nonstorage)

    def test_all_six_safe_setup_modes_are_zonal_without_running_sdk_setup(self):
        from unittest.mock import Mock, patch
        from .recovery_plan_native import ResiliencyNativeRecoveryPlanScenario
        from .test_resiliency_recovery_plan_failover_only_20261108 import ResiliencyFailoverOnly20261108Scenario
        from .test_resiliency_recovery_plan_finalize_ready_v2_20261109 import ResiliencyFinalizeReadyV2Scenario
        from .test_resiliency_recovery_plan_identity_assign_only_20261109 import (
            ResiliencyIdentityAssignOnly20261109Scenario)
        from .test_resiliency_recovery_plan_resume_only_20261109 import ResiliencyResumeOnly20261109Scenario
        from .test_resiliency_recovery_plan_update_retry import ResiliencyRecoveryPlanUpdateRetryScenario
        from .test_resiliency_recovery_plan_validate_failover_only_20261109 import (
            ResiliencyValidateFailoverOnly20261109Scenario)
        classes = (
            ResiliencyFailoverOnly20261108Scenario, ResiliencyFinalizeReadyV2Scenario,
            ResiliencyIdentityAssignOnly20261109Scenario, ResiliencyResumeOnly20261109Scenario,
            ResiliencyRecoveryPlanUpdateRetryScenario, ResiliencyValidateFailoverOnly20261109Scenario,
        )
        with patch.object(ResiliencyNativeRecoveryPlanScenario, 'setUp'):
            for scenario_type in classes:
                names = unittest.TestLoader().getTestCaseNames(scenario_type)
                self.assertEqual(len(names), 1)
                with self.subTest(scenario=scenario_type.__name__, name=names[0]):
                    scenario = scenario_type.__new__(scenario_type)
                    name = names[0]
                    unittest.TestCase.__init__(scenario, name)
                    scenario.kwargs = {'sg_name': 'shared', 'plan_name': 'owned'}
                    scenario._is_recording = Mock(return_value=False)
                    scenario.create_random_name = Mock(return_value='finite-manual-pause')
                    scenario.setUp()
                    self.assertEqual(scenario.plan_type, 'Zonal')
                    self.assertTrue(scenario.SAME_SUBSCRIPTION_FIXTURE)
                    self.assertEqual(scenario.kwargs['manual_action_name'], 'finite-manual-pause')
                    self.assertTrue(scenario.plan_id.endswith('/recoveryPlans/owned'))
