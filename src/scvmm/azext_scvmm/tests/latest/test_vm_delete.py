# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest
from unittest import mock

from azure.cli.core.azclierror import AzureResponseError, MutuallyExclusiveArgumentError
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.polling import LROPoller, NoPolling

from azext_scvmm import custom
from azext_scvmm.vendored_sdks.hybridcompute import HybridComputeManagementClient
from azext_scvmm.vendored_sdks.hybridcompute.models import Machine, MachineUpdate


SUBSCRIPTION_ID = '00000000-0000-0000-0000-000000000000'
RESOURCE_GROUP = 'test-rg'
MACHINE_NAME = 'test-vm'
MACHINE_ID = (
    f'/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}'
    f'/providers/Microsoft.HybridCompute/machines/{MACHINE_NAME}'
)


class DeleteVmTest(unittest.TestCase):

    def setUp(self):
        self.cmd = mock.Mock()
        self.client = mock.Mock(spec=custom.VirtualMachineInstancesOperations)
        self.machine_client = mock.Mock(spec=custom.MachinesOperations)
        self.poller = mock.Mock(spec=LROPoller)
        self.client.begin_delete.return_value = self.poller
        self.poller.result.return_value = None
        self.machine_client.get.return_value = Machine(location='eastus', kind='SCVMM')
        self.machine_client.update.return_value = Machine(location='eastus')

        self.calls = mock.Mock()
        self.calls.attach_mock(self.client, 'vm')
        self.calls.attach_mock(self.poller, 'deletion')
        self.calls.attach_mock(self.machine_client, 'machine')

        patches = mock.patch.multiple(
            custom, cf_machine=mock.DEFAULT, get_hcrp_machine_id=mock.DEFAULT,
            get_logger=mock.DEFAULT,
        )
        patched = patches.start()
        self.addCleanup(patches.stop)
        self.machine_factory = patched['cf_machine']
        self.machine_factory.return_value = self.machine_client
        patched['get_hcrp_machine_id'].return_value = MACHINE_ID
        self.logger = patched['get_logger'].return_value

    def _delete_vm(self, **kwargs):
        return custom.delete_vm(
            self.cmd, self.client, RESOURCE_GROUP, MACHINE_NAME, **kwargs,
        )

    def test_retained_scvmm_kind_is_cleared_after_deletion(self):
        for kind in ('SCVMM', 'scvmm', 'ScVmM'):
            with self.subTest(kind=kind):
                self.calls.reset_mock()
                self.machine_client.get.return_value.kind = kind

                self.assertIsNone(self._delete_vm())

                self.assertEqual(self.calls.mock_calls, [
                    mock.call.vm.begin_delete(MACHINE_ID, None, None),
                    mock.call.deletion.result(),
                    mock.call.machine.get(RESOURCE_GROUP, MACHINE_NAME),
                    mock.call.machine.update(RESOURCE_GROUP, MACHINE_NAME, mock.ANY),
                ])
                parameters = self.machine_client.update.call_args[0][2]
                self.assertIsInstance(parameters, MachineUpdate)
                self.assertEqual(parameters.serialize(), {'kind': ''})

    def test_empty_and_unrelated_kinds_are_unchanged(self):
        for kind in (None, '', 'VMware', 'HCI', 'AVS', 'Other', ' '):
            with self.subTest(kind=kind):
                self.calls.reset_mock()
                self.machine_client.get.return_value.kind = kind

                self._delete_vm()

                self.machine_client.get.assert_called_once_with(RESOURCE_GROUP, MACHINE_NAME)
                self.machine_client.update.assert_not_called()
                self.machine_client.delete.assert_not_called()

    def test_already_absent_vm_still_clears_retained_kind(self):
        for no_wait in (False, True):
            with self.subTest(no_wait=no_wait):
                self.calls.reset_mock()
                self.client.begin_delete.side_effect = ResourceNotFoundError('VM not found')

                self._delete_vm(no_wait=no_wait)

                self.poller.result.assert_not_called()
                self.machine_client.update.assert_called_once_with(
                    RESOURCE_GROUP, MACHINE_NAME, mock.ANY,
                )
                self.machine_client.delete.assert_not_called()
                self.logger.warning.assert_not_called()

    def test_missing_parent_needs_no_cleanup(self):
        for vm_missing in (False, True):
            with self.subTest(vm_missing=vm_missing):
                self.calls.reset_mock()
                self.client.begin_delete.side_effect = (
                    ResourceNotFoundError('VM not found') if vm_missing else None
                )
                self.machine_client.get.side_effect = ResourceNotFoundError('Machine not found')

                self._delete_vm()

                self.machine_client.update.assert_not_called()
                self.machine_client.delete.assert_not_called()

    def test_delete_request_failure_does_not_touch_parent(self):
        error = HttpResponseError('Delete request failed')
        self.client.begin_delete.side_effect = error

        with self.assertRaises(HttpResponseError) as caught:
            self._delete_vm()

        self.assertIs(caught.exception, error)
        self.poller.result.assert_not_called()
        self.assertEqual(self.machine_client.mock_calls, [])

    def test_polling_failure_does_not_touch_parent(self):
        for error in (HttpResponseError('Delete failed'), ResourceNotFoundError('Poll not found')):
            with self.subTest(error=type(error).__name__):
                self.calls.reset_mock()
                self.poller.result.side_effect = error

                with self.assertRaises(type(error)) as caught:
                    self._delete_vm()

                self.assertIs(caught.exception, error)
                self.assertEqual(self.machine_client.mock_calls, [])

    def test_parent_read_failure_is_not_swallowed(self):
        error = HttpResponseError('Machine read failed')
        self.machine_client.get.side_effect = error

        with self.assertRaises(HttpResponseError) as caught:
            self._delete_vm()

        self.assertIs(caught.exception, error)
        self.machine_client.update.assert_not_called()
        self.machine_client.delete.assert_not_called()

    def test_patch_failure_is_not_swallowed(self):
        for error in (HttpResponseError('Patch failed'), ResourceNotFoundError('Machine removed')):
            with self.subTest(error=type(error).__name__):
                self.calls.reset_mock()
                self.machine_client.update.side_effect = error

                with self.assertRaises(type(error)) as caught:
                    self._delete_vm()

                self.assertIs(caught.exception, error)
                self.poller.result.assert_called_once_with()
                self.machine_client.delete.assert_not_called()

    def test_patch_response_must_have_empty_kind(self):
        for kind in ('SCVMM', 'scvmm', 'VMware'):
            with self.subTest(kind=kind):
                self.calls.reset_mock()
                self.machine_client.update.return_value.kind = kind

                with self.assertRaisesRegex(AzureResponseError, 'kind'):
                    self._delete_vm()

                self.machine_client.update.assert_called_once_with(
                    RESOURCE_GROUP, MACHINE_NAME, mock.ANY,
                )

    def test_patch_response_accepts_empty_or_null_kind(self):
        for kind in ('', None):
            with self.subTest(kind=kind):
                self.calls.reset_mock()
                self.machine_client.update.return_value.kind = kind

                self._delete_vm()

                self.machine_client.update.assert_called_once_with(
                    RESOURCE_GROUP, MACHINE_NAME, mock.ANY,
                )

    def test_delete_options_are_preserved(self):
        cases = [
            ({'retain': True}, None, None),
            ({'force': True}, True, None),
            ({'delete_from_host': True}, None, True),
            ({'deleteFromHost': True}, None, True),
            ({'deleteFromHost': True, 'delete_from_host': False}, None, False),
        ]
        for options, force, delete_from_host in cases:
            with self.subTest(options=options):
                self.calls.reset_mock()

                self._delete_vm(**options)

                self.client.begin_delete.assert_called_once_with(
                    MACHINE_ID, force, delete_from_host,
                )
                self.machine_client.update.assert_called_once_with(
                    RESOURCE_GROUP, MACHINE_NAME, mock.ANY,
                )
                self.machine_client.delete.assert_not_called()

    def test_delete_machine_waits_and_does_not_patch(self):
        self._delete_vm(delete_machine=True, delete_from_host=True, force=True)

        self.assertEqual(self.calls.mock_calls, [
            mock.call.vm.begin_delete(MACHINE_ID, True, True),
            mock.call.deletion.result(),
            mock.call.machine.delete(RESOURCE_GROUP, MACHINE_NAME),
        ])

    def test_no_wait_delete_machine_keeps_existing_behavior(self):
        self._delete_vm(delete_machine=True, no_wait=True)

        self.assertEqual(self.calls.mock_calls, [
            mock.call.machine.delete(RESOURCE_GROUP, MACHINE_NAME),
        ])
        self.logger.warning.assert_not_called()

    def test_missing_vm_with_delete_machine_keeps_existing_behavior(self):
        self.client.begin_delete.side_effect = ResourceNotFoundError('VM not found')

        self._delete_vm(delete_machine=True)

        self.poller.result.assert_not_called()
        self.assertEqual(self.machine_client.mock_calls, [])

    def test_invalid_options_do_not_delete_or_patch(self):
        for options in (
            {'retain': True, 'delete_from_host': True},
            {'retain': True, 'deleteFromHost': True},
            {'no_wait': True, 'delete_machine': True, 'delete_from_host': True},
            {'no_wait': True, 'delete_machine': True, 'deleteFromHost': True},
        ):
            with self.subTest(options=options):
                self.calls.reset_mock()

                with self.assertRaises(MutuallyExclusiveArgumentError):
                    self._delete_vm(**options)

                self.assertEqual(self.calls.mock_calls, [])

    def test_no_wait_does_not_treat_no_polling_as_completed_deletion(self):
        response = mock.Mock()
        response.http_response.status_code = 202
        poller = LROPoller(mock.Mock(), response, lambda _: None, NoPolling())
        self.assertTrue(poller.done())
        self.client.begin_delete.return_value = poller

        with mock.patch.object(poller, 'result', wraps=poller.result) as result:
            self._delete_vm(no_wait=True, force=True, delete_from_host=True)

        result.assert_not_called()
        self.client.begin_delete.assert_called_once_with(MACHINE_ID, True, True, polling=False)
        self.assertEqual(self.machine_client.mock_calls, [])
        self.logger.warning.assert_called_once()
        message = self.logger.warning.call_args[0][0]
        self.assertIn('--no-wait', message)
        self.assertIn('az scvmm vm delete', message)

    def test_retry_after_no_wait_cleans_up_once(self):
        self._delete_vm(no_wait=True)
        self.assertEqual(self.machine_client.mock_calls, [])
        self.client.begin_delete.side_effect = ResourceNotFoundError('VM not found')

        self._delete_vm()
        self.machine_client.get.return_value.kind = None
        self._delete_vm()

        self.machine_client.update.assert_called_once_with(
            RESOURCE_GROUP, MACHINE_NAME, mock.ANY,
        )
        self.poller.result.assert_not_called()
        self.machine_client.delete.assert_not_called()

    def test_sdk_patch_payload_contains_only_top_level_empty_kind(self):
        sdk_client = HybridComputeManagementClient(
            credential=mock.Mock(), subscription_id=SUBSCRIPTION_ID,
        )
        self.addCleanup(sdk_client.close)
        self.machine_factory.return_value = sdk_client.machines

        with mock.patch.object(
            sdk_client.machines, 'get', return_value=Machine(location='eastus', kind='SCVMM'),
        ), mock.patch.object(
            sdk_client.machines, '_deserialize', return_value=Machine(location='eastus'),
        ), mock.patch.object(sdk_client._client._pipeline, 'run') as pipeline:
            pipeline.return_value.http_response.status_code = 200

            self._delete_vm()

        pipeline.assert_called_once()
        request = pipeline.call_args[0][0]
        self.assertEqual(request.method, 'PATCH')
        self.assertEqual(
            request.url, f'https://management.azure.com{MACHINE_ID}?api-version=2023-04-25-preview',
        )
        self.assertEqual(json.loads(request.body), {'kind': ''})

    def test_omitted_or_none_kind_does_not_serialize_an_empty_kind(self):
        self.assertEqual(MachineUpdate().serialize(), {})
        self.assertEqual(MachineUpdate(kind=None).serialize(), {})
