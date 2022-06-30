# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from azure.cli.core.util import CLIError
from azure.cli.core.azclierror import InvalidArgumentValueError
import azext_aks_preview._validators as validators
from azext_aks_preview._consts import ADDONS


class TestValidateIPRanges(unittest.TestCase):
    def test_simultaneous_allow_and_disallow_with_spaces(self):
        api_server_authorized_ip_ranges = " 0.0.0.0/32 , 129.1.1.1.1 "
        namespace = Namespace(api_server_authorized_ip_ranges)
        err = ("Setting --api-server-authorized-ip-ranges to 0.0.0.0/32 is not allowed with other IP ranges."
               "Refer to https://aka.ms/aks/whitelist for more details")

        with self.assertRaises(CLIError) as cm:
            validators.validate_ip_ranges(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_simultaneous_enable_and_disable_with_spaces(self):
        # an entry of "", 129.1.1.1.1 from command line is translated into " , 129.1.1.1.1"
        api_server_authorized_ip_ranges = " , 129.1.1.1.1"
        namespace = Namespace(api_server_authorized_ip_ranges)
        err = "--api-server-authorized-ip-ranges cannot be disabled and simultaneously enabled"

        with self.assertRaises(CLIError) as cm:
            validators.validate_ip_ranges(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_disable_authorized_ip_ranges(self):
        api_server_authorized_ip_ranges = ''
        namespace = Namespace(api_server_authorized_ip_ranges)
        validators.validate_ip_ranges(namespace)

    def test_local_ip_address(self):
        api_server_authorized_ip_ranges = "192.168.0.0,192.168.0.0/16"
        namespace = Namespace(api_server_authorized_ip_ranges)
        err = "--api-server-authorized-ip-ranges must be global non-reserved addresses or CIDRs"

        with self.assertRaises(CLIError) as cm:
            validators.validate_ip_ranges(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_invalid_ip(self):
        api_server_authorized_ip_ranges = "193.168.0"
        namespace = Namespace(api_server_authorized_ip_ranges)
        err = "--api-server-authorized-ip-ranges should be a list of IPv4 addresses or CIDRs"

        with self.assertRaises(CLIError) as cm:
            validators.validate_ip_ranges(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_IPv6(self):
        api_server_authorized_ip_ranges = "3ffe:1900:4545:3:200:f8ff:fe21:67cf"
        namespace = Namespace(api_server_authorized_ip_ranges)
        err = "--api-server-authorized-ip-ranges cannot be IPv6 addresses"

        with self.assertRaises(CLIError) as cm:
            validators.validate_ip_ranges(namespace)
        self.assertEqual(str(cm.exception), err)


class Namespace:
    def __init__(self, api_server_authorized_ip_ranges=None, cluster_autoscaler_profile=None, kubernetes_version=None):
        self.api_server_authorized_ip_ranges = api_server_authorized_ip_ranges
        self.cluster_autoscaler_profile = cluster_autoscaler_profile
        self.kubernetes_version = kubernetes_version


class TestSubnetId(unittest.TestCase):
    def test_invalid_subnet_id(self):
        invalid_vnet_subnet_id = "dummy subnet id"
        err = ("--vnet-subnet-id is not a valid Azure resource ID.")

        with self.assertRaises(CLIError) as cm:
            validators._validate_subnet_id(invalid_vnet_subnet_id, "--vnet-subnet-id")
        self.assertEqual(str(cm.exception), err)

    def test_valid_vnet_subnet_id(self):
        valid_subnet_id = "/subscriptions/testid/resourceGroups/MockedResourceGroup/providers/Microsoft.Network/virtualNetworks/MockedNetworkId/subnets/MockedSubNetId"
        validators._validate_subnet_id(valid_subnet_id, "something")

    def test_none_vnet_subnet_id(self):
        validators._validate_subnet_id(None, "something")

    def test_empty_vnet_subnet_id(self):
        validators._validate_subnet_id("", "something")


class MaxSurgeNamespace:
    def __init__(self, max_surge):
        self.max_surge = max_surge


class SpotMaxPriceNamespace:
    def __init__(self, spot_max_price):
        self.priority = "Spot"
        self.spot_max_price = spot_max_price


class MessageOfTheDayNamespace:
    def __init__(self, message_of_the_day, os_type):
        self.os_type = os_type
        self.message_of_the_day = message_of_the_day


class EnableCustomCATrustNamespace:
    def __init__(self, os_type, enable_custom_ca_trust):
        self.os_type = os_type
        self.enable_custom_ca_trust = enable_custom_ca_trust


class TestMaxSurge(unittest.TestCase):
    def test_valid_cases(self):
        valid = ["5", "33%", "1", "100%"]
        for v in valid:
            validators.validate_max_surge(MaxSurgeNamespace(v))

    def test_throws_on_string(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_max_surge(MaxSurgeNamespace("foobar"))
        self.assertTrue('int or percentage' in str(cm.exception), msg=str(cm.exception))

    def test_throws_on_negative(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_max_surge(MaxSurgeNamespace("-3"))
        self.assertTrue('positive' in str(cm.exception), msg=str(cm.exception))


class TestSpotMaxPrice(unittest.TestCase):
    def test_valid_cases(self):
        valid = [5, 5.12345, -1.0, 0.068, 0.071, 5.00000000]
        for v in valid:
            validators.validate_spot_max_price(SpotMaxPriceNamespace(v))

    def test_throws_if_more_than_5(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_spot_max_price(SpotMaxPriceNamespace(5.123456))
        self.assertTrue('--spot_max_price can only include up to 5 decimal places' in str(cm.exception), msg=str(cm.exception))

    def test_throws_if_non_valid_negative(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_spot_max_price(SpotMaxPriceNamespace(-2))
        self.assertTrue('--spot_max_price can only be any decimal value greater than zero, or -1 which indicates' in str(cm.exception), msg=str(cm.exception))
        with self.assertRaises(CLIError) as cm:
            validators.validate_spot_max_price(SpotMaxPriceNamespace(0))
        self.assertTrue('--spot_max_price can only be any decimal value greater than zero, or -1 which indicates' in str(cm.exception), msg=str(cm.exception))

    def test_throws_if_input_max_price_for_regular(self):
        ns = SpotMaxPriceNamespace(2)
        ns.priority = "Regular"
        with self.assertRaises(CLIError) as cm:
            validators.validate_spot_max_price(ns)
        self.assertTrue('--spot_max_price can only be set when --priority is Spot' in str(cm.exception), msg=str(cm.exception))


class TestMessageOfTheday(unittest.TestCase):
    def test_valid_cases(self):
        valid = ["foo", ""]
        for v in valid:
            validators.validate_message_of_the_day(MessageOfTheDayNamespace(v, "Linux"))

    def test_fail_if_os_type_windows(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_message_of_the_day(MessageOfTheDayNamespace("foo", "Windows"))
        self.assertTrue('--message-of-the-day can only be set for linux nodepools' in str(cm.exception), msg=str(cm.exception))

    def test_fail_if_os_type_invalid(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_message_of_the_day(MessageOfTheDayNamespace("foo", "invalid"))
        self.assertTrue('--message-of-the-day can only be set for linux nodepools' in str(cm.exception), msg=str(cm.exception))


class TestEnableCustomCATrust(unittest.TestCase):
    def test_pass_if_os_type_linux(self):
        validators.validate_enable_custom_ca_trust(EnableCustomCATrustNamespace("Linux", True))

    def test_fail_if_os_type_windows(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_enable_custom_ca_trust(EnableCustomCATrustNamespace("Windows", True))
        self.assertTrue('--enable_custom_ca_trust can only be set for Linux nodepools' in str(cm.exception), msg=str(cm.exception))

    def test_fail_if_os_type_invalid(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_enable_custom_ca_trust(EnableCustomCATrustNamespace("invalid", True))
        self.assertTrue('--enable_custom_ca_trust can only be set for Linux nodepools' in str(cm.exception), msg=str(cm.exception))


class ValidateAddonsNamespace:
    def __init__(self, addons):
        self.addons = addons


class TestValidateAddons(unittest.TestCase):
    def test_correct_addon(self):
        addons = list(ADDONS)
        if len(addons) > 0:
            first_addon = addons[0]
            namespace1 = ValidateAddonsNamespace(first_addon)

            try:
                validators.validate_addons(namespace1)
            except CLIError:
                self.fail("validate_addons failed unexpectedly with CLIError")

    def test_validate_addons(self):
        addons = list(ADDONS)
        if len(addons) > 0:
            first_addon = addons[0]
            midlen = int(len(first_addon) / 2)

            namespace = ValidateAddonsNamespace(
                first_addon[:midlen] + first_addon[midlen + 1:])
            self.assertRaises(CLIError, validators.validate_addons, namespace)

    def test_no_addon_match(self):
        namespace = ValidateAddonsNamespace("qfrnmjk")

        self.assertRaises(CLIError, validators.validate_addons, namespace)


class AssignIdentityNamespace:
    def __init__(self, assign_identity):
        self.assign_identity = assign_identity


class TestAssignIdentity(unittest.TestCase):
    def test_invalid_identity_id(self):
        invalid_identity_id = "dummy identity id"
        namespace = AssignIdentityNamespace(invalid_identity_id)
        err = ("--assign-identity is not a valid Azure resource ID.")

        with self.assertRaises(CLIError) as cm:
            validators.validate_assign_identity(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_valid_identity_id(self):
        valid_identity_id = "/subscriptions/testid/resourceGroups/MockedResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/mockIdentityID"
        namespace = AssignIdentityNamespace(valid_identity_id)
        validators.validate_assign_identity(namespace)

    def test_none_identity_id(self):
        none_identity_id = None
        namespace = AssignIdentityNamespace(none_identity_id)
        validators.validate_assign_identity(namespace)

    def test_empty_identity_id(self):
        empty_identity_id = ""
        namespace = AssignIdentityNamespace(empty_identity_id)
        validators.validate_assign_identity(namespace)


class PodIdentityNamespace:

    def __init__(self, identity_name):
        self.identity_name = identity_name


class TestValidatePodIdentityResourceName(unittest.TestCase):

    def test_valid_required_resource_name(self):
        validator = validators.validate_pod_identity_resource_name('identity_name', required=True)
        namespace = PodIdentityNamespace('test-name')
        validator(namespace)

    def test_missing_required_resource_name(self):
        validator = validators.validate_pod_identity_resource_name('identity_name', required=True)
        namespace = PodIdentityNamespace(None)

        with self.assertRaises(CLIError) as cm:
            validator(namespace)
        self.assertEqual(str(cm.exception), '--name is required')


class PodIdentityResourceNamespace:

    def __init__(self, namespace):
        self.namespace = namespace


class TestValidatePodIdentityResourceNamespace(unittest.TestCase):

    def test_valid_required_resource_name(self):
        namespace = PodIdentityResourceNamespace('test-name')
        validators.validate_pod_identity_resource_namespace(namespace)

    def test_missing_required_resource_name(self):
        namespace = PodIdentityResourceNamespace(None)

        with self.assertRaises(CLIError) as cm:
            validators.validate_pod_identity_resource_namespace(namespace)
        self.assertEqual(str(cm.exception), '--namespace is required')

class TestValidateKubernetesVersion(unittest.TestCase):

    def test_valid_full_kubernetes_version(self):
        kubernetes_version = "1.11.8"
        namespace = Namespace(kubernetes_version=kubernetes_version)

        validators.validate_k8s_version(namespace)

    def test_valid_alias_minor_version(self):
        kubernetes_version = "1.11"
        namespace = Namespace(kubernetes_version=kubernetes_version)

        validators.validate_k8s_version(namespace)

    def test_valid_empty_kubernetes_version(self):
        kubernetes_version = ""
        namespace = Namespace(kubernetes_version=kubernetes_version)

        validators.validate_k8s_version(namespace)

    def test_invalid_kubernetes_version(self):
        kubernetes_version = "1.2.3.4"

        namespace = Namespace(kubernetes_version=kubernetes_version)
        err = ("--kubernetes-version should be the full version number or alias minor version, "
               "such as \"1.7.12\" or \"1.7\"")

        with self.assertRaises(CLIError) as cm:
            validators.validate_k8s_version(namespace)
        self.assertEqual(str(cm.exception), err)

        kubernetes_version = "1."

        namespace = Namespace(kubernetes_version=kubernetes_version)

        with self.assertRaises(CLIError) as cm:
            validators.validate_k8s_version(namespace)
        self.assertEqual(str(cm.exception), err)

class HostGroupIDNamespace:

    def __init__(self, host_group_id):
        self.host_group_id = host_group_id

class TestValidateHostGroupID(unittest.TestCase):
    def test_invalid_host_group_id(self):
        invalid_host_group_id = "dummy group id"
        namespace = HostGroupIDNamespace(host_group_id=invalid_host_group_id)
        err = ("--host-group-id is not a valid Azure resource ID.")

        with self.assertRaises(CLIError) as cm:
            validators.validate_host_group_id(namespace)
        self.assertEqual(str(cm.exception), err)

class AzureKeyVaultKmsKeyIdNamespace:

    def __init__(self, azure_keyvault_kms_key_id):
        self.azure_keyvault_kms_key_id = azure_keyvault_kms_key_id

class TestValidateAzureKeyVaultKmsKeyId(unittest.TestCase):
    def test_invalid_azure_keyvault_kms_key_id_without_https(self):
        invalid_azure_keyvault_kms_key_id = "dummy key id"
        namespace = AzureKeyVaultKmsKeyIdNamespace(azure_keyvault_kms_key_id=invalid_azure_keyvault_kms_key_id)
        err = '--azure-keyvault-kms-key-id is not a valid Key Vault key ID. ' \
              'See https://docs.microsoft.com/en-us/azure/key-vault/general/about-keys-secrets-certificates#vault-name-and-object-name'

        with self.assertRaises(CLIError) as cm:
            validators.validate_azure_keyvault_kms_key_id(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_invalid_azure_keyvault_kms_key_id_without_key_version(self):
        invalid_azure_keyvault_kms_key_id = "https://fakekeyvault.vault.azure.net/keys/fakekeyname"
        namespace = AzureKeyVaultKmsKeyIdNamespace(azure_keyvault_kms_key_id=invalid_azure_keyvault_kms_key_id)
        err = '--azure-keyvault-kms-key-id is not a valid Key Vault key ID. ' \
              'See https://docs.microsoft.com/en-us/azure/key-vault/general/about-keys-secrets-certificates#vault-name-and-object-name'

        with self.assertRaises(CLIError) as cm:
            validators.validate_azure_keyvault_kms_key_id(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_invalid_azure_keyvault_kms_key_id_with_wrong_object_type(self):
        invalid_azure_keyvault_kms_key_id = "https://fakekeyvault.vault.azure.net/secrets/fakesecretname/fakesecretversion"
        namespace = AzureKeyVaultKmsKeyIdNamespace(azure_keyvault_kms_key_id=invalid_azure_keyvault_kms_key_id)
        err = '--azure-keyvault-kms-key-id is not a valid Key Vault key ID. ' \
              'See https://docs.microsoft.com/en-us/azure/key-vault/general/about-keys-secrets-certificates#vault-name-and-object-name'

        with self.assertRaises(CLIError) as cm:
            validators.validate_azure_keyvault_kms_key_id(namespace)
        self.assertEqual(str(cm.exception), err)


class AzureKeyVaultKmsKeyVaultResourceIdNamespace:

    def __init__(self, azure_keyvault_kms_key_vault_resource_id):
        self.azure_keyvault_kms_key_vault_resource_id = azure_keyvault_kms_key_vault_resource_id


class TestValidateAzureKeyVaultKmsKeyVaultResourceId(unittest.TestCase):
    def test_invalid_azure_keyvault_kms_key_vault_resource_id(self):
        invalid_azure_keyvault_kms_key_vault_resource_id = "invalid"
        namespace = AzureKeyVaultKmsKeyVaultResourceIdNamespace(azure_keyvault_kms_key_vault_resource_id=invalid_azure_keyvault_kms_key_vault_resource_id)
        err = '--azure-keyvault-kms-key-vault-resource-id is not a valid Azure resource ID.'

        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators.validate_azure_keyvault_kms_key_vault_resource_id(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_valid_azure_keyvault_kms_key_vault_resource_id(self):
        valid_azure_keyvault_kms_key_vault_resource_id = "/subscriptions/8ecadfc9-d1a3-4ea4-b844-0d9f87e4d7c8/resourceGroups/foo/providers/Microsoft.KeyVault/vaults/foo"
        namespace = AzureKeyVaultKmsKeyVaultResourceIdNamespace(azure_keyvault_kms_key_vault_resource_id=valid_azure_keyvault_kms_key_vault_resource_id)

        validators.validate_azure_keyvault_kms_key_vault_resource_id(namespace)


if __name__ == "__main__":
    unittest.main()
