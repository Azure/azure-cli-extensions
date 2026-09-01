# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
"""Unit tests for the --no flag on ``az vm repair restore`` (ADO Bug 39509209).

These are pure unit tests: they exercise the parameter-validation and cleanup
short-circuit logic directly and do not require an Azure session, an Azure CLI
context object, or ``LiveScenarioTest`` infrastructure.
"""
import unittest
from unittest import mock

from azure.cli.core.azclierror import CLIError

from azext_vm_repair.custom import restore
from azext_vm_repair.repair_utils import _clean_up_resources


class RestoreNoFlagMutexTest(unittest.TestCase):
    """Passing both --yes and --no to ``az vm repair restore`` must fail fast."""

    def test_yes_and_no_together_raises_cli_error(self):
        with self.assertRaises(CLIError) as ctx:
            restore(
                cmd=mock.MagicMock(),
                vm_name='dummy-vm',
                resource_group_name='dummy-rg',
                disk_name='dummy-disk',
                repair_vm_id='/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/dummy-rg/providers/Microsoft.Compute/virtualMachines/repair-vm',
                yes=True,
                no=True,
            )
        self.assertIn('mutually exclusive', str(ctx.exception).lower())


class CleanUpResourcesSkipTest(unittest.TestCase):
    """``skip_cleanup=True`` must short-circuit before any delete call and log preserved IDs."""

    def test_skip_cleanup_true_does_not_delete(self):
        preserved_ids = [
            '/subscriptions/x/resourceGroups/repair-rg/providers/Microsoft.Compute/virtualMachines/repair-vm',
            '/subscriptions/x/resourceGroups/repair-rg/providers/Microsoft.Compute/disks/repair-disk',
        ]
        with mock.patch('azext_vm_repair.repair_utils._list_resource_ids_in_rg', return_value=preserved_ids), \
                mock.patch('azext_vm_repair.repair_utils._call_az_command') as mock_call, \
                mock.patch('azext_vm_repair.repair_utils.prompt_y_n') as mock_prompt, \
                mock.patch('azext_vm_repair.repair_utils.logger') as mock_logger:
            _clean_up_resources('repair-rg', confirm=True, skip_cleanup=True)

        # No az command was invoked and no prompt was shown.
        mock_call.assert_not_called()
        mock_prompt.assert_not_called()
        # The preserved resource IDs were logged so the operator has an audit trail.
        warning_calls = ' '.join(str(c) for c in mock_logger.warning.call_args_list)
        self.assertIn('repair-vm', warning_calls)
        self.assertIn('repair-disk', warning_calls)

    def test_skip_cleanup_false_and_confirm_false_deletes(self):
        with mock.patch('azext_vm_repair.repair_utils._list_resource_ids_in_rg', return_value=[]), \
                mock.patch('azext_vm_repair.repair_utils._call_az_command') as mock_call, \
                mock.patch('azext_vm_repair.repair_utils.prompt_y_n') as mock_prompt:
            _clean_up_resources('repair-rg', confirm=False, skip_cleanup=False)

        mock_prompt.assert_not_called()
        mock_call.assert_called_once()
        self.assertIn('az group delete', mock_call.call_args[0][0])
        self.assertIn('repair-rg', mock_call.call_args[0][0])


if __name__ == '__main__':
    unittest.main()
