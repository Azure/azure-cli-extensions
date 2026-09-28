# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from azext_k8s_extension import consts, custom
from azext_k8s_extension._params import load_arguments
from azext_k8s_extension.utils import get_cluster_rp_api_version

from .MockClasses import MockCommand


class _ArgumentContext:
    def __init__(self, loader, command):
        self.loader = loader
        self.command = command

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def argument(self, name, *args, **kwargs):
        self.loader.arguments.setdefault(self.command, {})[name] = kwargs

    def deprecate(self, **kwargs):
        return kwargs


class _ArgumentLoader:
    def __init__(self):
        self.arguments = {}

    def argument_context(self, command, **kwargs):
        return _ArgumentContext(self, command)


class TestFleetArguments(unittest.TestCase):
    def test_fleets_is_an_accepted_cluster_type(self):
        loader = _ArgumentLoader()

        load_arguments(loader, None)

        extension_choices = loader.arguments[
            consts.EXTENSION_NAME
        ]["cluster_type"]["arg_type"].settings["choices"]
        extension_type_choices = loader.arguments[
            f"{consts.EXTENSION_NAME} extension-types"
        ]["cluster_type"]["arg_type"].settings["choices"]
        self.assertIn("fleets", extension_choices)
        self.assertIn("fleets", extension_type_choices)


class TestFleetResourceMapping(unittest.TestCase):
    def test_fleet_provider_and_api_version(self):
        self.assertEqual(
            (consts.FLEET_RP, consts.FLEET_API_VERSION),
            get_cluster_rp_api_version("fleets"),
        )

    @patch.object(custom, "get_subscription_id", return_value="subscription-id")
    @patch.object(custom, "cf_resources")
    def test_fleet_identity_uses_nested_fleet_resource_id(
        self, mock_cf_resources, _
    ):
        resources = mock_cf_resources.return_value
        resources.get_by_id.return_value = SimpleNamespace(location="West US 2")

        identity, location = getattr(custom, "__create_identity")(
            MockCommand(), "fleet-rg", "fleet-1", "fleets", consts.FLEET_RP
        )

        resources.get_by_id.assert_called_once_with(
            "/subscriptions/subscription-id/resourceGroups/fleet-rg/providers/"
            "Microsoft.ContainerService/fleets/fleet-1",
            consts.FLEET_API_VERSION,
        )
        self.assertEqual("SystemAssigned", identity.type)
        self.assertEqual("west us 2", location)

    def test_fleet_show_and_list_pass_provider_and_resource_type(self):
        client = MagicMock()

        custom.show_k8s_extension(
            client, "fleet-rg", "fleet-1", "flux", "fleets"
        )
        custom.list_k8s_extension(client, "fleet-rg", "fleet-1", "fleets")

        client.get.assert_called_once_with(
            "fleet-rg", consts.FLEET_RP, "fleets", "fleet-1", "flux"
        )
        client.list.assert_called_once_with(
            "fleet-rg", consts.FLEET_RP, "fleets", "fleet-1"
        )

    @patch.object(custom, "sdk_no_wait")
    @patch.object(custom, "validate_cc_registration")
    @patch.object(custom, "is_dogfood_cluster", return_value=True)
    def test_fleet_create_passes_provider_and_resource_type(
        self, _, __, mock_sdk_no_wait
    ):
        client = MagicMock()

        custom.create_k8s_extension(
            MockCommand(),
            client,
            "fleet-rg",
            "fleet-1",
            "flux",
            "fleets",
            "microsoft.flux",
        )

        args = mock_sdk_no_wait.call_args.args
        self.assertEqual(
            (
                False,
                client.begin_create,
                "fleet-rg",
                consts.FLEET_RP,
                "fleets",
                "fleet-1",
                "flux",
            ),
            args[:7],
        )

    @patch.object(custom, "sdk_no_wait")
    def test_fleet_update_passes_provider_and_resource_type(self, mock_sdk_no_wait):
        client = MagicMock()
        client.get.return_value = SimpleNamespace(extension_type="microsoft.flux")

        custom.update_k8s_extension(
            MockCommand(), client, "fleet-rg", "fleet-1", "flux", "fleets"
        )

        args = mock_sdk_no_wait.call_args.args
        self.assertEqual(
            (
                False,
                client.begin_update,
                "fleet-rg",
                consts.FLEET_RP,
                "fleets",
                "fleet-1",
                "flux",
            ),
            args[:7],
        )

    @patch.object(custom, "sdk_no_wait")
    @patch(
        "azext_k8s_extension.partner_extensions.DefaultExtension."
        "user_confirmation_factory"
    )
    def test_fleet_delete_passes_provider_and_resource_type(
        self, _, mock_sdk_no_wait
    ):
        client = MagicMock()
        client.get.return_value = SimpleNamespace(extension_type="microsoft.flux")

        custom.delete_k8s_extension(
            MockCommand(),
            client,
            "fleet-rg",
            "fleet-1",
            "flux",
            "fleets",
            yes=True,
        )

        args = mock_sdk_no_wait.call_args.args
        self.assertEqual(
            (
                False,
                client.begin_delete,
                "fleet-rg",
                consts.FLEET_RP,
                "fleets",
                "fleet-1",
                "flux",
            ),
            args[:7],
        )

    def test_fleet_extension_type_commands_pass_provider_and_resource_type(self):
        client = MagicMock()

        custom.list_extension_types_by_cluster(
            client, "fleet-rg", "fleet-1", "fleets"
        )
        custom.show_extension_type_by_cluster(
            client, "fleet-rg", "fleet-1", "fleets", "microsoft.flux"
        )
        custom.list_extension_type_versions_by_cluster(
            client, "fleet-rg", "fleets", "fleet-1", "microsoft.flux"
        )
        custom.show_extension_type_version_by_cluster(
            client, "fleet-rg", "fleets", "fleet-1", "microsoft.flux", "1.0.0"
        )

        self.assertEqual(
            ("fleet-rg", consts.FLEET_RP, "fleets", "fleet-1"),
            client.list.call_args.args[:4],
        )
        self.assertEqual(
            ("fleet-rg", consts.FLEET_RP, "fleets", "fleet-1", "microsoft.flux"),
            client.get.call_args.args,
        )
        self.assertEqual(
            ("fleet-rg", consts.FLEET_RP, "fleets", "fleet-1", "microsoft.flux"),
            client.cluster_list_versions.call_args.args[:5],
        )
        self.assertEqual(
            (
                "fleet-rg",
                consts.FLEET_RP,
                "fleets",
                "fleet-1",
                "microsoft.flux",
                "1.0.0",
            ),
            client.cluster_get_version.call_args.args,
        )


if __name__ == "__main__":
    unittest.main()
