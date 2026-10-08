# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import importlib.util
import json
import unittest
from http import HTTPStatus
from unittest import mock

from requests import Response

from azure.cli.core.azclierror import AzCLIError, CLIInternalError, HTTPError, ResourceNotFoundError
from azure.cli.core.util import CLIError, handle_exception

from azext_containerapp._client_factory import handle_show_exception
from azext_containerapp._clients import ContainerAppPreviewClient, ManagedEnvironmentPreviewClient


def _http_error(status_code, body):
    response = Response()
    response.status_code = status_code
    response.reason = HTTPStatus(status_code).phrase
    response._content = body.encode("utf-8")
    reason = f"{response.reason}({response.text})" if response.text else response.reason
    return HTTPError(reason, response)


def _exit_code(error):
    with mock.patch.object(AzCLIError, "print_error"), \
            mock.patch.object(AzCLIError, "send_telemetry"):
        return handle_exception(error)


class HandleShowExceptionTests(unittest.TestCase):

    def test_http_404_uses_status_instead_of_body(self):
        bodies = (
            json.dumps({"error": {"code": "ResourceNotFound", "message": "The resource was not found."}}),
            json.dumps({"error": {"code": "ResourceGroupNotFound", "message": "The resource group was not found."}}),
            "",
            "Resource was not found.",
            "{invalid JSON}",
        )
        for body in bodies:
            with self.subTest(body=body):
                error = _http_error(404, body)
                with self.assertRaises(ResourceNotFoundError) as raised:
                    handle_show_exception(error)
                self.assertEqual(str(error), str(raised.exception))
                self.assertIs(error, raised.exception.__cause__)
                self.assertEqual(3, _exit_code(raised.exception))

    def test_non_404_http_errors_keep_core_error_formatting(self):
        body = json.dumps({"error": {"code": "ResourceNotFound", "message": "The request failed."}})
        for status_code in (400, 403, 500):
            with self.subTest(status_code=status_code):
                error = _http_error(status_code, body)
                with self.assertRaises(CLIInternalError) as raised:
                    handle_show_exception(error)
                self.assertEqual("(ResourceNotFound) The request failed.", str(raised.exception))
                self.assertEqual(1, _exit_code(raised.exception))

    def test_non_http_error_is_unchanged(self):
        error = CLIError("ResourceNotFound")
        with self.assertRaises(CLIError) as raised:
            handle_show_exception(error)
        self.assertIs(error, raised.exception)


class ContainerappShowTests(unittest.TestCase):

    commands = (
        ("show_containerapp", ContainerAppPreviewClient, "containerApps"),
        ("show_managed_environment", ManagedEnvironmentPreviewClient, "managedEnvironments"),
    )

    def setUp(self):
        self.cmd = mock.MagicMock()
        self.cmd.cli_ctx.cloud.endpoints.resource_manager = "https://management.azure.com/"

    def _show(self, command, client, resource_type, error=None, result=None, **kwargs):
        # Only Arc diagnostics need kubernetes. Load an uncached copy of custom so
        # its mocked Arc helpers cannot leak into other command tests.
        spec = importlib.util.find_spec("azext_containerapp.custom")
        custom = importlib.util.module_from_spec(spec)
        arc_utils = mock.Mock()
        response = mock.Mock()
        response.json.return_value = result
        with mock.patch.dict("sys.modules", {"azext_containerapp._arc_utils": arc_utils}), \
                mock.patch("azure.cli.command_modules.containerapp.base_resource._validate_subscription_registered") as validate, \
                mock.patch("azure.cli.command_modules.containerapp._clients.get_subscription_id", return_value="subscription-id"), \
                mock.patch("azure.cli.command_modules.containerapp._clients.send_raw_request", side_effect=error, return_value=response) as send:
            spec.loader.exec_module(custom)
            try:
                return getattr(custom, command)(self.cmd, "test-resource", "resource-group", **kwargs)
            finally:
                self.assertEqual([], arc_utils.mock_calls)
                validate.assert_called_once_with(self.cmd, "Microsoft.App")
                send.assert_called_once_with(
                    self.cmd.cli_ctx,
                    "GET",
                    "https://management.azure.com/subscriptions/subscription-id/resourceGroups/resource-group/providers/Microsoft.App/"
                    f"{resource_type}/test-resource?api-version={client.api_version}",
                )

    def _assert_missing(self, command, client, resource_type):
        body = json.dumps({"error": {"code": "ResourceNotFound", "message": "The resource was not found."}})
        error = _http_error(404, body)
        with self.assertRaises(ResourceNotFoundError) as raised:
            self._show(command, client, resource_type, error=error)
        self.assertEqual(str(error), str(raised.exception))
        self.assertEqual(3, _exit_code(raised.exception))

    def test_containerapp_show_http_404(self):
        self._assert_missing(*self.commands[0])

    def test_containerapp_env_show_http_404(self):
        self._assert_missing(*self.commands[1])

    def test_show_non_404_http_errors_unchanged(self):
        for command, client, resource_type in self.commands:
            for status_code, code in ((400, "BadRequest"), (403, "AuthorizationFailed"), (500, "InternalServerError")):
                with self.subTest(command=command, status_code=status_code):
                    body = json.dumps({"error": {"code": code, "message": "The request failed."}})
                    error = _http_error(status_code, body)
                    with self.assertRaises(CLIInternalError) as raised:
                        self._show(command, client, resource_type, error=error)
                    self.assertEqual(f"({code}) The request failed.", str(raised.exception))
                    self.assertEqual(1, _exit_code(raised.exception))

    def test_show_non_http_errors_unchanged(self):
        for command, client, resource_type in self.commands:
            for error in (CLIError("The request failed."), ValueError("The request failed.")):
                with self.subTest(command=command, error=type(error).__name__):
                    with self.assertRaises(type(error)) as raised:
                        self._show(command, client, resource_type, error=error)
                    self.assertIs(error, raised.exception)

    def test_show_unstructured_non_404_http_error_unchanged(self):
        for command, client, resource_type in self.commands:
            with self.subTest(command=command):
                error = _http_error(403, "ResourceNotFound")
                with self.assertRaises(HTTPError) as raised:
                    self._show(command, client, resource_type, error=error)
                self.assertIs(error, raised.exception)

    def test_show_success_unchanged(self):
        for command, client, resource_type in self.commands:
            with self.subTest(command=command):
                result = {"properties": {"configuration": {"secrets": [{"name": "secret"}]}}}
                with mock.patch.object(ContainerAppPreviewClient, "list_secrets") as list_secrets:
                    self.assertIs(result, self._show(command, client, resource_type, result=result))
                list_secrets.assert_not_called()

    def test_containerapp_show_secrets_unchanged(self):
        result = {"properties": {"configuration": {"secrets": [{"name": "secret"}]}}}
        secrets = [{"name": "secret", "value": "value"}]
        with mock.patch.object(ContainerAppPreviewClient, "list_secrets", return_value={"value": secrets}) as list_secrets:
            output = self._show(*self.commands[0], result=result, show_secrets=True)
        self.assertEqual(secrets, output["properties"]["configuration"]["secrets"])
        list_secrets.assert_called_once_with(cmd=self.cmd, resource_group_name="resource-group", name="test-resource")


if __name__ == "__main__":
    unittest.main()
