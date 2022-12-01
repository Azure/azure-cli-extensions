# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.core.util import CLIError
from azext_aem.custom import EnhancedMonitoring  # pylint: disable=unused-import
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
import os
import sys
# pylint: disable=unused-argument,too-few-public-methods


class TestScope(object):
    GROUP_SCOPE = "group"
    RESOURCE_SCOPE = "resource"
    group_called = False
    res_called = False

    def func_scope_true(self, scope, role_definition_id):
        self.group_called = self.group_called or (scope == self.GROUP_SCOPE)
        self.res_called = self.res_called or (scope == self.RESOURCE_SCOPE)
        return True

    def func_scope_false(self, scope, role_definition_id):
        self.group_called = self.group_called or (scope == self.GROUP_SCOPE)
        self.res_called = self.res_called or (scope == self.RESOURCE_SCOPE)
        return False

    def func_scope_equal(self, scope, role_definition_id):
        self.group_called = self.group_called or (scope == self.GROUP_SCOPE)
        self.res_called = self.res_called or (scope == self.RESOURCE_SCOPE)
        return scope == self.RESOURCE_SCOPE


class VMAEM(ScenarioTest):

    ERR_EXT_NOT_INSTALLED_VERIFY = "VM Extension for SAP was not installed"
    ERR_EXT_NOT_INSTALLED_DELETE = "VM Extension for SAP is not installed"
    ERR_EXT_UPGRADE = ("Migration from the old extension to the new one is not supported. "
                       "Please remove the old extension first.")
    ERR_EXT_CONFIG_NOT_OK = "Configuration Not OK."

    IDENT_USER_SYSTEM_ASSIGNED = 'SystemAssigned, UserAssigned'
    IDENT_SYSTEM_ASSIGNED = 'SystemAssigned'
    IDENT_USER_ASSIGNED = 'UserAssigned'

    def _assert_new_extension(self, identity_type):
        new_publisher = "Microsoft.AzureCAT.AzureEnhancedMonitoring"
        new_type_win = "MonitorX64Windows"
        new_type_lnx = "MonitorX64Linux"

        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        extensions = self.cmd('vm extension list -g {rg} --vm-name {vm}').get_output_in_json()

        self.assertIsNotNone(extensions, msg="New extension is not installed")
        self.assertEqual(len(extensions), 1, msg="VM Extensions count does not equal 1")

        vm_identity = vm['identity']['type']
        self.assertEqual(vm_identity, identity_type, msg=f'VM does not have the expected identity. Expected: {identity_type} Actual: {vm_identity}')

        self.assertEqual(extensions[0]['publisher'], new_publisher)
        new_type = (extensions[0]['typePropertiesType'] == new_type_win) or (extensions[0]['typePropertiesType'] == new_type_lnx)
        self.assertTrue(new_type, msg=f'Extension is not of type {new_type_win} nor {new_type_lnx}')
        self.assertEqual(len(vm['resources']), 1, msg="VM Extensions count does not equal 1")

        self.cmd('vm aem verify -g {rg} -n {vm}')

    def _assert_old_extension(self):
        old_publisher_win = "Microsoft.AzureCAT.AzureEnhancedMonitoring"
        old_publisher_lnx = "Microsoft.OSTCExtensions"
        old_type_win = "AzureCATExtensionHandler"
        old_type_lnx = "AzureEnhancedMonitorForLinux"

        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        extensions = self.cmd('vm extension list -g {rg} --vm-name {vm}').get_output_in_json()

        self.assertIsNotNone(extensions, msg="Old extension is not installed")
        self.assertEqual(len(extensions), 1, msg="VM Extensions count does not equal 1")

        old_type = (extensions[0]['typePropertiesType'] == old_type_win) or (extensions[0]['typePropertiesType'] == old_type_lnx)
        old_publisher = (extensions[0]['publisher'] == old_publisher_win) or (extensions[0]['publisher'] == old_publisher_lnx)

        self.assertTrue(old_type, msg=f'Extension is not of type {old_type_win} nor {old_type_lnx}')
        self.assertTrue(old_publisher, msg=f'Extension Publisher is not {old_publisher_win} nor {old_publisher_lnx}')
        self.assertEqual(len(vm['resources']), 1, msg="VM Extensions count does not equal 1")

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer()
    def test_WithUserAssignedIdentity(self, resource_group):
        os.environ["AZURE_CLI_AEM_TEST"] = "test_WithUserAssignedIdentity"

        vm_name = 'vm1'
        ident_name = 'ident1'
        self.kwargs.update({
            'vm': vm_name,
            'ident': ident_name,
        })
        self.cmd('vm create -g {rg} -n {vm} --os-disk-name os-disk --image win2016datacenter --admin-username myadmin --admin-password thisisaTest!@')
        self.cmd('identity create -g {rg} -n {ident}')

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem delete --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_DELETE)
        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()

        self.assertIsNone(vm['resources'], msg="VM Extensions installed but should be empty")
        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_VERIFY)

        self.cmd('vm identity assign -g {rg} -n {vm} --identities {ident}')
        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        vm_identity = vm['identity']['type']
        self.assertEqual(vm_identity, self.IDENT_USER_ASSIGNED, msg=f'VM does not have the expected identity. Expected: {self.IDENT_USER_ASSIGNED} Actual: {vm_identity}')

        self.cmd('vm aem set --verbose -g {rg} -n {vm} --install-new-extension --set-access-to-individual-resources')

        self._assert_new_extension(self.IDENT_USER_SYSTEM_ASSIGNED)

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer()
    def test_WithoutIdentity(self, resource_group):
        os.environ["AZURE_CLI_AEM_TEST"] = "test_WithoutIdentity"

        vm_name = 'vm1'
        self.kwargs.update({
            'vm': vm_name
        })

        self.cmd('vm create -g {rg} -n {vm} --os-disk-name os-disk --image RedHat:RHEL:8.2:latest --generate-ssh-keys')

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem delete --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_DELETE)

        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        self.assertIsNone(vm['resources'], msg="VM Extensions installed but should be empty")

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_VERIFY, msg="Test of extension was positiv but should have failed")

        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        self.assertIsNone(vm['identity'], msg="VM still has an identity")

        self.cmd('vm aem set --verbose -g {rg} -n {vm} --install-new-extension')

        self._assert_new_extension(self.IDENT_SYSTEM_ASSIGNED)

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer()
    def test_WithSystemAssignedIdentity(self, resource_group):
        os.environ["AZURE_CLI_AEM_TEST"] = "test_WithSystemAssignedIdentity"

        vm_name = 'vm1'
        self.kwargs.update({
            'vm': vm_name
        })

        self.cmd('vm create -g {rg} -n {vm} --os-disk-name os-disk --image RedHat:RHEL:7.8:latest --generate-ssh-keys')

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem delete --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_DELETE)

        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        if vm['identity'] is None or (not vm['identity']['type'] == self.IDENT_SYSTEM_ASSIGNED):
            self.cmd('vm identity assign -g {rg} -n {vm}')
            vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()

        vm_identity = vm['identity']['type']
        self.assertEqual(vm_identity, self.IDENT_SYSTEM_ASSIGNED, msg=f'VM does not have the expected identity. Expected: {self.IDENT_SYSTEM_ASSIGNED} Actual: {vm_identity}')

        self.assertIsNone(vm['resources'], msg="VM Extensions installed but should be empty")
        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_VERIFY, msg="Test of extension was positiv but should have failed")

        self.cmd('vm aem set --verbose -g {rg} -n {vm} --install-new-extension')

        self._assert_new_extension(self.IDENT_SYSTEM_ASSIGNED)

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer()
    def test_ExtensionReinstall(self, resource_group):
        os.environ["AZURE_CLI_AEM_TEST"] = "test_ExtensionReinstall"

        vm_name = 'vm1'
        self.kwargs.update({
            'vm': vm_name
        })

        self.cmd('vm create -g {rg} -n {vm} --os-disk-name os-disk --image SUSE:sles-15-sp2:gen2:latest --generate-ssh-keys')

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem delete --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_DELETE)

        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        self.assertIsNone(vm['resources'], msg="VM Extensions installed but should be empty")

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_VERIFY, msg="Test of extension was positiv but should have failed")

        self.cmd('vm aem set --verbose -g {rg} -n {vm} --install-new-extension')

        self._assert_new_extension(self.IDENT_SYSTEM_ASSIGNED)

        self.cmd('vm aem set --verbose -g {rg} -n {vm} --install-new-extension')

        self._assert_new_extension(self.IDENT_SYSTEM_ASSIGNED)

    @ResourceGroupPreparer()
    def test_OldExtensionReinstall(self, resource_group):
        os.environ["AZURE_CLI_AEM_TEST"] = "test_OldExtensionReinstall"

        vm_name = 'vm1'
        self.kwargs.update({
            'vm': vm_name
        })

        self.cmd('vm create -g {rg} -n {vm} --os-disk-name os-disk --image win2016datacenter --admin-username myadmin --admin-password thisisaTest!@')

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem delete --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_DELETE)

        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        self.assertIsNone(vm['resources'], msg="VM Extensions installed but should be empty")

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_VERIFY, msg="Test of extension was positiv but should have failed")

        self.cmd('vm aem set --verbose -g {rg} -n {vm}')

        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        self._assert_old_extension()

        self.cmd('vm aem set --verbose -g {rg} -n {vm}')

        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        self._assert_old_extension()

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer()
    def test_ExtensionDowngrade(self, resource_group):
        os.environ["AZURE_CLI_AEM_TEST"] = "test_ExtensionDowngrade"

        vm_name = 'vm1'
        self.kwargs.update({
            'vm': vm_name
        })

        self.cmd('vm create -g {rg} -n {vm} --os-disk-name os-disk --image SUSE:sles-12-sp5:gen2:latest --generate-ssh-keys')

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem delete --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_DELETE)

        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        self.assertIsNone(vm['resources'], msg="VM Extensions installed but should be empty")

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_VERIFY, msg="Test of extension was positiv but should have failed")

        self.cmd('vm aem set --verbose -g {rg} -n {vm} --install-new-extension')

        self._assert_new_extension(self.IDENT_SYSTEM_ASSIGNED)

        self.cmd('vm aem set --verbose -g {rg} -n {vm}')

        self._assert_new_extension(self.IDENT_SYSTEM_ASSIGNED)

    @ResourceGroupPreparer()
    def test_ExtensionUpgrade(self, resource_group):
        os.environ["AZURE_CLI_AEM_TEST"] = "test_ExtensionUpgrade"

        vm_name = 'vm1'
        self.kwargs.update({
            'vm': vm_name
        })

        self.cmd('vm create -g {rg} -n {vm} --os-disk-name os-disk --image win2016datacenter --admin-username myadmin --admin-password thisisaTest!@')

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem delete --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_DELETE)

        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        self.assertIsNone(vm['resources'], msg="VM Extensions installed but should be empty")

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_VERIFY, msg="Test of extension was positiv but should have failed")

        self.cmd('vm aem set --verbose -g {rg} -n {vm}')

        self._assert_old_extension()

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem set --verbose -g {rg} -n {vm} --install-new-extension')
        self.assertEqual(str(cm.exception), self.ERR_EXT_UPGRADE, msg="Downgrade of extension should have failed!")

        self._assert_old_extension()

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer()
    def test_NewExtensionDiskAdd(self, resource_group):
        os.environ["AZURE_CLI_AEM_TEST"] = "test_NewExtensionDiskAdd"

        vm_name = 'vm1'
        self.kwargs.update({
            'vm': vm_name
        })

        self.cmd('vm create -g {rg} -n {vm} --os-disk-name os-disk --image win2016datacenter --admin-username myadmin --admin-password thisisaTest!@')

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem delete --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_DELETE)

        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        self.assertIsNone(vm['resources'], msg="VM Extensions installed but should be empty")

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_VERIFY, msg="Test of extension was positiv but should have failed")

        self.cmd('vm aem set --verbose -g {rg} -n {vm} --install-new-extension --set-access-to-individual-resources')
        self._assert_new_extension(self.IDENT_SYSTEM_ASSIGNED)

        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        self.cmd('vm disk attach -g {rg} --vm-name {vm} --name disk_name --new')

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_CONFIG_NOT_OK, msg="Test of extension was positiv but should have failed because of missing permissions to the added data disk")

        self.cmd('vm aem set --verbose -g {rg} -n {vm} --install-new-extension --set-access-to-individual-resources')
        self._assert_new_extension(self.IDENT_SYSTEM_ASSIGNED)

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer()
    def test_NewExtensionMultiNic(self, resource_group):
        os.environ["AZURE_CLI_AEM_TEST"] = "test_NewExtensionMultiNic"

        vm_name = 'vm1'
        nic_name_1 = 'nic1'
        nic_name_2 = 'nic2'
        vnet_name = 'vnet1'
        subnet_name_1 = 'frontend1'
        subnet_name_2 = 'frontend2'
        nsg_name = 'nsg1'
        self.kwargs.update({
            'vm': vm_name,
            'vnet': vnet_name,
            'subnet1': subnet_name_1,
            'subnet2': subnet_name_2,
            'nsg': nsg_name,
            'nic1': nic_name_1,
            'nic2': nic_name_2
        })

        self.cmd('network vnet create -g {rg} --name {vnet} --address-prefix 10.0.0.0/16 --subnet-name {subnet1} --subnet-prefix 10.0.1.0/24')
        self.cmd('network vnet subnet create -g {rg} --vnet-name {vnet} --name {subnet2} --address-prefix 10.0.2.0/24')
        self.cmd('network nsg create -g {rg} --name {nsg}')
        self.cmd('network nic create -g {rg} --name {nic1} --vnet-name {vnet} --subnet {subnet1} --network-security-group {nsg}')
        self.cmd('network nic create -g {rg} --name {nic2} --vnet-name {vnet} --subnet {subnet2} --network-security-group {nsg}')
        self.cmd('vm create -g {rg} --name {vm} --os-disk-name os-disk --image SUSE:sles-12-sp5:gen2:latest --generate-ssh-keys --nics {nic1} {nic2}')

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem delete --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_DELETE)

        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        self.assertIsNone(vm['resources'], msg="VM Extensions installed but should be empty")

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_VERIFY, msg="Test of extension was positiv but should have failed")

        self.cmd('vm aem set --verbose -g {rg} -n {vm} --install-new-extension --set-access-to-individual-resources')
        self._assert_new_extension(self.IDENT_SYSTEM_ASSIGNED)
        self.cmd('vm aem verify --verbose -g {rg} -n {vm}')

        self.cmd('vm aem delete --verbose -g {rg} -n {vm}')

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_VERIFY, msg="Test of extension was positiv but should have failed")

        self.cmd('vm aem set --verbose -g {rg} -n {vm}')
        self._assert_old_extension()

        self.cmd('vm aem delete --verbose -g {rg} -n {vm}')

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_VERIFY, msg="Test of extension was positiv but should have failed")

    @ResourceGroupPreparer(location='westus2')
    @AllowLargeResponse(size_kb=100024)
    def test_NewExtensionUltraDisk(self, resource_group):
        os.environ["AZURE_CLI_AEM_TEST"] = "test_NewExtensionUltraDisk"

        vm_name = 'vm1'
        self.kwargs.update({
            'vm': vm_name
        })

        self.cmd('vm create -g {rg} -n {vm} --os-disk-name os-disk -z 1 --size Standard_E2s_v3 --image win2016datacenter --admin-username myadmin --admin-password thisisaTest1234 --ultra-ssd-enabled')

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem delete --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_DELETE)

        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        self.assertIsNone(vm['resources'], msg="VM Extensions installed but should be empty")

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_VERIFY, msg="Test of extension was positiv but should have failed")

        self.cmd('vm aem set --verbose -g {rg} -n {vm} --install-new-extension --set-access-to-individual-resources')
        self._assert_new_extension(self.IDENT_SYSTEM_ASSIGNED)

        vm = self.cmd('vm show -g {rg} -n {vm}').get_output_in_json()
        self.cmd('vm disk attach -g {rg} --vm-name {vm} --name disk_name --sku UltraSSD_LRS --new')

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), self.ERR_EXT_CONFIG_NOT_OK, msg="Test of extension was positiv but should have failed because of missing permissions to the added data disk")

        self.cmd('vm aem set --verbose -g {rg} -n {vm} --install-new-extension --set-access-to-individual-resources')
        self._assert_new_extension(self.IDENT_SYSTEM_ASSIGNED)

    def test_scope_method(self):

        # | Permissions for RG | Permission for Resource (after check) | Result  |
        # |         Y          |           Y                           |   Y     |
        expected_check_result = True
        expected_group_call = False
        expected_res_call = False
        ok_count = 0
        nok_count = 0

        ok = set()
        nok = set()
        test_scope_result = TestScope()
        check_ok = EnhancedMonitoring._check_scope_permissions(True, True, test_scope_result.GROUP_SCOPE, test_scope_result.RESOURCE_SCOPE,
                                                               "role", ok, nok, test_scope_result.func_scope_true)
        self.assertTrue(check_ok == expected_check_result)
        self.assertTrue(test_scope_result.group_called == expected_group_call)
        self.assertTrue(test_scope_result.res_called == expected_res_call)
        self.assertTrue(len(ok) == ok_count)
        self.assertTrue(len(nok) == nok_count)

        # | Permissions for RG | Permission for Resource (after check) | Result |
        # |         Y          |           N                           |   Y    |
        expected_check_result = True
        expected_group_call = False
        expected_res_call = False
        ok_count = 0
        nok_count = 0

        ok = set()
        nok = set()
        test_scope_result = TestScope()
        check_ok = EnhancedMonitoring._check_scope_permissions(True, False, test_scope_result.GROUP_SCOPE, test_scope_result.RESOURCE_SCOPE,
                                                               "role", ok, nok, test_scope_result.func_scope_true)
        self.assertTrue(check_ok == expected_check_result)
        self.assertTrue(test_scope_result.group_called == expected_group_call)
        self.assertTrue(test_scope_result.res_called == expected_res_call)
        self.assertTrue(len(ok) == ok_count)
        self.assertTrue(len(nok) == nok_count)

        # | Permissions for RG | Permission for Resource (after check) | Result |
        # |         Y          |           ?                           |   Y    |
        expected_check_result = True
        expected_group_call = False
        expected_res_call = False
        ok_count = 0
        nok_count = 0

        ok = set()
        nok = set()
        test_scope_result = TestScope()
        check_ok = EnhancedMonitoring._check_scope_permissions(True, None, test_scope_result.GROUP_SCOPE, test_scope_result.RESOURCE_SCOPE,
                                                               "role", ok, nok, test_scope_result.func_scope_true)
        self.assertTrue(check_ok == expected_check_result)
        self.assertTrue(test_scope_result.group_called == expected_group_call)
        self.assertTrue(test_scope_result.res_called == expected_res_call)
        self.assertTrue(len(ok) == ok_count)
        self.assertTrue(len(nok) == nok_count)

        # | Permissions for RG | Permission for Resource (after check) | Result |
        # |         N          |           Y                           |   Y    |
        expected_check_result = True
        expected_group_call = False
        expected_res_call = False
        ok_count = 0
        nok_count = 0

        ok = set()
        nok = set()
        test_scope_result = TestScope()
        check_ok = EnhancedMonitoring._check_scope_permissions(False, True, test_scope_result.GROUP_SCOPE, test_scope_result.RESOURCE_SCOPE,
                                                               "role", ok, nok, test_scope_result.func_scope_true)
        self.assertTrue(check_ok == expected_check_result)
        self.assertTrue(test_scope_result.group_called == expected_group_call)
        self.assertTrue(test_scope_result.res_called == expected_res_call)
        self.assertTrue(len(ok) == ok_count)
        self.assertTrue(len(nok) == nok_count)

        # | Permissions for RG | Permission for Resource (after check) | Result |
        # |         N          |           N                           |   N    |
        expected_check_result = False
        expected_group_call = False
        expected_res_call = False
        ok_count = 0
        nok_count = 0

        ok = set()
        nok = set()
        test_scope_result = TestScope()
        check_ok = EnhancedMonitoring._check_scope_permissions(False, False, test_scope_result.GROUP_SCOPE, test_scope_result.RESOURCE_SCOPE,
                                                               "role", ok, nok, test_scope_result.func_scope_true)
        self.assertTrue(check_ok == expected_check_result)
        self.assertTrue(test_scope_result.group_called == expected_group_call)
        self.assertTrue(test_scope_result.res_called == expected_res_call)
        self.assertTrue(len(ok) == ok_count)
        self.assertTrue(len(nok) == nok_count)

        # | Permissions for RG | Permission for Resource (after check) | Result             |
        # |         N          |           ? (Y)                       | check resource (Y) |
        expected_check_result = True
        expected_group_call = False
        expected_res_call = True
        ok_count = 1
        nok_count = 0

        ok = set()
        nok = set()
        test_scope_result = TestScope()
        check_ok = EnhancedMonitoring._check_scope_permissions(False, None, test_scope_result.GROUP_SCOPE, test_scope_result.RESOURCE_SCOPE,
                                                               "role", ok, nok, test_scope_result.func_scope_true)
        self.assertTrue(check_ok == expected_check_result)
        self.assertTrue(test_scope_result.group_called == expected_group_call)
        self.assertTrue(test_scope_result.res_called == expected_res_call)
        self.assertTrue(len(ok) == ok_count)
        self.assertTrue(len(nok) == nok_count)

        # | Permissions for RG | Permission for Resource (after check) | Result             |
        # |         N          |           ? (N)                       | check resource (N) |
        expected_check_result = False
        expected_group_call = False
        expected_res_call = True
        ok_count = 0
        nok_count = 1

        ok = set()
        nok = set()
        test_scope_result = TestScope()
        check_ok = EnhancedMonitoring._check_scope_permissions(False, None, test_scope_result.GROUP_SCOPE, test_scope_result.RESOURCE_SCOPE,
                                                               "role", ok, nok, test_scope_result.func_scope_false)
        self.assertTrue(check_ok == expected_check_result)
        self.assertTrue(test_scope_result.group_called == expected_group_call)
        self.assertTrue(test_scope_result.res_called == expected_res_call)
        self.assertTrue(len(ok) == ok_count)
        self.assertTrue(len(nok) == nok_count)

        # | Permissions for RG | Permission for Resource (after check) | Result |
        # |         ?          |           Y                           |   Y    |
        expected_check_result = True
        expected_group_call = False
        expected_res_call = False
        ok_count = 0
        nok_count = 0

        ok = set()
        nok = set()
        test_scope_result = TestScope()
        check_ok = EnhancedMonitoring._check_scope_permissions(None, True, test_scope_result.GROUP_SCOPE, test_scope_result.RESOURCE_SCOPE,
                                                               "role", ok, nok, test_scope_result.func_scope_true)
        self.assertTrue(check_ok == expected_check_result)
        self.assertTrue(test_scope_result.group_called == expected_group_call)
        self.assertTrue(test_scope_result.res_called == expected_res_call)
        self.assertTrue(len(ok) == ok_count)
        self.assertTrue(len(nok) == nok_count)

        # | Permissions for RG | Permission for Resource (after check) | Result                   |
        # |         ? (Y)      |           N                           | check resource group (Y) |
        expected_check_result = True
        expected_group_call = True
        expected_res_call = False
        ok_count = 1
        nok_count = 0

        ok = set()
        nok = set()
        test_scope_result = TestScope()
        check_ok = EnhancedMonitoring._check_scope_permissions(None, False, test_scope_result.GROUP_SCOPE, test_scope_result.RESOURCE_SCOPE,
                                                               "role", ok, nok, test_scope_result.func_scope_true)
        self.assertTrue(check_ok == expected_check_result)
        self.assertTrue(test_scope_result.group_called == expected_group_call)
        self.assertTrue(test_scope_result.res_called == expected_res_call)
        self.assertTrue(len(ok) == ok_count)
        self.assertTrue(len(nok) == nok_count)

        # | Permissions for RG | Permission for Resource (after check) | Result                   |
        # |         ? (N)      |           N                           | check resource group (N) |
        expected_check_result = False
        expected_group_call = True
        expected_res_call = False
        ok_count = 0
        nok_count = 1

        ok = set()
        nok = set()
        test_scope_result = TestScope()
        check_ok = EnhancedMonitoring._check_scope_permissions(None, False, test_scope_result.GROUP_SCOPE, test_scope_result.RESOURCE_SCOPE,
                                                               "role", ok, nok, test_scope_result.func_scope_false)
        self.assertTrue(check_ok == expected_check_result)
        self.assertTrue(test_scope_result.group_called == expected_group_call)
        self.assertTrue(test_scope_result.res_called == expected_res_call)
        self.assertTrue(len(ok) == ok_count)
        self.assertTrue(len(nok) == nok_count)

        # | Permissions for RG | Permission for Resource (after check) | Result                                             |
        # |         ? (Y)      |           ?                           | check resource group, if no, check resource (Y)    |
        expected_check_result = True
        expected_group_call = True
        expected_res_call = False
        ok_count = 1
        nok_count = 0

        ok = set()
        nok = set()
        test_scope_result = TestScope()
        check_ok = EnhancedMonitoring._check_scope_permissions(None, None, test_scope_result.GROUP_SCOPE, test_scope_result.RESOURCE_SCOPE,
                                                               "role", ok, nok, test_scope_result.func_scope_true)
        self.assertTrue(check_ok == expected_check_result)
        self.assertTrue(test_scope_result.group_called == expected_group_call)
        self.assertTrue(test_scope_result.res_called == expected_res_call)
        self.assertTrue(len(ok) == ok_count)
        self.assertTrue(len(nok) == nok_count)

        # | Permissions for RG | Permission for Resource (after check) | Result                                             |
        # |         ? (N)      |           ? (Y)                       | check resource group, if no, check resource (N)(Y) |
        expected_check_result = True
        expected_group_call = True
        expected_res_call = True
        ok_count = 1
        nok_count = 1

        ok = set()
        nok = set()
        test_scope_result = TestScope()
        check_ok = EnhancedMonitoring._check_scope_permissions(None, None, test_scope_result.GROUP_SCOPE, test_scope_result.RESOURCE_SCOPE,
                                                               "role", ok, nok, test_scope_result.func_scope_equal)
        self.assertTrue(check_ok == expected_check_result)
        self.assertTrue(test_scope_result.group_called == expected_group_call)
        self.assertTrue(test_scope_result.res_called == expected_res_call)
        self.assertTrue(len(ok) == ok_count)
        self.assertTrue(len(nok) == nok_count)

        # | Permissions for RG | Permission for Resource (after check) | Result                                             |
        # |         ? (N)      |           ? (N)                       | check resource group, if no, check resource (N)(N) |
        expected_check_result = False
        expected_group_call = True
        expected_res_call = True
        ok_count = 0
        nok_count = 2

        ok = set()
        nok = set()
        test_scope_result = TestScope()
        check_ok = EnhancedMonitoring._check_scope_permissions(None, None, test_scope_result.GROUP_SCOPE, test_scope_result.RESOURCE_SCOPE,
                                                               "role", ok, nok, test_scope_result.func_scope_false)
        self.assertTrue(check_ok == expected_check_result)
        self.assertTrue(test_scope_result.group_called == expected_group_call)
        self.assertTrue(test_scope_result.res_called == expected_res_call)
        self.assertTrue(len(ok) == ok_count)
        self.assertTrue(len(nok) == nok_count)

    @ResourceGroupPreparer()
    def test_vm_aem_configure(self, resource_group):
        os.environ["AZURE_CLI_AEM_TEST"] = "test_vm_aem_configure"

        self.kwargs.update({
            'vm': 'vm1',
        })
        self.cmd('vm create -g {rg} -n {vm} --os-disk-name os-disk --image centos --generate-ssh-keys')
        self.cmd('vm aem set -g {rg} -n {vm} --verbose')
        self.cmd('vm aem verify -g {rg} -n {vm} --verbose')
        self.cmd('vm aem delete -g {rg} -n {vm} --verbose')

        err = ("VM Extension for SAP was not installed")
        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify --verbose -g {rg} -n {vm}')
        self.assertEqual(str(cm.exception), err)

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer()
    def test_vm_aem_configure_v2(self, resource_group):
        os.environ["AZURE_CLI_AEM_TEST"] = "test_vm_aem_configure_v2"

        self.kwargs.update({
            'vm': 'vm1',
        })
        self.cmd('vm create -g {rg} -n {vm} --os-disk-name os-disk --image centos --generate-ssh-keys')
        self.cmd('vm aem set -g {rg} -n {vm} --install-new-extension --verbose')
        self.cmd('vm aem verify -g {rg} -n {vm} --verbose')
        self.cmd('vm aem delete -g {rg} -n {vm} --verbose')

        err = ("VM Extension for SAP was not installed")
        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify -g {rg} -n {vm} --verbose')
        self.assertEqual(str(cm.exception), err)

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer()
    def test_vm_aem_configure_v2_individual(self, resource_group):
        os.environ["AZURE_CLI_AEM_TEST"] = "test_vm_aem_configure_v2_individual"

        self.kwargs.update({
            'vm': 'vm1',
        })
        self.cmd('vm create -g {rg} -n {vm} --os-disk-name os-disk --image centos --generate-ssh-keys')
        self.cmd('vm aem set -g {rg} -n {vm} --install-new-extension --set-access-to-individual-resources --verbose')
        self.cmd('vm aem verify -g {rg} -n {vm} --verbose')
        self.cmd('vm aem delete -g {rg} -n {vm} --verbose')

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify -g {rg} -n {vm} --verbose')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_VERIFY)

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer()
    def test_vm_aem_configure_v2_proxy(self, resource_group):
        os.environ["AZURE_CLI_AEM_TEST"] = "test_vm_aem_configure_v2_proxy"

        self.kwargs.update({
            'vm': 'vm1',
        })
        self.cmd('vm create -g {rg} -n {vm} --os-disk-name os-disk --image centos --generate-ssh-keys')
        self.cmd('vm aem set -g {rg} -n {vm} --install-new-extension --proxy-uri http://proxyhost:8080 --verbose')
        self.cmd('vm aem verify -g {rg} -n {vm} --verbose')
        self.cmd('vm aem delete -g {rg} -n {vm} --verbose')

        with self.assertRaises(CLIError) as cm:
            self.cmd('vm aem verify -g {rg} -n {vm} --verbose')
        self.assertEqual(str(cm.exception), self.ERR_EXT_NOT_INSTALLED_VERIFY)
