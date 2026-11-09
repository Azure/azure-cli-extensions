"""Reject false Ready-state Finalize coverage and native errors."""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from azure.cli.core.aaz import AAZCommand
from azure.cli.core.aaz._command_ctx import AAZCommandCtx, AAZObject, AAZObjectType
from azure.cli.core.commands.arm import verify_property
from azext_resiliency.aaz.latest.resiliency.recovery_plan._wait import Wait
from azext_resiliency.tests.latest import test_resiliency_recovery_plan_finalize_ready_v2_20261109 as _adapter


class FinalizeGuards(unittest.TestCase):
    def scenario(self, state='Ready', output=None, wait_exit=0):
        case = object.__new__(_adapter.ResiliencyFinalizeReadyV2Scenario)
        unittest.TestCase.__init__(
            case, 'test_resiliency_recovery_plan_native_finalize_ready_record_20261109_v2')
        case.cli_ctx = SimpleNamespace(invoke=Mock())
        case.recording_processors = []
        case.plan_id = '/providers/Microsoft.Management/serviceGroups/owned/recoveryPlans/ownedplan'
        case.kwargs = {'group_id': 'owned-group'}
        case._configure_runbook = Mock(return_value=(
            {'identity': {'principalId': 'owned-principal'}}, {'id': 'owned-resource'}))
        plan = {
            'id': case.plan_id,
            'properties': {'planState': state, 'provisioningState': 'Succeeded', 'planType': 'Zonal',
                           'recoveryGroupsSetting': {'defaultGroup': {
                               'properties': {'groupUniqueId': 'owned-group'}}}},
            'identity': {'type': 'SystemAssigned', 'principalId': 'owned-principal'}}
        finalize = SimpleNamespace(
            exit_code=0, output=json.dumps(output) if output is not None else '',
            get_output_in_json=lambda: output)
        wait = SimpleNamespace(exit_code=wait_exit, output='')
        case._plan = Mock(side_effect=[
            SimpleNamespace(get_output_in_json=lambda: plan), finalize, wait,
            SimpleNamespace(get_output_in_json=lambda: plan)])
        case._evidence = Mock()
        case.create_guid = Mock(return_value='00000000-0000-0000-0000-000000000001')
        case.successful_scenario = False
        return case

    def test_only_finalize_ready_case_is_collectable(self):
        self.assertEqual(
            unittest.defaultTestLoader.getTestCaseNames(_adapter.ResiliencyFinalizeReadyV2Scenario),
            ['test_resiliency_recovery_plan_native_finalize_ready_record_20261109_v2'])
        self.assertIsNone(
            _adapter.ResiliencyFinalizeReadyV2Scenario.test_resiliency__scenario_finalize)

    def test_warning_fixture_cannot_be_reported_as_ready_revalidation(self):
        case = self.scenario(state='Warning')
        with self.assertRaises(AssertionError):
            case.test_resiliency_recovery_plan_native_finalize_ready_record_20261109_v2()
        self.assertEqual(case._plan.call_count, 1)
        self.assertFalse(case.successful_scenario)

    def test_native_finalize_error_cannot_pass_using_ready_readback(self):
        case = self.scenario(output={'error': {'code': 'NativeFinalizeFailure'}})
        with self.assertRaises(AssertionError):
            case.test_resiliency_recovery_plan_native_finalize_ready_record_20261109_v2()
        self.assertEqual(case._plan.call_count, 2)
        self.assertFalse(case.successful_scenario)

    def test_failed_native_wait_cannot_prove_completion(self):
        case = self.scenario(wait_exit=1)
        with self.assertRaises(AssertionError):
            case.test_resiliency_recovery_plan_native_finalize_ready_record_20261109_v2()
        self.assertEqual(case._plan.call_count, 3)
        self.assertFalse(case.successful_scenario)

    def test_wait_without_plan_type_keeps_state_and_identity_guards(self):
        case = self.scenario()
        case.test_resiliency_recovery_plan_native_finalize_ready_record_20261109_v2()
        self.assertTrue(case.successful_scenario)
        command = case._plan.call_args_list[2].args[0]
        predicate = command.split('--custom "', 1)[1].split('" --interval', 1)[0]
        predicate = predicate.format(**case.kwargs)
        self.assertNotIn('planType', predicate)
        for state, provisioning, principal, expected in (
                ('Ready', 'Succeeded', 'owned-principal', True),
                ('Warning', 'Succeeded', 'owned-principal', False),
                ('Ready', 'Creating', 'owned-principal', False),
                ('Ready', 'Succeeded', 'foreign-principal', False)):
            with self.subTest(state=state, provisioning=provisioning, principal=principal):
                context = object.__new__(AAZCommandCtx)
                context._vars_schema = AAZObjectType()
                context.vars = AAZObject(schema=context._vars_schema, data={})
                context.set_var('instance', {
                    'properties': {'planState': state, 'provisioningState': provisioning, 'planType': 'Zonal'},
                    'identity': {'type': 'SystemAssigned', 'principalId': principal},
                }, schema_builder=Wait.RecoveryPlansGet._build_schema_on_200)
                native = AAZCommand.deserialize_output(context.vars.instance, client_flatten=False)
                self.assertNotIn('planType', native['properties'])
                self.assertEqual(bool(verify_property(native, predicate)), expected)
