# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock

from knack import CLI

from azure.cli.core._config import GLOBAL_CONFIG_DIR, ENV_VAR_PREFIX
from azure.cli.core.cloud import get_active_cloud
from azure.cli.core.profiles import get_sdk, ResourceType, supported_api_version

import azext_aks_preview._helpers as helpers

class MockCLI(CLI):
    def __init__(self):
        super(MockCLI, self).__init__(cli_name='mock_cli', config_dir=GLOBAL_CONFIG_DIR,
                                      config_env_var_prefix=ENV_VAR_PREFIX, commands_loader_cls=MockLoader)
        self.cloud = get_active_cloud(self)


class MockLoader(object):
    def __init__(self, ctx):
        self.ctx = ctx

    def get_models(self, *attr_args, **_):
        from azure.cli.core.profiles import get_sdk
        return get_sdk(self.ctx, ResourceType.MGMT_CONTAINERSERVICE, 'ManagedClusterAPIServerAccessProfile',
                       mod='models', operation_group='managed_clusters')


class MockCmd(object):
    def __init__(self, ctx, arguments={}):
        self.cli_ctx = ctx
        self.loader = MockLoader(self.cli_ctx)
        self.arguments = arguments

    def get_models(self, *attr_args, **kwargs):
        return get_sdk(self.cli_ctx, ResourceType.MGMT_CONTAINERSERVICE, 'ManagedClusterAPIServerAccessProfile',
                       mod='models', operation_group='managed_clusters')


class TestPopulateApiServerAccessProfile(unittest.TestCase):
     def setUp(self):
            self.cli = MockCLI()
        
    def test_single_cidr_with_spaces(self):
        api_server_authorized_ip_ranges = "0.0.0.0/32 "
        profile = helpers._populate_api_server_access_profile(MockCmd(self.cli), api_server_authorized_ip_ranges)
        self.assertListEqual(profile.authorized_ip_ranges, ["0.0.0.0/32"])

    def test_multi_cidr_with_spaces(self):
        api_server_authorized_ip_ranges = " 0.0.0.0/32 , 129.1.1.1/32"
        profile = helpers._populate_api_server_access_profile(MockCmd(self.cli), api_server_authorized_ip_ranges)
        self.assertListEqual(profile.authorized_ip_ranges, ["0.0.0.0/32", "129.1.1.1/32"])


class TestSetVmSetType(unittest.TestCase):
    def test_archaic_k8_version(self):
        version = "1.11.9"
        vm_type = helpers._set_vm_set_type("", version)
        self.assertEqual(vm_type, "AvailabilitySet")

    def test_archaic_k8_version_with_vm_set(self):
        version = "1.11.9"
        vm_type = helpers._set_vm_set_type("AvailabilitySet", version)
        self.assertEqual(vm_type, "AvailabilitySet")

    def test_no_vm_set(self):
        version = "1.15.0"
        vm_type = helpers._set_vm_set_type("", version)
        self.assertEqual(vm_type, "VirtualMachineScaleSets")

    def test_casing_vmss(self):
        version = "1.15.0"
        vm_type = helpers._set_vm_set_type("virtualmachineScaleSets", version)
        self.assertEqual(vm_type, "VirtualMachineScaleSets")

    def test_casing_as(self):
        version = "1.15.0"
        vm_type = helpers._set_vm_set_type("Availabilityset", version)
        self.assertEqual(vm_type, "AvailabilitySet")


class TestTrimContainerName(unittest.TestCase):
    def test_trim_fqdn_name_containing_hcp(self):
        container_name = 'abcdef-dns-ed55ba6d-hcp-centralus-azmk8s-io'
        expected_container_name = 'abcdef-dns-ed55ba6d'
        trim_container_name = helpers._trim_fqdn_name_containing_hcp(container_name)
        self.assertEqual(expected_container_name, trim_container_name)

    def test_trim_fqdn_name_trailing_dash(self):
        container_name = 'dns-ed55ba6ad-e48fe2bd-b4bc-4aac-bc23-29bc44154fe1-privatelink-centralus-azmk8s-io'
        expected_container_name = 'dns-ed55ba6ad-e48fe2bd-b4bc-4aac-bc23-29bc44154fe1-privatelink'
        trim_container_name = helpers._trim_fqdn_name_containing_hcp(
            container_name)
        self.assertEqual(expected_container_name, trim_container_name)

    def test_trim_fqdn_name_not_containing_hcp(self):
        container_name = 'abcdef-dns-ed55ba6d-e48fe2bd-b4bc-4aac-bc23-29bc44154fe1-privatelink-centralus-azmk8s-io'
        expected_container_name = 'abcdef-dns-ed55ba6d-e48fe2bd-b4bc-4aac-bc23-29bc44154fe1-privat'
        trim_container_name = helpers._trim_fqdn_name_containing_hcp(container_name)
        self.assertEqual(expected_container_name, trim_container_name)


class TestFuzzyMatch(unittest.TestCase):
    def setUp(self):
        self.expected = ['bord', 'birdy', 'fbird', 'bir', 'ird', 'birdwaj']

    def test_fuzzy_match(self):
        result = helpers._fuzzy_match(
            "bird", ["plane", "bord", "birdy", "fbird", "bir", "ird", "birdwaj", "bored", "biron", "bead"])

        self.assertCountEqual(result, self.expected)
        self.assertListEqual(result, self.expected)


if __name__ == "__main__":
    unittest.main()
