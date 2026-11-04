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
            "ProvisioningState of extension: Creating",
            "(CreateOrUpdateExtensionFailed) Creating extension 'azuremonitor-metrics' failed with "
            "error: (Conflict) There is a conflicting operation in progress for this extension. "
            "Please retry the operation.",
            "KeyVault 'mykv' could not be validated or it is not found.",
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
    def test_does_not_retry_unrelated_create_or_update_extension_failed(
        self, mock_execute, mock_sleep
    ):
        """
        A `CreateOrUpdateExtensionFailed` error is only a transient conflict when it
        explicitly reports a conflicting operation already in progress. Other
        CreateOrUpdateExtensionFailed causes (bad config, quota, etc.) must not be
        retried and must keep propagating unchanged.
        """
        mock_execute.side_effect = CLIError(
            "(CreateOrUpdateExtensionFailed) Creating extension 'azuremonitor-metrics' "
            "failed with error: (BadRequest) The extension configuration is invalid."
        )

        with self.assertRaisesRegex(CLIError, "CreateOrUpdateExtensionFailed"):
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

    @patch.dict("os.environ", {"AZURE_CLI_TEST_OPERATION_MAX_RETRIES": "2"})
    @patch("time.sleep", return_value=None)
    @patch("azure.cli.testsdk.base.execute")
    def test_does_not_retry_unrelated_keyvault_error(self, mock_execute, mock_sleep):
        """
        A KeyVault-related error is only treated as a transient dependency-readiness
        issue when it matches the exact, narrowly-scoped shape observed live:
        "KeyVault '<name>' could not be validated or it is not found." Any other
        KeyVault error (firewall/network denial, malformed request, wrong key
        permissions, etc.) is a genuine, persistent failure and must not be masked
        by a retry loop.
        """
        mock_execute.side_effect = CLIError(
            "KeyVault 'mykv': access is denied due to network firewall rules."
        )

        with self.assertRaisesRegex(CLIError, "network firewall rules"):
            self._make_instance()._execute_with_transient_conflict_retry(
                "aks create", False
            )

        mock_execute.assert_called_once()
        mock_sleep.assert_not_called()

    @patch.dict("os.environ", {
        "AZURE_CLI_TEST_OPERATION_MAX_RETRIES": "3",
        "AZURE_CLI_TEST_OPERATION_BASE_DELAY": "0.01",
    })
    @patch("time.sleep", return_value=None)
    @patch("random.uniform", return_value=0)
    @patch("azure.cli.testsdk.base.execute")
    def test_keyvault_validation_error_reraises_when_retries_exhausted(
        self, mock_execute, _mock_random, mock_sleep
    ):
        """
        A KeyVault validation error that never clears (e.g. a genuine
        misconfiguration rather than a propagation lag) must remain bounded by
        max_retries and ultimately re-raise the original error, never silently
        succeed or be skipped.
        """
        message = "KeyVault 'mykv' could not be validated or it is not found."
        mock_execute.side_effect = CLIError(message)

        with self.assertRaisesRegex(CLIError, "could not be validated"):
            self._make_instance()._execute_with_transient_conflict_retry(
                "aks create", False
            )

        self.assertEqual(mock_execute.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)


class TestAlreadyExistsConflictHandling(AKSRetryTestCase):
    def test_is_resource_already_exists_conflict_detects_message(self):
        instance = self._make_instance()

        self.assertTrue(
            instance._is_resource_already_exists_conflict(
                CLIError("Resource 'cliakstest123' already exists.")
            )
        )
        self.assertTrue(
            instance._is_resource_already_exists_conflict(
                CLIError("The Resource 'cliakstest123' ALREADY EXISTS in the given RG.")
            )
        )
        self.assertFalse(
            instance._is_resource_already_exists_conflict(
                CLIError("Another operation is in progress.")
            )
        )

    def test_build_show_command_for_aks_create(self):
        instance = self._make_instance()

        show_command = instance._build_show_command_for_already_existing_resource(
            "aks create --resource-group=rg1 --name=cluster1 --ssh-key-value=abc"
        )

        self.assertEqual(
            show_command, "aks show --resource-group rg1 --name cluster1"
        )

    def test_build_show_command_for_aks_create_with_short_options(self):
        instance = self._make_instance()

        show_command = instance._build_show_command_for_already_existing_resource(
            "aks create -g rg1 -n cluster1 --ssh-key-value abc"
        )

        self.assertEqual(
            show_command, "aks show --resource-group rg1 --name cluster1"
        )

    def test_build_show_command_for_nodepool_add(self):
        instance = self._make_instance()

        show_command = instance._build_show_command_for_already_existing_resource(
            "aks nodepool add --resource-group=rg1 --cluster-name=cluster1 --name=pool1"
        )

        self.assertEqual(
            show_command,
            "aks nodepool show --resource-group rg1 --cluster-name cluster1 --name pool1",
        )

    def test_build_show_command_returns_none_for_unrecognized_command(self):
        instance = self._make_instance()

        self.assertIsNone(
            instance._build_show_command_for_already_existing_resource(
                "aks delete --resource-group=rg1 --name=cluster1 --yes"
            )
        )

    def test_build_show_command_returns_none_when_missing_required_options(self):
        instance = self._make_instance()

        # aks nodepool add without --cluster-name cannot be translated to a show command.
        self.assertIsNone(
            instance._build_show_command_for_already_existing_resource(
                "aks nodepool add --resource-group=rg1 --name=pool1"
            )
        )

    @patch.dict("os.environ", {
        "AZURE_CLI_TEST_OPERATION_MAX_RETRIES": "3",
        "AZURE_CLI_TEST_OPERATION_BASE_DELAY": "0.01",
    })
    @patch("time.sleep", return_value=None)
    @patch("random.uniform", return_value=0)
    @patch("azure.cli.testsdk.base.execute")
    def test_already_exists_after_prior_retry_falls_back_to_show(
        self, mock_execute, _mock_random, mock_sleep
    ):
        """
        Regression coverage for the flaky race: a create is retried after a transient
        conflict, but the *original* attempt's async operation actually finishes
        server-side before the retry lands, so the retried create fails with
        "already exists". Since this happens on a retry (attempt > 0), it must be
        treated as success by switching to the equivalent 'show' command rather than
        re-raising.
        """
        settled_result = self._result({"provisioningState": "Succeeded"})
        mock_execute.side_effect = [
            CLIError("Another operation is in progress."),
            CLIError("Resource 'cliakstest123' already exists."),
            settled_result,
        ]

        instance = self._make_instance()
        result = instance._execute_with_transient_conflict_retry(
            "aks create --resource-group=rg1 --name=cliakstest123 --ssh-key-value=abc",
            False,
        )

        self.assertIs(result, settled_result)
        self.assertEqual(mock_execute.call_count, 3)
        mock_execute.assert_called_with(
            instance.cli_ctx,
            "aks show --resource-group rg1 --name cliakstest123",
            expect_failure=False,
        )
        # Only the first (transient-conflict) retry should have slept; the
        # already-exists fallback must not sleep before switching to 'show'.
        mock_sleep.assert_called_once()

    @patch.dict("os.environ", {"AZURE_CLI_TEST_OPERATION_MAX_RETRIES": "3"})
    @patch("time.sleep", return_value=None)
    @patch("azure.cli.testsdk.base.execute")
    def test_already_exists_on_first_attempt_still_raises(
        self, mock_execute, mock_sleep
    ):
        """
        Protects the intentional negative test for duplicate cluster names: an
        "already exists" failure on the very first attempt (no prior transient-conflict
        retry) must keep propagating unchanged, not be swallowed into a 'show' call.
        """
        mock_execute.side_effect = CLIError(
            "Resource 'cliakstest123' already exists."
        )

        with self.assertRaisesRegex(CLIError, "already exists"):
            self._make_instance()._execute_with_transient_conflict_retry(
                "aks create --resource-group=rg1 --name=cliakstest123 --ssh-key-value=abc",
                False,
            )

        mock_execute.assert_called_once()
        mock_sleep.assert_not_called()

    @patch.dict("os.environ", {"AZURE_CLI_TEST_OPERATION_MAX_RETRIES": "3"})
    @patch("time.sleep", return_value=None)
    @patch("azure.cli.testsdk.base.execute")
    def test_already_exists_on_first_attempt_raises_even_with_expect_failure(
        self, mock_execute, mock_sleep
    ):
        mock_execute.side_effect = CLIError(
            "Resource 'cliakstest123' already exists."
        )

        with self.assertRaises(CLIError):
            self._make_instance()._execute_with_transient_conflict_retry(
                "aks create --resource-group=rg1 --name=cliakstest123 --ssh-key-value=abc",
                True,
            )

        mock_execute.assert_called_once()
        mock_sleep.assert_not_called()


class TestAmbiguousLroStatusHandling(AKSRetryTestCase):
    """
    Unit coverage for recovering from azure-core's generic
    "Operation returned an invalid status 'OK'" poller error on `aks machine add` /
    `aks machine update`: verify the machine's real state via 'aks machine show'
    instead of trusting the uninformative message, but only trust that verification
    when it confirms a terminal 'Succeeded' state; any other outcome must keep
    failing with the original error.
    """

    def test_is_ambiguous_lro_status_error_detects_message(self):
        instance = self._make_instance()

        self.assertTrue(
            instance._is_ambiguous_lro_status_error(
                CLIError("Operation returned an invalid status 'OK'")
            )
        )
        self.assertFalse(
            instance._is_ambiguous_lro_status_error(
                CLIError("Operation returned an invalid status 'Bad Request'")
            )
        )
        self.assertFalse(
            instance._is_ambiguous_lro_status_error(
                CLIError("Another operation is in progress.")
            )
        )

    def test_build_show_command_for_machine_add(self):
        instance = self._make_instance()

        show_command = instance._build_show_command_for_machine(
            "aks machine add --resource-group=rg1 --cluster-name=cluster1 "
            "--nodepool-name=pool1 --machine-name=machine1 --vm-size=Standard_D4s_v3"
        )

        self.assertEqual(
            show_command,
            "aks machine show --resource-group rg1 --cluster-name cluster1 "
            "--nodepool-name pool1 --machine-name machine1",
        )

    def test_build_show_command_for_machine_update(self):
        instance = self._make_instance()

        show_command = instance._build_show_command_for_machine(
            "aks machine update --resource-group rg1 --cluster-name cluster1 "
            "--nodepool-name pool1 --machine-name machine1 --tags foo=bar"
        )

        self.assertEqual(
            show_command,
            "aks machine show --resource-group rg1 --cluster-name cluster1 "
            "--nodepool-name pool1 --machine-name machine1",
        )

    def test_build_show_command_for_machine_returns_none_for_unrecognized_command(self):
        instance = self._make_instance()

        self.assertIsNone(
            instance._build_show_command_for_machine(
                "aks machine show --resource-group=rg1 --cluster-name=cluster1 "
                "--nodepool-name=pool1 --machine-name=machine1"
            )
        )

    def test_build_show_command_for_machine_returns_none_when_missing_required_options(self):
        instance = self._make_instance()

        # Missing --machine-name cannot be translated to a show command.
        self.assertIsNone(
            instance._build_show_command_for_machine(
                "aks machine add --resource-group=rg1 --cluster-name=cluster1 "
                "--nodepool-name=pool1"
            )
        )

    @patch.dict("os.environ", {"AZURE_CLI_TEST_OPERATION_MAX_RETRIES": "3"})
    @patch("time.sleep", return_value=None)
    @patch("azure.cli.testsdk.base.execute")
    def test_ambiguous_status_error_recovers_when_show_confirms_succeeded(
        self, mock_execute, mock_sleep
    ):
        settled_result = self._result(
            {"properties": {"provisioningState": "Succeeded"}}
        )
        mock_execute.side_effect = [
            CLIError("Operation returned an invalid status 'OK'"),
            settled_result,
        ]

        instance = self._make_instance()
        result = instance._execute_with_transient_conflict_retry(
            "aks machine add --resource-group=rg1 --cluster-name=cluster1 "
            "--nodepool-name=pool1 --machine-name=machine1 --vm-size=Standard_D4s_v3",
            False,
        )

        self.assertIs(result, settled_result)
        self.assertEqual(mock_execute.call_count, 2)
        mock_execute.assert_called_with(
            instance.cli_ctx,
            "aks machine show --resource-group rg1 --cluster-name cluster1 "
            "--nodepool-name pool1 --machine-name machine1",
            expect_failure=False,
        )
        mock_sleep.assert_not_called()

    @patch.dict("os.environ", {"AZURE_CLI_TEST_OPERATION_MAX_RETRIES": "3"})
    @patch("time.sleep", return_value=None)
    @patch("azure.cli.testsdk.base.execute")
    def test_ambiguous_status_error_still_raises_when_show_reports_failure(
        self, mock_execute, mock_sleep
    ):
        """
        If 'show' confirms the machine genuinely did not succeed (or has no
        provisioningState at all), the original ambiguous error must still be
        raised: a real regression must never be silently tolerated.
        """
        original_error = CLIError("Operation returned an invalid status 'OK'")
        mock_execute.side_effect = [
            original_error,
            self._result({"properties": {"provisioningState": "Failed"}}),
        ]

        with self.assertRaisesRegex(CLIError, "invalid status 'OK'"):
            self._make_instance()._execute_with_transient_conflict_retry(
                "aks machine add --resource-group=rg1 --cluster-name=cluster1 "
                "--nodepool-name=pool1 --machine-name=machine1 --vm-size=Standard_D4s_v3",
                False,
            )

        self.assertEqual(mock_execute.call_count, 2)
        mock_sleep.assert_not_called()

    @patch.dict("os.environ", {"AZURE_CLI_TEST_OPERATION_MAX_RETRIES": "3"})
    @patch("time.sleep", return_value=None)
    @patch("azure.cli.testsdk.base.execute")
    def test_ambiguous_status_error_still_raises_when_show_itself_fails(
        self, mock_execute, mock_sleep
    ):
        """If the machine was never actually created, 'show' raises too (e.g. a 404);
        the original ambiguous error must still be the one that propagates."""
        original_error = CLIError("Operation returned an invalid status 'OK'")
        mock_execute.side_effect = [
            original_error,
            CLIError("Machine 'machine1' could not be found."),
        ]

        with self.assertRaisesRegex(CLIError, "invalid status 'OK'"):
            self._make_instance()._execute_with_transient_conflict_retry(
                "aks machine add --resource-group=rg1 --cluster-name=cluster1 "
                "--nodepool-name=pool1 --machine-name=machine1 --vm-size=Standard_D4s_v3",
                False,
            )

        self.assertEqual(mock_execute.call_count, 2)
        mock_sleep.assert_not_called()

    @patch.dict("os.environ", {"AZURE_CLI_TEST_OPERATION_MAX_RETRIES": "3"})
    @patch("time.sleep", return_value=None)
    @patch("azure.cli.testsdk.base.execute")
    def test_ambiguous_status_error_on_unrelated_command_raises_immediately(
        self, mock_execute, mock_sleep
    ):
        """Commands other than 'aks machine add/update' can't be translated to a
        'show', so the ambiguous error must propagate without any recovery attempt."""
        original_error = CLIError("Operation returned an invalid status 'OK'")
        mock_execute.side_effect = original_error

        with self.assertRaisesRegex(CLIError, "invalid status 'OK'"):
            self._make_instance()._execute_with_transient_conflict_retry(
                "aks create --resource-group=rg1 --name=cluster1 --ssh-key-value=abc",
                False,
            )

        mock_execute.assert_called_once()
        mock_sleep.assert_not_called()

    @patch.dict("os.environ", {"AZURE_CLI_TEST_OPERATION_MAX_RETRIES": "3"})
    @patch("time.sleep", return_value=None)
    @patch("azure.cli.testsdk.base.execute")
    def test_ambiguous_status_error_raises_with_expect_failure(
        self, mock_execute, mock_sleep
    ):
        """A deliberate negative test that expects failure must never be recovered
        into a success via the 'show' fallback."""
        original_error = CLIError("Operation returned an invalid status 'OK'")
        mock_execute.side_effect = original_error

        with self.assertRaisesRegex(CLIError, "invalid status 'OK'"):
            self._make_instance()._execute_with_transient_conflict_retry(
                "aks machine add --resource-group=rg1 --cluster-name=cluster1 "
                "--nodepool-name=pool1 --machine-name=machine1 --vm-size=Standard_D4s_v3",
                True,
            )

        mock_execute.assert_called_once()
        mock_sleep.assert_not_called()


class TestOsSkuRetirementSkip(AKSRetryTestCase):
    """
    Unit coverage for `_cmd_or_skip_if_os_sku_retired`, which was broadened this session
    to recognize both `InvalidOSSKU` (Flatcar's retirement error code) and
    `WindowsSKUNotSupported` (WindowsAnnual's retirement error code) as valid retirement
    signals, instead of only the former.
    """

    def test_skips_on_flatcar_retirement_error(self):
        instance = self._make_instance()
        instance.cmd = MagicMock(
            side_effect=CLIError(
                "(InvalidOSSKU) OSSKU='Flatcar' is invalid, details: Flatcar Container "
                "Linux for AKS (preview) was retired on 2026-06-08 and is no longer "
                "available for new node pools."
            )
        )

        with self.assertRaises(unittest.SkipTest):
            instance._cmd_or_skip_if_os_sku_retired("aks nodepool add", os_sku="Flatcar")

    def test_skips_on_windows_annual_retirement_error(self):
        instance = self._make_instance()
        instance.cmd = MagicMock(
            side_effect=CLIError(
                '(WindowsSKUNotSupported) Requested Windows SKU "WindowsAnnual" is not '
                'supported. Details: "Windows Annual Channel has been retired. Creation '
                'of new Windows Annual agent pools is no longer supported. Use Windows2022 '
                'or Windows2025 instead."'
            )
        )

        with self.assertRaises(unittest.SkipTest):
            instance._cmd_or_skip_if_os_sku_retired(
                "aks nodepool add", os_sku="WindowsAnnual"
            )

    def test_propagates_unrelated_errors(self):
        instance = self._make_instance()
        instance.cmd = MagicMock(
            side_effect=CLIError("(BadRequest) something unrelated went wrong")
        )

        with self.assertRaisesRegex(CLIError, "unrelated"):
            instance._cmd_or_skip_if_os_sku_retired(
                "aks nodepool add", os_sku="WindowsAnnual"
            )

    def test_propagates_when_os_sku_name_does_not_match(self):
        """A retirement-shaped error for a *different* OS SKU must not be swallowed."""
        instance = self._make_instance()
        instance.cmd = MagicMock(
            side_effect=CLIError(
                "(InvalidOSSKU) OSSKU='Flatcar' is invalid, details: Flatcar Container "
                "Linux for AKS (preview) was retired on 2026-06-08 and is no longer "
                "available for new node pools."
            )
        )

        with self.assertRaisesRegex(CLIError, "Flatcar"):
            instance._cmd_or_skip_if_os_sku_retired(
                "aks nodepool add", os_sku="WindowsAnnual"
            )

    def test_returns_result_when_command_succeeds(self):
        instance = self._make_instance()
        expected = self._result({"provisioningState": "Succeeded"})
        instance.cmd = MagicMock(return_value=expected)

        result = instance._cmd_or_skip_if_os_sku_retired(
            "aks nodepool add", os_sku="WindowsAnnual"
        )

        self.assertIs(result, expected)


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
