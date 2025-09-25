# --------------------------------------------------------------------------------------------
# INVALID CASES FOR LOCAL DNS CONFIG TESTS
# These tests cover invalid, error, and edge-case scenarios for local DNS config handling.
# --------------------------------------------------------------------------------------------

import os
from .test_localdns_profile import assert_dns_overrides_equal, vnetDnsOverridesExpected, kubeDnsOverridesExpected
from azext_aks_preview.tests.latest.custom_preparers import AKSCustomResourceGroupPreparer
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

class InvalidLocalDnsConfigTests:
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix="clitest", location="westus2")
    def test_aks_nodepool_update_with_localdns_invalid_mode(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("np", 6)
        valid_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "required_mode_with_valid_dns_overrides.json")
        invalid_mode_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "invalid_mode.json")
        self.kwargs.update({
            "resource_group": resource_group,
            "name": aks_name,
            "nodepool_name": nodepool_name,
            "ssh_key_value": self.generate_ssh_keys(),
            "valid_config": valid_config_path,
            "invalid_mode_config": invalid_mode_config_path
        })

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count 1 --ssh-key-value={ssh_key_value} --generate-ssh-keys "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        add_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --node-count 1 --localdns-config={valid_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(add_cmd, checks=[self.check("provisioningState", "Succeeded")])

        update_cmd = (
            "aks nodepool update --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --localdns-config={invalid_mode_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
        )
        try:
            self.cmd(update_cmd)
            assert False, "Expected failure for invalid mode, but command succeeded."
        except Exception as ex:
            assert "invalid" in str(ex).lower() or "error" in str(ex).lower() or "mode" in str(ex).lower(), f"Unexpected error: {ex}"

        self.cmd(
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix="clitest", location="westus2")
    def test_aks_nodepool_update_with_localdns_empty_config(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("np", 6)
        empty_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "empty_config.json")
        self.kwargs.update({
            "resource_group": resource_group,
            "name": aks_name,
            "nodepool_name": nodepool_name,
            "ssh_key_value": self.generate_ssh_keys(),
            "empty_config": empty_config_path
        })

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count 1 --ssh-key-value={ssh_key_value} --generate-ssh-keys "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        add_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --node-count 1 --localdns-config={empty_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(add_cmd, checks=[self.check("provisioningState", "Succeeded")])

        update_cmd = (
            "aks nodepool update --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --localdns-config={empty_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
        )
        try:
            self.cmd(update_cmd)
            assert False, "Expected failure for empty config, but command succeeded."
        except Exception as ex:
            assert "invalid" in str(ex).lower() or "error" in str(ex).lower() or "config" in str(ex).lower(), f"Unexpected error: {ex}"

        self.cmd(
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix="clitest", location="westus2")
    def test_aks_nodepool_update_with_localdns_required_mode_invalid_vnetdns(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("np", 6)
        valid_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "required_mode_with_valid_dns_overrides.json")
        invalid_vnetdns_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "invalid_vnetdns.json")
        self.kwargs.update({
            "resource_group": resource_group,
            "name": aks_name,
            "nodepool_name": nodepool_name,
            "ssh_key_value": self.generate_ssh_keys(),
            "valid_config": valid_config_path,
            "invalid_vnetdns_config": invalid_vnetdns_config_path
        })

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count 1 --ssh-key-value={ssh_key_value} --generate-ssh-keys "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        add_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --node-count 1 --localdns-config={valid_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(add_cmd, checks=[self.check("provisioningState", "Succeeded")])

        update_cmd = (
            "aks nodepool update --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --localdns-config={invalid_vnetdns_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
        )
        try:
            self.cmd(update_cmd)
            assert False, "Expected failure for invalid vnetdns, but command succeeded."
        except Exception as ex:
            assert "invalid" in str(ex).lower() or "error" in str(ex).lower() or "vnetdns" in str(ex).lower(), f"Unexpected error: {ex}"

        self.cmd(
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix="clitest", location="westus2")
    def test_aks_nodepool_update_with_localdns_required_mode_invalid_kubedns(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("np", 6)
        valid_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "required_mode_with_valid_dns_overrides.json")
        invalid_kubedns_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "invalid_kubedns.json")
        self.kwargs.update({
            "resource_group": resource_group,
            "name": aks_name,
            "nodepool_name": nodepool_name,
            "ssh_key_value": self.generate_ssh_keys(),
            "valid_config": valid_config_path,
            "invalid_kubedns_config": invalid_kubedns_config_path
        })

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count 1 --ssh-key-value={ssh_key_value} --generate-ssh-keys "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        add_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --node-count 1 --localdns-config={valid_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(add_cmd, checks=[self.check("provisioningState", "Succeeded")])

        update_cmd = (
            "aks nodepool update --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --localdns-config={invalid_kubedns_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
        )
        try:
            self.cmd(update_cmd)
            assert False, "Expected failure for invalid kubedns, but command succeeded."
        except Exception as ex:
            assert "invalid" in str(ex).lower() or "error" in str(ex).lower() or "kubedns" in str(ex).lower(), f"Unexpected error: {ex}"

        self.cmd(
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix="clitest", location="westus2")
    def test_aks_nodepool_add_with_localdns_missing_mode(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("np", 6)
        missing_mode_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "missing_mode.json")
        self.kwargs.update({
            "resource_group": resource_group,
            "name": aks_name,
            "nodepool_name": nodepool_name,
            "ssh_key_value": self.generate_ssh_keys(),
            "missing_mode_config": missing_mode_config_path
        })

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count 1 --ssh-key-value={ssh_key_value} --generate-ssh-keys "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        add_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --node-count 1 --localdns-config={missing_mode_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
            "--kubernetes-version 1.33.0"
        )
        try:
            self.cmd(add_cmd)
            assert False, "Expected failure for missing mode, but command succeeded."
        except Exception as ex:
            assert "invalid" in str(ex).lower() or "error" in str(ex).lower() or "mode" in str(ex).lower(), f"Unexpected error: {ex}"

        self.cmd(
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix="clitest", location="westus2")
    def test_aks_nodepool_add_with_localdns_required_mode_empty_overrides(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("np", 6)
        empty_overrides_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "required_mode_empty_overrides.json")
        self.kwargs.update({
            "resource_group": resource_group,
            "name": aks_name,
            "nodepool_name": nodepool_name,
            "ssh_key_value": self.generate_ssh_keys(),
            "empty_overrides_config": empty_overrides_config_path
        })

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count 1 --ssh-key-value={ssh_key_value} --generate-ssh-keys "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        add_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --node-count 1 --localdns-config={empty_overrides_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
            "--kubernetes-version 1.33.0"
        )
        try:
            self.cmd(add_cmd)
            assert False, "Expected failure for empty overrides in required mode, but command succeeded."
        except Exception as ex:
            assert "invalid" in str(ex).lower() or "error" in str(ex).lower() or "overrides" in str(ex).lower(), f"Unexpected error: {ex}"

        self.cmd(
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix="clitest", location="westus2")
    def test_aks_nodepool_add_with_localdns_required_mode_partial_invalid(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("np", 6)
        partial_invalid_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "required_mode_partial_invalid.json")
        self.kwargs.update({
            "resource_group": resource_group,
            "name": aks_name,
            "nodepool_name": nodepool_name,
            "ssh_key_value": self.generate_ssh_keys(),
            "partial_invalid_config": partial_invalid_config_path
        })

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count 1 --ssh-key-value={ssh_key_value} --generate-ssh-keys "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        add_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --node-count 1 --localdns-config={partial_invalid_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
            "--kubernetes-version 1.33.0"
        )
        try:
            self.cmd(add_cmd)
            assert False, "Expected failure for partial invalid config in required mode, but command succeeded."
        except Exception as ex:
            assert "invalid" in str(ex).lower() or "error" in str(ex).lower() or "config" in str(ex).lower(), f"Unexpected error: {ex}"

        self.cmd(
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix="clitest", location="westus2")
    def test_aks_nodepool_add_with_localdns_required_mode_extra_property(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("np", 6)
        extra_property_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "required_mode_extra_property.json")
        self.kwargs.update({
            "resource_group": resource_group,
            "name": aks_name,
            "nodepool_name": nodepool_name,
            "ssh_key_value": self.generate_ssh_keys(),
            "extra_property_config": extra_property_config_path
        })

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count 1 --ssh-key-value={ssh_key_value} --generate-ssh-keys "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        add_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --node-count 1 --localdns-config={extra_property_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
            "--kubernetes-version 1.33.0"
        )
        try:
            self.cmd(add_cmd)
            assert False, "Expected failure for extra property in required mode, but command succeeded."
        except Exception as ex:
            assert "invalid" in str(ex).lower() or "error" in str(ex).lower() or "property" in str(ex).lower(), f"Unexpected error: {ex}"

        self.cmd(
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix="clitest", location="westus2")
    def test_aks_nodepool_add_with_localdns_empty_mode(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("np", 6)
        empty_mode_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "empty_mode.json")
        self.kwargs.update({
            "resource_group": resource_group,
            "name": aks_name,
            "nodepool_name": nodepool_name,
            "ssh_key_value": self.generate_ssh_keys(),
            "empty_mode_config": empty_mode_config_path
        })

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count 1 --ssh-key-value={ssh_key_value} --generate-ssh-keys "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        add_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --node-count 1 --localdns-config={empty_mode_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
            "--kubernetes-version 1.33.0"
        )
        try:
            self.cmd(add_cmd)
            assert False, "Expected failure for empty mode, but command succeeded."
        except Exception as ex:
            assert "invalid" in str(ex).lower() or "error" in str(ex).lower() or "mode" in str(ex).lower(), f"Unexpected error: {ex}"

        self.cmd(
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix="clitest", location="westus2")
    def test_aks_nodepool_add_with_localdns_null_mode(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("np", 6)
        null_mode_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "null_mode.json")
        self.kwargs.update({
            "resource_group": resource_group,
            "name": aks_name,
            "nodepool_name": nodepool_name,
            "ssh_key_value": self.generate_ssh_keys(),
            "null_mode_config": null_mode_config_path
        })

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count 1 --ssh-key-value={ssh_key_value} --generate-ssh-keys "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        add_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --node-count 1 --localdns-config={null_mode_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
            "--kubernetes-version 1.33.0"
        )
        try:
            self.cmd(add_cmd)
            assert False, "Expected failure for null mode, but command succeeded."
        except Exception as ex:
            assert "invalid" in str(ex).lower() or "error" in str(ex).lower() or "mode" in str(ex).lower(), f"Unexpected error: {ex}"

        self.cmd(
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix="clitest", location="westus2")
    def test_aks_nodepool_add_with_localdns_empty_config(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("np", 6)
        empty_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "empty_config.json")
        self.kwargs.update({
            "resource_group": resource_group,
            "name": aks_name,
            "nodepool_name": nodepool_name,
            "ssh_key_value": self.generate_ssh_keys(),
            "empty_config": empty_config_path
        })

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count 1 --ssh-key-value={ssh_key_value} --generate-ssh-keys "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        add_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --node-count 1 --localdns-config={empty_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
            "--kubernetes-version 1.33.0"
        )
        try:
            self.cmd(add_cmd)
            assert False, "Expected failure for empty config, but command succeeded."
        except Exception as ex:
            assert "invalid" in str(ex).lower() or "error" in str(ex).lower() or "config" in str(ex).lower(), f"Unexpected error: {ex}"

        self.cmd(
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix="clitest", location="westus2")
    def test_aks_nodepool_add_with_localdns_null_config(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("np", 6)
        null_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "null_config.json")
        self.kwargs.update({
            "resource_group": resource_group,
            "name": aks_name,
            "nodepool_name": nodepool_name,
            "ssh_key_value": self.generate_ssh_keys(),
            "null_config": null_config_path
        })

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count 1 --ssh-key-value={ssh_key_value} --generate-ssh-keys "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        add_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --node-count 1 --localdns-config={null_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
            "--kubernetes-version 1.33.0"
        )
        try:
            self.cmd(add_cmd)
            assert False, "Expected failure for null config, but command succeeded."
        except Exception as ex:
            assert "invalid" in str(ex).lower() or "error" in str(ex).lower() or "config" in str(ex).lower(), f"Unexpected error: {ex}"

        self.cmd(
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix="clitest", location="westus2")
    def test_aks_nodepool_add_with_localdns_invalid_mode(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("np", 6)
        valid_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "required_mode_with_valid_dns_overrides.json")
        invalid_mode_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "invalid_mode.json")
        self.kwargs.update({
            "resource_group": resource_group,
            "name": aks_name,
            "nodepool_name": nodepool_name,
            "ssh_key_value": self.generate_ssh_keys(),
            "valid_config": valid_config_path,
            "invalid_mode_config": invalid_mode_config_path
        })

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count 1 --ssh-key-value={ssh_key_value} --generate-ssh-keys "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        add_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --node-count 1 --localdns-config={valid_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(add_cmd, checks=[self.check("provisioningState", "Succeeded")])

        update_cmd = (
            "aks nodepool update --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --localdns-config={invalid_mode_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
        )
        try:
            self.cmd(update_cmd)
            assert False, "Expected failure for invalid mode, but command succeeded."
        except Exception as ex:
            assert "invalid" in str(ex).lower() or "error" in str(ex).lower() or "mode" in str(ex).lower(), f"Unexpected error: {ex}"

        self.cmd(
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix="clitest", location="westus2")
    def test_aks_nodepool_add_with_localdns_required_mode_invalid_vnetdns(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("np", 6)
        valid_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "required_mode_with_valid_dns_overrides.json")
        invalid_vnetdns_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "invalid_vnetdns.json")
        self.kwargs.update({
            "resource_group": resource_group,
            "name": aks_name,
            "nodepool_name": nodepool_name,
            "ssh_key_value": self.generate_ssh_keys(),
            "valid_config": valid_config_path,
            "invalid_vnetdns_config": invalid_vnetdns_config_path
        })

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count 1 --ssh-key-value={ssh_key_value} --generate-ssh-keys "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        add_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --node-count 1 --localdns-config={valid_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(add_cmd, checks=[self.check("provisioningState", "Succeeded")])

        update_cmd = (
            "aks nodepool update --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --localdns-config={invalid_vnetdns_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
        )
        try:
            self.cmd(update_cmd)
            assert False, "Expected failure for invalid vnetdns, but command succeeded."
        except Exception as ex:
            assert "invalid" in str(ex).lower() or "error" in str(ex).lower() or "vnetdns" in str(ex).lower(), f"Unexpected error: {ex}"

        self.cmd(
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix="clitest", location="westus2")
    def test_aks_nodepool_add_with_localdns_required_mode_invalid_kubedns(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("np", 6)
        valid_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "required_mode_with_valid_dns_overrides.json")
        invalid_kubedns_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "localdnsconfig", "invalid_kubedns.json")
        self.kwargs.update({
            "resource_group": resource_group,
            "name": aks_name,
            "nodepool_name": nodepool_name,
            "ssh_key_value": self.generate_ssh_keys(),
            "valid_config": valid_config_path,
            "invalid_kubedns_config": invalid_kubedns_config_path
        })

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count 1 --ssh-key-value={ssh_key_value} --generate-ssh-keys "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        add_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --node-count 1 --localdns-config={valid_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
            "--kubernetes-version 1.33.0"
        )
        self.cmd(add_cmd, checks=[self.check("provisioningState", "Succeeded")])

        update_cmd = (
            "aks nodepool update --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool_name} --localdns-config={invalid_kubedns_config} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/LocalDNSPreview "
        )
        try:
            self.cmd(update_cmd)
            assert False, "Expected failure for invalid kubedns, but command succeeded."
        except Exception as ex:
            assert "invalid" in str(ex).lower() or "error" in str(ex).lower() or "kubedns" in str(ex).lower(), f"Unexpected error: {ex}"

        self.cmd(
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait",
            checks=[self.is_empty()],
        )
