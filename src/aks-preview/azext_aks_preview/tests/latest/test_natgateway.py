# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest

import azext_aks_preview._natgateway as natgateway
from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview.managed_cluster_decorator import (
    AKSPreviewManagedClusterModels,
)
from azext_aks_preview.tests.latest.mocks import MockCLI, MockCmd


class TestCreateNatGatewayProfile(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        # store all the models used by nat gateway
        self.nat_gateway_models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW).nat_gateway_models

    def test_empty_arguments(self):
        profile = natgateway.create_nat_gateway_profile(None, None, models=self.nat_gateway_models)
        self.assertIsNone(profile)

    def test_nonempty_arguments(self):
        managed_outbound_ip_count = 2
        idle_timeout = 30

        profile = natgateway.create_nat_gateway_profile(managed_outbound_ip_count, idle_timeout, models=self.nat_gateway_models)

        self.assertEqual(profile.managed_outbound_ip_profile.count, managed_outbound_ip_count)
        self.assertEqual(profile.idle_timeout_in_minutes, idle_timeout)


class TestUpdateNatGatewayProfile(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        # store all the models used by nat gateway
        self.nat_gateway_models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW).nat_gateway_models

    def test_empty_arguments(self):
        origin_profile = self.nat_gateway_models.ManagedClusterNATGatewayProfile(
            managed_outbound_ip_profile=self.nat_gateway_models.ManagedClusterManagedOutboundIPProfile(
                count=1
            ),
            idle_timeout_in_minutes=4
        )

        profile = natgateway.update_nat_gateway_profile(None, None, origin_profile, models=self.nat_gateway_models)

        self.assertEqual(profile.managed_outbound_ip_profile.count, origin_profile.managed_outbound_ip_profile.count)
        self.assertEqual(profile.idle_timeout_in_minutes, origin_profile.idle_timeout_in_minutes)

    def test_reset_empty_arguments(self):
        origin_profile = self.nat_gateway_models.ManagedClusterNATGatewayProfile(
            managed_outbound_ip_profile=self.nat_gateway_models.ManagedClusterManagedOutboundIPProfile(
                count=1
            ),
            idle_timeout_in_minutes=4
        )

        profile = natgateway.update_nat_gateway_profile(0, None, origin_profile, models=self.nat_gateway_models)

        self.assertEqual(profile.managed_outbound_ip_profile.count, 0)
        self.assertEqual(profile.idle_timeout_in_minutes, origin_profile.idle_timeout_in_minutes)

    def test_nonempty_arguments(self):
        origin_profile = self.nat_gateway_models.ManagedClusterNATGatewayProfile(
            managed_outbound_ip_profile=self.nat_gateway_models.ManagedClusterManagedOutboundIPProfile(
                count=1
            ),
            idle_timeout_in_minutes=4
        )
        new_managed_outbound_ip_count = 2
        new_idle_timeout = 30

        profile = natgateway.update_nat_gateway_profile(new_managed_outbound_ip_count, new_idle_timeout, origin_profile, models=self.nat_gateway_models)

        self.assertEqual(profile.managed_outbound_ip_profile.count, new_managed_outbound_ip_count)
        self.assertEqual(profile.idle_timeout_in_minutes, new_idle_timeout)


class TestIsNatGatewayProfileProvided(unittest.TestCase):
    def test_empty_arguments(self):
        result = natgateway.is_nat_gateway_profile_provided(None, None)
        self.assertFalse(result)

    def test_nonempty_managed_outbound_ip_count(self):
        result = natgateway.is_nat_gateway_profile_provided(1, None)
        self.assertTrue(result)

    def test_nonempty_idle_timeout(self):
        result = natgateway.is_nat_gateway_profile_provided(None, 4)
        self.assertTrue(result)

    def test_nonempty_arguments(self):
        result = natgateway.is_nat_gateway_profile_provided(1, 4)
        self.assertTrue(result)


class TestCreateNatGatewayV2Profile(unittest.TestCase):
    def setUp(self):
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.nat_gateway_models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW).nat_gateway_models

    def test_v2_with_managed_outbound_ipv6_count(self):
        profile = natgateway.create_nat_gateway_profile(
            2, 30, models=self.nat_gateway_models,
            managed_outbound_ipv6_count=4,
        )
        self.assertEqual(profile.managed_outbound_ip_profile.count, 2)
        self.assertEqual(profile.managed_outbound_ip_profile.count_i_pv6, 4)
        self.assertEqual(profile.idle_timeout_in_minutes, 30)

    def test_v2_with_outbound_ip_ids(self):
        ip_ids = "/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Network/publicIPAddresses/ip1"
        profile = natgateway.create_nat_gateway_profile(
            None, None, models=self.nat_gateway_models,
            outbound_ip_ids=ip_ids,
        )
        self.assertIsNotNone(profile)
        self.assertEqual(len(profile.outbound_i_ps.public_i_ps), 1)
        self.assertEqual(profile.outbound_i_ps.public_i_ps[0], ip_ids)

    def test_v2_with_multiple_outbound_ip_ids(self):
        ip_ids = "/sub/rg/ip1,/sub/rg/ip2"
        profile = natgateway.create_nat_gateway_profile(
            None, None, models=self.nat_gateway_models,
            outbound_ip_ids=ip_ids,
        )
        self.assertEqual(len(profile.outbound_i_ps.public_i_ps), 2)
        self.assertEqual(profile.outbound_i_ps.public_i_ps[0], "/sub/rg/ip1")
        self.assertEqual(profile.outbound_i_ps.public_i_ps[1], "/sub/rg/ip2")

    def test_v2_with_outbound_ip_ids_whitespace(self):
        ip_ids = "/sub/rg/ip1, /sub/rg/ip2"
        profile = natgateway.create_nat_gateway_profile(
            None, None, models=self.nat_gateway_models,
            outbound_ip_ids=ip_ids,
        )
        self.assertEqual(len(profile.outbound_i_ps.public_i_ps), 2)
        self.assertEqual(profile.outbound_i_ps.public_i_ps[1], "/sub/rg/ip2")

    def test_v2_with_outbound_ip_ids_trailing_comma(self):
        ip_ids = "/sub/rg/ip1,"
        profile = natgateway.create_nat_gateway_profile(
            None, None, models=self.nat_gateway_models,
            outbound_ip_ids=ip_ids,
        )
        self.assertEqual(len(profile.outbound_i_ps.public_i_ps), 1)

    def test_v2_with_outbound_ip_prefix_ids(self):
        prefix_ids = "/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Network/publicIPPrefixes/prefix1"
        profile = natgateway.create_nat_gateway_profile(
            None, None, models=self.nat_gateway_models,
            outbound_ip_prefix_ids=prefix_ids,
        )
        self.assertIsNotNone(profile)
        self.assertEqual(len(profile.outbound_ip_prefixes.public_ip_prefixes), 1)
        self.assertEqual(profile.outbound_ip_prefixes.public_ip_prefixes[0], prefix_ids)

    def test_v2_only_ipv6_count(self):
        profile = natgateway.create_nat_gateway_profile(
            None, None, models=self.nat_gateway_models,
            managed_outbound_ipv6_count=8,
        )
        self.assertIsNotNone(profile)
        self.assertEqual(profile.managed_outbound_ip_profile.count_i_pv6, 8)

    def test_create_with_sku_standardv2(self):
        profile = natgateway.create_nat_gateway_profile(
            None, None, models=self.nat_gateway_models,
            nat_gateway_sku="StandardV2",
        )
        self.assertIsNotNone(profile)
        self.assertEqual(profile.sku, "StandardV2")

    def test_create_with_sku_standard(self):
        profile = natgateway.create_nat_gateway_profile(
            2, 30, models=self.nat_gateway_models,
            nat_gateway_sku="Standard",
        )
        self.assertEqual(profile.sku, "Standard")
        self.assertEqual(profile.managed_outbound_ip_profile.count, 2)


class TestUpdateNatGatewayV2Profile(unittest.TestCase):
    def setUp(self):
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.nat_gateway_models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW).nat_gateway_models

    def test_v2_update_with_ipv6_count(self):
        origin_profile = self.nat_gateway_models.ManagedClusterNATGatewayProfile(
            managed_outbound_ip_profile=self.nat_gateway_models.ManagedClusterManagedOutboundIPProfile(count=1),
            idle_timeout_in_minutes=4,
        )
        profile = natgateway.update_nat_gateway_profile(
            None, None, origin_profile, models=self.nat_gateway_models,
            managed_outbound_ipv6_count=4,
        )
        self.assertEqual(profile.managed_outbound_ip_profile.count, 1)
        self.assertEqual(profile.managed_outbound_ip_profile.count_i_pv6, 4)

    def test_v2_update_with_outbound_ip_ids(self):
        origin_profile = self.nat_gateway_models.ManagedClusterNATGatewayProfile(idle_timeout_in_minutes=4)
        ip_ids = "/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Network/publicIPAddresses/ip1"
        profile = natgateway.update_nat_gateway_profile(
            None, None, origin_profile, models=self.nat_gateway_models,
            outbound_ip_ids=ip_ids,
        )
        self.assertEqual(len(profile.outbound_i_ps.public_i_ps), 1)

    def test_v2_empty_v2_params_returns_original(self):
        origin_profile = self.nat_gateway_models.ManagedClusterNATGatewayProfile(
            managed_outbound_ip_profile=self.nat_gateway_models.ManagedClusterManagedOutboundIPProfile(count=2),
            idle_timeout_in_minutes=10,
        )
        profile = natgateway.update_nat_gateway_profile(
            None, None, origin_profile, models=self.nat_gateway_models,
        )
        self.assertEqual(profile.managed_outbound_ip_profile.count, 2)
        self.assertEqual(profile.idle_timeout_in_minutes, 10)

    def test_v2_update_with_sku(self):
        origin_profile = self.nat_gateway_models.ManagedClusterNATGatewayProfile(
            idle_timeout_in_minutes=4,
        )
        profile = natgateway.update_nat_gateway_profile(
            None, None, origin_profile, models=self.nat_gateway_models,
            nat_gateway_sku="StandardV2",
        )
        self.assertEqual(profile.sku, "StandardV2")


class TestIsNatGatewayV2ProfileProvided(unittest.TestCase):
    def test_only_ipv6_count(self):
        result = natgateway.is_nat_gateway_profile_provided(None, None, managed_outbound_ipv6_count=4)
        self.assertTrue(result)

    def test_only_outbound_ip_ids(self):
        result = natgateway.is_nat_gateway_profile_provided(None, None, outbound_ip_ids="/sub/ip1")
        self.assertTrue(result)

    def test_only_outbound_ip_prefix_ids(self):
        result = natgateway.is_nat_gateway_profile_provided(None, None, outbound_ip_prefix_ids="/sub/prefix1")
        self.assertTrue(result)

    def test_all_none(self):
        result = natgateway.is_nat_gateway_profile_provided(None, None, None, None, None)
        self.assertFalse(result)

    def test_only_sku(self):
        result = natgateway.is_nat_gateway_profile_provided(None, None, nat_gateway_sku="StandardV2")
        self.assertTrue(result)


class TestValidateNatGatewayV2Params(unittest.TestCase):
    """Test the cross-parameter validator for V2-only params."""

    def _make_namespace(self, **kwargs):
        from types import SimpleNamespace
        defaults = {
            'nat_gateway_managed_outbound_ipv6_count': None,
            'nat_gateway_outbound_ip_ids': None,
            'nat_gateway_outbound_ip_prefix_ids': None,
            'outbound_type': None,
            'nat_gateway_sku': None,
        }
        defaults.update(kwargs)
        return SimpleNamespace(**defaults)

    def test_v2_params_rejected_when_outbound_type_is_legacy_v2(self):
        # managedNATGatewayV2 is unknown to the 2026-06-02-preview API (dropped from OutboundType);
        # V2 params must now go with managedNATGateway (+ --outbound-type-sku StandardV2).
        from azure.cli.core.azclierror import InvalidArgumentValueError
        from azext_aks_preview._validators import validate_nat_gateway_v2_params
        ns = self._make_namespace(
            nat_gateway_managed_outbound_ipv6_count=4,
            outbound_type='managedNATGatewayV2',
        )
        with self.assertRaises(InvalidArgumentValueError):
            validate_nat_gateway_v2_params(ns)

    def test_v2_params_rejected_when_outbound_type_omitted(self):
        """On create --outbound-type must be set explicitly to managedNATGateway."""
        from azure.cli.core.azclierror import InvalidArgumentValueError
        from azext_aks_preview._validators import validate_nat_gateway_v2_params
        ns = self._make_namespace(
            nat_gateway_managed_outbound_ipv6_count=3,
            outbound_type=None,
        )
        with self.assertRaises(InvalidArgumentValueError):
            validate_nat_gateway_v2_params(ns)

    def test_v2_params_rejected_when_outbound_type_is_non_v2(self):
        from azure.cli.core.azclierror import InvalidArgumentValueError
        from azext_aks_preview._validators import validate_nat_gateway_v2_params
        ns = self._make_namespace(
            nat_gateway_managed_outbound_ipv6_count=4,
            outbound_type='loadBalancer',
        )
        with self.assertRaises(InvalidArgumentValueError):
            validate_nat_gateway_v2_params(ns)

    def test_no_v2_params_passes_always(self):
        from azext_aks_preview._validators import validate_nat_gateway_v2_params
        ns = self._make_namespace(outbound_type='loadBalancer')
        # No V2 params set, should not raise
        validate_nat_gateway_v2_params(ns)

    def test_v2_params_allowed_when_outbound_type_is_managed_nat_gateway(self):
        from azext_aks_preview._validators import validate_nat_gateway_v2_params
        ns = self._make_namespace(
            nat_gateway_managed_outbound_ipv6_count=4,
            outbound_type='managedNATGateway',
        )
        # GA shape: V2 params are valid with managedNATGateway (+ --outbound-type-sku StandardV2)
        validate_nat_gateway_v2_params(ns)

    def test_v2_params_rejected_when_sku_is_standard(self):
        # V2-only params cannot ride on the Standard (V1) SKU; they require StandardV2.
        from azure.cli.core.azclierror import InvalidArgumentValueError
        from azext_aks_preview._validators import validate_nat_gateway_v2_params
        ns = self._make_namespace(
            nat_gateway_managed_outbound_ipv6_count=4,
            outbound_type='managedNATGateway',
            nat_gateway_sku='Standard',
        )
        with self.assertRaises(InvalidArgumentValueError):
            validate_nat_gateway_v2_params(ns)

    def test_v2_params_allowed_when_sku_is_standardv2(self):
        from azext_aks_preview._validators import validate_nat_gateway_v2_params
        ns = self._make_namespace(
            nat_gateway_managed_outbound_ipv6_count=4,
            outbound_type='managedNATGateway',
            nat_gateway_sku='StandardV2',
        )
        validate_nat_gateway_v2_params(ns)


class TestValidateOutboundTypeSku(unittest.TestCase):
    """Test the --outbound-type-sku cross-parameter validator."""

    def _make_namespace(self, **kwargs):
        from types import SimpleNamespace
        defaults = {
            'nat_gateway_sku': None,
            'outbound_type': None,
        }
        defaults.update(kwargs)
        return SimpleNamespace(**defaults)

    def test_sku_allowed_with_managed_nat_gateway(self):
        from azext_aks_preview._validators import validate_outbound_type_sku
        ns = self._make_namespace(nat_gateway_sku='StandardV2', outbound_type='managedNATGateway')
        validate_outbound_type_sku(ns)

    def test_sku_rejected_with_legacy_managed_nat_gateway_v2(self):
        # managedNATGatewayV2 is not a valid outbound type on the 2026-06-02-preview API.
        from azure.cli.core.azclierror import InvalidArgumentValueError
        from azext_aks_preview._validators import validate_outbound_type_sku
        ns = self._make_namespace(nat_gateway_sku='Standard', outbound_type='managedNATGatewayV2')
        with self.assertRaises(InvalidArgumentValueError):
            validate_outbound_type_sku(ns)

    def test_sku_rejected_when_outbound_type_omitted(self):
        """On create --outbound-type must be set explicitly to managedNATGateway."""
        from azure.cli.core.azclierror import InvalidArgumentValueError
        from azext_aks_preview._validators import validate_outbound_type_sku
        ns = self._make_namespace(nat_gateway_sku='StandardV2', outbound_type=None)
        with self.assertRaises(InvalidArgumentValueError):
            validate_outbound_type_sku(ns)

    def test_sku_rejected_with_non_nat_outbound_type(self):
        from azure.cli.core.azclierror import InvalidArgumentValueError
        from azext_aks_preview._validators import validate_outbound_type_sku
        ns = self._make_namespace(nat_gateway_sku='StandardV2', outbound_type='loadBalancer')
        with self.assertRaises(InvalidArgumentValueError):
            validate_outbound_type_sku(ns)

    def test_no_sku_passes_always(self):
        from azext_aks_preview._validators import validate_outbound_type_sku
        ns = self._make_namespace(outbound_type='loadBalancer')
        validate_outbound_type_sku(ns)


class TestValidateOutboundTypeSkuForUpdate(unittest.TestCase):
    """Test the --outbound-type-sku validator on update (omitted --outbound-type allowed)."""

    def _make_namespace(self, **kwargs):
        from types import SimpleNamespace
        defaults = {
            'nat_gateway_sku': None,
            'outbound_type': None,
        }
        defaults.update(kwargs)
        return SimpleNamespace(**defaults)

    def test_sku_allowed_when_outbound_type_omitted(self):
        """On update the outbound type may be omitted when the cluster is already managed NAT gw."""
        from azext_aks_preview._validators import validate_outbound_type_sku_for_update
        ns = self._make_namespace(nat_gateway_sku='StandardV2', outbound_type=None)
        validate_outbound_type_sku_for_update(ns)

    def test_sku_allowed_with_managed_nat_gateway(self):
        from azext_aks_preview._validators import validate_outbound_type_sku_for_update
        ns = self._make_namespace(nat_gateway_sku='StandardV2', outbound_type='managedNATGateway')
        validate_outbound_type_sku_for_update(ns)

    def test_sku_rejected_with_non_nat_outbound_type(self):
        from azure.cli.core.azclierror import InvalidArgumentValueError
        from azext_aks_preview._validators import validate_outbound_type_sku_for_update
        ns = self._make_namespace(nat_gateway_sku='StandardV2', outbound_type='loadBalancer')
        with self.assertRaises(InvalidArgumentValueError):
            validate_outbound_type_sku_for_update(ns)

    def test_no_sku_passes_always(self):
        from azext_aks_preview._validators import validate_outbound_type_sku_for_update
        ns = self._make_namespace(outbound_type='loadBalancer')
        validate_outbound_type_sku_for_update(ns)


class TestValidateNatGatewayV2ParamsForUpdate(unittest.TestCase):
    """Test the V2-only NAT gateway params validator on update."""

    def _make_namespace(self, **kwargs):
        from types import SimpleNamespace
        defaults = {
            'nat_gateway_managed_outbound_ipv6_count': None,
            'nat_gateway_outbound_ip_ids': None,
            'nat_gateway_outbound_ip_prefix_ids': None,
            'outbound_type': None,
            'nat_gateway_sku': None,
        }
        defaults.update(kwargs)
        return SimpleNamespace(**defaults)

    def test_v2_params_allowed_when_outbound_type_omitted(self):
        """On update the outbound type may be omitted when the cluster is already managed NAT gw."""
        from azext_aks_preview._validators import validate_nat_gateway_v2_params_for_update
        ns = self._make_namespace(nat_gateway_managed_outbound_ipv6_count=3, outbound_type=None)
        validate_nat_gateway_v2_params_for_update(ns)

    def test_v2_params_allowed_when_outbound_type_is_managed_nat_gateway(self):
        from azext_aks_preview._validators import validate_nat_gateway_v2_params_for_update
        ns = self._make_namespace(
            nat_gateway_managed_outbound_ipv6_count=4,
            outbound_type='managedNATGateway',
        )
        validate_nat_gateway_v2_params_for_update(ns)

    def test_v2_params_rejected_when_outbound_type_is_non_nat(self):
        from azure.cli.core.azclierror import InvalidArgumentValueError
        from azext_aks_preview._validators import validate_nat_gateway_v2_params_for_update
        ns = self._make_namespace(
            nat_gateway_managed_outbound_ipv6_count=4,
            outbound_type='loadBalancer',
        )
        with self.assertRaises(InvalidArgumentValueError):
            validate_nat_gateway_v2_params_for_update(ns)

    def test_v2_params_rejected_when_sku_is_standard(self):
        from azure.cli.core.azclierror import InvalidArgumentValueError
        from azext_aks_preview._validators import validate_nat_gateway_v2_params_for_update
        ns = self._make_namespace(
            nat_gateway_managed_outbound_ipv6_count=4,
            outbound_type='managedNATGateway',
            nat_gateway_sku='Standard',
        )
        with self.assertRaises(InvalidArgumentValueError):
            validate_nat_gateway_v2_params_for_update(ns)

    def test_no_v2_params_passes_always(self):
        from azext_aks_preview._validators import validate_nat_gateway_v2_params_for_update
        ns = self._make_namespace(outbound_type='loadBalancer')
        validate_nat_gateway_v2_params_for_update(ns)


if __name__ == '__main__':
    unittest.main()
