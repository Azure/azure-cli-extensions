# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock

from azure.cli.core.aaz import AAZFreeFormDictType
from azure.cli.core.azclierror import ResourceNotFoundError
from azure.cli.core.mock import DummyCli
from azure.cli.core.util import get_error_type_by_status_code, handle_exception
from azure.cli.testsdk.base import ExecutionResult
from azure.cli.testsdk.exceptions import CliExecutionError

from azext_maintenance import MaintenanceManagementClientCommandsLoader
from azext_maintenance.manual.scheduledevents import Acknowledge, ListAcknowledge
from .test_maintenance_scenario import (
    step__scheduledevents_acknowledge,
    step__scheduledevents_list_acknowledge_not_found,
)


class ScheduledEventsResponseHandlingTest(TestCase):
    STATUS_NAMES = {
        400: 'BadRequest',
        404: 'NotFound',
        405: 'MethodNotAllowed',
        500: 'InternalServerError',
    }
    ACKNOWLEDGE_RESPONSE = {
        "Error": {
            "Code": "InvalidScheduledEventId",
            "Details": [{"Target": "event-id"}],
        },
    }
    LIST_ACKNOWLEDGE_MULTI_STATUS_RESPONSE = {
        "error": {
            "code": "MultiStatusResponse",
            "message": "The operation returned different statuses for the Scheduled Events. "
                       "Review each event's result for details.",
            "details": [
                {
                    "target": "event-id",
                    "code": "NotFound",
                    "message": "Scheduled event not found",
                },
            ],
        },
    }
    LIST_ACKNOWLEDGE_BAD_REQUEST_RESPONSE = {
        "error": {
            "code": "BadRequest",
            "message": "Invalid resource type or parameters. The valid ResourceParentTypes are "
                       "virtualMachines, virtualMachineScaleSets and availabilitySets. "
                       "ScheduledEventId has to be GUID.",
        },
    }
    LIST_ACKNOWLEDGE_NOT_FOUND_RESPONSE = {
        "error": {
            "code": "InvalidScheduledEventId",
            "message": "Scheduled event not found",
        },
    }
    LIST_ACKNOWLEDGE_NOT_IMPLEMENTED_RESPONSE = {
        "error": {
            "code": "NotImplemented",
            "message": "This operation is not supported in the region of resource provided. "
                       "Please check documentation for further details.",
        },
    }
    LIST_ACKNOWLEDGE_INTERNAL_ERROR_RESPONSE = {
        "error": {
            "code": "InternalServerError",
            "message": "Encountered an internal service error. Please try again later.",
        },
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
            LIST_ACKNOWLEDGE_MULTI_STATUS_RESPONSE,
        ),
        (
            ListAcknowledge.ScheduledEventOperationGroupAcknowledgeList,
            400,
            LIST_ACKNOWLEDGE_BAD_REQUEST_RESPONSE,
        ),
        (
            ListAcknowledge.ScheduledEventOperationGroupAcknowledgeList,
            404,
            LIST_ACKNOWLEDGE_NOT_FOUND_RESPONSE,
        ),
        (
            ListAcknowledge.ScheduledEventOperationGroupAcknowledgeList,
            405,
            LIST_ACKNOWLEDGE_NOT_IMPLEMENTED_RESPONSE,
        ),
        (
            ListAcknowledge.ScheduledEventOperationGroupAcknowledgeList,
            500,
            LIST_ACKNOWLEDGE_INTERNAL_ERROR_RESPONSE,
        ),
    )

    @staticmethod
    def _build_operation(operation_cls, status_code, payload, body=None):
        if body is None:
            body = json.dumps(payload).encode('utf-8')
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

    def test_207_responses_are_returned_without_throwing(self):
        for operation_cls, status_code, payload in self.CASES:
            if status_code != 207:
                continue
            with self.subTest(status_code=status_code):
                operation = self._build_operation(operation_cls, status_code, payload)

                operation()

                set_var_call = operation.ctx.set_var.call_args
                self.assertEqual(("instance", payload), set_var_call.args)
                schema_builder = set_var_call.kwargs["schema_builder"]
                self.assertIsInstance(schema_builder(), AAZFreeFormDictType)
                operation.client.send_request.return_value.http_response.body.assert_called_once_with()
                operation.on_error.assert_not_called()

    def test_non_2xx_responses_raise_with_json_body(self):
        for operation_cls, status_code, payload in self.CASES:
            if 200 <= status_code < 300:
                continue
            with self.subTest(operation=operation_cls.__name__, status_code=status_code):
                operation = self._build_operation(operation_cls, status_code, payload)
                with self.assertRaises(get_error_type_by_status_code(str(status_code))) as error:
                    operation()

                self.assertEqual(
                    f'{self.STATUS_NAMES[status_code]}\n{json.dumps(payload, indent=2)}',
                    str(error.exception),
                )
                self.assertNotIn('Exception Details:', str(error.exception))
                operation.ctx.set_var.assert_not_called()
                operation.on_200.assert_not_called()
                operation.on_error.assert_not_called()

    def test_non_2xx_cli_renderer_displays_json_and_returns_failure(self):
        for operation_cls, status_code, payload in self.CASES:
            if 200 <= status_code < 300:
                continue
            with self.subTest(operation=operation_cls.__name__, status_code=status_code):
                operation = self._build_operation(operation_cls, status_code, payload)
                with self.assertRaises(get_error_type_by_status_code(str(status_code))) as error:
                    operation()

                stdout = StringIO()
                with redirect_stdout(stdout), self.assertLogs('cli.azure.cli.core.azclierror', level='ERROR') as logs:
                    exit_code = handle_exception(error.exception)

                self.assertEqual(3 if status_code == 404 else 1, exit_code)
                self.assertEqual('', stdout.getvalue())
                self.assertEqual(1, len(logs.records))
                self.assertEqual(
                    f'{self.STATUS_NAMES[status_code]}\n{json.dumps(payload, indent=2)}',
                    logs.records[0].getMessage(),
                )
                self.assertNotIn('Exception Details:', logs.records[0].getMessage())

    def test_live_not_found_checks_use_sdk_exception_pipeline(self):
        for step in (step__scheduledevents_acknowledge, step__scheduledevents_list_acknowledge_not_found):
            for payload in (
                    self.LIST_ACKNOWLEDGE_NOT_FOUND_RESPONSE,
                    {'Error': {'Code': 'InvalidScheduledEventId', 'Message': 'Scheduled event not found'}}):
                with self.subTest(step=step.__name__, payload=payload):
                    cli = Mock(data={})
                    # This is what ScenarioTest's patched handle_exception raises.
                    cli.invoke.side_effect = CliExecutionError(
                        ResourceNotFoundError(f'NotFound\n{json.dumps(payload, indent=2)}'))
                    scenario = TestCase()
                    scenario.cmd = lambda command, checks: ExecutionResult(cli, command).assert_with_checks(checks)

                    step(scenario)

                    cli.invoke.assert_called_once()

    def test_live_not_found_checks_reject_success(self):
        for step in (step__scheduledevents_acknowledge, step__scheduledevents_list_acknowledge_not_found):
            with self.subTest(step=step.__name__):
                scenario = TestCase()
                scenario.cmd = Mock(return_value=SimpleNamespace(exit_code=0))
                with self.assertRaises(AssertionError):
                    step(scenario)

    def test_unknown_http_status_preserves_json_error(self):
        for operation_cls in (Acknowledge.ScheduledEventOperationGroupAcknowledge,
                              ListAcknowledge.ScheduledEventOperationGroupAcknowledgeList):
            with self.subTest(operation=operation_cls.__name__):
                payload = self.LIST_ACKNOWLEDGE_INTERNAL_ERROR_RESPONSE
                operation = self._build_operation(operation_cls, 599, payload)
                with self.assertRaises(get_error_type_by_status_code('599')) as error:
                    operation()

                self.assertEqual(f'HTTP599\n{json.dumps(payload, indent=2)}', str(error.exception))
                operation.ctx.set_var.assert_not_called()

    def test_malformed_error_bodies_use_generated_error_handler(self):
        for operation_cls in (Acknowledge.ScheduledEventOperationGroupAcknowledge,
                              ListAcknowledge.ScheduledEventOperationGroupAcknowledgeList):
            for body in (b'<html>Bad Gateway</html>', b'{invalid', b'\xff'):
                with self.subTest(operation=operation_cls.__name__, body=body):
                    operation = self._build_operation(operation_cls, 502, None, body=body)
                    with self.assertRaisesRegex(RuntimeError, 'Generated error handler was called'):
                        operation()
                    operation.on_error.assert_called_once_with(operation.client.send_request.return_value.http_response)
                    operation.ctx.set_var.assert_not_called()

    def test_empty_204_response_does_not_raise(self):
        for operation_cls in (Acknowledge.ScheduledEventOperationGroupAcknowledge,
                              ListAcknowledge.ScheduledEventOperationGroupAcknowledgeList):
            operation = self._build_operation(operation_cls, 204, None, body=b'')
            self.assertIsNone(operation())
            operation.on_error.assert_not_called()
            operation.ctx.set_var.assert_not_called()

    def test_empty_non_200_responses_use_generated_error_handler(self):
        for operation_cls, payload in (
                (Acknowledge.ScheduledEventOperationGroupAcknowledge, self.ACKNOWLEDGE_RESPONSE),
                (ListAcknowledge.ScheduledEventOperationGroupAcknowledgeList,
                 self.LIST_ACKNOWLEDGE_INTERNAL_ERROR_RESPONSE)):
            operation = self._build_operation(operation_cls, 500, payload, body=b"")
            response = operation.client.send_request.return_value.http_response

            self.assertRaisesRegex(RuntimeError, "Generated error handler was called", operation)

            operation.on_error.assert_called_once_with(response)
            operation.deserialize_http_content.assert_not_called()
            operation.ctx.set_var.assert_not_called()

    def test_200_responses_use_generated_handler(self):
        for operation_cls in (Acknowledge.ScheduledEventOperationGroupAcknowledge,
                              ListAcknowledge.ScheduledEventOperationGroupAcknowledgeList):
            with self.subTest(operation=operation_cls.__name__):
                operation = self._build_operation(operation_cls, 200, {"value": "Successfully approved scheduled event"})

                operation()

                operation.on_200.assert_called_once_with(operation.client.send_request.return_value)
                operation.ctx.set_var.assert_not_called()

    def test_generated_200_handler_sets_success_output(self):
        for operation_cls in (Acknowledge.ScheduledEventOperationGroupAcknowledge,
                              ListAcknowledge.ScheduledEventOperationGroupAcknowledgeList):
            with self.subTest(operation=operation_cls.__name__):
                payload = {'value': 'Successfully approved scheduled event'}
                operation = self._build_operation(operation_cls, 200, payload)
                del operation.on_200  # Exercise the real generated success handler.

                operation()

                self.assertEqual(('instance', payload), operation.ctx.set_var.call_args.args)
                operation.on_error.assert_not_called()
                operation.client.send_request.return_value.http_response.body.assert_not_called()

    def test_custom_commands_replace_generated_commands(self):
        loader = MaintenanceManagementClientCommandsLoader(cli_ctx=DummyCli())

        command_table = loader.load_command_table(["maintenance", "scheduledevents", "acknowledge"])

        self.assertIsInstance(command_table["maintenance scheduledevents acknowledge"], Acknowledge)
        self.assertIsInstance(command_table["maintenance scheduledevents list-acknowledge"], ListAcknowledge)