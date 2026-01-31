# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Unit tests for azure-changesafety CLI extension.

Tests cover ChangeRecord, StageMap, and StageProgression commands.
"""

import copy
import datetime
import sys
import types
from types import SimpleNamespace
from unittest import mock

from azure.cli.testsdk import ScenarioTest, JMESPathCheck

from azext_changesafety.custom import (
    _inject_change_definition_into_content,
    _inject_targets_into_result,
    _normalize_targets_arg,
)
from azure.cli.core.aaz import AAZAnyType, has_value
from azure.cli.core.aaz._arg_action import AAZArgActionOperations, _ELEMENT_APPEND_KEY


# =============================================================================
# ChangeRecord Tests
# =============================================================================


class ChangeRecordScenario(ScenarioTest):
    """Test scenarios for ChangeRecord CRUD operations."""

    FAKE_SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
    _SCENARIO_STATE = {}

    class _DummyPoller:  # pylint: disable=too-few-public-methods
        """Mock poller for LRO operations."""

        def result(self, timeout=None):  # pylint: disable=unused-argument
            return None

        def wait(self, timeout=None):  # pylint: disable=unused-argument
            return None

        def done(self):
            return True

        def add_done_callback(self, func):
            if func:
                func(self)

    @staticmethod
    def _dummy_ctx_with_change_definition(payload):
        """Create a dummy context with change_definition variable."""
        dummy = SimpleNamespace()
        dummy.to_serialized_data = lambda: payload
        return SimpleNamespace(vars=SimpleNamespace(change_definition=dummy))

    @classmethod
    def _ensure_msrestazure_stub(cls):
        """Ensure msrestazure stub is available for tests."""
        if 'msrestazure' in sys.modules:
            return

        msrestazure = types.ModuleType('msrestazure')
        azure_operation = types.ModuleType('msrestazure.azure_operation')

        class AzureOperationPoller:  # pylint: disable=too-few-public-methods
            def _delay(self, *args, **kwargs):  # pylint: disable=unused-argument
                return

        azure_operation.AzureOperationPoller = AzureOperationPoller
        arm_polling = types.ModuleType('msrestazure.polling.arm_polling')

        class ARMPolling:  # pylint: disable=too-few-public-methods
            def _delay(self, *args, **kwargs):  # pylint: disable=unused-argument
                return

        arm_polling.ARMPolling = ARMPolling
        polling = types.ModuleType('msrestazure.polling')
        polling.arm_polling = arm_polling

        msrestazure.azure_operation = azure_operation
        msrestazure.polling = polling

        sys.modules['msrestazure'] = msrestazure
        sys.modules['msrestazure.azure_operation'] = azure_operation
        sys.modules['msrestazure.polling'] = polling
        sys.modules['msrestazure.polling.arm_polling'] = arm_polling

    @staticmethod
    def _get_arg_value(cmd, arg_name, default=None):
        """Get argument value from command context."""
        arg = getattr(cmd.ctx.args, arg_name, None)
        if arg is None or not has_value(arg):
            return default
        return arg.to_serialized_data()

    @staticmethod
    def _build_mock_instance(
            name,
            resource_group,
            subscription_id,
            change_type,
            rollout_type,
            targets,
            comments=None,
            change_definition=None,
            stage_map=None,
            anticipated_start_time=None,
            anticipated_end_time=None):
        """Build a mock ChangeRecord instance."""
        return {
            "id": f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.ChangeSafety/changeRecords/{name}",
            "name": name,
            "type": "Microsoft.ChangeSafety/changeRecords",
            "location": "eastus",
            "properties": {
                "changeType": change_type,
                "rolloutType": rollout_type,
                "comments": comments,
                "anticipatedStartTime": anticipated_start_time,
                "anticipatedEndTime": anticipated_end_time,
                "stageMap": stage_map,
                "changeDefinition": change_definition or {
                    "kind": "Targets",
                    "name": name,
                    "details": {
                        "targets": targets or []
                    }
                }
            }
        }

    @staticmethod
    def _mock_create_execute(cmd):
        """Mock execute for ChangeRecordCreate."""
        cls = ChangeRecordScenario
        cmd.pre_operations()
        name = cls._get_arg_value(cmd, "change_record_name", "mock-change")
        resource_group = cls._get_arg_value(cmd, "resource_group", "mock-rg")
        subscription_id = cmd.ctx.subscription_id or cls.FAKE_SUBSCRIPTION_ID
        change_type = cls._get_arg_value(cmd, "change_type", "ManualTouch")
        rollout_type = cls._get_arg_value(cmd, "rollout_type", "Normal")
        comments = cls._get_arg_value(cmd, "comments")
        targets = copy.deepcopy(cmd._parsed_targets or [])
        change_definition_var = getattr(cmd.ctx.vars, "change_definition", None)
        change_definition_value = change_definition_var.to_serialized_data() if change_definition_var else None
        stage_map_arg = getattr(cmd.ctx.args, "stage_map", None)
        stage_map_value = None
        if stage_map_arg is not None:
            if hasattr(stage_map_arg, "to_serialized_data") and has_value(stage_map_arg):
                stage_map_value = stage_map_arg.to_serialized_data()
            elif isinstance(stage_map_arg, dict):
                stage_map_value = stage_map_arg
        if isinstance(stage_map_value, dict) and "resource_id" in stage_map_value and "resourceId" not in stage_map_value:
            stage_map_value = {**stage_map_value}
            stage_map_value["resourceId"] = stage_map_value.pop("resource_id")
        start_time = cls._get_arg_value(cmd, "anticipated_start_time")
        end_time = cls._get_arg_value(cmd, "anticipated_end_time")
        instance = cls._build_mock_instance(
            name=name,
            resource_group=resource_group,
            subscription_id=subscription_id,
            change_type=change_type,
            rollout_type=rollout_type,
            targets=targets,
            comments=comments,
            change_definition=change_definition_value,
            stage_map=stage_map_value,
            anticipated_start_time=start_time,
            anticipated_end_time=end_time,
        )
        cls._SCENARIO_STATE["instance"] = copy.deepcopy(instance)
        cmd.ctx.set_var("instance", copy.deepcopy(instance), schema_builder=lambda: AAZAnyType())
        cmd.post_operations()
        return iter(())

    @staticmethod
    def _mock_update_execute(cmd):
        """Mock execute for ChangeRecordUpdate."""
        cls = ChangeRecordScenario
        cmd._parsed_targets = getattr(cmd, '_parsed_targets', None) or []  # pylint: disable=protected-access
        cmd.pre_operations()
        current = copy.deepcopy(cls._SCENARIO_STATE.get("instance"))
        if current is None:
            name = cls._get_arg_value(cmd, "change_record_name", "mock-change")
            resource_group = cls._get_arg_value(cmd, "resource_group", "mock-rg")
            subscription_id = cmd.ctx.subscription_id or cls.FAKE_SUBSCRIPTION_ID
            current = cls._build_mock_instance(
                name=name,
                resource_group=resource_group,
                subscription_id=subscription_id,
                change_type="ManualTouch",
                rollout_type="Normal",
                targets=[],
            )
        new_change_type = cls._get_arg_value(cmd, "change_type")
        new_rollout = cls._get_arg_value(cmd, "rollout_type")
        new_comments = cls._get_arg_value(cmd, "comments")
        new_start = cls._get_arg_value(cmd, "anticipated_start_time")
        new_end = cls._get_arg_value(cmd, "anticipated_end_time")
        stage_map_arg = getattr(cmd.ctx.args, "stage_map", None)
        stage_map_value = None
        if stage_map_arg is not None:
            if hasattr(stage_map_arg, "to_serialized_data") and has_value(stage_map_arg):
                stage_map_value = stage_map_arg.to_serialized_data()
            elif isinstance(stage_map_arg, dict):
                stage_map_value = stage_map_arg
        if isinstance(stage_map_value, dict) and "resource_id" in stage_map_value and "resourceId" not in stage_map_value:
            stage_map_value = {**stage_map_value}
            stage_map_value["resourceId"] = stage_map_value.pop("resource_id")
        change_definition_var = getattr(cmd.ctx.vars, "change_definition", None)
        change_definition_value = change_definition_var.to_serialized_data() if change_definition_var else None
        if new_change_type:
            current["properties"]["changeType"] = new_change_type
        if new_rollout:
            current["properties"]["rolloutType"] = new_rollout
        if new_comments is not None:
            current["properties"]["comments"] = new_comments
        if new_start is not None:
            current["properties"]["anticipatedStartTime"] = new_start
        if new_end is not None:
            current["properties"]["anticipatedEndTime"] = new_end
        if stage_map_value is not None:
            current["properties"]["stageMap"] = stage_map_value
        if change_definition_value is not None:
            current["properties"]["changeDefinition"] = change_definition_value
        elif cmd._parsed_targets:  # pylint: disable=protected-access
            current["properties"]["changeDefinition"]["details"]["targets"] = copy.deepcopy(cmd._parsed_targets)  # pylint: disable=protected-access
        cls._SCENARIO_STATE["instance"] = copy.deepcopy(current)
        cmd.ctx.set_var("instance", copy.deepcopy(current), schema_builder=lambda: AAZAnyType())
        cmd.post_operations()
        return iter(())

    @staticmethod
    def _mock_show_execute(cmd):
        """Mock execute for ChangeRecordShow."""
        cls = ChangeRecordScenario
        cmd.pre_operations()
        instance = copy.deepcopy(cls._SCENARIO_STATE.get("instance"))
        cmd.ctx.set_var("instance", instance, schema_builder=lambda: AAZAnyType())
        cmd.post_operations()
        return iter(())

    @staticmethod
    def _mock_delete_execute(cmd):
        """Mock execute for ChangeRecordDelete."""
        cls = ChangeRecordScenario
        cmd.pre_operations()
        cls._SCENARIO_STATE.pop("instance", None)
        cmd.post_operations()
        return iter(())

    @staticmethod
    def _mock_build_lro_poller(cmd, executor, extract_result):  # pylint: disable=unused-argument
        """Mock LRO poller builder."""
        executor()
        return ChangeRecordScenario._DummyPoller()

    def setUp(self):
        type(self)._ensure_msrestazure_stub()
        super().setUp()
        type(self)._SCENARIO_STATE.clear()
        self._patchers = [
            mock.patch('azext_changesafety.custom.ChangeRecordCreate._execute_operations', new=type(self)._mock_create_execute),
            mock.patch('azext_changesafety.custom.ChangeRecordUpdate._execute_operations', new=type(self)._mock_update_execute),
            mock.patch('azext_changesafety.custom.ChangeRecordShow._execute_operations', new=type(self)._mock_show_execute),
            mock.patch('azext_changesafety.custom.ChangeRecordDelete._execute_operations', new=type(self)._mock_delete_execute),
            mock.patch('azext_changesafety.custom.ChangeRecordDelete.build_lro_poller', new=type(self)._mock_build_lro_poller),
        ]
        for patcher in self._patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    # -------------------------------------------------------------------------
    # Unit Tests for Helper Functions
    # -------------------------------------------------------------------------

    def test_normalize_targets_from_operations(self):
        """Test _normalize_targets_arg with AAZArgActionOperations."""
        operations = AAZArgActionOperations.__new__(AAZArgActionOperations)
        operations._ops = [  # pylint: disable=protected-access
            ((_ELEMENT_APPEND_KEY,), "env=prod"),
            ((0, "resourceId"), "/subscriptions/000/resourceGroups/rg/providers/Microsoft.Web/sites/app"),
            ((0, "operation"), "delete"),
            ((1,), "subscriptionId=00000000-0000-0000-0000-000000000000"),
        ]

        normalized = _normalize_targets_arg(operations)

        assert normalized == [
            "env=prod,resourceId=/subscriptions/000/resourceGroups/rg/providers/Microsoft.Web/sites/app,operation=delete",
            "subscriptionId=00000000-0000-0000-0000-000000000000",
        ]

    def test_normalize_targets_from_serializable_value(self):
        """Test _normalize_targets_arg with serializable value."""
        class DummySerializable:
            def to_serialized_data(self):
                return ["rg=my-rg", None, "", "operation=show"]

        normalized = _normalize_targets_arg(DummySerializable())

        assert normalized == ["rg=my-rg", "operation=show"]

    def test_normalize_targets_from_list_of_strings(self):
        """Test _normalize_targets_arg with list of strings."""
        raw_targets = [" resourceId=/foo ", "", "operation=PUT", None]

        normalized = _normalize_targets_arg(raw_targets)

        assert normalized == ["resourceId=/foo", "operation=PUT"]

    def test_normalize_targets_with_none_returns_empty(self):
        """Test _normalize_targets_arg with None returns empty list."""
        assert _normalize_targets_arg(None) == []

    def test_inject_change_definition_into_content_adds_properties(self):
        """Test _inject_change_definition_into_content adds to properties."""
        ctx = self._dummy_ctx_with_change_definition({"details": {"targets": []}})
        content = {"properties": {"existing": "value"}}

        result = _inject_change_definition_into_content(content, ctx)

        assert result["properties"]["existing"] == "value"
        assert result["properties"]["changeDefinition"] == {"details": {"targets": []}}

    def test_inject_change_definition_with_empty_payload_noop(self):
        """Test _inject_change_definition_into_content with empty payload is no-op."""
        ctx = self._dummy_ctx_with_change_definition({})
        original = {"properties": {"foo": "bar"}}

        result = _inject_change_definition_into_content(original.copy(), ctx)

        assert result == original

    def test_inject_targets_into_result_updates_nested_properties(self):
        """Test _inject_targets_into_result updates nested properties."""
        data = {"properties": {"changeDefinition": {"details": {}}}}
        targets = [{"resourceId": "/foo"}]

        _inject_targets_into_result(data, targets)

        assert data["properties"]["changeDefinition"]["details"]["targets"] == targets

    def test_inject_targets_does_not_override_existing(self):
        """Test _inject_targets_into_result does not override existing targets."""
        existing = [{"resourceId": "/existing"}]
        data = {"changeDefinition": {"details": {"targets": existing.copy()}}}
        new_targets = [{"resourceId": "/new"}]

        _inject_targets_into_result(data, new_targets)

        assert data["changeDefinition"]["details"]["targets"] == existing

    # -------------------------------------------------------------------------
    # Integration Tests for ChangeRecord Commands
    # -------------------------------------------------------------------------

    def test_default_schedule_times_applied_on_create(self):
        """Test that default schedule times are applied on create."""
        resource_group = "rgScheduleDefaults"
        change_record_name = self.create_random_name('chg', 12)
        target_resource = (
            f"/subscriptions/{self.FAKE_SUBSCRIPTION_ID}/resourceGroups/{resource_group}/"
            "providers/Microsoft.Compute/virtualMachines/myVm"
        )
        self.kwargs.update({
            "rg": resource_group,
            "name": change_record_name,
            "change_type": "ManualTouch",
            "rollout_type": "Normal",
            "targets": f"resourceId={target_resource},operation=PATCH",
        })

        result = self.cmd(
            'az changesafety changerecord create -g {rg} -n {name} '
            '--change-type {change_type} --rollout-type {rollout_type} '
            '--targets "{targets}"',
        ).get_output_in_json()

        start = datetime.datetime.fromisoformat(result['properties']['anticipatedStartTime'].replace('Z', '+00:00'))
        end = datetime.datetime.fromisoformat(result['properties']['anticipatedEndTime'].replace('Z', '+00:00'))
        delta_seconds = abs((end - start).total_seconds() - 8 * 3600)
        self.assertLessEqual(delta_seconds, 5)

    def test_stage_map_name_shortcut(self):
        """Test --stagemap-name shortcut is expanded to full resource ID."""
        resource_group = "rgStageMapShortcut"
        change_record_name = self.create_random_name('chg', 12)
        stage_map_name = "rollout-plan"
        target_resource = (
            f"/subscriptions/{self.FAKE_SUBSCRIPTION_ID}/resourceGroups/{resource_group}/"
            "providers/Microsoft.Storage/storageAccounts/demo"
        )
        expected_stage_map = f"/subscriptions/{self.FAKE_SUBSCRIPTION_ID}/providers/Microsoft.ChangeSafety/stageMaps/{stage_map_name}"
        self.kwargs.update({
            "rg": resource_group,
            "name": change_record_name,
            "change_type": "ManualTouch",
            "rollout_type": "Normal",
            "targets": f"resourceId={target_resource},operation=PATCH",
            "stage_map_name": stage_map_name,
            "subscription": self.FAKE_SUBSCRIPTION_ID,
        })

        result = self.cmd(
            'az changesafety changerecord create -g {rg} -n {name} '
            '--change-type {change_type} --rollout-type {rollout_type} '
            '--targets "{targets}" --stagemap-name {stage_map_name} --subscription {subscription}',
        ).get_output_in_json()

        self.assertEqual(result["properties"]["stageMap"]["resourceId"], expected_stage_map)

    def test_change_record_crud_scenario(self):
        """Test full CRUD scenario for ChangeRecord."""
        resource_group = "rgChangeSafetyScenario"
        change_record_name = self.create_random_name('chg', 12)
        target_resource = (
            f"/subscriptions/{self.FAKE_SUBSCRIPTION_ID}/resourceGroups/{resource_group}/"
            "providers/Microsoft.Compute/virtualMachines/myVm"
        )
        self.kwargs.update({
            "rg": resource_group,
            "name": change_record_name,
            "change_type": "ManualTouch",
            "rollout_type": "Normal",
            "updated_rollout": "Emergency",
            "targets": f"resourceId={target_resource},operation=PATCH",
        })

        # Create
        create_checks = [
            JMESPathCheck('name', change_record_name),
            JMESPathCheck('properties.changeType', 'ManualTouch'),
            JMESPathCheck('properties.rolloutType', 'Normal'),
            JMESPathCheck('properties.changeDefinition.details.targets[0].resourceId', target_resource),
            JMESPathCheck('properties.changeDefinition.details.targets[0].httpMethod', 'PATCH'),
        ]
        self.cmd(
            'az changesafety changerecord create -g {rg} -n {name} '
            '--change-type {change_type} --rollout-type {rollout_type} '
            '--targets "{targets}" --comments "Initial deployment"',
            checks=create_checks,
        )

        # Update
        update_checks = [
            JMESPathCheck('properties.rolloutType', 'Emergency'),
            JMESPathCheck('properties.comments', 'Escalated rollout'),
        ]
        self.cmd(
            'az changesafety changerecord update -g {rg} -n {name} '
            '--rollout-type {updated_rollout} --comments "Escalated rollout"',
            checks=update_checks,
        )

        # Show
        self.cmd(
            'az changesafety changerecord show -g {rg} -n {name}',
            checks=[
                JMESPathCheck('properties.comments', 'Escalated rollout'),
                JMESPathCheck('properties.changeDefinition.details.targets[0].resourceId', target_resource),
            ],
        )

        # Delete
        self.cmd('az changesafety changerecord delete -g {rg} -n {name} -y')
        self.assertNotIn("instance", type(self)._SCENARIO_STATE)


# =============================================================================
# StageMap Tests
# =============================================================================


class StageMapScenario(ScenarioTest):
    """Test scenarios for StageMap CRUD operations."""

    FAKE_SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
    _SCENARIO_STATE = {}

    class _DummyPoller:  # pylint: disable=too-few-public-methods
        """Mock poller for LRO operations."""

        def result(self, timeout=None):  # pylint: disable=unused-argument
            return None

        def wait(self, timeout=None):  # pylint: disable=unused-argument
            return None

        def done(self):
            return True

        def add_done_callback(self, func):
            if func:
                func(self)

    @staticmethod
    def _build_mock_stagemap(name, subscription_id, stages=None):
        """Build a mock StageMap instance."""
        return {
            "id": f"/subscriptions/{subscription_id}/providers/Microsoft.ChangeSafety/stageMaps/{name}",
            "name": name,
            "type": "Microsoft.ChangeSafety/stageMaps",
            "properties": {
                "stages": stages or [
                    {"name": "Stage1", "sequence": 1},
                    {"name": "Stage2", "sequence": 2},
                ]
            }
        }

    @staticmethod
    def _mock_create_execute(cmd):
        """Mock execute for StageMap Create."""
        cls = StageMapScenario
        cmd.pre_operations()
        name_arg = getattr(cmd.ctx.args, "stage_map_name", None)
        name = name_arg.to_serialized_data() if name_arg and has_value(name_arg) else "mock-stagemap"
        subscription_id = cmd.ctx.subscription_id or cls.FAKE_SUBSCRIPTION_ID
        stages_arg = getattr(cmd.ctx.args, "stages", None)
        stages = stages_arg.to_serialized_data() if stages_arg and has_value(stages_arg) else None
        instance = cls._build_mock_stagemap(name, subscription_id, stages)
        cls._SCENARIO_STATE["stagemap"] = copy.deepcopy(instance)
        cmd.ctx.set_var("instance", copy.deepcopy(instance), schema_builder=lambda: AAZAnyType())
        cmd.post_operations()
        return iter(())

    @staticmethod
    def _mock_show_execute(cmd):
        """Mock execute for StageMap Show."""
        cls = StageMapScenario
        cmd.pre_operations()
        instance = copy.deepcopy(cls._SCENARIO_STATE.get("stagemap"))
        cmd.ctx.set_var("instance", instance, schema_builder=lambda: AAZAnyType())
        cmd.post_operations()
        return iter(())

    @staticmethod
    def _mock_update_execute(cmd):
        """Mock execute for StageMap Update."""
        cls = StageMapScenario
        cmd.pre_operations()
        current = copy.deepcopy(cls._SCENARIO_STATE.get("stagemap"))
        if current is None:
            name_arg = getattr(cmd.ctx.args, "stage_map_name", None)
            name = name_arg.to_serialized_data() if name_arg and has_value(name_arg) else "mock-stagemap"
            subscription_id = cmd.ctx.subscription_id or cls.FAKE_SUBSCRIPTION_ID
            current = cls._build_mock_stagemap(name, subscription_id)
        stages_arg = getattr(cmd.ctx.args, "stages", None)
        if stages_arg and has_value(stages_arg):
            current["properties"]["stages"] = stages_arg.to_serialized_data()
        cls._SCENARIO_STATE["stagemap"] = copy.deepcopy(current)
        cmd.ctx.set_var("instance", copy.deepcopy(current), schema_builder=lambda: AAZAnyType())
        cmd.post_operations()
        return iter(())

    @staticmethod
    def _mock_delete_execute(cmd):
        """Mock execute for StageMap Delete."""
        cls = StageMapScenario
        cmd.pre_operations()
        cls._SCENARIO_STATE.pop("stagemap", None)
        cmd.post_operations()
        return iter(())

    @staticmethod
    def _mock_list_execute(cmd):
        """Mock execute for StageMap List."""
        cls = StageMapScenario
        cmd.pre_operations()
        stagemap = cls._SCENARIO_STATE.get("stagemap")
        result = [stagemap] if stagemap else []
        cmd.ctx.set_var("instance", {"value": result}, schema_builder=lambda: AAZAnyType())
        cmd.post_operations()
        return iter(())

    @staticmethod
    def _mock_build_lro_poller(cmd, executor, extract_result):  # pylint: disable=unused-argument
        """Mock LRO poller builder."""
        executor()
        return StageMapScenario._DummyPoller()

    def setUp(self):
        super().setUp()
        type(self)._SCENARIO_STATE.clear()
        self._patchers = [
            mock.patch('azext_changesafety.aaz.latest.changesafety.stagemap._create.Create._execute_operations', new=type(self)._mock_create_execute),
            mock.patch('azext_changesafety.aaz.latest.changesafety.stagemap._show.Show._execute_operations', new=type(self)._mock_show_execute),
            mock.patch('azext_changesafety.aaz.latest.changesafety.stagemap._update.Update._execute_operations', new=type(self)._mock_update_execute),
            mock.patch('azext_changesafety.aaz.latest.changesafety.stagemap._delete.Delete._execute_operations', new=type(self)._mock_delete_execute),
            mock.patch('azext_changesafety.aaz.latest.changesafety.stagemap._list.List._execute_operations', new=type(self)._mock_list_execute),
            mock.patch('azext_changesafety.aaz.latest.changesafety.stagemap._delete.Delete.build_lro_poller', new=type(self)._mock_build_lro_poller),
        ]
        for patcher in self._patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_stagemap_create(self):
        """Test StageMap create command."""
        stagemap_name = self.create_random_name('stgmap', 12)
        self.kwargs.update({
            "name": stagemap_name,
            "subscription": self.FAKE_SUBSCRIPTION_ID,
        })

        result = self.cmd(
            'az changesafety stagemap create --stage-map-name {name} '
            '--stages "[{{name:Stage1,sequence:1}},{{name:Stage2,sequence:2}}]" '
            '--subscription {subscription}',
        ).get_output_in_json()

        self.assertEqual(result["name"], stagemap_name)
        self.assertIn("stages", result["properties"])

    def test_stagemap_show(self):
        """Test StageMap show command."""
        stagemap_name = self.create_random_name('stgmap', 12)
        self.kwargs.update({
            "name": stagemap_name,
            "subscription": self.FAKE_SUBSCRIPTION_ID,
        })

        # Create first
        self.cmd(
            'az changesafety stagemap create --stage-map-name {name} '
            '--stages "[{{name:Stage1,sequence:1}}]" '
            '--subscription {subscription}',
        )

        # Show
        result = self.cmd(
            'az changesafety stagemap show --stage-map-name {name} '
            '--subscription {subscription}',
        ).get_output_in_json()

        self.assertEqual(result["name"], stagemap_name)

    def test_stagemap_delete(self):
        """Test StageMap delete command."""
        stagemap_name = self.create_random_name('stgmap', 12)
        self.kwargs.update({
            "name": stagemap_name,
            "subscription": self.FAKE_SUBSCRIPTION_ID,
        })

        # Create first
        self.cmd(
            'az changesafety stagemap create --stage-map-name {name} '
            '--stages "[{{name:Stage1,sequence:1}}]" '
            '--subscription {subscription}',
        )

        # Delete
        self.cmd(
            'az changesafety stagemap delete --stage-map-name {name} '
            '--subscription {subscription} --yes',
        )

        self.assertNotIn("stagemap", type(self)._SCENARIO_STATE)


# =============================================================================
# StageProgression Tests
# =============================================================================


class StageProgressionScenario(ScenarioTest):
    """Test scenarios for StageProgression CRUD operations."""

    FAKE_SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
    _SCENARIO_STATE = {}

    class _DummyPoller:  # pylint: disable=too-few-public-methods
        """Mock poller for LRO operations."""

        def result(self, timeout=None):  # pylint: disable=unused-argument
            return None

        def wait(self, timeout=None):  # pylint: disable=unused-argument
            return None

        def done(self):
            return True

        def add_done_callback(self, func):
            if func:
                func(self)

    @staticmethod
    def _build_mock_stageprogression(name, change_record_name, subscription_id, stage_reference, status="InProgress", comments=None):
        """Build a mock StageProgression instance."""
        return {
            "id": f"/subscriptions/{subscription_id}/providers/Microsoft.ChangeSafety/changeRecords/{change_record_name}/stageProgressions/{name}",
            "name": name,
            "type": "Microsoft.ChangeSafety/changeRecords/stageProgressions",
            "properties": {
                "stageReference": stage_reference,
                "status": status,
                "comments": comments,
            }
        }

    @staticmethod
    def _mock_create_execute(cmd):
        """Mock execute for StageProgression Create."""
        cls = StageProgressionScenario
        cmd.pre_operations()
        name_arg = getattr(cmd.ctx.args, "stage_progression_name", None)
        name = name_arg.to_serialized_data() if name_arg and has_value(name_arg) else "mock-progression"
        cr_arg = getattr(cmd.ctx.args, "change_record_name", None)
        change_record_name = cr_arg.to_serialized_data() if cr_arg and has_value(cr_arg) else "mock-changerecord"
        subscription_id = cmd.ctx.subscription_id or cls.FAKE_SUBSCRIPTION_ID
        stage_ref_arg = getattr(cmd.ctx.args, "stage_reference", None)
        stage_reference = stage_ref_arg.to_serialized_data() if stage_ref_arg and has_value(stage_ref_arg) else "Stage1"
        status_arg = getattr(cmd.ctx.args, "status", None)
        status = status_arg.to_serialized_data() if status_arg and has_value(status_arg) else "InProgress"
        comments_arg = getattr(cmd.ctx.args, "comments", None)
        comments = comments_arg.to_serialized_data() if comments_arg and has_value(comments_arg) else None
        instance = cls._build_mock_stageprogression(name, change_record_name, subscription_id, stage_reference, status, comments)
        cls._SCENARIO_STATE["stageprogression"] = copy.deepcopy(instance)
        cmd.ctx.set_var("instance", copy.deepcopy(instance), schema_builder=lambda: AAZAnyType())
        cmd.post_operations()
        return iter(())

    @staticmethod
    def _mock_show_execute(cmd):
        """Mock execute for StageProgression Show."""
        cls = StageProgressionScenario
        cmd.pre_operations()
        instance = copy.deepcopy(cls._SCENARIO_STATE.get("stageprogression"))
        cmd.ctx.set_var("instance", instance, schema_builder=lambda: AAZAnyType())
        cmd.post_operations()
        return iter(())

    @staticmethod
    def _mock_update_execute(cmd):
        """Mock execute for StageProgression Update."""
        cls = StageProgressionScenario
        cmd.pre_operations()
        current = copy.deepcopy(cls._SCENARIO_STATE.get("stageprogression"))
        if current is None:
            name_arg = getattr(cmd.ctx.args, "stage_progression_name", None)
            name = name_arg.to_serialized_data() if name_arg and has_value(name_arg) else "mock-progression"
            cr_arg = getattr(cmd.ctx.args, "change_record_name", None)
            change_record_name = cr_arg.to_serialized_data() if cr_arg and has_value(cr_arg) else "mock-changerecord"
            subscription_id = cmd.ctx.subscription_id or cls.FAKE_SUBSCRIPTION_ID
            current = cls._build_mock_stageprogression(name, change_record_name, subscription_id, "Stage1")
        status_arg = getattr(cmd.ctx.args, "status", None)
        if status_arg and has_value(status_arg):
            current["properties"]["status"] = status_arg.to_serialized_data()
        comments_arg = getattr(cmd.ctx.args, "comments", None)
        if comments_arg and has_value(comments_arg):
            current["properties"]["comments"] = comments_arg.to_serialized_data()
        cls._SCENARIO_STATE["stageprogression"] = copy.deepcopy(current)
        cmd.ctx.set_var("instance", copy.deepcopy(current), schema_builder=lambda: AAZAnyType())
        cmd.post_operations()
        return iter(())

    @staticmethod
    def _mock_delete_execute(cmd):
        """Mock execute for StageProgression Delete."""
        cls = StageProgressionScenario
        cmd.pre_operations()
        cls._SCENARIO_STATE.pop("stageprogression", None)
        cmd.post_operations()
        return iter(())

    @staticmethod
    def _mock_list_execute(cmd):
        """Mock execute for StageProgression List."""
        cls = StageProgressionScenario
        cmd.pre_operations()
        progression = cls._SCENARIO_STATE.get("stageprogression")
        result = [progression] if progression else []
        cmd.ctx.set_var("instance", {"value": result}, schema_builder=lambda: AAZAnyType())
        cmd.post_operations()
        return iter(())

    @staticmethod
    def _mock_build_lro_poller(cmd, executor, extract_result):  # pylint: disable=unused-argument
        """Mock LRO poller builder."""
        executor()
        return StageProgressionScenario._DummyPoller()

    def setUp(self):
        super().setUp()
        type(self)._SCENARIO_STATE.clear()
        self._patchers = [
            mock.patch('azext_changesafety.aaz.latest.changesafety.stageprogression._create.Create._execute_operations', new=type(self)._mock_create_execute),
            mock.patch('azext_changesafety.aaz.latest.changesafety.stageprogression._show.Show._execute_operations', new=type(self)._mock_show_execute),
            mock.patch('azext_changesafety.aaz.latest.changesafety.stageprogression._update.Update._execute_operations', new=type(self)._mock_update_execute),
            mock.patch('azext_changesafety.aaz.latest.changesafety.stageprogression._delete.Delete._execute_operations', new=type(self)._mock_delete_execute),
            mock.patch('azext_changesafety.aaz.latest.changesafety.stageprogression._list.List._execute_operations', new=type(self)._mock_list_execute),
            mock.patch('azext_changesafety.aaz.latest.changesafety.stageprogression._delete.Delete.build_lro_poller', new=type(self)._mock_build_lro_poller),
        ]
        for patcher in self._patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_stageprogression_create(self):
        """Test StageProgression create command."""
        progression_name = self.create_random_name('prog', 12)
        change_record_name = "test-changerecord"
        self.kwargs.update({
            "name": progression_name,
            "change_record": change_record_name,
            "subscription": self.FAKE_SUBSCRIPTION_ID,
        })

        result = self.cmd(
            'az changesafety stageprogression create -n {name} '
            '--change-record-name {change_record} '
            '--stage-reference Stage1 --status InProgress '
            '--subscription {subscription}',
        ).get_output_in_json()

        self.assertEqual(result["name"], progression_name)
        self.assertEqual(result["properties"]["stageReference"], "Stage1")
        self.assertEqual(result["properties"]["status"], "InProgress")

    def test_stageprogression_show(self):
        """Test StageProgression show command."""
        progression_name = self.create_random_name('prog', 12)
        change_record_name = "test-changerecord"
        self.kwargs.update({
            "name": progression_name,
            "change_record": change_record_name,
            "subscription": self.FAKE_SUBSCRIPTION_ID,
        })

        # Create first
        self.cmd(
            'az changesafety stageprogression create -n {name} '
            '--change-record-name {change_record} '
            '--stage-reference Stage1 --status InProgress '
            '--subscription {subscription}',
        )

        # Show
        result = self.cmd(
            'az changesafety stageprogression show -n {name} '
            '--change-record-name {change_record} '
            '--subscription {subscription}',
        ).get_output_in_json()

        self.assertEqual(result["name"], progression_name)

    def test_stageprogression_update(self):
        """Test StageProgression update command."""
        progression_name = self.create_random_name('prog', 12)
        change_record_name = "test-changerecord"
        self.kwargs.update({
            "name": progression_name,
            "change_record": change_record_name,
            "subscription": self.FAKE_SUBSCRIPTION_ID,
        })

        # Create first
        self.cmd(
            'az changesafety stageprogression create -n {name} '
            '--change-record-name {change_record} '
            '--stage-reference Stage1 --status InProgress '
            '--subscription {subscription}',
        )

        # Update
        result = self.cmd(
            'az changesafety stageprogression update -n {name} '
            '--change-record-name {change_record} '
            '--status Completed --comments "Stage completed successfully" '
            '--subscription {subscription}',
        ).get_output_in_json()

        self.assertEqual(result["properties"]["status"], "Completed")
        self.assertEqual(result["properties"]["comments"], "Stage completed successfully")

    def test_stageprogression_delete(self):
        """Test StageProgression delete command."""
        progression_name = self.create_random_name('prog', 12)
        change_record_name = "test-changerecord"
        self.kwargs.update({
            "name": progression_name,
            "change_record": change_record_name,
            "subscription": self.FAKE_SUBSCRIPTION_ID,
        })

        # Create first
        self.cmd(
            'az changesafety stageprogression create -n {name} '
            '--change-record-name {change_record} '
            '--stage-reference Stage1 --status InProgress '
            '--subscription {subscription}',
        )

        # Delete
        self.cmd(
            'az changesafety stageprogression delete -n {name} '
            '--change-record-name {change_record} '
            '--subscription {subscription} --yes',
        )

        self.assertNotIn("stageprogression", type(self)._SCENARIO_STATE)

    def test_stageprogression_crud_scenario(self):
        """Test full CRUD scenario for StageProgression."""
        progression_name = self.create_random_name('prog', 12)
        change_record_name = "deployment-cr"
        self.kwargs.update({
            "name": progression_name,
            "change_record": change_record_name,
            "subscription": self.FAKE_SUBSCRIPTION_ID,
        })

        # Create
        self.cmd(
            'az changesafety stageprogression create -n {name} '
            '--change-record-name {change_record} '
            '--stage-reference Stage1 --status InProgress '
            '--subscription {subscription}',
            checks=[
                JMESPathCheck('name', progression_name),
                JMESPathCheck('properties.stageReference', 'Stage1'),
                JMESPathCheck('properties.status', 'InProgress'),
            ],
        )

        # Update
        self.cmd(
            'az changesafety stageprogression update -n {name} '
            '--change-record-name {change_record} '
            '--status Completed --comments "Finished stage 1" '
            '--subscription {subscription}',
            checks=[
                JMESPathCheck('properties.status', 'Completed'),
                JMESPathCheck('properties.comments', 'Finished stage 1'),
            ],
        )

        # Show
        self.cmd(
            'az changesafety stageprogression show -n {name} '
            '--change-record-name {change_record} '
            '--subscription {subscription}',
            checks=[
                JMESPathCheck('properties.status', 'Completed'),
            ],
        )

        # Delete
        self.cmd(
            'az changesafety stageprogression delete -n {name} '
            '--change-record-name {change_record} '
            '--subscription {subscription} --yes',
        )
        self.assertNotIn("stageprogression", type(self)._SCENARIO_STATE)


# =============================================================================
# Live Tests for Recordings (Run with: azdev test azure-changesafety --live)
# =============================================================================


def _ensure_msrestazure_stub():
    """Ensure msrestazure stub is available for tests."""
    if 'msrestazure' in sys.modules:
        return
    msrestazure = types.ModuleType('msrestazure')
    azure_operation = types.ModuleType('msrestazure.azure_operation')

    class AzureOperationPoller:  # pylint: disable=too-few-public-methods
        def _delay(self, *args, **kwargs):  # pylint: disable=unused-argument
            return

    azure_operation.AzureOperationPoller = AzureOperationPoller
    arm_polling = types.ModuleType('msrestazure.polling.arm_polling')

    class ARMPolling:  # pylint: disable=too-few-public-methods
        def _delay(self, *args, **kwargs):  # pylint: disable=unused-argument
            return

    arm_polling.ARMPolling = ARMPolling
    polling = types.ModuleType('msrestazure.polling')
    polling.arm_polling = arm_polling
    msrestazure.azure_operation = azure_operation
    msrestazure.polling = polling
    sys.modules['msrestazure'] = msrestazure
    sys.modules['msrestazure.azure_operation'] = azure_operation
    sys.modules['msrestazure.polling'] = polling
    sys.modules['msrestazure.polling.arm_polling'] = arm_polling


# Ensure stub is loaded before test collection
_ensure_msrestazure_stub()


class ChangeSafetyLiveScenario(ScenarioTest):
    """Live test scenarios for generating recordings.

    Run with: azdev test azure-changesafety --live
    Or: pytest test_changesafety.py::ChangeSafetyLiveScenario --live

    These tests make actual API calls and generate YAML recordings.
    """

    def test_changesafety_full_scenario(self):
        """Full CRUD scenario for ChangeRecord, StageMap, and StageProgression."""
        # Use random names to avoid conflicts
        stagemap_name = self.create_random_name('stgmap', 15)
        change_record_name = self.create_random_name('cr', 15)
        progression_name = self.create_random_name('prog', 15)

        self.kwargs.update({
            'stagemap_name': stagemap_name,
            'cr_name': change_record_name,
            'prog_name': progression_name,
        })

        # =================================================================
        # StageMap CRUD
        # =================================================================

        # Create StageMap
        self.cmd(
            'az changesafety stagemap create '
            '--stage-map-name {stagemap_name} '
            '--stages "[{{name:Canary,sequence:1}},{{name:Production,sequence:2}}]"',
            checks=[
                JMESPathCheck('name', stagemap_name),
                JMESPathCheck('properties.stages[0].name', 'Canary'),
                JMESPathCheck('properties.stages[1].name', 'Production'),
            ]
        )

        # Show StageMap
        self.cmd(
            'az changesafety stagemap show --stage-map-name {stagemap_name}',
            checks=[
                JMESPathCheck('name', stagemap_name),
            ]
        )

        # Note: List commands skipped - response too large for recording

        # =================================================================
        # ChangeRecord CRUD
        # =================================================================

        # Create ChangeRecord with StageMap reference
        self.cmd(
            'az changesafety changerecord create '
            '-n {cr_name} '
            '--change-type AppDeployment '
            '--rollout-type Normal '
            '--stagemap-name {stagemap_name} '
            '--targets "subscriptionId=$(az account show --query id -o tsv)"',
            checks=[
                JMESPathCheck('name', change_record_name),
                JMESPathCheck('properties.changeType', 'AppDeployment'),
            ]
        )

        # Show ChangeRecord
        self.cmd(
            'az changesafety changerecord show -n {cr_name}',
            checks=[
                JMESPathCheck('name', change_record_name),
            ]
        )

        # Update ChangeRecord
        self.cmd(
            'az changesafety changerecord update -n {cr_name} '
            '--rollout-type Emergency --comments "Escalated"',
            checks=[
                JMESPathCheck('properties.rolloutType', 'Emergency'),
                JMESPathCheck('properties.comments', 'Escalated'),
            ]
        )

        # =================================================================
        # StageProgression CRUD
        # =================================================================

        # Create StageProgression
        self.cmd(
            'az changesafety stageprogression create '
            '--change-record-name {cr_name} '
            '-n {prog_name} '
            '--stage-reference Canary '
            '--status InProgress',
            checks=[
                JMESPathCheck('name', progression_name),
                JMESPathCheck('properties.stageReference', 'Canary'),
                JMESPathCheck('properties.status', 'InProgress'),
            ]
        )

        # Show StageProgression
        self.cmd(
            'az changesafety stageprogression show '
            '--change-record-name {cr_name} -n {prog_name}',
            checks=[
                JMESPathCheck('name', progression_name),
            ]
        )

        # Update StageProgression
        self.cmd(
            'az changesafety stageprogression update '
            '--change-record-name {cr_name} -n {prog_name} '
            '--status Completed --comments "Canary passed"',
            checks=[
                JMESPathCheck('properties.status', 'Completed'),
            ]
        )

        # Delete StageProgression
        self.cmd('az changesafety stageprogression delete '
                 '--change-record-name {cr_name} -n {prog_name} --yes')

        # =================================================================
        # Cleanup
        # =================================================================

        # Note: ChangeRecord may need to be in terminal state to delete
        # Delete StageMap (if not referenced)
        self.cmd('az changesafety stagemap delete --stage-map-name {stagemap_name} --yes')

