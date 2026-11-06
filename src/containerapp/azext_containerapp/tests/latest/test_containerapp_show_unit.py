# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import tempfile
import unittest
from io import StringIO
from unittest import mock

from requests import Response

from azure.cli.core import MainCommandsLoader
from azure.cli.core.azclierror import HTTPError, ResourceNotFoundError
from azure.cli.core.commands import _load_extension_command_loader
from azure.cli.core.mock import DummyCli

from azext_containerapp._client_factory import handle_non_404_status_code_exception
from azext_containerapp._clients import ContainerAppPreviewClient


class _ContainerappTestCommandsLoader(MainCommandsLoader):

    def load_command_table(self, args):
        command_table, _, loader = _load_extension_command_loader(self, args, 'azext_containerapp')
        self.command_table.update(command_table)
        self.cmd_to_loader_map.update({name: [loader] for name in command_table})
        return self.command_table


def _http_error(status_code, code, message):
    response = Response()
    response.status_code = status_code
    body = json.dumps({"error": {"code": code, "message": message}})
    return HTTPError(body, response)


class ContainerappShowCommandTest(unittest.TestCase):

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        environment = mock.patch.dict(os.environ, {
            "AZURE_CONFIG_DIR": directory.name,
            "AZURE_CORE_COLLECT_TELEMETRY": "no",
        })
        environment.start()
        self.addCleanup(environment.stop)
        self.cli = DummyCli(commands_loader_cls=_ContainerappTestCommandsLoader)
        for patcher in [
                mock.patch(
                    "azure.cli.core._profile.Profile.load_cached_subscriptions",
                    return_value=[{"id": "00000000-0000-0000-0000-000000000000", "name": "test-subscription"}]),
                mock.patch(
                    "azure.cli.command_modules.containerapp.base_resource.BaseResource."
                    "validate_subscription_registered"),
                mock.patch(
                    "azure.cli.command_modules.containerapp._clients.get_subscription_id",
                    return_value="00000000-0000-0000-0000-000000000000")]:
            patcher.start()
            self.addCleanup(patcher.stop)
        raw_request = mock.patch("azure.cli.command_modules.containerapp._clients.send_raw_request")
        self.raw_request = raw_request.start()
        self.addCleanup(raw_request.stop)
        secrets = mock.patch.object(ContainerAppPreviewClient, "list_secrets")
        self.list_secrets = secrets.start()
        self.addCleanup(secrets.stop)

    def _invoke(self, show_secrets=False, debug=False):
        output = StringIO()
        args = [
            "containerapp", "show", "--name", "nonexistent-app", "--resource-group", "test-group",
            "--subscription", "00000000-0000-0000-0000-000000000000",
        ]
        if show_secrets:
            args.append("--show-secrets")
        if debug:
            args.append("--debug")
        exit_code = self.cli.invoke(args, out_file=output)
        return exit_code, output.getvalue()

    def test_missing_app_show_returns_exit_code_3(self):
        for show_secrets, debug in [(False, False), (True, False), (False, True)]:
            with self.subTest(show_secrets=show_secrets, debug=debug):
                self.raw_request.side_effect = _http_error(
                    404, "ResourceNotFound", "The requested container app was not found.")
                with self.assertLogs(level="ERROR") as errors, self.assertRaises(SystemExit) as exit_context:
                    self._invoke(show_secrets, debug)
                self.assertEqual(3, exit_context.exception.code)
                self.assertIn("ResourceNotFound", "\n".join(errors.output))
                self.assertIn("was not found", "\n".join(errors.output))
                self.assertIn("nonexistent-app", "\n".join(errors.output))
                self.assertIn("test-group", "\n".join(errors.output))
                self.list_secrets.assert_not_called()

    def test_non_404_show_keeps_exit_code_1_and_service_error(self):
        self.raw_request.side_effect = _http_error(
            403, "AuthorizationFailed", "The client is not authorized to read the container app.")
        with self.assertLogs(level="ERROR") as errors:
            exit_code, _ = self._invoke()
        self.assertEqual(1, exit_code)
        self.assertIn("AuthorizationFailed", "\n".join(errors.output))
        self.assertIn("not authorized", "\n".join(errors.output))
        self.list_secrets.assert_not_called()

    def test_successful_show_with_and_without_secrets(self):
        for show_secrets in [False, True]:
            with self.subTest(show_secrets=show_secrets):
                app = {
                    "name": "nonexistent-app",
                    "properties": {"configuration": {"secrets": [{"name": "example-secret"}]}},
                }
                self.raw_request.return_value.json.return_value = app
                self.list_secrets.reset_mock()
                self.list_secrets.return_value = {
                    "value": [{"name": "example-secret", "value": "example-value"}],
                }
                exit_code, output = self._invoke(show_secrets)
                self.assertEqual(0, exit_code)
                self.assertEqual(app, json.loads(output))
                expected = self.list_secrets.return_value["value"] if show_secrets else [{"name": "example-secret"}]
                self.assertEqual(expected, json.loads(output)["properties"]["configuration"]["secrets"])
                request_args = self.raw_request.call_args.args
                self.assertEqual("GET", request_args[1])
                self.assertIn("/resourceGroups/test-group/providers/Microsoft.App/containerApps/nonexistent-app",
                              request_args[2])
                self.assertTrue(request_args[2].endswith("api-version=" + ContainerAppPreviewClient.api_version))
                if show_secrets:
                    self.list_secrets.assert_called_once()
                else:
                    self.list_secrets.assert_not_called()


class ContainerappShowClientTest(unittest.TestCase):

    @mock.patch("azure.cli.command_modules.containerapp._clients.get_subscription_id")
    @mock.patch("azure.cli.command_modules.containerapp._clients.send_raw_request")
    def test_not_found_keeps_response_for_existing_resource_checks(self, raw_request, _):
        error = _http_error(404, "ResourceNotFound", "The requested container app was not found.")
        raw_request.side_effect = error
        with self.assertRaises(ResourceNotFoundError) as raised:
            ContainerAppPreviewClient.show(mock.MagicMock(), "test-group", "nonexistent-app")
        self.assertIs(error.response, raised.exception.response)
        self.assertIs(raised.exception, handle_non_404_status_code_exception(raised.exception))

    @mock.patch("azure.cli.command_modules.containerapp._clients.get_subscription_id")
    @mock.patch("azure.cli.command_modules.containerapp._clients.send_raw_request")
    def test_404_is_classified_without_parsing_the_body(self, raw_request, _):
        response = Response()
        response.status_code = 404
        raw_request.side_effect = HTTPError("Not Found", response)
        with self.assertRaisesRegex(ResourceNotFoundError, "nonexistent-app"):
            ContainerAppPreviewClient.show(mock.MagicMock(), "test-group", "nonexistent-app")

    @mock.patch("azure.cli.command_modules.containerapp._clients.get_subscription_id")
    @mock.patch("azure.cli.command_modules.containerapp._clients.send_raw_request")
    def test_other_http_errors_are_reraised_unchanged(self, raw_request, _):
        for status_code in [400, 401, 403, 409, 429, 500]:
            with self.subTest(status_code=status_code):
                error = _http_error(status_code, "OtherError", "The original service error.")
                raw_request.side_effect = error
                with self.assertRaises(HTTPError) as raised:
                    ContainerAppPreviewClient.show(mock.MagicMock(), "test-group", "nonexistent-app")
                self.assertIs(error, raised.exception)
