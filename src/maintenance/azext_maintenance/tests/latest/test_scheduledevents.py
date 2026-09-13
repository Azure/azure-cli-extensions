# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock

from azure.cli.core.aaz import AAZFreeFormDictType
from azure.cli.core.mock import DummyCli

from azext_maintenance import MaintenanceManagementClientCommandsLoader
from azext_maintenance.manual.scheduledevents import Acknowledge, ListAcknowledge


class ScheduledEventsResponseHandlingTest(TestCase):
    ACKNOWLEDGE_RESPONSE = {
        "Error": {
            "Code": "InvalidScheduledEventId",
            "Details": [{"Target": "event-id"}],
        },
    }
    LIST_ACKNOWLEDGE_RESPONSE = {
        "Response": {"Code": "MultiStatusResponse"},
        "Details": [{"Code": "NotFound", "Target": "event-id"}],
    }
    CASES = (
        (
            Acknowledge.ScheduledEventOperationGroupAcknowledge,
            207,
            ACKNOWLEDGE_RESPONSE,
        ),
        (
            Acknowledge.ScheduledEventOperationGroupAcknowledge,
            400,
            ACKNOWLEDGE_RESPONSE,
        ),
        (
            Acknowledge.ScheduledEventOperationGroupAcknowledge,
            404,
            ACKNOWLEDGE_RESPONSE,
        ),
        (
            Acknowledge.ScheduledEventOperationGroupAcknowledge,
            500,
            ACKNOWLEDGE_RESPONSE,
        ),
        (
            ListAcknowledge.ScheduledEventOperationGroupAcknowledgeList,
            207,
            LIST_ACKNOWLEDGE_RESPONSE,
        ),
        (
            ListAcknowledge.ScheduledEventOperationGroupAcknowledgeList,
            400,
            LIST_ACKNOWLEDGE_RESPONSE,
        ),
        (
            ListAcknowledge.ScheduledEventOperationGroupAcknowledgeList,
            404,
            LIST_ACKNOWLEDGE_RESPONSE,
        ),
        (
            ListAcknowledge.ScheduledEventOperationGroupAcknowledgeList,
            500,
            LIST_ACKNOWLEDGE_RESPONSE,
        ),
    )

    @staticmethod
    def _build_operation(operation_cls, status_code, payload, body=b"{}"):
        operation = object.__new__(operation_cls)
        operation.ctx = Mock()
        operation.client = Mock()
        operation.make_request = Mock(return_value=object())
        operation.deserialize_http_content = Mock(return_value=payload)
        operation.on_200 = Mock()
        operation.on_error = Mock(side_effect=RuntimeError("Generated error handler was called"))
        operation.client.send_request.return_value = SimpleNamespace(
            http_response=SimpleNamespace(status_code=status_code, body=Mock(return_value=body))
        )
        return operation

    def test_non_200_responses_are_returned_without_throwing(self):
        for operation_cls, status_code, payload in self.CASES:
            with self.subTest(status_code=status_code):
                operation = self._build_operation(operation_cls, status_code, payload)

                operation()

                set_var_call = operation.ctx.set_var.call_args
                self.assertEqual(("instance", payload), set_var_call.args)
                schema_builder = set_var_call.kwargs["schema_builder"]
                self.assertIsInstance(schema_builder(), AAZFreeFormDictType)
                operation.client.send_request.return_value.http_response.body.assert_called_once_with()
                operation.on_error.assert_not_called()

    def test_empty_non_200_responses_use_generated_error_handler(self):
        for operation_cls, payload in (
                (Acknowledge.ScheduledEventOperationGroupAcknowledge, self.ACKNOWLEDGE_RESPONSE),
                (ListAcknowledge.ScheduledEventOperationGroupAcknowledgeList, self.LIST_ACKNOWLEDGE_RESPONSE)):
            operation = self._build_operation(operation_cls, 500, payload, body=b"")
            response = operation.client.send_request.return_value.http_response

            self.assertRaisesRegex(RuntimeError, "Generated error handler was called", operation)

            operation.on_error.assert_called_once_with(response)
            operation.deserialize_http_content.assert_not_called()
            operation.ctx.set_var.assert_not_called()

    def test_200_responses_use_generated_handler(self):
        for operation_cls, _, payload in self.CASES:
            with self.subTest(operation=operation_cls.__name__):
                operation = self._build_operation(operation_cls, 200, payload)

                operation()

                operation.on_200.assert_called_once_with(operation.client.send_request.return_value)
                operation.ctx.set_var.assert_not_called()

    def test_custom_commands_replace_generated_commands(self):
        loader = MaintenanceManagementClientCommandsLoader(cli_ctx=DummyCli())

        command_table = loader.load_command_table(["maintenance", "scheduledevents", "acknowledge"])

        self.assertIsInstance(command_table["maintenance scheduledevents acknowledge"], Acknowledge)
        self.assertIsInstance(command_table["maintenance scheduledevents list-acknowledge"], ListAcknowledge)