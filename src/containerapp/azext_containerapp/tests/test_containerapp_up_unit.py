# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest
from types import SimpleNamespace
from unittest import mock

import requests
from azure.cli.core.azclierror import CLIInternalError, HTTPError
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from azext_containerapp import _up_utils, custom
from azext_containerapp._up_utils import ContainerApp


def arm_error(status, code, exception_type=HTTPError):
    response = requests.Response()
    response.status_code = status
    response.reason = code
    response._content = json.dumps({"error": {"code": code, "message": "App lookup failed"}}).encode()
    if exception_type is HTTPError:
        return HTTPError(response.text, response)
    return exception_type(message=response.text, response=response)


def lookup_errors():
    return [
        requests.ConnectionError("Network is unreachable"),
        requests.ConnectTimeout("Connection timed out"),
        requests.ReadTimeout("Read timed out"),
        arm_error(401, "Unauthorized"),
        arm_error(403, "AuthorizationFailed"),
        arm_error(429, "TooManyRequests"),
        arm_error(500, "InternalServerError"),
        arm_error(503, "ServiceUnavailable"),
        arm_error(429, "TooManyRequests", HttpResponseError),
        arm_error(500, "InternalServerError", HttpResponseError),
        arm_error(500, "ResourceNotFound"),
        ResourceNotFoundError(message="ResourceNotFound without an HTTP response"),
        ValueError("Invalid response"),
    ]


class ContainerAppUpLookupUnitTest(unittest.TestCase):
    def up(self, **overrides):
        arguments = {
            "cmd": None,
            "resource_group_name": "resource-group",
            "name": "app",
            "managed_env": "environment",
            "image": "example.com/app:new",
            "env_vars": None,
            "ingress": None,
            "target_port": None,
            "registry_server": None,
            "registry_user": None,
            "registry_pass": None,
            "workload_profile_name": None,
        }
        arguments.update(overrides)
        return custom.containerapp_up_logic(**arguments)

    def test_uncertain_lookup_errors_never_deploy(self):
        for error in lookup_errors():
            with self.subTest(error=type(error).__name__, message=str(error)):
                with mock.patch.object(custom.ContainerAppPreviewClient, "show", side_effect=error), \
                        mock.patch.object(custom, "create_containerapp") as create, \
                        mock.patch.object(custom, "update_containerapp_logic") as update:
                    with self.assertRaises(type(error)) as raised:
                        self.up()
                    self.assertIs(error, raised.exception)
                    create.assert_not_called()
                    update.assert_not_called()

    def test_confirmed_not_found_creates(self):
        errors = [
            arm_error(404, "ResourceNotFound"),
            arm_error(404, "ResourceNotFound", HttpResponseError),
            arm_error(404, "ResourceNotFound", ResourceNotFoundError),
        ]
        for error in errors:
            with self.subTest(error=type(error).__name__):
                with mock.patch.object(custom.ContainerAppPreviewClient, "show", side_effect=error), \
                        mock.patch.object(custom, "create_containerapp", return_value={"name": "app"}) as create, \
                        mock.patch.object(custom, "update_containerapp_logic") as update:
                    self.assertEqual({"name": "app"}, self.up())
                    create.assert_called_once()
                    self.assertEqual("example.com/app:new", create.call_args.kwargs["image"])
                    update.assert_not_called()

    def test_existing_app_updates_without_implicit_configuration(self):
        with mock.patch.object(custom.ContainerAppPreviewClient, "show", return_value={"name": "app"}), \
                mock.patch.object(custom, "create_containerapp") as create, \
                mock.patch.object(custom, "update_containerapp_logic", return_value={"name": "app"}) as update:
            self.assertEqual({"name": "app"}, self.up())
            create.assert_not_called()
            update.assert_called_once()
            arguments = update.call_args.kwargs
            self.assertEqual("example.com/app:new", arguments["image"])
            for argument in ("replace_env_vars", "ingress", "target_port", "system_assigned", "user_assigned"):
                self.assertIsNone(arguments[argument])

    def test_empty_lookup_response_never_deploys(self):
        for response in (None, {}):
            with self.subTest(response=response):
                with mock.patch.object(custom.ContainerAppPreviewClient, "show", return_value=response), \
                        mock.patch.object(custom, "create_containerapp") as create, \
                        mock.patch.object(custom, "update_containerapp_logic") as update:
                    with self.assertRaisesRegex(CLIInternalError, "returned an empty response"):
                        self.up()
                    create.assert_not_called()
                    update.assert_not_called()

    def test_new_quickstart_app_retains_creation_defaults(self):
        with mock.patch.object(custom.ContainerAppPreviewClient, "show",
                               side_effect=arm_error(404, "ResourceNotFound")), \
                mock.patch.object(custom, "create_containerapp") as create:
            self.up(image="mcr.microsoft.com/k8se/quickstart:latest")
            self.assertEqual("external", create.call_args.kwargs["ingress"])
            self.assertEqual(80, create.call_args.kwargs["target_port"])

    def test_new_foundry_app_retains_creation_defaults(self):
        with mock.patch.object(custom.ContainerAppPreviewClient, "show",
                               side_effect=arm_error(404, "ResourceNotFound")), \
                mock.patch.object(custom, "create_containerapp") as create:
            self.up(image="mcr.microsoft.com/k8se/aca-foundry-model-host:latest")
            self.assertEqual("external", create.call_args.kwargs["ingress"])
            self.assertEqual(8000, create.call_args.kwargs["target_port"])

    def test_explicit_ingress_and_port_are_preserved(self):
        for response in ({"name": "app"}, arm_error(404, "ResourceNotFound")):
            with self.subTest(existing=isinstance(response, dict)):
                with mock.patch.object(custom.ContainerAppPreviewClient, "show") as show, \
                        mock.patch.object(custom, "create_containerapp") as create, \
                        mock.patch.object(custom, "update_containerapp_logic") as update:
                    if isinstance(response, dict):
                        show.return_value = response
                    else:
                        show.side_effect = response
                    self.up(image="mcr.microsoft.com/k8se/quickstart:latest", ingress="internal", target_port=3000)
                    deploy = update if isinstance(response, dict) else create
                    self.assertEqual("internal", deploy.call_args.kwargs["ingress"])
                    self.assertEqual(3000, deploy.call_args.kwargs["target_port"])


class ContainerAppUpPreflightUnitTest(unittest.TestCase):
    def make_app(self):
        return ContainerApp(None, "app", SimpleNamespace(name="resource-group"))

    def test_constructor_propagates_uncertain_lookup_errors(self):
        for error in lookup_errors():
            with self.subTest(error=type(error).__name__, message=str(error)):
                with mock.patch.object(custom.ContainerAppPreviewClient, "show", side_effect=error):
                    with self.assertRaises(type(error)) as raised:
                        self.make_app()
                    self.assertIs(error, raised.exception)

    def test_later_preflight_failure_is_not_absence(self):
        error = requests.ConnectionError("Network is unreachable")
        with mock.patch.object(custom.ContainerAppPreviewClient, "show",
                               side_effect=[{"name": "app"}, error]):
            app = self.make_app()
            self.assertTrue(app.exists)
            with self.assertRaises(requests.ConnectionError):
                app.check_exists()

    def test_confirmed_not_found_is_absence(self):
        for exception_type in (HTTPError, HttpResponseError, ResourceNotFoundError):
            with self.subTest(exception_type=exception_type.__name__):
                with mock.patch.object(custom.ContainerAppPreviewClient, "show",
                                       side_effect=arm_error(404, "ResourceNotFound", exception_type)):
                    app = self.make_app()
                    self.assertFalse(app.exists)
                    self.assertIsNone(app.get())

    def test_successful_preflight_confirms_presence(self):
        definition = {"name": "app"}
        with mock.patch.object(custom.ContainerAppPreviewClient, "show", return_value=definition):
            app = self.make_app()
            self.assertTrue(app.exists)
            self.assertIs(definition, app.get())

    def test_empty_preflight_response_is_not_absence(self):
        for response in (None, {}):
            with self.subTest(response=response):
                with mock.patch.object(custom.ContainerAppPreviewClient, "show", return_value=response):
                    with self.assertRaisesRegex(CLIInternalError, "returned an empty response"):
                        self.make_app()

    def test_cloud_build_placeholder_has_no_image_ingress_defaults(self):
        with mock.patch.object(custom.ContainerAppPreviewClient, "show",
                               side_effect=arm_error(404, "ResourceNotFound")), \
                mock.patch.object(custom, "create_containerapp") as create, \
                mock.patch.object(_up_utils, "run_cloud_build", return_value="example.com/app:built"), \
                mock.patch("builtins.open", mock.mock_open()):
            app = self.make_app()
            app.env = mock.Mock()
            app.env.is_connected_environment.return_value = False
            self.assertEqual("example.com/app:built",
                             app.build_container_from_source_with_cloud_build_service("source", None, "eastus"))
            create.assert_called_once()
            self.assertIsNone(create.call_args.kwargs["ingress"])
            self.assertIsNone(create.call_args.kwargs["target_port"])


class ContainerAppUpCommandUnitTest(unittest.TestCase):
    def setUp(self):
        self.cmd = SimpleNamespace(cli_ctx=SimpleNamespace(data={}))
        resources = mock.patch.multiple(
            _up_utils, ResourceGroup=mock.DEFAULT, Extension=mock.DEFAULT,
            CustomLocation=mock.DEFAULT, ContainerAppEnvironment=mock.DEFAULT,
            _set_up_defaults=mock.DEFAULT, up_output=mock.DEFAULT)
        self.resources = resources.start()
        self.addCleanup(resources.stop)
        self.resources["ResourceGroup"].return_value.name = "resource-group"
        for name in ("register_provider_if_needed", "create_containerapp", "update_containerapp_logic"):
            patcher = mock.patch.object(custom, name)
            setattr(self, name, patcher.start())
            self.addCleanup(patcher.stop)
        patcher = mock.patch.object(ContainerApp, "create_acr_if_needed")
        patcher.start()
        self.addCleanup(patcher.stop)

    def up(self, image="mcr.microsoft.com/k8se/quickstart:latest"):
        custom.containerapp_up(self.cmd, "app", resource_group_name="resource-group", image=image)

    def test_preflight_failure_stops_before_provisioning(self):
        definition = {"name": "app", "properties": {"provisioningState": "Succeeded"}}
        for error in lookup_errors():
            for prior_responses in ([], [definition]):
                with self.subTest(error=type(error).__name__, prior_lookups=len(prior_responses)):
                    with mock.patch.object(custom.ContainerAppPreviewClient, "show",
                                           side_effect=prior_responses + [error]):
                        with self.assertRaises(type(error)) as raised:
                            self.up()
                        self.assertIs(error, raised.exception)
                        for name in ("ResourceGroup", "Extension", "CustomLocation", "ContainerAppEnvironment"):
                            self.resources[name].return_value.create_if_needed.assert_not_called()
                        self.create_containerapp.assert_not_called()
                        self.update_containerapp_logic.assert_not_called()

    def test_final_lookup_failure_never_deploys_after_successful_preflight(self):
        definition = {"name": "app", "properties": {"provisioningState": "Succeeded"}}
        error = requests.ConnectionError("Network is unreachable")
        with mock.patch.object(custom.ContainerAppPreviewClient, "show",
                               side_effect=[definition, definition, definition, error]):
            with self.assertRaises(requests.ConnectionError) as raised:
                self.up()
            self.assertIs(error, raised.exception)
            self.create_containerapp.assert_not_called()
            self.update_containerapp_logic.assert_not_called()

    def test_special_image_update_has_no_creation_defaults(self):
        definition = {"name": "app", "properties": {"provisioningState": "Succeeded"}}
        for image in ("mcr.microsoft.com/k8se/quickstart:latest",
                      "mcr.microsoft.com/k8se/aca-foundry-model-host:latest"):
            with self.subTest(image=image):
                with mock.patch.object(custom.ContainerAppPreviewClient, "show", return_value=definition):
                    self.update_containerapp_logic.reset_mock()
                    self.up(image=image)
                    self.create_containerapp.assert_not_called()
                    self.update_containerapp_logic.assert_called_once()
                    self.assertIsNone(self.update_containerapp_logic.call_args.kwargs["ingress"])
                    self.assertIsNone(self.update_containerapp_logic.call_args.kwargs["target_port"])

    def test_app_appearing_after_preflight_updates_without_defaults(self):
        with mock.patch.object(custom.ContainerAppPreviewClient, "show", side_effect=[
                arm_error(404, "ResourceNotFound"), arm_error(404, "ResourceNotFound"), {"name": "app"}]):
            self.up()
            self.create_containerapp.assert_not_called()
            self.update_containerapp_logic.assert_called_once()
            self.assertIsNone(self.update_containerapp_logic.call_args.kwargs["ingress"])
            self.assertIsNone(self.update_containerapp_logic.call_args.kwargs["target_port"])
