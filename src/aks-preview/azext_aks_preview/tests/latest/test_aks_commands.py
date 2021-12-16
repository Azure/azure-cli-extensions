# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import os
import tempfile

from azure.cli.testsdk import (
    ResourceGroupPreparer, RoleBasedServicePrincipalPreparer, ScenarioTest, live_only)
from azure.cli.command_modules.acs._format import version_to_tuple
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from knack.util import CLIError

from .recording_processors import KeyReplacer
from .custom_preparers import AKSCustomResourceGroupPreparer


def _get_test_data_file(filename):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(curr_dir, 'data', filename)


class AzureKubernetesServiceScenarioTest(ScenarioTest):
    def __init__(self, method_name):
        super(AzureKubernetesServiceScenarioTest, self).__init__(
            method_name, recording_processors=[KeyReplacer()]
        )

    def _get_versions(self, location):
        """Return the previous and current Kubernetes minor release versions, such as ("1.11.6", "1.12.4")."""
        versions = self.cmd(
            "az aks get-versions -l westus2 --query 'orchestrators[].orchestratorVersion'").get_output_in_json()
        # sort by semantic version, from newest to oldest
        versions = sorted(versions, key=version_to_tuple, reverse=True)
        upgrade_version = versions[0]
        # find the first version that doesn't start with the latest major.minor.
        prefix = upgrade_version[:upgrade_version.rfind('.')]
        create_version = next(x for x in versions if not x.startswith(prefix))
        return create_version, upgrade_version

    @classmethod
    def generate_ssh_keys(cls):
        # If the `--ssh-key-value` option is not specified, the validator will try to read the ssh-key from the "~/.ssh" directory,
        # and if no key exists, it will call the method provided by azure-cli.core to generate one under the "~/.ssh" directory.
        # In order to avoid misuse of personal ssh-key during testing and the race condition that is prone to occur when key creation
        # is handled by azure-cli when performing test cases concurrently, we provide this function as a workround.

        # In the scenario of runner and AKS check-in pipeline, a temporary ssh-key will be generated in advance under the
        # "tests/latest/data/.ssh" sub-directory of the acs module in the cloned azure-cli repository when setting up the
        # environment. Each test case will read the ssh-key from a pre-generated file during execution, so there will be no
        # race conditions caused by concurrent reading and writing/creating of the same file.
        acs_base_dir = os.getenv("ACS_BASE_DIR", None)
        if acs_base_dir:
            pre_generated_ssh_key_path = os.path.join(acs_base_dir, "tests/latest/data/.ssh/id_rsa.pub")
            if os.path.exists(pre_generated_ssh_key_path):
                return pre_generated_ssh_key_path.replace('\\', '\\\\')

        # In the CLI check-in pipeline scenario, the following fake ssh-key will be used. Each test case will read the ssh-key from
        # a different temporary file during execution, so there will be no race conditions caused by concurrent reading and
        # writing/creating of the same file.
        TEST_SSH_KEY_PUB = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCbIg1guRHbI0lV11wWDt1r2cUdcNd27CJsg+SfgC7miZeubtwUhbsPdhMQsfDyhOWHq1+ZL0M+nJZV63d/1dhmhtgyOqejUwrPlzKhydsbrsdUor+JmNJDdW01v7BXHyuymT8G4s09jCasNOwiufbP/qp72ruu0bIA1nySsvlf9pCQAuFkAnVnf/rFhUlOkhtRpwcq8SUNY2zRHR/EKb/4NWY1JzR4sa3q2fWIJdrrX0DvLoa5g9bIEd4Df79ba7v+yiUBOS0zT2ll+z4g9izHK3EO5d8hL4jYxcjKs+wcslSYRWrascfscLgMlMGh0CdKeNTDjHpGPncaf3Z+FwwwjWeuiNBxv7bJo13/8B/098KlVDl4GZqsoBCEjPyJfV6hO0y/LkRGkk7oHWKgeWAfKtfLItRp00eZ4fcJNK9kCaSMmEugoZWcI7NGbZXzqFWqbpRI7NcDP9+WIQ+i9U5vqWsqd/zng4kbuAJ6UuKqIzB0upYrLShfQE3SAck8oaLhJqqq56VfDuASNpJKidV+zq27HfSBmbXnkR/5AK337dc3MXKJypoK/QPMLKUAP5XLPbs+NddJQV7EZXd29DLgp+fRIg3edpKdO7ZErWhv7d+3Kws+e1Y+ypmR2WIVSwVyBEUfgv2C8Ts9gnTF4pNcEY/S2aBicz5Ew2+jdyGNQQ== test@example.com\n"  # pylint: disable=line-too-long
        _, pathname = tempfile.mkstemp()
        with open(pathname, 'w') as key_file:
            key_file.write(TEST_SSH_KEY_PUB)
        return pathname.replace('\\', '\\\\')

    @live_only()  # live only is required for test environment setup like `az login`
    @AllowLargeResponse()
    def test_get_version(self):
        versions_cmd = 'aks get-versions -l westus2'
        self.cmd(versions_cmd, checks=[
            self.check(
                'type', 'Microsoft.ContainerService/locations/orchestrators'),
            self.check('orchestrators[0].orchestratorType', 'Kubernetes')
        ])

    @live_only()  # live only is required for test environment setup like `az login`
    @AllowLargeResponse()
    def test_get_os_options(self):
        osOptions_cmd = 'aks get-os-options -l westus2'
        self.cmd(osOptions_cmd, checks=[
            self.check(
                'type', 'Microsoft.ContainerService/locations/osOptions')
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='eastus')
    def test_aks_create_and_update_with_managed_nat_gateway_outbound(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--vm-set-type VirtualMachineScaleSets -c 1 ' \
                     '--outbound-type=managedNATGateway ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('networkProfile.outboundType', 'managedNATGateway'),
        ])

        update_cmd = 'aks update --resource-group={resource_group} --name={name} ' \
                     '--nat-gateway-managed-outbound-ip-count 2 ' \
                     '--nat-gateway-idle-timeout 30 '
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('networkProfile.outboundType', 'managedNATGateway'),
            self.check('networkProfile.natGatewayProfile.idleTimeoutInMinutes', 30),
            self.check('networkProfile.natGatewayProfile.managedOutboundIpProfile.count', 2),
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_and_update_with_managed_aad(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--vm-set-type VirtualMachineScaleSets -c 1 ' \
                     '--enable-aad --aad-admin-group-object-ids 00000000-0000-0000-0000-000000000001 ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.managed', True),
            self.check(
                'aadProfile.adminGroupObjectIDs[0]', '00000000-0000-0000-0000-000000000001')
        ])

        update_cmd = 'aks update --resource-group={resource_group} --name={name} ' \
                     '--aad-admin-group-object-ids 00000000-0000-0000-0000-000000000002 ' \
                     '--aad-tenant-id 00000000-0000-0000-0000-000000000003 -o json'
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.managed', True),
            self.check(
                'aadProfile.adminGroupObjectIDs[0]', '00000000-0000-0000-0000-000000000002'),
            self.check('aadProfile.tenantId',
                       '00000000-0000-0000-0000-000000000003')
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='canadacentral')
    def test_aks_create_aadv1_and_update_with_managed_aad(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--vm-set-type VirtualMachineScaleSets -c 1 ' \
                     '--aad-server-app-id 00000000-0000-0000-0000-000000000001 ' \
                     '--aad-server-app-secret fake-secret ' \
                     '--aad-client-app-id 00000000-0000-0000-0000-000000000002 ' \
                     '--aad-tenant-id d5b55040-0c14-48cc-a028-91457fc190d9 ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.managed', None),
            self.check('aadProfile.serverAppId',
                       '00000000-0000-0000-0000-000000000001'),
            self.check('aadProfile.clientAppId',
                       '00000000-0000-0000-0000-000000000002'),
            self.check('aadProfile.tenantId',
                       'd5b55040-0c14-48cc-a028-91457fc190d9')
        ])

        update_cmd = 'aks update --resource-group={resource_group} --name={name} ' \
                     '--enable-aad ' \
                     '--aad-admin-group-object-ids 00000000-0000-0000-0000-000000000003 ' \
                     '--aad-tenant-id 00000000-0000-0000-0000-000000000004 -o json'
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.managed', True),
            self.check(
                'aadProfile.adminGroupObjectIDs[0]', '00000000-0000-0000-0000-000000000003'),
            self.check('aadProfile.tenantId',
                       '00000000-0000-0000-0000-000000000004')
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='canadacentral')
    def test_aks_create_nonaad_and_update_with_managed_aad(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--vm-set-type VirtualMachineScaleSets --node-count=1 ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile', None)
        ])

        update_cmd = 'aks update --resource-group={resource_group} --name={name} ' \
                     '--enable-aad ' \
                     '--aad-admin-group-object-ids 00000000-0000-0000-0000-000000000001 ' \
                     '--aad-tenant-id 00000000-0000-0000-0000-000000000002 -o json'
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.managed', True),
            self.check(
                'aadProfile.adminGroupObjectIDs[0]', '00000000-0000-0000-0000-000000000001'),
            self.check('aadProfile.tenantId',
                       '00000000-0000-0000-0000-000000000002')
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_and_update_with_managed_aad_enable_azure_rbac(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--vm-set-type VirtualMachineScaleSets -c 1 ' \
                     '--enable-aad --aad-admin-group-object-ids 00000000-0000-0000-0000-000000000001 ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.managed', True),
            self.check(
                'aadProfile.adminGroupObjectIDs[0]', '00000000-0000-0000-0000-000000000001')
        ])

        update_cmd = 'aks update --resource-group={resource_group} --name={name} ' \
                     '--enable-azure-rbac -o json'
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.enableAzureRbac', True)
        ])

        update_cmd = 'aks update --resource-group={resource_group} --name={name} ' \
                     '--disable-azure-rbac -o json'
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aadProfile.enableAzureRbac', False)
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_ingress_appgw_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity ' \
                     '-a ingress-appgw --appgw-subnet-cidr 10.2.0.0/16 ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ingressApplicationGateway.enabled', True),
            self.check(
                'addonProfiles.ingressApplicationGateway.config.subnetCIDR', "10.2.0.0/16")
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_ingress_appgw_addon_with_deprecated_subet_prefix(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity ' \
                     '-a ingress-appgw --appgw-subnet-prefix 10.2.0.0/16 ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ingressApplicationGateway.enabled', True),
            self.check(
                'addonProfiles.ingressApplicationGateway.config.subnetCIDR', "10.2.0.0/16")
        ])

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_byo_subnet_with_ingress_appgw_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        vnet_name = self.create_random_name('cliakstest', 16)
        appgw_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'aks_name': aks_name,
            'vnet_name': vnet_name,
            'appgw_name': appgw_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create virtual network
        create_vnet = 'network vnet create --resource-group={resource_group} --name={vnet_name} ' \
                      '--address-prefix 11.0.0.0/16 --subnet-name aks-subnet --subnet-prefix 11.0.0.0/24  -o json'
        vnet = self.cmd(create_vnet, checks=[
            self.check('newVNet.provisioningState', 'Succeeded')
        ]).get_output_in_json()

        create_subnet = 'network vnet subnet create -n appgw-subnet --resource-group={resource_group} --vnet-name {vnet_name} ' \
                        '--address-prefixes 11.0.1.0/24  -o json'
        self.cmd(create_subnet, checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        vnet_id = vnet['newVNet']["id"]
        assert vnet_id is not None
        self.kwargs.update({
            'vnet_id': vnet_id,
        })

        # create aks cluster
        create_cmd = 'aks create --resource-group={resource_group} --name={aks_name} --enable-managed-identity ' \
                     '--vnet-subnet-id {vnet_id}/subnets/aks-subnet -a ingress-appgw ' \
                     '--appgw-name gateway --appgw-subnet-id {vnet_id}/subnets/appgw-subnet ' \
                     '--yes --ssh-key-value={ssh_key_value} -o json'
        aks_cluster = self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ingressApplicationGateway.enabled', True),
            self.check(
                'addonProfiles.ingressApplicationGateway.config.applicationGatewayName', "gateway"),
            self.check('addonProfiles.ingressApplicationGateway.config.subnetId',
                       vnet_id + '/subnets/appgw-subnet')
        ]).get_output_in_json()

        addon_client_id = aks_cluster["addonProfiles"]["ingressApplicationGateway"]["identity"]["clientId"]

        self.kwargs.update({
            'addon_client_id': addon_client_id,
        })

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_byo_appgw_with_ingress_appgw_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        vnet_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'aks_name': aks_name,
            'vnet_name': vnet_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create virtual network
        create_vnet = 'network vnet create --resource-group={resource_group} --name={vnet_name} ' \
                      '--address-prefix 11.0.0.0/16 --subnet-name aks-subnet --subnet-prefix 11.0.0.0/24  -o json'
        vnet = self.cmd(create_vnet, checks=[
            self.check('newVNet.provisioningState', 'Succeeded')
        ]).get_output_in_json()

        create_subnet = 'network vnet subnet create -n appgw-subnet --resource-group={resource_group} --vnet-name {vnet_name} ' \
                        '--address-prefixes 11.0.1.0/24  -o json'
        self.cmd(create_subnet, checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        vnet_id = vnet['newVNet']["id"]
        assert vnet_id is not None
        self.kwargs.update({
            'vnet_id': vnet_id,
        })

        # create public ip for app gateway
        create_pip = 'network public-ip create -n appgw-ip -g {resource_group} ' \
                     '--allocation-method Static --sku Standard  -o json'
        self.cmd(create_pip, checks=[
            self.check('publicIp.provisioningState', 'Succeeded')
        ])

        # create app gateway
        create_appgw = 'network application-gateway create -n appgw -g {resource_group} ' \
                       '--sku Standard_v2 --public-ip-address appgw-ip --subnet {vnet_id}/subnets/appgw-subnet'
        self.cmd(create_appgw)

        # construct group id
        from msrestazure.tools import parse_resource_id, resource_id
        parsed_vnet_id = parse_resource_id(vnet_id)
        group_id = resource_id(subscription=parsed_vnet_id["subscription"],
                               resource_group=parsed_vnet_id["resource_group"])
        appgw_id = group_id + "/providers/Microsoft.Network/applicationGateways/appgw"

        self.kwargs.update({
            'appgw_id': appgw_id,
            'appgw_group_id': group_id
        })

        # create aks cluster
        create_cmd = 'aks create -n {aks_name} -g {resource_group} --enable-managed-identity ' \
                     '--vnet-subnet-id {vnet_id}/subnets/aks-subnet ' \
                     '-a ingress-appgw --appgw-id {appgw_id} ' \
                     '--yes --ssh-key-value={ssh_key_value} -o json'
        aks_cluster = self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ingressApplicationGateway.enabled', True),
            self.check(
                'addonProfiles.ingressApplicationGateway.config.applicationGatewayId', appgw_id)
        ]).get_output_in_json()

        addon_client_id = aks_cluster["addonProfiles"]["ingressApplicationGateway"]["identity"]["clientId"]

        self.kwargs.update({
            'addon_client_id': addon_client_id,
        })

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_openservicemesh_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity ' \
                     '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-OpenServiceMesh ' \
                     '-a open-service-mesh --ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh.enabled', True),
        ])

    @live_only()  # live only is required for test environment setup like `az login`
    @AllowLargeResponse()
    def test_aks_addon_list_available(self):
        list_available_cmd = 'aks addon list-available -o json'
        addon_list = self.cmd(list_available_cmd).get_output_in_json()

        assert len(addon_list) == 10
        assert addon_list[0]['name'] == "http_application_routing"
        assert addon_list[1]['name'] == "monitoring"
        assert addon_list[2]['name'] == "virtual-node"
        assert addon_list[3]['name'] == "azure-policy"
        assert addon_list[4]['name'] == "kube-dashboard"
        assert addon_list[5]['name'] == "ingress-appgw"
        assert addon_list[6]['name'] == "open-service-mesh"
        assert addon_list[7]['name'] == "confcom"
        assert addon_list[8]['name'] == "gitops"
        assert addon_list[9]['name'] == "azure-keyvault-secrets-provider"

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_addon_list_all_disabled(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh', None),
        ])

        list_cmd = 'aks addon list --resource-group={resource_group} --name={name} -o json'
        addon_list = self.cmd(list_cmd).get_output_in_json()

        assert len(addon_list) > 0

        for addon in addon_list:
            assert not addon["enabled"]


    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_addon_list_confcom_enabled(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} ' \
                     '-a confcom -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', True),
            self.check(
                'addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled', "false")
        ])

        list_cmd = 'aks addon list --resource-group={resource_group} --name={name} -o json'
        addon_list = self.cmd(list_cmd).get_output_in_json()

        assert len(addon_list) > 0

        for addon in addon_list:
            if addon["name"] == "confcom":
                assert addon["enabled"]
            else:
                assert not addon["enabled"]


    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_addon_list_openservicemesh_enabled(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} ' \
                     '-a open-service-mesh -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh.enabled', True),
        ])

        list_cmd = 'aks addon list --resource-group={resource_group} --name={name} -o json'
        addon_list = self.cmd(list_cmd).get_output_in_json()

        assert len(addon_list) > 0

        for addon in addon_list:
            if addon["name"] == "open-service-mesh":
                assert addon["enabled"]
            else:
                assert not addon["enabled"]


    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_addon_show_all_disabled(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh', None),
        ])

        show_cmd = 'aks addon show --resource-group={resource_group} --name={name} ' \
                   '-a open-service-mesh -o json'

        with self.assertRaisesRegexp(CLIError, 'Addon "open-service-mesh" is not enabled in this cluster.'):
            self.cmd(show_cmd)

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_addon_show_confcom_enabled(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} ' \
                     '-a confcom -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', True),
            self.check(
                'addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled', "false")
        ])

        show_cmd = 'aks addon show --resource-group={resource_group} --name={name} ' \
                   '-a confcom -o json'

        self.cmd(show_cmd, checks=[
            self.check("api_key", "ACCSGXDevicePlugin"),
            self.check("name", "confcom"),
            self.exists('config')
        ])


    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_addon_show_openservicemesh_enabled(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} ' \
                     '-a open-service-mesh -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh.enabled', True),
        ])

        show_cmd = 'aks addon show --resource-group={resource_group} --name={name} ' \
                   '-a open-service-mesh -o json'

        self.cmd(show_cmd, checks=[
            self.check("api_key", "openServiceMesh"),
            self.check("name", "open-service-mesh"),
            self.exists('identity')
        ])


    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_addon_enable_with_openservicemesh(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh', None),
        ])

        enable_cmd = 'aks addon enable --addon open-service-mesh --resource-group={resource_group} --name={name} -o json'
        self.cmd(enable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh.enabled', True),
        ])


    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_addon_disable_openservicemesh(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} ' \
                     '-a open-service-mesh -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh.enabled', True),
        ])

        disable_cmd = 'aks addon disable --addon open-service-mesh --resource-group={resource_group} --name={name} -o json'
        self.cmd(disable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh.enabled', False),
            self.check('addonProfiles.openServiceMesh.config', None)
        ])


    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_addon_enable_with_azurekeyvaultsecretsprovider(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.azureKeyvaultSecretsProvider', None)
        ])

        enable_cmd = 'aks addon enable --addon azure-keyvault-secrets-provider --resource-group={resource_group} --name={name} -o json'
        self.cmd(enable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.enabled', True),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation', "false")
        ])

        disable_cmd = 'aks addon disable --addon azure-keyvault-secrets-provider --resource-group={resource_group} --name={name} -o json'
        self.cmd(disable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.enabled', False),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config', None)
        ])

        enable_with_secret_rotation_cmd = 'aks addon enable --addon azure-keyvault-secrets-provider --enable-secret-rotation --resource-group={resource_group} --name={name} -o json'
        self.cmd(enable_with_secret_rotation_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.enabled', True),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation', "true")
        ])

        # delete
        cmd = 'aks delete --resource-group={resource_group} --name={name} --yes --no-wait'
        self.cmd(cmd, checks=[
            self.is_empty(),
        ])


    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_addon_enable_confcom_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} ' \
                     '-o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin', None)
        ])

        enable_cmd = 'aks addon enable --addon confcom --resource-group={resource_group} --name={name} -o json'
        self.cmd(enable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', True),
            self.check(
                'addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled', "false")
        ])


    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_addon_disable_confcom_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} ' \
                     '-a confcom -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', True),
            self.check(
                'addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled', "false")
        ])

        disable_cmd = 'aks addon disable --addon confcom --resource-group={resource_group} --name={name} -o json'
        self.cmd(disable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', False),
            self.check('addonProfiles.ACCSGXDevicePlugin.config', None)
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_addon_update_all_disabled(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} ' \
                     '-o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin', None)
        ])

        update_cmd = 'aks addon update --addon confcom --resource-group={resource_group} --name={name} -o json'
        with self.assertRaisesRegexp(CLIError, 'Addon "confcom" is not enabled in this cluster.'):
            self.cmd(update_cmd)

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_addon_update_with_confcom(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin', None)
        ])

        enable_cmd = 'aks addon enable --addon confcom --resource-group={resource_group} --name={name} -o json'
        self.cmd(enable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', True),
            self.check(
                'addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled', "false")
        ])

        update_cmd = 'aks addon update --resource-group={resource_group} --name={name} ' \
                     '-a confcom --enable-sgxquotehelper -o json'
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', True),
            self.check(
                'addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled', "true")
        ])

        delete_cmd = 'aks delete --resource-group={resource_group} --name={name} --yes --no-wait'
        self.cmd(delete_cmd, checks=[
            self.is_empty(),
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_addon_update_with_azurekeyvaultsecretsprovider(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.azureKeyvaultSecretsProvider', None)
        ])

        enable_cmd = 'aks addon enable --addon azure-keyvault-secrets-provider --resource-group={resource_group} --name={name} -o json'
        self.cmd(enable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.enabled', True),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation', "false")
        ])

        update_with_secret_rotation_cmd = 'aks addon update --addon azure-keyvault-secrets-provider --enable-secret-rotation --resource-group={resource_group} --name={name} -o json'
        self.cmd(update_with_secret_rotation_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.enabled', True),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation', "true")
        ])

        # delete
        cmd = 'aks delete --resource-group={resource_group} --name={name} --yes --no-wait'
        self.cmd(cmd, checks=[
            self.is_empty(),
        ])


    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_enable_addon_with_openservicemesh(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh', None),
        ])

        enable_cmd = 'aks enable-addons --addons open-service-mesh --resource-group={resource_group} --name={name} -o json'
        self.cmd(enable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh.enabled', True),
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_disable_addon_openservicemesh(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity ' \
                     '-a open-service-mesh --ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh.enabled', True),
        ])

        disable_cmd = 'aks disable-addons --addons open-service-mesh --resource-group={resource_group} --name={name} -o json'
        self.cmd(disable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.openServiceMesh.enabled', False),
            self.check('addonProfiles.openServiceMesh.config', None)
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_azurekeyvaultsecretsprovider_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '-a azure-keyvault-secrets-provider --ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.enabled', True),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation', "false"),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config.rotationPollInterval', "2m")
        ])

        # delete
        cmd = 'aks delete --resource-group={resource_group} --name={name} --yes --no-wait'
        self.cmd(cmd, checks=[
            self.is_empty(),
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_addon_with_azurekeyvaultsecretsprovider_with_secret_rotation(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '-a azure-keyvault-secrets-provider --enable-secret-rotation --rotation-poll-interval 30m ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.enabled', True),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation', "true"),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config.rotationPollInterval', "30m")
        ])

        # delete
        cmd = 'aks delete --resource-group={resource_group} --name={name} --yes --no-wait'
        self.cmd(cmd, checks=[
            self.is_empty(),
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_enable_addon_with_azurekeyvaultsecretsprovider(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.azureKeyvaultSecretsProvider', None)
        ])

        enable_cmd = 'aks enable-addons --addons azure-keyvault-secrets-provider --resource-group={resource_group} --name={name} -o json'
        self.cmd(enable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.enabled', True),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation', "false")
        ])

        update_enable_cmd = 'aks update --resource-group={resource_group} --name={name} --enable-secret-rotation --rotation-poll-interval 120s -o json'
        self.cmd(update_enable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.enabled', True),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation', "true"),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config.rotationPollInterval', "120s")
        ])

        update_disable_cmd = 'aks update --resource-group={resource_group} --name={name} --disable-secret-rotation -o json'
        self.cmd(update_disable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.enabled', True),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation', "false"),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config.rotationPollInterval', "120s")
        ])

        disable_cmd = 'aks disable-addons --addons azure-keyvault-secrets-provider --resource-group={resource_group} --name={name} -o json'
        self.cmd(disable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.enabled', False),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config', None)
        ])

        enable_with_secret_rotation_cmd = 'aks enable-addons --addons azure-keyvault-secrets-provider --enable-secret-rotation --rotation-poll-interval 1h --resource-group={resource_group} --name={name} -o json'
        self.cmd(enable_with_secret_rotation_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.enabled', True),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation', "true"),
            self.check(
                'addonProfiles.azureKeyvaultSecretsProvider.config.rotationPollInterval', "1h")
        ])

        # delete
        cmd = 'aks delete --resource-group={resource_group} --name={name} --yes --no-wait'
        self.cmd(cmd, checks=[
            self.is_empty(),
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_confcom_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity ' \
                     '-a confcom --ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', True),
            self.check(
                'addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled', "false")
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_confcom_addon_helper_enabled(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity ' \
                     '-a confcom --enable-sgxquotehelper --ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', True),
            self.check(
                'addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled', "true")
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_enable_addons_confcom_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin', None)
        ])

        enable_cmd = 'aks enable-addons --addons confcom --resource-group={resource_group} --name={name} -o json'
        self.cmd(enable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', True),
            self.check(
                'addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled', "false")
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_disable_addons_confcom_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-managed-identity ' \
                     '-a confcom --ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', True),
            self.check(
                'addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled', "false")
        ])

        disable_cmd = 'aks disable-addons --addons confcom --resource-group={resource_group} --name={name} -o json'
        self.cmd(disable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.ACCSGXDevicePlugin.enabled', False),
            self.check('addonProfiles.ACCSGXDevicePlugin.config', None)
        ])

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_virtual_node_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        vnet_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'aks_name': aks_name,
            'vnet_name': vnet_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create virtual network
        create_vnet = 'network vnet create --resource-group={resource_group} --name={vnet_name} ' \
                      '--address-prefix 11.0.0.0/16 --subnet-name aks-subnet --subnet-prefix 11.0.0.0/24  -o json'
        vnet = self.cmd(create_vnet, checks=[
            self.check('newVNet.provisioningState', 'Succeeded')
        ]).get_output_in_json()

        create_subnet = 'network vnet subnet create -n aci-subnet --resource-group={resource_group} --vnet-name {vnet_name} ' \
                        '--address-prefixes 11.0.1.0/24  -o json'
        self.cmd(create_subnet, checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        vnet_id = vnet['newVNet']["id"]
        assert vnet_id is not None
        self.kwargs.update({
            'vnet_id': vnet_id,
        })

        # create aks cluster
        create_cmd = 'aks create --resource-group={resource_group} --name={aks_name} --enable-managed-identity ' \
                     '--vnet-subnet-id {vnet_id}/subnets/aks-subnet --network-plugin azure ' \
                     '-a virtual-node --aci-subnet-name aci-subnet --yes ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        aks_cluster = self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.aciConnectorLinux.enabled', True),
            self.check(
                'addonProfiles.aciConnectorLinux.config.SubnetName', "aci-subnet")
        ]).get_output_in_json()

        addon_client_id = aks_cluster["addonProfiles"]["aciConnectorLinux"]["identity"]["clientId"]

        self.kwargs.update({
            'addon_client_id': addon_client_id,
        })

        # delete
        cmd = 'aks delete --resource-group={resource_group} --name={aks_name} --yes --no-wait'
        self.cmd(cmd, checks=[
            self.is_empty(),
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_stop_and_start(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

        stop_cmd = 'aks stop --resource-group={resource_group} --name={name}'
        self.cmd(stop_cmd)

        start_cmd = 'aks start --resource-group={resource_group} --name={name}'
        self.cmd(start_cmd)

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_managed_disk(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })
        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--vm-set-type VirtualMachineScaleSets -c 1 ' \
                     '--node-osdisk-type=Managed ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('agentPoolProfiles[0].osDiskType', 'Managed'),
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_ephemeral_disk(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--vm-set-type VirtualMachineScaleSets -c 1 ' \
                     '--node-osdisk-type=Ephemeral --node-osdisk-size 60 ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('agentPoolProfiles[0].osDiskType', 'Ephemeral'),
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='eastus')
    def test_aks_create_with_ossku(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })
        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--vm-set-type VirtualMachineScaleSets -c 1 ' \
                     '--os-sku CBLMariner ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('agentPoolProfiles[0].osSku', 'CBLMariner'),
        ])
        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='eastus')
    def test_aks_nodepool_add_with_workload_runtime(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        node_pool_name = self.create_random_name('c', 6)
        node_pool_name_second = self.create_random_name('c', 6)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'node_pool_name': node_pool_name,
            'node_pool_name_second': node_pool_name_second,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--nodepool-name {node_pool_name} -c 1 ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

        self.cmd('aks nodepool add '
                 '--resource-group={resource_group} '
                 '--cluster-name={name} '
                 '--name={node_pool_name_second} '
                 '--workload-runtime WasmWasi',
                 checks=[
                    self.check('provisioningState', 'Succeeded'),
                    self.check('workloadRuntime', 'WasmWasi'),
                 ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])


    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='eastus')
    def test_aks_nodepool_add_with_ossku(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        node_pool_name = self.create_random_name('c', 6)
        node_pool_name_second = self.create_random_name('c', 6)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'node_pool_name': node_pool_name,
            'node_pool_name_second': node_pool_name_second,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--nodepool-name {node_pool_name} -c 1 ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

        # nodepool get-upgrades
        self.cmd('aks nodepool add '
                 '--resource-group={resource_group} '
                 '--cluster-name={name} '
                 '--name={node_pool_name_second} '
                 '--os-sku CBLMariner',
                 checks=[
                    self.check('provisioningState', 'Succeeded'),
                    self.check('osSku', 'CBLMariner'),
                 ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='centraluseuap')
    def test_aks_nodepool_stop_and_start(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        nodepool_name = self.create_random_name('c', 6)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'nodepool_name' : nodepool_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create aks cluster
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
        ])
        # add nodepool
        self.cmd('aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool_name} --node-count=2', checks=[
            self.check('provisioningState', 'Succeeded')
        ])
        # stop nodepool
        self.cmd('aks nodepool stop --resource-group={resource_group} --cluster-name={name} --nodepool-name={nodepool_name} --aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/PreviewStartStopAgentPool', checks=[
            self.check('powerState.code', 'Stopped')
        ])
        #start nodepool
        self.cmd('aks nodepool start --resource-group={resource_group} --cluster-name={name} --nodepool-name={nodepool_name} --aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/PreviewStartStopAgentPool', checks=[
            self.check('powerState.code', 'Running')
        ])
        # delete AKS cluster
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='eastus')
    def test_aks_nodepool_add_with_gpu_instance_profile(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        node_pool_name = self.create_random_name('c', 6)
        node_pool_name_second = self.create_random_name('c', 6)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'node_pool_name': node_pool_name,
            'node_pool_name_second': node_pool_name_second,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--nodepool-name {node_pool_name} -c 1 ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

        # nodepool get-upgrades
        self.cmd('aks nodepool add '
                 '--resource-group={resource_group} '
                 '--cluster-name={name} '
                 '--name={node_pool_name_second} '
                 '--gpu-instance-profile=MIG3g '
                 '-c 1 '
                 '--aks-custom-headers UseGPUDedicatedVHD=true '
                 '--node-vm-size=standard_nd96asr_v4',
                 checks=[
                    self.check('provisioningState', 'Succeeded'),
                    self.check('gpuInstanceProfile', 'MIG3g'),
                 ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_nodepool_get_upgrades(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        node_pool_name = self.create_random_name('c', 6)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'node_pool_name': node_pool_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--nodepool-name {node_pool_name} -c 1 ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

        # nodepool get-upgrades
        self.cmd('aks nodepool get-upgrades '
                 '--resource-group={resource_group} '
                 '--cluster-name={name} '
                 '--nodepool-name={node_pool_name}',
                 checks=[
                     # if rerun the recording, please update latestNodeImageVersion to the latest value
                     self.check_pattern('latestNodeImageVersion',
                                'AKSUbuntu-1804gen2containerd-2021.(0[1-9]|1[012]).(0[1-9]|[12]\d|3[01])'),
                     self.check(
                         'type', "Microsoft.ContainerService/managedClusters/agentPools/upgradeProfiles")
                 ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_snapshot(self, resource_group, resource_group_location):
        create_version, upgrade_version = self._get_versions(resource_group_location)
        aks_name = self.create_random_name('cliakstest', 16)
        aks_name2 = self.create_random_name('cliakstest', 16)
        nodepool_name = self.create_random_name('c', 6)
        nodepool_name2 = self.create_random_name('c', 6)
        snapshot_name = self.create_random_name('s', 16)

        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'aks_name2': aks_name2,
            'location': resource_group_location,
            'nodepool_name': nodepool_name,
            'nodepool_name2': nodepool_name2,
            'snapshot_name': snapshot_name,
            'k8s_version': create_version,
            'upgrade_k8s_version': upgrade_version,
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create an aks cluster not using snapshot
        create_cmd = 'aks create --resource-group {resource_group} --name {name} --location {location} ' \
                     '--nodepool-name {nodepool_name} ' \
                     '--node-count 1 ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        response = self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded')
        ]).get_output_in_json()

        cluster_resource_id = response["id"]
        assert cluster_resource_id is not None
        nodepool_resource_id = cluster_resource_id + "/agentPools/" + nodepool_name
        self.kwargs.update({
            'nodepool_resource_id': nodepool_resource_id,
        })
        print("The nodepool resource id %s " % nodepool_resource_id)

        # create snapshot from the nodepool
        create_snapshot_cmd = 'aks snapshot create --resource-group {resource_group} --name {snapshot_name} --location {location} ' \
                              '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/SnapshotPreview ' \
                              '--nodepool-id {nodepool_resource_id} -o json'
        response = self.cmd(create_snapshot_cmd, checks=[
            self.check('creationData.sourceResourceId', nodepool_resource_id)
        ]).get_output_in_json()

        snapshot_resource_id = response["id"]
        assert snapshot_resource_id is not None
        self.kwargs.update({
            'snapshot_resource_id': snapshot_resource_id,
        })
        print("The snapshot resource id %s " % snapshot_resource_id)

        # delete the original AKS cluster
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

        # show the snapshot
        show_snapshot_cmd = 'aks snapshot show --resource-group {resource_group} --name {snapshot_name} -o json'
        response = self.cmd(show_snapshot_cmd, checks=[
            self.check('creationData.sourceResourceId', nodepool_resource_id)
        ]).get_output_in_json()

        # list the snapshots
        list_snapshot_cmd = 'aks snapshot list --resource-group {resource_group} -o json'
        response = self.cmd(list_snapshot_cmd, checks=[]).get_output_in_json()
        assert len(response) > 0

        # create another aks cluster using this snapshot
        create_cmd = 'aks create --resource-group {resource_group} --name {aks_name2} --location {location} ' \
                     '--nodepool-name {nodepool_name} ' \
                     '--node-count 1 --snapshot-id {snapshot_resource_id} ' \
                     '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/SnapshotPreview ' \
                     '-k {k8s_version} ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('agentPoolProfiles[0].creationData.sourceResourceId', snapshot_resource_id)
        ]).get_output_in_json()

        # add a new nodepool to this cluster using this snapshot
        add_nodepool_cmd = 'aks nodepool add --resource-group={resource_group} --cluster-name={aks_name2} --name={nodepool_name2} --node-count 1 ' \
                           '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/SnapshotPreview ' \
                           '-k {k8s_version} ' \
                           '--snapshot-id {snapshot_resource_id} -o json'
        self.cmd(add_nodepool_cmd,
            checks=[
                self.check('provisioningState', 'Succeeded'),
                self.check('creationData.sourceResourceId', snapshot_resource_id)
        ])

        # upgrade this cluster (snapshot is not allowed for cluster upgrading), snapshot info is reset
        create_cmd = 'aks upgrade --resource-group {resource_group} --name {aks_name2} -k {upgrade_k8s_version} --yes -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('agentPoolProfiles[0].creationData', None),
            self.check('agentPoolProfiles[1].creationData', None)
        ])

        # upgrade the nodepool2 using this snapshot again
        upgrade_node_image_only_nodepool_cmd = 'aks nodepool upgrade ' \
                                               '--resource-group {resource_group} ' \
                                               '--cluster-name {aks_name2} ' \
                                               '-n {nodepool_name2} ' \
                                               '--node-image-only --no-wait ' \
                                               '--snapshot-id {snapshot_resource_id} -o json'
        self.cmd(upgrade_node_image_only_nodepool_cmd)

        get_nodepool_cmd = 'aks nodepool show ' \
                           '--resource-group={resource_group} ' \
                           '--cluster-name={aks_name2} ' \
                           '-n {nodepool_name2} '
        self.cmd(get_nodepool_cmd, checks=[
            self.check('provisioningState', 'UpgradingNodeImageVersion'),
            self.check('creationData.sourceResourceId', snapshot_resource_id)
        ])

        # delete the 2nd AKS cluster
        self.cmd('aks delete -g {resource_group} -n {aks_name2} --yes --no-wait', checks=[self.is_empty()])

        # delete the snapshot
        delete_snapshot_cmd = 'aks snapshot delete --resource-group {resource_group} --name {snapshot_name} --yes --no-wait'
        self.cmd(delete_snapshot_cmd, checks=[
            self.is_empty()
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_upgrade_node_image_only_cluster(self, resource_group, resource_group_location):
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        node_pool_name = self.create_random_name('c', 6)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'node_pool_name': node_pool_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--nodepool-name {node_pool_name} ' \
                     '--vm-set-type VirtualMachineScaleSets --node-count=1 ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        upgrade_node_image_only_cluster_cmd = 'aks upgrade ' \
                                              '-g {resource_group} ' \
                                              '-n {name} ' \
                                              '--node-image-only ' \
                                              '--yes'
        self.cmd(upgrade_node_image_only_cluster_cmd, checks=[
            self.check(
                'agentPoolProfiles[0].provisioningState', 'UpgradingNodeImageVersion')
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_upgrade_node_image_only_nodepool(self, resource_group, resource_group_location):
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        node_pool_name = self.create_random_name('c', 6)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'node_pool_name': node_pool_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--nodepool-name {node_pool_name} ' \
                     '--vm-set-type VirtualMachineScaleSets --node-count=1 ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        upgrade_node_image_only_nodepool_cmd = 'aks nodepool upgrade ' \
                                               '--resource-group {resource_group} ' \
                                               '--cluster-name {name} ' \
                                               '-n {node_pool_name} ' \
                                               '--node-image-only ' \
                                               '--no-wait'
        self.cmd(upgrade_node_image_only_nodepool_cmd)

        get_nodepool_cmd = 'aks nodepool show ' \
                           '--resource-group={resource_group} ' \
                           '--cluster-name={name} ' \
                           '-n {node_pool_name} '
        self.cmd(get_nodepool_cmd, checks=[
            self.check('provisioningState', 'UpgradingNodeImageVersion')
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_upgrade_nodepool(self, resource_group, resource_group_location):
        create_version, upgrade_version = self._get_versions(resource_group_location)
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'dns_name_prefix': self.create_random_name('cliaksdns', 16),
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'windows_admin_username': 'azureuser1',
            'windows_admin_password': 'replace-Password1234$',
            'nodepool2_name': 'npwin',
            'k8s_version': create_version,
            'upgrade_k8s_version': upgrade_version,
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create AKS cluster
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--dns-name-prefix={dns_name_prefix} --node-count=1 ' \
                     '--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} ' \
                     '--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure ' \
                     '--kubernetes-version={k8s_version} --ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.exists('fqdn'),
            self.exists('nodeResourceGroup'),
            self.check('provisioningState', 'Succeeded'),
            self.check('windowsProfile.adminUsername', 'azureuser1')
        ])

        # add Windows nodepool
        self.cmd('aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --os-type Windows --node-count=1', checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # upgrade cluster control plane only
        self.cmd('aks upgrade --resource-group={resource_group} --name={name} --kubernetes-version={upgrade_k8s_version} --yes', checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # upgrade Windows nodepool
        self.cmd('aks nodepool upgrade --resource-group={resource_group} --cluster-name={name} ' \
                 '--name={nodepool2_name} --kubernetes-version={upgrade_k8s_version} ' \
                 '--aks-custom-headers WindowsContainerRuntime=containerd', checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # delete AKS cluster
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_windows(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'dns_name_prefix': self.create_random_name('cliaksdns', 16),
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'windows_admin_username': 'azureuser1',
            'windows_admin_password': 'replace-Password1234$',
            'nodepool2_name': 'npwin',
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--dns-name-prefix={dns_name_prefix} --node-count=1 ' \
                     '--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} ' \
                     '--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.exists('fqdn'),
            self.exists('nodeResourceGroup'),
            self.check('provisioningState', 'Succeeded'),
            self.check('windowsProfile.adminUsername', 'azureuser1')
        ])

        # nodepool add
        self.cmd('aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --os-type Windows --node-count=1', checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # update Windows license type
        self.cmd('aks update --resource-group={resource_group} --name={name} --enable-ahub', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('windowsProfile.licenseType', 'Windows_Server')
        ])

        # nodepool delete
        self.cmd(
            'aks nodepool delete --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --no-wait', checks=[self.is_empty()])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='eastus')
    def test_aks_create_with_fips(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'dns_name_prefix': self.create_random_name('cliaksdns', 16),
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'nodepool2_name': 'np2',
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-fips-image ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('agentPoolProfiles[0].enableFips', True)
        ])

        # nodepool add
        self.cmd('aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --enable-fips-image', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('enableFips', True)
        ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_ahub(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'dns_name_prefix': self.create_random_name('cliaksdns', 16),
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'windows_admin_username': 'azureuser1',
            'windows_admin_password': 'replace-Password1234$',
            'nodepool2_name': 'npwin',
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--dns-name-prefix={dns_name_prefix} --node-count=1 ' \
                     '--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} ' \
                     '--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure --enable-ahub ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.exists('fqdn'),
            self.exists('nodeResourceGroup'),
            self.check('provisioningState', 'Succeeded'),
            self.check('windowsProfile.adminUsername', 'azureuser1'),
            self.check('windowsProfile.licenseType', 'Windows_Server')
        ])

        # nodepool add
        self.cmd('aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --os-type Windows --node-count=1', checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # update Windows license type
        self.cmd('aks update --resource-group={resource_group} --name={name} --disable-ahub', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('windowsProfile.licenseType', 'None')
        ])

        # nodepool delete
        self.cmd(
            'aks nodepool delete --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --no-wait', checks=[self.is_empty()])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westeurope')
    def test_aks_update_to_msi_cluster(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

        # update to MSI cluster
        self.cmd('aks update --resource-group={resource_group} --name={name} --enable-managed-identity --yes', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('identity.type', 'SystemAssigned')
        ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='eastus')
    def test_aks_create_with_gitops_addon(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} -a gitops ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.gitops.enabled', True),
        ])

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='eastus')
    def test_aks_enable_addon_with_gitops(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.gitops', None),
        ])

        enable_cmd = 'aks enable-addons --addons gitops --resource-group={resource_group} --name={name} -o json'
        self.cmd(enable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.gitops.enabled', True),
        ])

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='eastus')
    def test_aks_disable_addon_gitops(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} -a gitops ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.gitops.enabled', True),
        ])

        disable_cmd = 'aks disable-addons --addons gitops --resource-group={resource_group} --name={name} -o json'
        self.cmd(disable_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('addonProfiles.gitops.enabled', False),
            self.check('addonProfiles.gitops.config', None)
        ])

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westeurope')
    def test_aks_update_to_msi_cluster_with_addons(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --enable-addons monitoring ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

        # update to MSI cluster
        self.cmd('aks update --resource-group={resource_group} --name={name} --enable-managed-identity --yes', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('identity.type', 'SystemAssigned')
        ])

        # check egress
        endpoints = self.cmd('aks egress-endpoints list --resource-group={resource_group} --name={name}').get_output_in_json()
        categories = [e["category"] for e in endpoints]
        assert "addon-monitoring" in categories

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_monitoring_aad_auth_msi(self, resource_group, resource_group_location,):
        aks_name = self.create_random_name('cliakstest', 16)
        self.create_new_cluster_with_monitoring_aad_auth(resource_group, resource_group_location, aks_name, user_assigned_identity=False)

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_monitoring_aad_auth_uai(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.create_new_cluster_with_monitoring_aad_auth(resource_group, resource_group_location, aks_name, user_assigned_identity=True)

    def create_new_cluster_with_monitoring_aad_auth(self, resource_group, resource_group_location, aks_name, user_assigned_identity=False):
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'location': resource_group_location,
            'ssh_key_value': self.generate_ssh_keys()
        })

        if user_assigned_identity:
            uai_cmd = f'identity create -g {resource_group} -n {aks_name}_uai'
            resp = self.cmd(uai_cmd).get_output_in_json()
            identity_id = resp["id"]
            print("********************")
            print(f"identity_id: {identity_id}")
            print("********************")

        # create
        create_cmd = f'aks create --resource-group={resource_group} --name={aks_name} --location={resource_group_location} ' \
                     '--enable-managed-identity ' \
                     '--enable-addons monitoring ' \
                     '--enable-msi-auth-for-monitoring ' \
                     '--node-count 1 ' \
                     '--ssh-key-value={ssh_key_value} '
        create_cmd += f'--assign-identity {identity_id}' if user_assigned_identity else ''

        response = self.cmd(create_cmd, checks=[
            self.check('addonProfiles.omsagent.enabled', True),
            self.check('addonProfiles.omsagent.config.useAADAuth', 'True')
        ]).get_output_in_json()

        cluster_resource_id = response["id"]
        subscription = cluster_resource_id.split("/")[2]
        workspace_resource_id = response["addonProfiles"]["omsagent"]["config"]["logAnalyticsWorkspaceResourceID"]
        workspace_name = workspace_resource_id.split("/")[-1]
        workspace_resource_group = workspace_resource_id.split("/")[4]

        # check that the DCR was created
        dataCollectionRuleName = f"MSCI-{workspace_name}"
        dcr_resource_id = f"/subscriptions/{subscription}/resourceGroups/{workspace_resource_group}/providers/Microsoft.Insights/dataCollectionRules/{dataCollectionRuleName}"
        get_cmd = f'rest --method get --url https://management.azure.com{dcr_resource_id}?api-version=2019-11-01-preview'
        self.cmd(get_cmd, checks=[
            self.check('properties.destinations.logAnalytics[0].workspaceResourceId', f'{workspace_resource_id}')
        ])

        # check that the DCR-A was created
        dcra_resource_id = f"{cluster_resource_id}/providers/Microsoft.Insights/dataCollectionRuleAssociations/send-to-{workspace_name}"
        get_cmd = f'rest --method get --url https://management.azure.com{dcra_resource_id}?api-version=2019-11-01-preview'
        self.cmd(get_cmd, checks=[
            self.check('properties.dataCollectionRuleId', f'{dcr_resource_id}')
        ])

        # make sure monitoring can be smoothly disabled
        self.cmd(f'aks disable-addons -a monitoring -g={resource_group} -n={aks_name}')

        # delete
        self.cmd(f'aks delete -g {resource_group} -n {aks_name} --yes --no-wait', checks=[self.is_empty()])


    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_enable_monitoring_with_aad_auth_msi(self, resource_group, resource_group_location,):
        aks_name = self.create_random_name('cliakstest', 16)
        self.enable_monitoring_existing_cluster_aad_atuh(resource_group, resource_group_location, aks_name, user_assigned_identity=False)

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_enable_monitoring_with_aad_auth_uai(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.enable_monitoring_existing_cluster_aad_atuh(resource_group, resource_group_location, aks_name, user_assigned_identity=True)

    def enable_monitoring_existing_cluster_aad_atuh(self, resource_group, resource_group_location, aks_name, user_assigned_identity=False):
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'location': resource_group_location,
            'ssh_key_value': self.generate_ssh_keys()
        })

        if user_assigned_identity:
            uai_cmd = f'identity create -g {resource_group} -n {aks_name}_uai'
            resp = self.cmd(uai_cmd).get_output_in_json()
            identity_id = resp["id"]
            print("********************")
            print(f"identity_id: {identity_id}")
            print("********************")

        # create
        create_cmd = f'aks create --resource-group={resource_group} --name={aks_name} --location={resource_group_location} ' \
                     '--enable-managed-identity ' \
                     '--node-count 1 ' \
                     '--ssh-key-value={ssh_key_value} '
        create_cmd += f'--assign-identity {identity_id}' if user_assigned_identity else ''
        self.cmd(create_cmd)

        enable_monitoring_cmd = f'aks enable-addons -a monitoring --resource-group={resource_group} --name={aks_name} ' \
                                '--enable-msi-auth-for-monitoring '

        response = self.cmd(enable_monitoring_cmd, checks=[
            self.check('addonProfiles.omsagent.enabled', True),
            self.check('addonProfiles.omsagent.config.useAADAuth', 'True')
        ]).get_output_in_json()

        cluster_resource_id = response["id"]
        subscription = cluster_resource_id.split("/")[2]
        workspace_resource_id = response["addonProfiles"]["omsagent"]["config"]["logAnalyticsWorkspaceResourceID"]
        workspace_name = workspace_resource_id.split("/")[-1]
        workspace_resource_group = workspace_resource_id.split("/")[4]

        # check that the DCR was created
        dataCollectionRuleName = f"MSCI-{workspace_name}"
        dcr_resource_id = f"/subscriptions/{subscription}/resourceGroups/{workspace_resource_group}/providers/Microsoft.Insights/dataCollectionRules/{dataCollectionRuleName}"
        get_cmd = f'rest --method get --url https://management.azure.com{dcr_resource_id}?api-version=2019-11-01-preview'
        self.cmd(get_cmd, checks=[
            self.check('properties.destinations.logAnalytics[0].workspaceResourceId', f'{workspace_resource_id}')
        ])

        # check that the DCR-A was created
        dcra_resource_id = f"{cluster_resource_id}/providers/Microsoft.Insights/dataCollectionRuleAssociations/send-to-{workspace_name}"
        get_cmd = f'rest --method get --url https://management.azure.com{dcra_resource_id}?api-version=2019-11-01-preview'
        self.cmd(get_cmd, checks=[
            self.check('properties.dataCollectionRuleId', f'{dcr_resource_id}')
        ])

        # make sure monitoring can be smoothly disabled
        self.cmd(f'aks disable-addons -a monitoring -g={resource_group} -n={aks_name}')

        # delete
        self.cmd(f'aks delete -g {resource_group} -n {aks_name} --yes --no-wait', checks=[self.is_empty()])

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_monitoring_legacy_auth(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'location': resource_group_location,
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--enable-managed-identity ' \
                     '--enable-addons monitoring ' \
                     '--node-count 1 ' \
                     '--ssh-key-value={ssh_key_value} '
        response = self.cmd(create_cmd, checks=[
            self.check('addonProfiles.omsagent.enabled', True),
            self.exists('addonProfiles.omsagent.config.logAnalyticsWorkspaceResourceID'),
            self.check('addonProfiles.omsagent.config.useAADAuth', 'False')
        ]).get_output_in_json()

        # make sure a DCR was not created

        cluster_resource_id = response["id"]
        subscription = cluster_resource_id.split("/")[2]
        workspace_resource_id = response["addonProfiles"]["omsagent"]["config"]["logAnalyticsWorkspaceResourceID"]
        workspace_name = workspace_resource_id.split("/")[-1]
        workspace_resource_group = workspace_resource_id.split("/")[4]

        try:
            # check that the DCR was created
            dataCollectionRuleName = f"MSCI-{workspace_name}"
            dcr_resource_id = f"/subscriptions/{subscription}/resourceGroups/{workspace_resource_group}/providers/Microsoft.Insights/dataCollectionRules/{dataCollectionRuleName}"
            get_cmd = f'rest --method get --url https://management.azure.com{dcr_resource_id}?api-version=2019-11-01-preview'
            self.cmd(get_cmd, checks=[
                self.check('properties.destinations.logAnalytics[0].workspaceResourceId', f'{workspace_resource_id}')
            ])

            assert False
        except Exception as err:
            pass  # this is expected


        # make sure monitoring can be smoothly disabled
        self.cmd(f'aks disable-addons -a monitoring -g={resource_group} -n={aks_name}')

        # delete
        self.cmd(f'aks delete -g {resource_group} -n {aks_name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_auto_upgrade_channel(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'location': resource_group_location,
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--enable-managed-identity ' \
                     '--auto-upgrade-channel rapid ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('autoUpgradeProfile.upgradeChannel', 'rapid')
        ])

        # update upgrade channel
        self.cmd('aks update --resource-group={resource_group} --name={name} --auto-upgrade-channel stable', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('autoUpgradeProfile.upgradeChannel', 'stable')
        ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_node_config(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'kc_path': _get_test_data_file('kubeletconfig.json'),
            'oc_path': _get_test_data_file('linuxosconfig.json'),
            'ssh_key_value': self.generate_ssh_keys()
        })

        # use custom feature so it does not require subscription to regiter the feature
        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--kubelet-config={kc_path} --linux-os-config={oc_path} ' \
                     '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/CustomNodeConfigPreview ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('agentPoolProfiles[0].kubeletConfig.cpuManagerPolicy', 'static'),
            self.check('agentPoolProfiles[0].kubeletConfig.containerLogMaxSizeMb', 20),
            self.check('agentPoolProfiles[0].linuxOsConfig.swapFileSizeMb', 1500),
            self.check('agentPoolProfiles[0].linuxOsConfig.sysctls.netIpv4TcpTwReuse', True)
        ])

        # nodepool add
        nodepool_cmd = 'aks nodepool add --resource-group={resource_group} --cluster-name={name} --name=nodepool2 --node-count=1 ' \
                       '--kubelet-config={kc_path} --linux-os-config={oc_path} --aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/CustomNodeConfigPreview'
        self.cmd(nodepool_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('kubeletConfig.cpuCfsQuotaPeriod', '200ms'),
            self.check('kubeletConfig.podMaxPids', 120),
            self.check('kubeletConfig.containerLogMaxSizeMb', 20),
            self.check('linuxOsConfig.sysctls.netCoreSomaxconn', 163849)
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_http_proxy_config(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'http_proxy_path': _get_test_data_file('httpproxyconfig.json'),
            'ssh_key_value': self.generate_ssh_keys()
        })

        # use custom feature so it does not require subscription to regiter the feature
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --http-proxy-config={http_proxy_path} ' \
                     '--ssh-key-value={ssh_key_value} -o json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('httpProxyConfig', None),
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_none_private_dns_zone(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--node-count=1 --load-balancer-sku=standard ' \
                     '--enable-private-cluster --private-dns-zone none ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.exists('privateFqdn'),
            self.exists('nodeResourceGroup'),
            self.check('provisioningState', 'Succeeded'),
            self.check('apiServerAccessProfile.privateDNSZone', 'None'),
        ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_private_cluster_public_fqdn(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--enable-private-cluster --node-count=1 ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.exists('privateFqdn'),
            self.exists('fqdn'),
            self.check('provisioningState', 'Succeeded'),
            self.check('apiServerAccessProfile.enablePrivateClusterPublicFqdn', True),
        ])

        # update
        update_cmd = 'aks update --resource-group={resource_group} --name={name} --disable-public-fqdn'
        self.cmd(update_cmd, checks=[
            self.exists('privateFqdn'),
            self.check('fqdn', None),
            self.check('provisioningState', 'Succeeded'),
            self.check('apiServerAccessProfile.enablePrivateClusterPublicFqdn', False),
        ])

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_fqdn_subdomain(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        identity_name = self.create_random_name('cliakstest', 16)
        subdomain_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'identity_name': identity_name,
            'subdomain_name': subdomain_name,
            'location': resource_group_location,
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create private dns zone
        create_private_dns_zone = 'network private-dns zone create --resource-group={resource_group} --name="privatelink.{location}.azmk8s.io"'
        zone = self.cmd(create_private_dns_zone, checks=[
            self.check('provisioningState', 'Succeeded')
        ]).get_output_in_json()
        zone_id = zone["id"]
        assert zone_id is not None
        self.kwargs.update({
            'zone_id': zone_id,
        })

        # create identity
        create_identity = 'identity create --resource-group={resource_group} --name={identity_name}'
        identity = self.cmd(create_identity, checks=[
            self.check('name', identity_name)
        ]).get_output_in_json()
        identity_id = identity["principalId"]
        identity_resource_id = identity["id"]
        assert identity_id is not None
        self.kwargs.update({
            'identity_id': identity_id,
            'identity_resource_id': identity_resource_id,
        })

        # assign
        from unittest import mock
        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            assignment = self.cmd(
                'role assignment create --assignee-object-id={identity_id} --role "Private DNS Zone Contributor" --scope={zone_id} --assignee-principal-type ServicePrincipal').get_output_in_json()
        assert assignment["roleDefinitionId"] is not None

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--node-count=1 --fqdn-subdomain={subdomain_name} --load-balancer-sku=standard ' \
                     '--enable-private-cluster --private-dns-zone={zone_id} --enable-managed-identity --assign-identity {identity_resource_id} ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.exists('privateFqdn'),
            self.exists('fqdnSubdomain'),
            self.exists('nodeResourceGroup'),
            self.check('provisioningState', 'Succeeded'),
            self.check('apiServerAccessProfile.privateDnsZone', zone_id),
        ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_pod_identity_enabled(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'location': resource_group_location,
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--enable-managed-identity ' \
                     '--enable-pod-identity --enable-pod-identity-with-kubenet ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('podIdentityProfile.enabled', True),
            self.check('podIdentityProfile.allowNetworkPluginKubenet', True)
        ])

        # update: disable
        cmd = 'aks update --resource-group={resource_group} --name={name} --disable-pod-identity'
        self.cmd(cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('podIdentityProfile.enabled', None)
        ])

        # update: enable
        cmd = 'aks update --resource-group={resource_group} --name={name} --enable-pod-identity --enable-pod-identity-with-kubenet'
        self.cmd(cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('podIdentityProfile.enabled', True),
            self.check('podIdentityProfile.allowNetworkPluginKubenet', True)
        ])

        # pod identity exception: add
        cmd = ('aks pod-identity exception add --cluster-name={name} --resource-group={resource_group} '
               '--namespace test-namespace --name test-name --pod-labels foo=bar')
        self.cmd(cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('podIdentityProfile.enabled', True),
            self.check(
                'podIdentityProfile.userAssignedIdentityExceptions[0].name', 'test-name'),
            self.check(
                'podIdentityProfile.userAssignedIdentityExceptions[0].namespace', 'test-namespace'),
            self.check(
                'podIdentityProfile.userAssignedIdentityExceptions[0].podLabels.foo', 'bar'),
        ])

        # pod identity exception: update
        cmd = ('aks pod-identity exception update --cluster-name={name} --resource-group={resource_group} '
               '--namespace test-namespace --name test-name --pod-labels foo=bar a=b')
        self.cmd(cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('podIdentityProfile.enabled', True),
            self.check(
                'podIdentityProfile.userAssignedIdentityExceptions[0].name', 'test-name'),
            self.check(
                'podIdentityProfile.userAssignedIdentityExceptions[0].namespace', 'test-namespace'),
            self.check(
                'podIdentityProfile.userAssignedIdentityExceptions[0].podLabels.foo', 'bar'),
            self.check(
                'podIdentityProfile.userAssignedIdentityExceptions[0].podLabels.a', 'b'),
        ])

        # pod identity exception: delete
        cmd = ('aks pod-identity exception delete --cluster-name={name} --resource-group={resource_group} '
               '--namespace test-namespace --name test-name')
        self.cmd(cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('podIdentityProfile.enabled', True),
            self.check(
                'podIdentityProfile.userAssignedIdentityExceptions', None),
        ])

        # delete
        cmd = 'aks delete --resource-group={resource_group} --name={name} --yes --no-wait'
        self.cmd(cmd, checks=[
            self.is_empty(),
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_using_azurecni_with_pod_identity_enabled(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'location': resource_group_location,
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--enable-managed-identity ' \
                     '--enable-pod-identity --network-plugin azure ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('podIdentityProfile.enabled', True)
        ])

        # update: disable
        cmd = 'aks update --resource-group={resource_group} --name={name} --disable-pod-identity'
        self.cmd(cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('podIdentityProfile.enabled', None)
        ])

        # update: enable
        cmd = 'aks update --resource-group={resource_group} --name={name} --enable-pod-identity'
        self.cmd(cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('podIdentityProfile.enabled', True)
        ])

        # pod identity exception: add
        cmd = ('aks pod-identity exception add --cluster-name={name} --resource-group={resource_group} '
               '--namespace test-namespace --name test-name --pod-labels foo=bar')
        self.cmd(cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('podIdentityProfile.enabled', True),
            self.check(
                'podIdentityProfile.userAssignedIdentityExceptions[0].name', 'test-name'),
            self.check(
                'podIdentityProfile.userAssignedIdentityExceptions[0].namespace', 'test-namespace'),
            self.check(
                'podIdentityProfile.userAssignedIdentityExceptions[0].podLabels.foo', 'bar'),
        ])

        # pod identity exception: update
        cmd = ('aks pod-identity exception update --cluster-name={name} --resource-group={resource_group} '
               '--namespace test-namespace --name test-name --pod-labels foo=bar a=b')
        self.cmd(cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('podIdentityProfile.enabled', True),
            self.check(
                'podIdentityProfile.userAssignedIdentityExceptions[0].name', 'test-name'),
            self.check(
                'podIdentityProfile.userAssignedIdentityExceptions[0].namespace', 'test-namespace'),
            self.check(
                'podIdentityProfile.userAssignedIdentityExceptions[0].podLabels.foo', 'bar'),
            self.check(
                'podIdentityProfile.userAssignedIdentityExceptions[0].podLabels.a', 'b'),
        ])

        # pod identity exception: delete
        cmd = ('aks pod-identity exception delete --cluster-name={name} --resource-group={resource_group} '
               '--namespace test-namespace --name test-name')
        self.cmd(cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('podIdentityProfile.enabled', True),
            self.check(
                'podIdentityProfile.userAssignedIdentityExceptions', None),
        ])

        # delete
        cmd = 'aks delete --resource-group={resource_group} --name={name} --yes --no-wait'
        self.cmd(cmd, checks=[
            self.is_empty(),
        ])

    # the pod identity add command creates role assignment with random uuid
    # for this case we cannot use recording to capture the fixture, therefore we need to mark it as live_only
    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_pod_identity_usage(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        identity_name = self.create_random_name('id', 6)
        binding_selector_name = 'binding_test'
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'location': resource_group_location,
            'identity_name': identity_name,
            'binding_selector': binding_selector_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create identity
        cmd = 'identity create --resource-group={resource_group} --name={identity_name} --location={location}'
        application_identity = self.cmd(cmd, checks=[
            self.check('name', identity_name)
        ]).get_output_in_json()
        self.kwargs.update({
            'application_identity_id': application_identity['id'],
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--enable-managed-identity ' \
                     '--enable-pod-identity --enable-pod-identity-with-kubenet ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('podIdentityProfile.enabled', True)
        ])

        # pod identity: add
        cmd = ('aks pod-identity add --cluster-name={name} --resource-group={resource_group} '
               '--namespace test-namespace --name test-name --identity-resource-id={application_identity_id}')
        self.cmd(cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('podIdentityProfile.enabled', True),
            self.check(
                'podIdentityProfile.userAssignedIdentities[0].name', 'test-name'),
            self.check(
                'podIdentityProfile.userAssignedIdentities[0].namespace', 'test-namespace'),
            self.check(
                'podIdentityProfile.userAssignedIdentities[0].provisioningState', 'Assigned'),
            self.check(
                'podIdentityProfile.userAssignedIdentities[0].identity.clientId', application_identity['clientId']),
            self.check(
                'podIdentityProfile.userAssignedIdentities[0].identity.objectId', application_identity['principalId']),
            self.check(
                'podIdentityProfile.userAssignedIdentities[0].identity.resourceId', application_identity['id']),
        ])

        # pod identity: delete
        cmd = ('aks pod-identity delete --cluster-name={name} --resource-group={resource_group} '
               '--namespace test-namespace --name test-name')
        self.cmd(cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('podIdentityProfile.enabled', True),
            self.check('podIdentityProfile.userAssignedIdentities', None),
        ])

        # pod identity: add with binding selector
        cmd = ('aks pod-identity add --cluster-name={name} --resource-group={resource_group} '
               '--namespace test-namespace-binding-selector --name test-name-binding-selector '
               '--identity-resource-id={application_identity_id} --binding-selector={binding_selector}')
        self.cmd(cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('podIdentityProfile.enabled', True),
            self.check(
                'podIdentityProfile.userAssignedIdentities[0].name', 'test-name-binding-selector'),
            self.check(
                'podIdentityProfile.userAssignedIdentities[0].namespace', 'test-namespace-binding-selector'),
            self.check(
                'podIdentityProfile.userAssignedIdentities[0].provisioningState', 'Assigned'),
            self.check(
                'podIdentityProfile.userAssignedIdentities[0].bindingSelector', binding_selector_name),
            self.check(
                'podIdentityProfile.userAssignedIdentities[0].identity.clientId', application_identity['clientId']),
            self.check(
                'podIdentityProfile.userAssignedIdentities[0].identity.objectId', application_identity['principalId']),
            self.check(
                'podIdentityProfile.userAssignedIdentities[0].identity.resourceId', application_identity['id']),
        ])

        # delete
        cmd = 'aks delete --resource-group={resource_group} --name={name} --yes --no-wait'
        self.cmd(cmd, checks=[
            self.is_empty(),
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_update_with_windows_password(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'dns_name_prefix': self.create_random_name('cliaksdns', 16),
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'windows_admin_username': 'azureuser1',
            'windows_admin_password': self.create_random_name('p@0A', 16),
            'nodepool2_name': 'npwin',
            'new_windows_admin_password': self.create_random_name('n!C3', 16),
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--dns-name-prefix={dns_name_prefix} --node-count=1 ' \
                     '--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} ' \
                     '--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.exists('fqdn'),
            self.exists('nodeResourceGroup'),
            self.check('provisioningState', 'Succeeded'),
            self.check('windowsProfile.adminUsername', 'azureuser1')
        ])

        # nodepool add
        self.cmd('aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --os-type Windows --node-count=1', checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # update Windows password
        self.cmd('aks update --resource-group={resource_group} --name={name} --windows-admin-password {new_windows_admin_password}', checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

        # nodepool delete
        self.cmd(
            'aks nodepool delete --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --no-wait', checks=[self.is_empty()])

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_custom_kubelet_identity(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        control_plane_identity_name = self.create_random_name('cliakstest', 16)
        kubelet_identity_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'control_plane_identity_name': control_plane_identity_name,
            'kubelet_identity_name': kubelet_identity_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create control plane identity
        control_plane_identity = 'identity create --resource-group={resource_group} --name={control_plane_identity_name}'
        c_identity = self.cmd(control_plane_identity, checks=[
            self.check('name', control_plane_identity_name)
        ]).get_output_in_json()
        control_plane_identity_resource_id = c_identity["id"]
        assert control_plane_identity_resource_id is not None
        self.kwargs.update({
            'control_plane_identity_resource_id': control_plane_identity_resource_id,
        })

        # create kubelet identity
        kubelet_identity = 'identity create --resource-group={resource_group} --name={kubelet_identity_name}'
        k_identity = self.cmd(kubelet_identity, checks=[
            self.check('name', kubelet_identity_name)
        ]).get_output_in_json()
        kubelet_identity_resource_id = k_identity["id"]
        assert kubelet_identity_resource_id is not None
        self.kwargs.update({
            'kubelet_identity_resource_id': kubelet_identity_resource_id,
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--node-count=1 --enable-managed-identity ' \
                     '--assign-identity {control_plane_identity_resource_id} --assign-kubelet-identity {kubelet_identity_resource_id} ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.exists('identity'),
            self.exists('identityProfile'),
            self.check('provisioningState', 'Succeeded'),
            self.check('identityProfile.kubeletidentity.resourceId',
                       kubelet_identity_resource_id),
        ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_disable_local_accounts(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--enable-managed-identity --disable-local-accounts ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('disableLocalAccounts', True)
        ])

        # update to enable local accounts
        self.cmd('aks update --resource-group={resource_group} --name={name} --enable-local-accounts', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('disableLocalAccounts', False)
        ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_enable_utlra_ssd(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
                     '--node-vm-size Standard_D2s_v3 --zones 1 2 3 --enable-ultra-ssd ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_maintenanceconfiguration(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'mc_path': _get_test_data_file('maintenanceconfig.json'),
            'ssh_key_value': self.generate_ssh_keys()
        })

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # maintenanceconfiguration add
        maintenance_configuration_add_cmd = 'aks maintenanceconfiguration add -g {resource_group} --cluster-name {name} -n default --weekday Monday --start-hour 1'
        self.cmd(
            maintenance_configuration_add_cmd, checks=[
                self.check('timeInWeek[0].day', 'Monday'),
                self.check('timeInWeek[0].day', 'Monday'),
                self.check('timeInWeek[0].hourSlots | contains(@, `1`)', True)]
        )

        # maintenanceconfiguration update (from config file)
        maintenance_configuration_update_cmd = 'aks maintenanceconfiguration update -g {resource_group} --cluster-name {name} -n default --config-file {mc_path}'
        self.cmd(
            maintenance_configuration_update_cmd, checks=[
                self.check("timeInWeek[*].day | contains(@, 'Tuesday') && contains(@, 'Wednesday')", True),
                self.check("timeInWeek[*].hourSlots[*] | contains([0], `2`) && contains([1], `6`)", True),
                self.check("notAllowedTime | length(@) == `2`", True)]
        )

        # maintenanceconfiguration show
        maintenance_configuration_show_cmd = 'aks maintenanceconfiguration show -g {resource_group} --cluster-name {name} -n default'
        self.cmd(
            maintenance_configuration_show_cmd, checks=[
                self.check("name == 'default'", True)]
        )

        # maintenanceconfiguration delete
        maintenance_configuration_delete_cmd = 'aks maintenanceconfiguration delete -g {resource_group} --cluster-name {name} -n default'
        self.cmd(
            maintenance_configuration_delete_cmd, checks=[self.is_empty()])

        # maintenanceconfiguration list
        maintenance_configuration_list_cmd = 'aks maintenanceconfiguration list -g {resource_group} --cluster-name {name}'
        self.cmd(
            maintenance_configuration_list_cmd, checks=[self.is_empty()])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='centraluseuap')
    def test_aks_create_with_windows_gmsa(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'dns_name_prefix': self.create_random_name('cliaksdns', 16),
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'windows_admin_username': 'azureuser1',
            'windows_admin_password': 'replace-Password1234$',
            'nodepool2_name': 'npwin',
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--dns-name-prefix={dns_name_prefix} --node-count=1 ' \
                     '--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} ' \
                     '--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure ' \
                     '--ssh-key-value={ssh_key_value} --enable-windows-gmsa --yes ' \
                     '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKSWindowsGmsaPreview'
        self.cmd(create_cmd, checks=[
            self.exists('fqdn'),
            self.exists('nodeResourceGroup'),
            self.check('provisioningState', 'Succeeded'),
            self.check('windowsProfile.adminUsername', 'azureuser1'),
            self.check('windowsProfile.gmsaProfile.enabled', 'True')
        ])

        # nodepool add
        self.cmd('aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --os-type Windows --node-count=1', checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # nodepool delete
        self.cmd(
            'aks nodepool delete --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --no-wait', checks=[self.is_empty()])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='centraluseuap', preserve_default_location=True)
    def test_aks_create_dualstack_with_default_network(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'ssh_key_value': self.generate_ssh_keys(),
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--ip-families IPv4,IPv6 --ssh-key-value={ssh_key_value} --kubernetes-version 1.21.2 ' \
                     '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-EnableDualStack'

        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('networkProfile.podCidrs[] | length(@)', 2),
            self.check('networkProfile.serviceCidrs[] | length(@)', 2),
            self.check('networkProfile.ipFamilies', ['IPv4', 'IPv6'])
        ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_default_network(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'ssh_key_value': self.generate_ssh_keys(),
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--pod-cidr 172.126.0.0/16 --service-cidr 172.56.0.0/16 --dns-service-ip 172.56.0.10 ' \
                     '--pod-cidrs 172.126.0.0/16 --service-cidrs 172.56.0.0/16 --ip-families IPv4 ' \
                     '--network-plugin kubenet --ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('networkProfile.podCidr', '172.126.0.0/16'),
            self.check('networkProfile.podCidrs', ['172.126.0.0/16']),
            self.check('networkProfile.serviceCidr', '172.56.0.0/16'),
            self.check('networkProfile.serviceCidrs', ['172.56.0.0/16']),
            self.check('networkProfile.ipFamilies', ['IPv4'])
        ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2', preserve_default_location=True)
    def test_aks_create_and_update_outbound_ips(self, resource_group, resource_group_location):
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        init_pip_name = self.create_random_name('cliakstest', 16)
        update_pip_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'init_pip_name': init_pip_name,
            'update_pip_name': update_pip_name,
            'ssh_key_value': self.generate_ssh_keys(),
        })

        create_init_pip = 'network public-ip create -g {resource_group} -n {init_pip_name} --sku Standard'
        init_pip = self.cmd(create_init_pip, checks=[
            self.check('publicIp.provisioningState', 'Succeeded')
        ]).get_output_in_json()

        create_update_pip = 'network public-ip create -g {resource_group} -n {update_pip_name} --sku Standard'
        update_pip = self.cmd(create_update_pip, checks=[
            self.check('publicIp.provisioningState', 'Succeeded')
        ]).get_output_in_json()

        init_pip_id = init_pip['publicIp']['id']
        update_pip_id = update_pip['publicIp']['id']

        assert init_pip_id is not None
        assert update_pip_id is not None
        self.kwargs.update({
            'init_pip_id': init_pip_id,
            'update_pip_id': update_pip_id,
        })

        # create cluster
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--ssh-key-value={ssh_key_value} --load-balancer-outbound-ips {init_pip_id}'

        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('networkProfile.loadBalancerProfile.effectiveOutboundIPs[] | length(@)', 1),
            self.check('networkProfile.loadBalancerProfile.effectiveOutboundIPs[0].id', init_pip_id)
        ])

        # update cluster
        update_cmd = 'aks update -g {resource_group} -n {name} --load-balancer-outbound-ips {update_pip_id}'

        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('networkProfile.loadBalancerProfile.effectiveOutboundIPs[] | length(@)', 1),
            self.check('networkProfile.loadBalancerProfile.effectiveOutboundIPs[0].id', update_pip_id)
        ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='centraluseuap', preserve_default_location=True)
    def test_aks_create_and_update_ipv6_count(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'ssh_key_value': self.generate_ssh_keys(),
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--pod-cidr 172.126.0.0/16 --service-cidr 172.56.0.0/16 --dns-service-ip 172.56.0.10 ' \
                     '--pod-cidrs 172.126.0.0/16,2001:abcd:1234::/64 --service-cidrs 172.56.0.0/16,2001:ffff::/108 ' \
                     '--ip-families IPv4,IPv6 --load-balancer-managed-outbound-ipv6-count 2 ' \
                     '--network-plugin kubenet --ssh-key-value={ssh_key_value} --kubernetes-version 1.21.2 ' \
                     '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-EnableDualStack'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('networkProfile.podCidr', '172.126.0.0/16'),
            self.check('networkProfile.podCidrs', ['172.126.0.0/16', '2001:abcd:1234::/64']),
            self.check('networkProfile.serviceCidr', '172.56.0.0/16'),
            self.check('networkProfile.serviceCidrs', ['172.56.0.0/16', '2001:ffff::/108']),
            self.check('networkProfile.ipFamilies', ['IPv4', 'IPv6']),
            self.check('networkProfile.loadBalancerProfile.managedOutboundIPs.countIpv6', 2),
            self.check('networkProfile.loadBalancerProfile.managedOutboundIPs.count', 1),
            self.check('networkProfile.loadBalancerProfile.effectiveOutboundIPs[] | length(@)', 3)
        ])

        # update
        update_cmd = 'aks update -g {resource_group} -n {name} --load-balancer-managed-outbound-ipv6-count 4'

        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('networkProfile.podCidr', '172.126.0.0/16'),
            self.check('networkProfile.podCidrs', ['172.126.0.0/16', '2001:abcd:1234::/64']),
            self.check('networkProfile.serviceCidr', '172.56.0.0/16'),
            self.check('networkProfile.serviceCidrs', ['172.56.0.0/16', '2001:ffff::/108']),
            self.check('networkProfile.ipFamilies', ['IPv4', 'IPv6']),
            self.check('networkProfile.loadBalancerProfile.managedOutboundIPs.countIpv6', 4),
            self.check('networkProfile.loadBalancerProfile.managedOutboundIPs.count', 1),
            self.check('networkProfile.loadBalancerProfile.effectiveOutboundIPs[] | length(@)', 5)
        ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])
    
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='centraluseuap')
    def test_aks_update_with_windows_gmsa(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'dns_name_prefix': self.create_random_name('cliaksdns', 16),
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'windows_admin_username': 'azureuser1',
            'windows_admin_password': 'replace-Password1234$',
            'nodepool2_name': 'npwin',
            'ssh_key_value': self.generate_ssh_keys()
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--dns-name-prefix={dns_name_prefix} --node-count=1 ' \
                     '--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} ' \
                     '--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure ' \
                     '--ssh-key-value={ssh_key_value}'
        self.cmd(create_cmd, checks=[
            self.exists('fqdn'),
            self.exists('nodeResourceGroup'),
            self.check('provisioningState', 'Succeeded'),
            self.check('windowsProfile.adminUsername', 'azureuser1'),
            self.not_exists('windowsProfile.gmsaProfile')
        ])

        # nodepool add
        self.cmd('aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --os-type Windows --node-count=1', checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # update Windows gmsa
        update_cmd = "aks update --resource-group={resource_group} --name={name} --enable-windows-gmsa --yes " \
                     "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKSWindowsGmsaPreview"
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('windowsProfile.gmsaProfile.enabled', 'True')
        ])

        # nodepool delete
        self.cmd(
            'aks nodepool delete --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --no-wait', checks=[self.is_empty()])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])


    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_nodepool_update_label_msi(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        nodepool1_name = "nodepool1"
        nodepool2_name = "nodepool2"
        nodepool3_name = "nodepool3"
        tags = "key1=value1"
        new_tags = "key2=value2"
        labels = "label1=value1"
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'dns_name_prefix': self.create_random_name('cliaksdns', 16),
            'ssh_key_value': self.generate_ssh_keys(),
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'tags': tags,
            'new_tags': new_tags,
            'labels': labels,
            'nodepool1_name': nodepool1_name,
            'nodepool2_name': nodepool2_name,
            'nodepool3_name': nodepool3_name
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--dns-name-prefix={dns_name_prefix} --node-count=1 --ssh-key-value={ssh_key_value} '
        self.cmd(create_cmd, checks=[
            self.exists('fqdn'),
            self.exists('nodeResourceGroup'),
            self.check('provisioningState', 'Succeeded')
        ])

        # show
        self.cmd('aks show -g {resource_group} -n {name}', checks=[
            self.check('type', '{resource_type}'),
            self.check('name', '{name}'),
            self.exists('nodeResourceGroup'),
            self.check('resourceGroup', '{resource_group}'),
            self.check('agentPoolProfiles[0].count', 1),
            self.check('agentPoolProfiles[0].osType', 'Linux'),
            self.check('agentPoolProfiles[0].vmSize', 'Standard_DS2_v2'),
            self.check('agentPoolProfiles[0].mode', 'System'),
            self.check('dnsPrefix', '{dns_name_prefix}'),
            self.exists('kubernetesVersion')
        ])

        # get-credentials
        fd, temp_path = tempfile.mkstemp()
        self.kwargs.update({'file': temp_path})
        try:
            self.cmd(
                'aks get-credentials -g {resource_group} -n {name} --file "{file}"')
            self.assertGreater(os.path.getsize(temp_path), 0)
        finally:
            os.close(fd)
            os.remove(temp_path)

        self.cmd('aks nodepool update --resource-group={resource_group} --cluster-name={name} --name={nodepool1_name} --labels {labels}', checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

        # nodepool list
        self.cmd('aks nodepool list --resource-group={resource_group} --cluster-name={name}', checks=[
            self.check('[0].mode', 'System'),
            self.check('[0].nodeLabels.label1', 'value1'),
        ])

        # nodepool update nodepool2 label
        self.cmd('aks nodepool update --resource-group={resource_group} --cluster-name={name} --name={nodepool1_name} --labels label1=value2', checks=[
            self.check('nodeLabels.label1', 'value2')
        ])

        # nodepool show
        self.cmd('aks nodepool show --resource-group={resource_group} --cluster-name={name} --name={nodepool1_name}', checks=[
            self.check('nodeLabels.label1', 'value2')
        ])


    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_update_label_msi(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        nodepool1_name = "nodepool1"
        nodepool2_name = "nodepool2"
        tags = "key1=value1"
        new_tags = "key2=value2"
        nodepool_labels = "label1=value1 label2=value2"
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'dns_name_prefix': self.create_random_name('cliaksdns', 16),
            'ssh_key_value': self.generate_ssh_keys(),
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'tags': tags,
            'new_tags': new_tags,
            'nodepool1_name': nodepool1_name,
            'nodepool2_name': nodepool2_name,
            'nodepool_labels': nodepool_labels,
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--dns-name-prefix={dns_name_prefix} --node-count=1 --ssh-key-value={ssh_key_value} '
        self.cmd(create_cmd, checks=[
            self.exists('fqdn'),
            self.exists('nodeResourceGroup'),
            self.check('provisioningState', 'Succeeded')
        ])

        update_cmd = 'aks update --resource-group={resource_group} --name={name} ' \
                     '--nodepool-labels {nodepool_labels}'
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('agentPoolProfiles[0].nodeLabels.label1', 'value1'),
            self.check('agentPoolProfiles[0].nodeLabels.label2', 'value2'),
        ])

        update_cmd = 'aks update --resource-group={resource_group} --name={name} ' \
                     '--nodepool-labels label1=value11'
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('agentPoolProfiles[0].nodeLabels.label1', 'value11'),
            self.check('agentPoolProfiles[0].nodeLabels.label2', None),
        ])
