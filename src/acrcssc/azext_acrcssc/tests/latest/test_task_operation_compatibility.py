# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest import mock

from azure.cli.core.mock import DummyCli

from azext_acrcssc.helper._taskoperations import (
    _cancel_task_runs,
    _delete_task,
    _get_file_task_run_values_parameter,
    _get_task_operation,
    _update_task_schedule,
    _update_task_yaml)


class TestTaskOperationCompatibility(unittest.TestCase):
    def setUp(self):
        self.cmd = SimpleNamespace(cli_ctx=DummyCli())
        self.registry = SimpleNamespace(
            name="mockregistry",
            id=(
                "/subscriptions/00000000-0000-0000-0000-000000000000/"
                "resourceGroups/mockrg/providers/Microsoft.ContainerRegistry/"
                "registries/mockregistry"))

    def test_get_task_operation_uses_current_sdk_methods(self):
        for operation_name in ("cancel", "delete", "schedule_run", "update"):
            with self.subTest(operation_name=operation_name):
                client = mock.Mock(spec_set=[operation_name])

                operation, is_long_running = _get_task_operation(
                    client,
                    operation_name)

                self.assertIs(operation, getattr(client, operation_name))
                self.assertFalse(is_long_running)

    def test_get_task_operation_uses_legacy_sdk_methods(self):
        for operation_name in ("cancel", "delete", "schedule_run", "update"):
            with self.subTest(operation_name=operation_name):
                legacy_operation_name = f"begin_{operation_name}"
                client = mock.Mock(spec_set=[legacy_operation_name])

                operation, is_long_running = _get_task_operation(
                    client,
                    operation_name)

                self.assertIs(operation, getattr(client, legacy_operation_name))
                self.assertTrue(is_long_running)

    @mock.patch("azext_acrcssc.helper._taskoperations.LongRunningOperation")
    @mock.patch("azext_acrcssc.helper._taskoperations._delete_task_role_assignment")
    @mock.patch("azext_acrcssc.helper._taskoperations.cf_acr_tasks")
    def test_delete_task_uses_current_sdk_delete(
            self,
            mock_cf_acr_tasks,
            _,
            mock_long_running_operation):
        client = mock.Mock(spec_set=["delete"])
        mock_cf_acr_tasks.return_value = client

        _delete_task(self.cmd, self.registry, "mocktask")

        client.delete.assert_called_once_with(
            "mockrg",
            "mockregistry",
            "mocktask")
        mock_long_running_operation.assert_not_called()

    def test_file_task_run_values_parameter_uses_current_sdk_name(self):
        model = SimpleNamespace(
            __annotations__={"values_property": list})

        self.assertEqual(
            _get_file_task_run_values_parameter(model),
            "values_property")

    def test_file_task_run_values_parameter_uses_legacy_sdk_name(self):
        model = SimpleNamespace(
            __annotations__={},
            _attribute_map={"values": {}})

        self.assertEqual(
            _get_file_task_run_values_parameter(model),
            "values")

    def test_file_task_run_values_parameter_rejects_unknown_model(self):
        model = SimpleNamespace(
            __annotations__={},
            _attribute_map={})

        with self.assertRaisesRegex(
                TypeError,
                "defines neither values_property nor values"):
            _get_file_task_run_values_parameter(model)

    @mock.patch("azext_acrcssc.helper._taskoperations.LongRunningOperation")
    @mock.patch("azext_acrcssc.helper._taskoperations._delete_task_role_assignment")
    @mock.patch("azext_acrcssc.helper._taskoperations.cf_acr_tasks")
    def test_delete_task_uses_legacy_sdk_begin_delete(
            self,
            mock_cf_acr_tasks,
            _,
            mock_long_running_operation):
        client = mock.Mock(spec_set=["begin_delete"])
        client.begin_delete.return_value = mock.sentinel.delete_poller
        mock_cf_acr_tasks.return_value = client

        _delete_task(self.cmd, self.registry, "mocktask")

        client.begin_delete.assert_called_once_with(
            "mockrg",
            "mockregistry",
            "mocktask")
        mock_long_running_operation.assert_called_once_with(self.cmd.cli_ctx)
        mock_long_running_operation.return_value.assert_called_once_with(
            mock.sentinel.delete_poller)

    @mock.patch("azext_acrcssc.helper._taskoperations.LongRunningOperation")
    def test_legacy_update_operations_wait_for_completion(
            self,
            mock_long_running_operation):
        client = mock.Mock(spec_set=["begin_update"])
        client.begin_update.side_effect = (
            mock.sentinel.yaml_poller,
            mock.sentinel.schedule_poller)
        task = SimpleNamespace(name="mocktask")
        models = SimpleNamespace(
            EncodedTaskStepUpdateParameters=mock.Mock(),
            TaskUpdateParameters=mock.Mock(),
            TimerTriggerUpdateParameters=mock.Mock(),
            TriggerUpdateParameters=mock.Mock())

        _update_task_yaml(
            self.cmd,
            client,
            models,
            self.registry,
            "mockrg",
            task,
            "encoded-task")
        _update_task_schedule(
            self.cmd,
            client,
            models,
            self.registry,
            "mockrg",
            "0 0 * * *",
            False)

        self.assertEqual(
            mock_long_running_operation.return_value.call_args_list,
            [
                mock.call(mock.sentinel.yaml_poller),
                mock.call(mock.sentinel.schedule_poller),
            ])

    @mock.patch("azext_acrcssc.helper._taskoperations.LongRunningOperation")
    def test_current_update_operations_do_not_use_lro(
            self,
            mock_long_running_operation):
        client = mock.Mock(spec_set=["update"])
        task = SimpleNamespace(name="mocktask")
        models = SimpleNamespace(
            EncodedTaskStepUpdateParameters=mock.Mock(),
            TaskUpdateParameters=mock.Mock(),
            TimerTriggerUpdateParameters=mock.Mock(),
            TriggerUpdateParameters=mock.Mock())

        _update_task_yaml(
            self.cmd,
            client,
            models,
            self.registry,
            "mockrg",
            task,
            "encoded-task")
        _update_task_schedule(
            self.cmd,
            client,
            models,
            self.registry,
            "mockrg",
            "0 0 * * *",
            False)

        self.assertEqual(client.update.call_count, 2)
        mock_long_running_operation.assert_not_called()

    @mock.patch("azext_acrcssc.helper._taskoperations.LongRunningOperation")
    def test_legacy_cancel_uses_run_id_and_waits(
            self,
            mock_long_running_operation):
        client = mock.Mock(spec_set=["begin_cancel"])
        client.begin_cancel.return_value = mock.sentinel.cancel_poller
        task = SimpleNamespace(name="mocktask", run_id="mock-run-id")

        _cancel_task_runs(
            self.cmd,
            client,
            "mockregistry",
            "mockrg",
            [task])

        client.begin_cancel.assert_called_once_with(
            "mockrg",
            "mockregistry",
            "mock-run-id")
        mock_long_running_operation.assert_called_once_with(self.cmd.cli_ctx)
        mock_long_running_operation.return_value.assert_called_once_with(
            mock.sentinel.cancel_poller)

    @mock.patch("azext_acrcssc.helper._taskoperations.LongRunningOperation")
    def test_current_cancel_uses_run_id_without_lro(
            self,
            mock_long_running_operation):
        client = mock.Mock(spec_set=["cancel"])
        task = SimpleNamespace(name="mocktask", run_id="mock-run-id")

        _cancel_task_runs(
            self.cmd,
            client,
            "mockregistry",
            "mockrg",
            [task])

        client.cancel.assert_called_once_with(
            "mockrg",
            "mockregistry",
            "mock-run-id")
        mock_long_running_operation.assert_not_called()
