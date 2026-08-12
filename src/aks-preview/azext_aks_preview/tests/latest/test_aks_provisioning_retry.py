# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch, PropertyMock

from azure.cli.testsdk.checkers import JMESPathCheck
from knack.util import CLIError


class MockExecutionResult:
    def __init__(self, output_json):
        self._json = output_json
        self.output = json.dumps(output_json)
        self.json_value = None

    def get_output_in_json(self):
        return self._json

    def assert_with_checks(self, *args):
        checks = []
        for each in args:
            if isinstance(each, list):
                checks.extend(each)
            elif callable(each):
                checks.append(each)
        for check in checks:
            check(self)
        return self


class AKSRetryTestCase(unittest.TestCase):
    def _make_instance(self):
        from azext_aks_preview.tests.latest.test_aks_commands import (
            AzureKubernetesServiceScenarioTest,
        )
        instance = object.__new__(AzureKubernetesServiceScenarioTest)
        instance.kwargs = {}
        instance._apply_kwargs = lambda command: command
        instance.cli_ctx = MagicMock()
        return instance

    @staticmethod
    def _result(data):
        return MockExecutionResult(data)


class TestCmdRetryDispatch(AKSRetryTestCase):
    @patch.dict("os.environ", {
        "AZURE_CLI_TEST_RETRY_PROVISIONING_CHECK": "true",
    })
    @patch(
        "azure.cli.testsdk.scenario_tests.config.TestConfig.record_mode",
        new_callable=PropertyMock,
        return_value=True,
    )
    def test_retry_enabled_live_instance_disables_recording(self, _record_mode):
        from azext_aks_preview.tests.latest.test_aks_commands import (
            AzureKubernetesServiceScenarioTest,
        )

        instance = AzureKubernetesServiceScenarioTest(
            "test_aks_addon_list_available"
        )

        self.assertTrue(instance.disable_recording)

    @patch.dict("os.environ", {
        "AZURE_CLI_TEST_RETRY_PROVISIONING_CHECK": "true",
    })
    @patch(
        "azure.cli.testsdk.scenario_tests.config.TestConfig.record_mode",
        new_callable=PropertyMock,
        return_value=True,
    )
    def test_retry_enabled_live_instance_never_saves_cassette(self, _record_mode):
        from azext_aks_preview.tests.latest.test_aks_commands import (
            AzureKubernetesServiceScenarioTest,
        )
        instance = AzureKubernetesServiceScenarioTest(
            "test_aks_addon_list_available"
        )
        instance.cassette = MagicMock()
        instance.cassette.dirty = True
        fd, temp_recording_file = tempfile.mkstemp()
        os.close(fd)
        instance.temp_recording_file = temp_recording_file

        instance._save_recording_file()

        self.assertFalse(instance.cassette.dirty)
        self.assertFalse(os.path.exists(temp_recording_file))

    @patch.dict("os.environ", {"AZURE_CLI_TEST_RETRY_PROVISIONING_CHECK": "true"})
    def test_live_command_without_checks_uses_retry_path(self):
        instance = self._make_instance()
        instance.is_live = True
        instance._cmd_with_retry = MagicMock()

        instance.cmd("aks delete", checks=None, expect_failure=False)

        instance._cmd_with_retry.assert_called_once_with("aks delete", [], False)


class TestProvisioningStateRetry(AKSRetryTestCase):
    @patch.dict("os.environ", {
        "AZURE_CLI_TEST_PROVISIONING_MAX_RETRIES": "2",
        "AZURE_CLI_TEST_PROVISIONING_BASE_DELAY": "0.01",
    })
    @patch("time.sleep", return_value=None)
    @patch("random.uniform", return_value=0)
    @patch("azure.cli.testsdk.base.execute")
    def test_polls_nested_arm_state_then_refetches_native_result(
        self, mock_execute, _mock_random, _mock_sleep
    ):
        resource_id = (
            "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.ContainerService/"
            "managedClusters/cluster"
        )
        initial_result = self._result({
            "id": resource_id,
            "provisioningState": "Updating",
        })
        settled_result = self._result({
            "id": resource_id,
            "provisioningState": "Succeeded",
            "feature": {"enabled": True},
        })
        mock_execute.side_effect = [
            initial_result,
            self._result({"properties": {"provisioningState": "Updating"}}),
            self._result({"properties": {"provisioningState": "Succeeded"}}),
        ]
        instance = self._make_instance()
        instance._refetch_settled_aks_result = MagicMock(return_value=settled_result)

        result = instance._cmd_with_retry(
            "aks update",
            [
                JMESPathCheck("provisioningState", "Succeeded"),
                JMESPathCheck("feature.enabled", True),
            ],
            False,
        )

        self.assertIs(result, settled_result)
        instance._refetch_settled_aks_result.assert_called_once_with(
            resource_id, initial_result
        )

    @patch.dict("os.environ", {
        "AZURE_CLI_TEST_PROVISIONING_MAX_RETRIES": "2",
        "AZURE_CLI_TEST_PROVISIONING_BASE_DELAY": "0.01",
    })
    @patch("time.sleep", return_value=None)
    @patch("random.uniform", return_value=0)
    @patch("azure.cli.testsdk.base.execute")
    def test_times_out_when_state_never_settles(
        self, mock_execute, _mock_random, _mock_sleep
    ):
        poll = self._result({"properties": {"provisioningState": "Updating"}})
        mock_execute.side_effect = [
            self._result({
                "id": "/subscriptions/sub/resourceGroups/rg/providers/"
                      "Microsoft.ContainerService/managedClusters/cluster",
                "provisioningState": "Updating",
            }),
            poll,
            poll,
        ]

        with self.assertRaises(TimeoutError):
            self._make_instance()._cmd_with_retry(
                "aks update",
                [JMESPathCheck("provisioningState", "Succeeded")],
                False,
            )


class TestTransientConflictRetry(AKSRetryTestCase):
    @patch.dict("os.environ", {
        "AZURE_CLI_TEST_OPERATION_MAX_RETRIES": "2",
        "AZURE_CLI_TEST_OPERATION_BASE_DELAY": "0.01",
    })
    @patch("time.sleep", return_value=None)
    @patch("random.uniform", return_value=0)
    @patch("azure.cli.testsdk.base.execute")
    def test_retries_only_known_transient_conflicts(
        self, mock_execute, _mock_random, mock_sleep
    ):
        messages = [
            "Operation is not allowed: Another operation is in progress.",
            "Operation is not allowed because there's an in-progress update managed cluster operation",
            "Operation is not allowed: in-progress PutExtensionAddonHandler.PUT operation",
            "The managed cluster test is in Updating state, please wait for it to succeed.",
            "ProvisioningState of extension: Updating",
        ]
        for message in messages:
            with self.subTest(message=message):
                expected = self._result({"provisioningState": "Succeeded"})
                mock_execute.reset_mock()
                mock_sleep.reset_mock()
                mock_execute.side_effect = [CLIError(message), expected]

                result = self._make_instance()._execute_with_transient_conflict_retry(
                    "aks update", False
                )

                self.assertIs(result, expected)
                self.assertEqual(mock_execute.call_count, 2)
                mock_sleep.assert_called_once()

    @patch.dict("os.environ", {"AZURE_CLI_TEST_OPERATION_MAX_RETRIES": "2"})
    @patch("time.sleep", return_value=None)
    @patch("azure.cli.testsdk.base.execute")
    def test_does_not_retry_other_errors(self, mock_execute, mock_sleep):
        mock_execute.side_effect = CLIError("Invalid parameter")

        with self.assertRaisesRegex(CLIError, "Invalid parameter"):
            self._make_instance()._execute_with_transient_conflict_retry(
                "aks update", False
            )

        mock_execute.assert_called_once()
        mock_sleep.assert_not_called()

    @patch.dict("os.environ", {"AZURE_CLI_TEST_OPERATION_MAX_RETRIES": "2"})
    @patch("time.sleep", return_value=None)
    @patch("azure.cli.testsdk.base.execute")
    def test_does_not_retry_expected_failure(self, mock_execute, mock_sleep):
        mock_execute.side_effect = CLIError(
            "Operation is not allowed: Another operation is in progress."
        )

        with self.assertRaises(CLIError):
            self._make_instance()._execute_with_transient_conflict_retry(
                "aks update", True
            )

        mock_execute.assert_called_once()
        mock_sleep.assert_not_called()


class TestRefetchSettledResult(AKSRetryTestCase):
    @patch("azure.cli.testsdk.base.execute")
    def test_refetches_agentpool_with_native_show(self, mock_execute):
        expected = self._result({"provisioningState": "Succeeded"})
        mock_execute.return_value = expected
        resource_id = (
            "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.ContainerService/"
            "managedClusters/cluster/agentPools/pool"
        )
        instance = self._make_instance()

        result = instance._refetch_settled_aks_result(resource_id, MagicMock())

        self.assertIs(result, expected)
        mock_execute.assert_called_once_with(
            instance.cli_ctx,
            "aks nodepool show --resource-group rg --cluster-name cluster --name pool",
            expect_failure=False,
        )


if __name__ == "__main__":
    unittest.main()
