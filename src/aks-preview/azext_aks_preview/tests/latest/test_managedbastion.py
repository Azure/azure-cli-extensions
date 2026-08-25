# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from knack.util import CLIError

from azext_aks_preview.managedbastion import update_managed_bastion_profile


class TestUpdateManagedBastionProfile(unittest.TestCase):
    def setUp(self):
        self.cmd = MagicMock()
        def get_model(model_name, **_):
            if model_name == "NetworkProfile":
                return lambda: SimpleNamespace(bastion_profile=None)
            return lambda: SimpleNamespace(enabled=None)

        self.cmd.get_models.side_effect = get_model
        self.client = MagicMock()
        self.headers = {"x-ms-test": "value"}

    def test_enable_creates_profiles_and_sets_options(self):
        instance = SimpleNamespace(network_profile=None)
        self.client.get.return_value = instance

        with patch(
            "azext_aks_preview.managedbastion.sdk_no_wait",
            return_value="result",
        ) as mock_sdk_no_wait:
            result = update_managed_bastion_profile(
                self.cmd,
                self.client,
                "rg",
                "cluster",
                no_wait=True,
                aks_custom_headers=self.headers,
                enabled=True,
                enabling=True,
                bastion_sku="Standard",
                bastion_public_ip="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Network/publicIPAddresses/ip",
                bastion_scale_units=2,
            )

        self.assertEqual(result, "result")
        profile = instance.network_profile.bastion_profile
        self.assertTrue(profile.enabled)
        self.assertEqual(profile.sku, "Standard")
        self.assertEqual(
            profile.public_ip_address_id,
            "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Network/publicIPAddresses/ip",
        )
        self.assertEqual(profile.scale_units, 2)
        self.client.get.assert_called_once_with("rg", "cluster", headers=self.headers)
        mock_sdk_no_wait.assert_called_once_with(
            True,
            self.client.begin_create_or_update,
            "rg",
            "cluster",
            instance,
            headers=self.headers,
        )

    def test_enable_rejects_already_enabled_profile(self):
        self.client.get.return_value = SimpleNamespace(
            network_profile=SimpleNamespace(
                bastion_profile=SimpleNamespace(enabled=True)
            )
        )

        with self.assertRaisesRegex(CLIError, "Bastion is already enabled"):
            update_managed_bastion_profile(
                self.cmd,
                self.client,
                "rg",
                "cluster",
                enabled=True,
                enabling=True,
            )

        self.client.begin_create_or_update.assert_not_called()

    def test_update_requires_enabled_profile(self):
        self.client.get.return_value = SimpleNamespace(
            network_profile=SimpleNamespace(
                bastion_profile=SimpleNamespace(enabled=False)
            )
        )

        with self.assertRaisesRegex(CLIError, "Bastion is not enabled"):
            update_managed_bastion_profile(
                self.cmd,
                self.client,
                "rg",
                "cluster",
                enabled=True,
                require_enabled=True,
            )

        self.client.begin_create_or_update.assert_not_called()

    def test_update_preserves_unspecified_fields(self):
        profile = SimpleNamespace(
            enabled=True,
            sku="standard",
            public_ip_address_id="public-ip-id",
            scale_units=2,
        )
        instance = SimpleNamespace(
            network_profile=SimpleNamespace(bastion_profile=profile)
        )
        self.client.get.return_value = instance

        with patch("azext_aks_preview.managedbastion.sdk_no_wait"):
            update_managed_bastion_profile(
                self.cmd,
                self.client,
                "rg",
                "cluster",
                enabled=True,
                require_enabled=True,
                bastion_scale_units=4,
            )

        self.assertTrue(profile.enabled)
        self.assertEqual(profile.sku, "standard")
        self.assertEqual(profile.public_ip_address_id, "public-ip-id")
        self.assertEqual(profile.scale_units, 4)

    def test_disable_preserves_profile_configuration(self):
        profile = SimpleNamespace(
            enabled=True,
            sku="premium",
            public_ip_address_id="public-ip-id",
            scale_units=4,
        )
        self.client.get.return_value = SimpleNamespace(
            network_profile=SimpleNamespace(bastion_profile=profile)
        )

        with patch("azext_aks_preview.managedbastion.sdk_no_wait"):
            update_managed_bastion_profile(
                self.cmd,
                self.client,
                "rg",
                "cluster",
                enabled=False,
            )

        self.assertFalse(profile.enabled)
        self.assertEqual(profile.sku, "premium")
        self.assertEqual(profile.public_ip_address_id, "public-ip-id")
        self.assertEqual(profile.scale_units, 4)


if __name__ == "__main__":
    unittest.main()