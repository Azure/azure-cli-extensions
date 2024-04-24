# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from types import SimpleNamespace

import azext_aks_preview._validators as validators
import azext_aks_preview.azurecontainerstorage._consts as acstor_consts
import azext_aks_preview.azurecontainerstorage._validators as acstor_validator
from azext_aks_preview._consts import ADDONS
from azure.cli.core.azclierror import (
    ArgumentUsageError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
)
from azure.cli.core.util import CLIError


class TestValidateIPRanges(unittest.TestCase):
    def test_simultaneous_allow_and_disallow_with_spaces(self):
        api_server_authorized_ip_ranges = " 0.0.0.0/32 , 129.1.1.1.1 "
        namespace = Namespace(api_server_authorized_ip_ranges)
        err = (
            "Setting --api-server-authorized-ip-ranges to 0.0.0.0/32 is not allowed with other IP ranges."
            "Refer to https://aka.ms/aks/whitelist for more details"
        )

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
        api_server_authorized_ip_ranges = ""
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
    def __init__(
        self,
        api_server_authorized_ip_ranges=None,
        cluster_autoscaler_profile=None,
        kubernetes_version=None,
    ):
        self.api_server_authorized_ip_ranges = api_server_authorized_ip_ranges
        self.cluster_autoscaler_profile = cluster_autoscaler_profile
        self.kubernetes_version = kubernetes_version


class TestSubnetId(unittest.TestCase):
    def test_invalid_subnet_id(self):
        invalid_vnet_subnet_id = "dummy subnet id"
        err = "--vnet-subnet-id is not a valid Azure resource ID."

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


class CustomCATrustCertificatesNamespace:
    def __init__(self, os_type, custom_ca_trust_certificates):
        self.os_type = os_type
        self.custom_ca_trust_certificates = custom_ca_trust_certificates


class DisableWindowsOutboundNatNamespace:
    def __init__(self, os_type, disable_windows_outbound_nat):
        self.os_type = os_type
        self.disable_windows_outbound_nat = disable_windows_outbound_nat


class TestMaxSurge(unittest.TestCase):
    def test_valid_cases(self):
        valid = ["5", "33%", "1", "100%"]
        for v in valid:
            validators.validate_max_surge(MaxSurgeNamespace(v))

    def test_throws_on_string(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_max_surge(MaxSurgeNamespace("foobar"))
        self.assertTrue("int or percentage" in str(cm.exception), msg=str(cm.exception))

    def test_throws_on_negative(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_max_surge(MaxSurgeNamespace("-3"))
        self.assertTrue("positive" in str(cm.exception), msg=str(cm.exception))


class TestSpotMaxPrice(unittest.TestCase):
    def test_valid_cases(self):
        valid = [5, 5.12345, -1.0, 0.068, 0.071, 5.00000000]
        for v in valid:
            validators.validate_spot_max_price(SpotMaxPriceNamespace(v))

    def test_throws_if_more_than_5(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_spot_max_price(SpotMaxPriceNamespace(5.123456))
        self.assertTrue(
            "--spot_max_price can only include up to 5 decimal places"
            in str(cm.exception),
            msg=str(cm.exception),
        )

    def test_throws_if_non_valid_negative(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_spot_max_price(SpotMaxPriceNamespace(-2))
        self.assertTrue(
            "--spot_max_price can only be any decimal value greater than zero, or -1 which indicates"
            in str(cm.exception),
            msg=str(cm.exception),
        )
        with self.assertRaises(CLIError) as cm:
            validators.validate_spot_max_price(SpotMaxPriceNamespace(0))
        self.assertTrue(
            "--spot_max_price can only be any decimal value greater than zero, or -1 which indicates"
            in str(cm.exception),
            msg=str(cm.exception),
        )

    def test_throws_if_input_max_price_for_regular(self):
        ns = SpotMaxPriceNamespace(2)
        ns.priority = "Regular"
        with self.assertRaises(CLIError) as cm:
            validators.validate_spot_max_price(ns)
        self.assertTrue(
            "--spot_max_price can only be set when --priority is Spot"
            in str(cm.exception),
            msg=str(cm.exception),
        )


class TestMessageOfTheday(unittest.TestCase):
    def test_valid_cases(self):
        valid = ["foo", ""]
        for v in valid:
            validators.validate_message_of_the_day(MessageOfTheDayNamespace(v, "Linux"))

    def test_fail_if_os_type_windows(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_message_of_the_day(
                MessageOfTheDayNamespace("foo", "Windows")
            )
        self.assertTrue(
            "--message-of-the-day can only be set for linux nodepools"
            in str(cm.exception),
            msg=str(cm.exception),
        )

    def test_fail_if_os_type_invalid(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_message_of_the_day(
                MessageOfTheDayNamespace("foo", "invalid")
            )
        self.assertTrue(
            "--message-of-the-day can only be set for linux nodepools"
            in str(cm.exception),
            msg=str(cm.exception),
        )


class TestEnableCustomCATrust(unittest.TestCase):
    def test_pass_if_os_type_linux(self):
        validators.validate_enable_custom_ca_trust(
            EnableCustomCATrustNamespace("Linux", True)
        )

    def test_fail_if_os_type_windows(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_enable_custom_ca_trust(
                EnableCustomCATrustNamespace("Windows", True)
            )
        self.assertTrue(
            "--enable_custom_ca_trust can only be set for Linux nodepools"
            in str(cm.exception),
            msg=str(cm.exception),
        )

    def test_fail_if_os_type_invalid(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_enable_custom_ca_trust(
                EnableCustomCATrustNamespace("invalid", True)
            )
        self.assertTrue(
            "--enable_custom_ca_trust can only be set for Linux nodepools"
            in str(cm.exception),
            msg=str(cm.exception),
        )


class TestCustomCATrustCertificates(unittest.TestCase):
    def test_valid_cases(self):
        valid = ["foo", ""]
        for v in valid:
            validators.validate_custom_ca_trust_certificates(
                CustomCATrustCertificatesNamespace("Linux", v)
            )

    def test_fail_if_os_type_windows(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_custom_ca_trust_certificates(
                CustomCATrustCertificatesNamespace("Windows", "foo")
            )
        self.assertTrue(
            "--custom-ca-trust-certificates can only be set for linux nodepools"
            in str(cm.exception),
            msg=str(cm.exception),
        )

    def test_fail_if_os_type_invalid(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_custom_ca_trust_certificates(
                CustomCATrustCertificatesNamespace("invalid", "foo")
            )
        self.assertTrue(
            "--custom-ca-trust-certificates can only be set for linux nodepools"
            in str(cm.exception),
            msg=str(cm.exception),
        )


class TestDisableWindowsOutboundNAT(unittest.TestCase):
    def test_pass_if_os_type_windows(self):
        validators.validate_disable_windows_outbound_nat(
            DisableWindowsOutboundNatNamespace("Windows", True)
        )

    def test_fail_if_os_type_linux(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_disable_windows_outbound_nat(
                DisableWindowsOutboundNatNamespace("Linux", True)
            )
        self.assertTrue(
            "--disable-windows-outbound-nat can only be set for Windows nodepools"
            in str(cm.exception),
            msg=str(cm.exception),
        )

    def test_fail_if_os_type_invalid(self):
        with self.assertRaises(CLIError) as cm:
            validators.validate_disable_windows_outbound_nat(
                DisableWindowsOutboundNatNamespace("invalid", True)
            )
        self.assertTrue(
            "--disable-windows-outbound-nat can only be set for Windows nodepools"
            in str(cm.exception),
            msg=str(cm.exception),
        )


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
                first_addon[:midlen] + first_addon[midlen + 1:]
            )
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
        err = "--assign-identity is not a valid Azure resource ID."

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
        validator = validators.validate_pod_identity_resource_name(
            "identity_name", required=True
        )
        namespace = PodIdentityNamespace("test-name")
        validator(namespace)

    def test_missing_required_resource_name(self):
        validator = validators.validate_pod_identity_resource_name(
            "identity_name", required=True
        )
        namespace = PodIdentityNamespace(None)

        with self.assertRaises(CLIError) as cm:
            validator(namespace)
        self.assertEqual(str(cm.exception), "--name is required")


class PodIdentityResourceNamespace:
    def __init__(self, namespace):
        self.namespace = namespace


class TestValidatePodIdentityResourceNamespace(unittest.TestCase):
    def test_valid_required_resource_name(self):
        namespace = PodIdentityResourceNamespace("test-name")
        validators.validate_pod_identity_resource_namespace(namespace)

    def test_missing_required_resource_name(self):
        namespace = PodIdentityResourceNamespace(None)

        with self.assertRaises(CLIError) as cm:
            validators.validate_pod_identity_resource_namespace(namespace)
        self.assertEqual(str(cm.exception), "--namespace is required")


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
        err = (
            "--kubernetes-version should be the full version number or alias minor version, "
            'such as "1.7.12" or "1.7"'
        )

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
        err = "--host-group-id is not a valid Azure resource ID."

        with self.assertRaises(CLIError) as cm:
            validators.validate_host_group_id(namespace)
        self.assertEqual(str(cm.exception), err)


class AzureKeyVaultKmsKeyIdNamespace:
    def __init__(self, azure_keyvault_kms_key_id):
        self.azure_keyvault_kms_key_id = azure_keyvault_kms_key_id


class TestValidateAzureKeyVaultKmsKeyId(unittest.TestCase):
    def test_invalid_azure_keyvault_kms_key_id_without_https(self):
        invalid_azure_keyvault_kms_key_id = "dummy key id"
        namespace = AzureKeyVaultKmsKeyIdNamespace(
            azure_keyvault_kms_key_id=invalid_azure_keyvault_kms_key_id
        )
        err = (
            "--azure-keyvault-kms-key-id is not a valid Key Vault key ID. "
            "See https://docs.microsoft.com/en-us/azure/key-vault/general/about-keys-secrets-certificates#vault-name-and-object-name"
        )

        with self.assertRaises(CLIError) as cm:
            validators.validate_azure_keyvault_kms_key_id(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_invalid_azure_keyvault_kms_key_id_without_key_version(self):
        invalid_azure_keyvault_kms_key_id = (
            "https://fakekeyvault.vault.azure.net/keys/fakekeyname"
        )
        namespace = AzureKeyVaultKmsKeyIdNamespace(
            azure_keyvault_kms_key_id=invalid_azure_keyvault_kms_key_id
        )
        err = (
            "--azure-keyvault-kms-key-id is not a valid Key Vault key ID. "
            "See https://docs.microsoft.com/en-us/azure/key-vault/general/about-keys-secrets-certificates#vault-name-and-object-name"
        )

        with self.assertRaises(CLIError) as cm:
            validators.validate_azure_keyvault_kms_key_id(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_invalid_azure_keyvault_kms_key_id_with_wrong_object_type(self):
        invalid_azure_keyvault_kms_key_id = "https://fakekeyvault.vault.azure.net/secrets/fakesecretname/fakesecretversion"
        namespace = AzureKeyVaultKmsKeyIdNamespace(
            azure_keyvault_kms_key_id=invalid_azure_keyvault_kms_key_id
        )
        err = (
            "--azure-keyvault-kms-key-id is not a valid Key Vault key ID. "
            "See https://docs.microsoft.com/en-us/azure/key-vault/general/about-keys-secrets-certificates#vault-name-and-object-name"
        )

        with self.assertRaises(CLIError) as cm:
            validators.validate_azure_keyvault_kms_key_id(namespace)
        self.assertEqual(str(cm.exception), err)


class AzureKeyVaultKmsKeyVaultResourceIdNamespace:
    def __init__(self, azure_keyvault_kms_key_vault_resource_id):
        self.azure_keyvault_kms_key_vault_resource_id = (
            azure_keyvault_kms_key_vault_resource_id
        )


class TestValidateAzureKeyVaultKmsKeyVaultResourceId(unittest.TestCase):
    def test_invalid_azure_keyvault_kms_key_vault_resource_id(self):
        invalid_azure_keyvault_kms_key_vault_resource_id = "invalid"
        namespace = AzureKeyVaultKmsKeyVaultResourceIdNamespace(
            azure_keyvault_kms_key_vault_resource_id=invalid_azure_keyvault_kms_key_vault_resource_id
        )
        err = "--azure-keyvault-kms-key-vault-resource-id is not a valid Azure resource ID."

        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators.validate_azure_keyvault_kms_key_vault_resource_id(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_valid_azure_keyvault_kms_key_vault_resource_id(self):
        valid_azure_keyvault_kms_key_vault_resource_id = "/subscriptions/8ecadfc9-d1a3-4ea4-b844-0d9f87e4d7c8/resourceGroups/foo/providers/Microsoft.KeyVault/vaults/foo"
        namespace = AzureKeyVaultKmsKeyVaultResourceIdNamespace(
            azure_keyvault_kms_key_vault_resource_id=valid_azure_keyvault_kms_key_vault_resource_id
        )

        validators.validate_azure_keyvault_kms_key_vault_resource_id(namespace)


class TestValidateNodepoolName(unittest.TestCase):
    def test_invalid_nodepool_name_too_long(self):
        namespace = SimpleNamespace(
            **{
                "nodepool_name": "tooLongNodepoolName",
            }
        )
        with self.assertRaises(InvalidArgumentValueError):
            validators.validate_nodepool_name(namespace)

    def test_invalid_agent_pool_name_too_long(self):
        namespace = SimpleNamespace(
            **{
                "agent_pool_name": "tooLongNodepoolName",
            }
        )
        with self.assertRaises(InvalidArgumentValueError):
            validators.validate_agent_pool_name(namespace)

    def test_invalid_nodepool_name_not_alnum(self):
        namespace = SimpleNamespace(
            **{
                "nodepool_name": "invalid-np*",
            }
        )
        with self.assertRaises(InvalidArgumentValueError):
            validators.validate_nodepool_name(namespace)

    def test_invalid_agent_pool_name_not_alnum(self):
        namespace = SimpleNamespace(
            **{
                "agent_pool_name": "invalid-np*",
            }
        )
        with self.assertRaises(InvalidArgumentValueError):
            validators.validate_agent_pool_name(namespace)

    def test_valid_nodepool_name(self):
        namespace = SimpleNamespace(
            **{
                "nodepool_name": "np100",
            }
        )
        validators.validate_nodepool_name(namespace)

    def test_valid_agent_pool_name(self):
        namespace = SimpleNamespace(
            **{
                "agent_pool_name": "np100",
            }
        )
        validators.validate_agent_pool_name(namespace)


class TestValidateAllowedHostPorts(unittest.TestCase):
    def test_invalid_allowed_host_ports(self):
        namespace = SimpleNamespace(
            **{
                "allowed_host_ports": "80,443,8080",
            }
        )
        with self.assertRaises(InvalidArgumentValueError):
            validators.validate_allowed_host_ports(namespace)

    def test_valid_allowed_host_ports(self):
        namespace = SimpleNamespace(
            **{
                "allowed_host_ports": "80/tcp,443/tcp,8080-8090/tcp,53/udp",
            }
        )
        validators.validate_allowed_host_ports(namespace)


class TestValidateApplicationSecurityGroups(unittest.TestCase):
    def test_invalid_application_security_groups(self):
        namespace = SimpleNamespace(
            **{
                "asg_ids": "invalid",
            }
        )
        with self.assertRaises(InvalidArgumentValueError):
            validators.validate_application_security_groups(namespace)

    def test_empty_application_security_groups(self):
        namespace = SimpleNamespace(
            **{
                "asg_ids": "",
            }
        )
        validators.validate_application_security_groups(namespace)

    def test_multiple_application_security_groups(self):
        asg_ids = ",".join(
            [
                "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg1/providers/Microsoft.Network/applicationSecurityGroups/asg1",
                "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg2/providers/Microsoft.Network/applicationSecurityGroups/asg2",
            ]
        )
        namespace = SimpleNamespace(
            **{
                "asg_ids": asg_ids,
            }
        )
        validators.validate_application_security_groups(namespace)


class MaintenanceWindowNameSpace:
    def __init__(self, utc_offset=None, start_date=None, start_time=None):
        self.utc_offset = utc_offset
        self.start_date = start_date
        self.start_time = start_time


class TestValidateMaintenanceWindow(unittest.TestCase):
    def test_invalid_utc_offset(self):
        namespace = MaintenanceWindowNameSpace(utc_offset="5:00")
        err = '--utc-offset must be in format: "+/-HH:mm". For example, "+05:30" and "-12:00".'
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators.validate_utc_offset(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_valid_utc_offset(self):
        namespace = MaintenanceWindowNameSpace(utc_offset="+05:00")
        validators.validate_utc_offset(namespace)

    def test_invalid_start_date(self):
        namespace = MaintenanceWindowNameSpace(start_date="2023/01/01")
        err = '--start-date must be in format: "yyyy-MM-dd". For example, "2023-01-01".'
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators.validate_start_date(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_valid_start_datet(self):
        namespace = MaintenanceWindowNameSpace(start_date="2023-01-01")
        validators.validate_start_date(namespace)

    def test_invalid_start_time(self):
        namespace = MaintenanceWindowNameSpace(start_time="3am")
        err = (
            '--start-time must be in format "HH:mm". For example, "09:30" and "17:00".'
        )
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validators.validate_start_time(namespace)
        self.assertEqual(str(cm.exception), err)

    def test_valid_start_time(self):
        namespace = MaintenanceWindowNameSpace(start_date="00:30")
        validators.validate_start_time(namespace)


class TestValidateDisableAzureContainerStorage(unittest.TestCase):
    def test_disable_when_extension_not_installed(self):
        is_extension_installed = False
        err = (
            "Invalid usage of --disable-azure-container-storage. "
            "Azure Container Storage is not enabled in the cluster."
        )
        with self.assertRaises(InvalidArgumentValueError) as cm:
            acstor_validator.validate_disable_azure_container_storage_params(
                None, None, None, None, None, None, is_extension_installed, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_disable_flag_with_storage_pool_name(self):
        storage_pool_name = "pool-name"
        err = (
            "Conflicting flags. Cannot define --storage-pool-name value "
            "when --disable-azure-container-storage is set."
        )
        with self.assertRaises(MutuallyExclusiveArgumentError) as cm:
            acstor_validator.validate_disable_azure_container_storage_params(
                None, storage_pool_name, None, None, None, None, True, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_disable_flag_with_storage_pool_sku(self):
        storage_pool_sku = acstor_consts.CONST_STORAGE_POOL_SKU_PREMIUM_LRS
        err = (
            "Conflicting flags. Cannot define --storage-pool-sku value "
            "when --disable-azure-container-storage is set."
        )
        with self.assertRaises(MutuallyExclusiveArgumentError) as cm:
            acstor_validator.validate_disable_azure_container_storage_params(
                None, None, storage_pool_sku, None, None, None, True, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_disable_flag_with_storage_pool_size(self):
        storage_pool_size = "5Gi"
        err = (
            "Conflicting flags. Cannot define --storage-pool-size value "
            "when --disable-azure-container-storage is set."
        )
        with self.assertRaises(MutuallyExclusiveArgumentError) as cm:
            acstor_validator.validate_disable_azure_container_storage_params(
                None, None, None, None, storage_pool_size, None, True, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_disable_flag_with_storage_pool_option_not_ephemeralDisk(self):
        storage_pool_option = acstor_consts.CONST_STORAGE_POOL_OPTION_NVME
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_AZURE_DISK
        err = (
            "Cannot define --storage-pool-option value when "
            "--disable-azure-container-storage is not set to ephemeralDisk."
        )
        with self.assertRaises(ArgumentUsageError) as cm:
            acstor_validator.validate_disable_azure_container_storage_params(
                storage_pool_type, None, None, storage_pool_option, None, None, True, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_disable_flag_with_storage_pool_option_not_set_both_ephemeralDisk_enabled(self):
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK
        err = (
            "Value of --storage-pool-option must be defined since ephemeralDisk of both "
            "the types: NVMe and Temp are enabled in the cluster."
        )
        with self.assertRaises(RequiredArgumentMissingError) as cm:
            acstor_validator.validate_disable_azure_container_storage_params(
                storage_pool_type, None, None, None, None, None, True, False, False, True, True
            )
        self.assertEqual(str(cm.exception), err)

    def test_disable_flag_with_nodepool_list(self):
        nodepool_list = "test,test1"
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_AZURE_DISK
        err = (
            "Conflicting flags. Cannot define --azure-container-storage-nodepools value "
            "when --disable-azure-container-storage is set."
        )
        with self.assertRaises(MutuallyExclusiveArgumentError) as cm:
            acstor_validator.validate_disable_azure_container_storage_params(
                storage_pool_type, None, None, None, None, nodepool_list, True, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_disable_type_when_not_enabled(self):
        pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_AZURE_DISK
        is_azureDisk_enabled = False
        err = (
            "Invalid --disable-azure-container-storage value. "
            "Azure Container Storage is not enabled for storagepool "
            "type {0} in the cluster.".format(pool_type)
        )
        with self.assertRaises(ArgumentUsageError) as cm:
            acstor_validator.validate_disable_azure_container_storage_params(
                pool_type, None, None, None, None, None, True, is_azureDisk_enabled, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_disable_only_storage_pool_installed(self):
        pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_AZURE_DISK
        err = (
            "Since azureDisk is the only storagepool type enabled for Azure Container Storage, "
            "disabling the storagepool type will lead to disabling Azure Container Storage from the cluster. "
            "To disable Azure Container Storage, set --disable-azure-container-storage to all."
        )
        with self.assertRaises(ArgumentUsageError) as cm:
            acstor_validator.validate_disable_azure_container_storage_params(
                pool_type, None, None, None, None, None, True, True, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_disable_only_storagepool_type_enabled(self):
        pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_AZURE_DISK
        is_azureDisk_enabled = True
        err = (
            "Since azureDisk is the only storagepool type enabled for Azure Container Storage, "
            "disabling the storagepool type will lead to disabling Azure Container Storage from the cluster. "
            "To disable Azure Container Storage, set --disable-azure-container-storage to all."
        )
        with self.assertRaises(ArgumentUsageError) as cm:
            acstor_validator.validate_disable_azure_container_storage_params(
                pool_type, None, None, None, None, None, True, is_azureDisk_enabled, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_valid_disable(self):
        pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_ELASTIC_SAN
        acstor_validator.validate_disable_azure_container_storage_params(
            pool_type, None, None, None, None, None, True, False, True, True, False
        )


class TestValidateEnableAzureContainerStorage(unittest.TestCase):
    def test_enable_with_invalid_storage_pool_name(self):
        storage_pool_name = "my_test_pool"
        err = (
            "Invalid --storage-pool-name value. "
            "Accepted values are lowercase alphanumeric characters, "
            "'-' or '.', and must start and end with an alphanumeric character."
        )
        with self.assertRaises(InvalidArgumentValueError) as cm:
            acstor_validator.validate_enable_azure_container_storage_params(
                None, storage_pool_name, None, None, None, None, None, False, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_enable_with_sku_and_ephemeral_disk_pool(self):
        storage_pool_name = "valid-name"
        storage_pool_sku = acstor_consts.CONST_STORAGE_POOL_SKU_PREMIUM_LRS
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK
        err = "Cannot set --storage-pool-sku when --enable-azure-container-storage is ephemeralDisk."
        with self.assertRaises(ArgumentUsageError) as cm:
            acstor_validator.validate_enable_azure_container_storage_params(
                storage_pool_type, storage_pool_name, storage_pool_sku, None, None, None, None, False, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_enable_with_sku_and_elastic_san_pool(self):
        storage_pool_name = "valid-name"
        storage_pool_sku = acstor_consts.CONST_STORAGE_POOL_SKU_PREMIUMV2_LRS
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_ELASTIC_SAN
        supported_skus = (
            acstor_consts.CONST_STORAGE_POOL_SKU_PREMIUM_LRS
            + ", "
            + acstor_consts.CONST_STORAGE_POOL_SKU_PREMIUM_ZRS
        )
        err = (
            "Invalid --storage-pool-sku value. "
            "Supported value for --storage-pool-sku are {0} "
            "when --enable-azure-container-storage is set to elasticSan.".format(
                supported_skus
            )
        )
        with self.assertRaises(ArgumentUsageError) as cm:
            acstor_validator.validate_enable_azure_container_storage_params(
                storage_pool_type, storage_pool_name, storage_pool_sku, None, None, None, None, False, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_enable_with_option_and_non_ephemeral_disk_pool(self):
        storage_pool_name = "valid-name"
        storage_pool_option = acstor_consts.CONST_STORAGE_POOL_OPTION_NVME
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_AZURE_DISK
        err = "Cannot set --storage-pool-option when --enable-azure-container-storage is not ephemeralDisk."
        with self.assertRaises(ArgumentUsageError) as cm:
            acstor_validator.validate_enable_azure_container_storage_params(
                storage_pool_type, storage_pool_name, None, storage_pool_option, None, None, None, False, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_enable_with_option_all_and_ephemeral_disk_pool(self):
        storage_pool_name = "valid-name"
        storage_pool_option = acstor_consts.CONST_ACSTOR_ALL
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK
        err = "Cannot set --storage-pool-option value as all when --enable-azure-container-storage is set."
        with self.assertRaises(InvalidArgumentValueError) as cm:
            acstor_validator.validate_enable_azure_container_storage_params(
                storage_pool_type, storage_pool_name, None, storage_pool_option, None, None, None, False, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_enable_with_invalid_storage_pool_size(self):
        storage_pool_name = "valid-name"
        storage_pool_size = "5"
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_AZURE_DISK
        err = "Value for --storage-pool-size should be defined with size followed by Gi or Ti e.g. 512Gi or 2Ti."
        with self.assertRaises(ArgumentUsageError) as cm:
            acstor_validator.validate_enable_azure_container_storage_params(
                storage_pool_type, storage_pool_name, None, None, storage_pool_size, None, None, False, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_enable_with_invalid_size_for_esan_storage_pool(self):
        storage_pool_name = "valid-name"
        storage_pool_size = "512Gi"
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_ELASTIC_SAN
        err = "Value for --storage-pool-size must be at least 1Ti when --enable-azure-container-storage is elasticSan."
        with self.assertRaises(ArgumentUsageError) as cm:
            acstor_validator.validate_enable_azure_container_storage_params(
                storage_pool_type, storage_pool_name, None, None, storage_pool_size, None, None, False, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_invalid_comma_separated_nodepool_list(self):
        nodepool_list = "pool1, 1pool"
        storage_pool_name = "valid-name"
        storage_pool_size = "5Ti"
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_AZURE_DISK
        err = (
            "Invalid --azure-container-storage-nodepools value. "
            "Accepted value is a comma separated string of valid node pool "
            "names without any spaces.\nA valid node pool name may only contain lowercase "
            "alphanumeric characters and must begin with a lowercase letter."
        )
        with self.assertRaises(InvalidArgumentValueError) as cm:
            acstor_validator.validate_enable_azure_container_storage_params(
                storage_pool_type, storage_pool_name, None, None, storage_pool_size, nodepool_list, None, False, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_missing_nodepool_from_cluster_nodepool_list_single(self):
        storage_pool_name = "valid-name"
        storage_pool_size = "5Ti"
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK
        storage_pool_option = acstor_consts.CONST_STORAGE_POOL_OPTION_NVME
        nodepool_list = "pool1"
        agentpools = [{"name": "nodepool1", "vm_size": "Standard_L8s_v3"}]
        err = (
            "Node pool: pool1 not found. Please provide a comma separated "
            "string of existing node pool names in --azure-container-storage-nodepools."
            "\nNode pool available in the cluster is: nodepool1."
            "\nAborting installation of Azure Container Storage."
        )
        with self.assertRaises(InvalidArgumentValueError) as cm:
            acstor_validator.validate_enable_azure_container_storage_params(
                storage_pool_type, storage_pool_name, None, storage_pool_option, storage_pool_size, nodepool_list, agentpools, False, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_missing_nodepool_from_cluster_nodepool_list_multiple(self):
        storage_pool_name = "valid-name"
        storage_pool_size = "5Ti"
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK
        storage_pool_option = acstor_consts.CONST_STORAGE_POOL_OPTION_SSD
        nodepool_list = "pool1,pool2"
        agentpools = [{"name": "nodepool1"}, {"name": "nodepool2"}]
        err = (
            "Node pool: pool1 not found. Please provide a comma separated "
            "string of existing node pool names in --azure-container-storage-nodepools."
            "\nNode pools available in the cluster are: nodepool1, nodepool2."
            "\nAborting installation of Azure Container Storage."
        )
        with self.assertRaises(InvalidArgumentValueError) as cm:
            acstor_validator.validate_enable_azure_container_storage_params(
                storage_pool_type, storage_pool_name, None, storage_pool_option, storage_pool_size, nodepool_list, agentpools, False, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_valid_enable_for_azure_disk_pool(self):
        storage_pool_name = "valid-name"
        storage_pool_size = "5Ti"
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_AZURE_DISK
        storage_pool_sku = acstor_consts.CONST_STORAGE_POOL_SKU_PREMIUM_LRS
        nodepool_list = "nodepool1,nodepool2"
        agentpools = [{"name": "nodepool1"}, {"name": "nodepool2"}]
        acstor_validator.validate_enable_azure_container_storage_params(
            storage_pool_type, storage_pool_name, storage_pool_sku, None, storage_pool_size, nodepool_list, agentpools, False, False, False, False, False
        )

    def test_valid_enable_for_ephemeral_disk_pool(self):
        storage_pool_name = "valid-name"
        storage_pool_size = "5Ti"
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK
        storage_pool_option = acstor_consts.CONST_STORAGE_POOL_OPTION_NVME
        nodepool_list = "nodepool1"
        agentpools = [{"name": "nodepool1", "vm_size": "Standard_L8s_v3"}, {"name": "nodepool2", "vm_size": "Standard_L8s_v3"}]
        acstor_validator.validate_enable_azure_container_storage_params(
            storage_pool_type, storage_pool_name, None, storage_pool_option, storage_pool_size, nodepool_list, agentpools, False, False, False, False, False
        )

    def test_extension_installed_nodepool_list_defined(self):
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_AZURE_DISK
        nodepool_list = "nodepool1,nodepool2"
        err = (
            "Cannot set --azure-container-storage-nodepools while using "
            "--enable-azure-container-storage to enable a type of storagepool "
            "in a cluster where Azure Container Storage is already installed."
        )
        with self.assertRaises(ArgumentUsageError) as cm:
            acstor_validator.validate_enable_azure_container_storage_params(
                storage_pool_type, None, None, None, None, nodepool_list, None, True, False, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_extension_installed_storagepool_type_installed(self):
        storage_pool_name = "valid-name"
        storage_pool_size = "5Ti"
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_AZURE_DISK
        storage_pool_sku = acstor_consts.CONST_STORAGE_POOL_SKU_PREMIUM_LRS
        agentpools = [{"name": "nodepool1", "node_labels": {"acstor.azure.com/io-engine": "acstor"}}, {"name": "nodepool2"}]
        err = (
            "Invalid --enable-azure-container-storage value. "
            "Azure Container Storage is already enabled for storagepool type "
            "{0} in the cluster.".format(storage_pool_type)
        )
        with self.assertRaises(ArgumentUsageError) as cm:
            acstor_validator.validate_enable_azure_container_storage_params(
                storage_pool_type, storage_pool_name, storage_pool_sku, None, storage_pool_size, None, agentpools, True, True, False, False, False
            )
        self.assertEqual(str(cm.exception), err)

    def test_valid_cluster_update(self):
        storage_pool_name = "valid-name"
        storage_pool_size = "5Ti"
        storage_pool_type = acstor_consts.CONST_STORAGE_POOL_TYPE_AZURE_DISK
        storage_pool_sku = acstor_consts.CONST_STORAGE_POOL_SKU_PREMIUM_LRS
        agentpools = [{"name": "nodepool1", "node_labels": {"acstor.azure.com/io-engine": "acstor"}}, {"name": "nodepool2"}]
        acstor_validator.validate_enable_azure_container_storage_params(
            storage_pool_type, storage_pool_name, storage_pool_sku, None, storage_pool_size, None, agentpools, True, False, False, False, False
        )


class TestValidateCustomEndpoints(unittest.TestCase):
    def test_empty_custom_endpoints(self):
        namespace = SimpleNamespace(
            **{
                "custom_endpoints": [],
            }
        )
        validators.validate_custom_endpoints(namespace)

    def test_invalid_custom_endpoints(self):
        namespace = SimpleNamespace(
            **{
                "custom_endpoints": ["https://example.com"],
            }
        )
        with self.assertRaises(InvalidArgumentValueError):
            validators.validate_custom_endpoints(namespace)

    def test_valid_custom_endpoints(self):
        namespace = SimpleNamespace(
            **{
                "custom_endpoints": ["example.com", "microsoft.com"],
            }
        )
        validators.validate_custom_endpoints(namespace)


if __name__ == "__main__":
    unittest.main()
