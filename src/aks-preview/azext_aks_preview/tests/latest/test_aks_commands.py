# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import pty
import subprocess
import tempfile
import time

from azext_aks_preview._consts import CONST_CUSTOM_CA_TEST_CERT
from azext_aks_preview._format import aks_machine_list_table_format
from azext_aks_preview.tests.latest.custom_preparers import (
    AKSCustomResourceGroupPreparer,
)
from azext_aks_preview.tests.latest.recording_processors import KeyReplacer
from azure.cli.command_modules.acs._format import version_to_tuple
from azure.cli.core.azclierror import ClientRequestError
from azure.core.exceptions import (HttpResponseError)
from azure.cli.testsdk import CliTestError, ScenarioTest, live_only
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from knack.util import CLIError


def _get_test_data_file(filename):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(curr_dir, "data", filename)


class AzureKubernetesServiceScenarioTest(ScenarioTest):
    def __init__(self, method_name):
        super(AzureKubernetesServiceScenarioTest, self).__init__(
            method_name, recording_processors=[KeyReplacer()]
        )

    def _get_versions(self, location):
        """Return the previous and current Kubernetes minor release versions, such as ("1.11.6", "1.12.4")."""
        versions = self.cmd(
            "az aks get-versions -l {} --query 'values[*].patchVersions.keys(@)[]'".format(
                location
            )
        ).get_output_in_json()
        # sort by semantic version, from newest to oldest
        versions = sorted(versions, key=version_to_tuple, reverse=True)
        upgrade_version = versions[0]
        # find the first version that doesn't start with the latest major.minor.
        prefix = upgrade_version[: upgrade_version.rfind(".")]
        create_version = next(x for x in versions if not x.startswith(prefix))
        return create_version, upgrade_version

    def _get_version_in_range(
        self, location: str, min_version: str, max_version: str
    ) -> str:
        """Return the version which is greater than min_version and less than max_version."""
        versions = self.cmd(
            "az aks get-versions -l {} --query 'values[*].patchVersions.keys(@)[]'".format(
                location
            )
        ).get_output_in_json()
        versions = sorted(versions, key=version_to_tuple, reverse=True)
        for version in versions:
            if version > min_version and version < max_version:
                return version
        return ""

    def _get_lts_version(self, location):
        """Return the latest LTS version in the given location."""
        data = self.cmd(
            "az aks get-versions -l {}".format(
                location
            )
        ).get_output_in_json()
        lts_versions = []
        for version_block in data.get("values", []):
            caps = version_block.get("capabilities", {})
            sps = caps.get("supportPlan", [])
            for sp in sps:
                if sp == "AKSLongTermSupport":
                    lts_versions.append(version_block.get("version", ""))
                    break
        # remove empty strings
        lts_versions = [x for x in lts_versions if x]
        # sort by semantic version, from newest to oldest
        lts_versions = sorted(lts_versions, key=lambda x: list(map(int, x.split("."))), reverse=True)
        return lts_versions[0] if lts_versions else None

    def _get_asm_supported_revision(self, location):
        revisions_cmd = f"aks mesh get-revisions -l {location}"
        revisions = self.cmd(revisions_cmd).get_output_in_json()
        assert len(revisions["meshRevisions"]) > 0
        return revisions['meshRevisions'][0]['revision']

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
            pre_generated_ssh_key_path = os.path.join(
                acs_base_dir, "tests/latest/data/.ssh/id_rsa.pub"
            )
            if os.path.exists(pre_generated_ssh_key_path):
                return pre_generated_ssh_key_path.replace("\\", "\\\\")

        # In the CLI check-in pipeline scenario, the following fake ssh-key will be used. Each test case will read the ssh-key from
        # a different temporary file during execution, so there will be no race conditions caused by concurrent reading and
        # writing/creating of the same file.
        TEST_SSH_KEY_PUB = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCbIg1guRHbI0lV11wWDt1r2cUdcNd27CJsg+SfgC7miZeubtwUhbsPdhMQsfDyhOWHq1+ZL0M+nJZV63d/1dhmhtgyOqejUwrPlzKhydsbrsdUor+JmNJDdW01v7BXHyuymT8G4s09jCasNOwiufbP/qp72ruu0bIA1nySsvlf9pCQAuFkAnVnf/rFhUlOkhtRpwcq8SUNY2zRHR/EKb/4NWY1JzR4sa3q2fWIJdrrX0DvLoa5g9bIEd4Df79ba7v+yiUBOS0zT2ll+z4g9izHK3EO5d8hL4jYxcjKs+wcslSYRWrascfscLgMlMGh0CdKeNTDjHpGPncaf3Z+FwwwjWeuiNBxv7bJo13/8B/098KlVDl4GZqsoBCEjPyJfV6hO0y/LkRGkk7oHWKgeWAfKtfLItRp00eZ4fcJNK9kCaSMmEugoZWcI7NGbZXzqFWqbpRI7NcDP9+WIQ+i9U5vqWsqd/zng4kbuAJ6UuKqIzB0upYrLShfQE3SAck8oaLhJqqq56VfDuASNpJKidV+zq27HfSBmbXnkR/5AK337dc3MXKJypoK/QPMLKUAP5XLPbs+NddJQV7EZXd29DLgp+fRIg3edpKdO7ZErWhv7d+3Kws+e1Y+ypmR2WIVSwVyBEUfgv2C8Ts9gnTF4pNcEY/S2aBicz5Ew2+jdyGNQQ== test@example.com\n"  # pylint: disable=line-too-long
        _, pathname = tempfile.mkstemp()
        with open(pathname, "w") as key_file:
            key_file.write(TEST_SSH_KEY_PUB)
        return pathname.replace("\\", "\\\\")

    @AllowLargeResponse()
    def test_get_version(self):
        versions_cmd = "aks get-versions -l westus2"
        versions = self.cmd(versions_cmd).get_output_in_json()
        assert len(versions["values"]) > 0

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_create_and_update_with_managed_nat_gateway_outbound(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--vm-set-type VirtualMachineScaleSets -c 1 "
            "--outbound-type=managedNATGateway "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.outboundType", "managedNATGateway"),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--nat-gateway-managed-outbound-ip-count 2 "
            "--nat-gateway-idle-timeout 30 "
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.outboundType", "managedNATGateway"),
                self.check("networkProfile.natGatewayProfile.idleTimeoutInMinutes", 30),
                self.check(
                    "networkProfile.natGatewayProfile.managedOutboundIpProfile.count", 2
                ),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_update_outbound_from_slb_to_natgateway(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--vm-set-type VirtualMachineScaleSets -c 1 "
            "--outbound-type=loadbalancer  --load-balancer-managed-outbound-ip-count 2 "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.outboundType", "loadBalancer"),
                self.check(
                    "networkProfile.loadBalancerProfile.managedOutboundIPs.count", 2
                ),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--nat-gateway-managed-outbound-ip-count 2 "
            "--nat-gateway-idle-timeout 30 "
            "--outbound-type managedNATGateway "
            "--aks-custom-header AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-OutBoundTypeMigrationPreview"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.outboundType", "managedNATGateway"),
                self.check("networkProfile.natGatewayProfile.idleTimeoutInMinutes", 30),
                self.check(
                    "networkProfile.natGatewayProfile.managedOutboundIpProfile.count", 2
                ),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_and_update_with_managed_aad(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--vm-set-type VirtualMachineScaleSets -c 1 "
            "--enable-aad --aad-admin-group-object-ids 00000000-0000-0000-0000-000000000001 "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("aadProfile.managed", True),
                self.check(
                    "aadProfile.adminGroupObjectIDs[0]",
                    "00000000-0000-0000-0000-000000000001",
                ),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--aad-admin-group-object-ids 00000000-0000-0000-0000-000000000002 "
            "--aad-tenant-id 00000000-0000-0000-0000-000000000003 -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("aadProfile.managed", True),
                self.check(
                    "aadProfile.adminGroupObjectIDs[0]",
                    "00000000-0000-0000-0000-000000000002",
                ),
                self.check(
                    "aadProfile.tenantId", "00000000-0000-0000-0000-000000000003"
                ),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="canadacentral"
    )
    def test_aks_create_aadv1_and_update_with_managed_aad(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--vm-set-type VirtualMachineScaleSets -c 1 "
            "--aad-server-app-id 00000000-0000-0000-0000-000000000001 "
            "--aad-server-app-secret fake-secret "
            "--aad-client-app-id 00000000-0000-0000-0000-000000000002 "
            "--aad-tenant-id d5b55040-0c14-48cc-a028-91457fc190d9 "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AADv1AllowCreate "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("aadProfile.managed", None),
                self.check(
                    "aadProfile.serverAppId", "00000000-0000-0000-0000-000000000001"
                ),
                self.check(
                    "aadProfile.clientAppId", "00000000-0000-0000-0000-000000000002"
                ),
                self.check(
                    "aadProfile.tenantId", "d5b55040-0c14-48cc-a028-91457fc190d9"
                ),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--enable-aad "
            "--aad-admin-group-object-ids 00000000-0000-0000-0000-000000000003 "
            "--aad-tenant-id 00000000-0000-0000-0000-000000000004 -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("aadProfile.managed", True),
                self.check(
                    "aadProfile.adminGroupObjectIDs[0]",
                    "00000000-0000-0000-0000-000000000003",
                ),
                self.check(
                    "aadProfile.tenantId", "00000000-0000-0000-0000-000000000004"
                ),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="canadacentral"
    )
    def test_aks_create_nonaad_and_update_with_managed_aad(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--vm-set-type VirtualMachineScaleSets --node-count=1 "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("aadProfile", None),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--enable-aad "
            "--aad-admin-group-object-ids 00000000-0000-0000-0000-000000000001 "
            "--aad-tenant-id 00000000-0000-0000-0000-000000000002 -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("aadProfile.managed", True),
                self.check(
                    "aadProfile.adminGroupObjectIDs[0]",
                    "00000000-0000-0000-0000-000000000001",
                ),
                self.check(
                    "aadProfile.tenantId", "00000000-0000-0000-0000-000000000002"
                ),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_and_update_with_managed_aad_enable_azure_rbac(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--vm-set-type VirtualMachineScaleSets -c 1 "
            "--enable-aad --aad-admin-group-object-ids 00000000-0000-0000-0000-000000000001 "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("aadProfile.managed", True),
                self.check(
                    "aadProfile.adminGroupObjectIDs[0]",
                    "00000000-0000-0000-0000-000000000001",
                ),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--enable-azure-rbac -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("aadProfile.enableAzureRbac", True),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--disable-azure-rbac -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("aadProfile.enableAzureRbac", False),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_and_update_with_node_restriction(
        self, resource_group, resource_group_location
    ):
        specific_version = self._get_version_in_range(
            resource_group_location, "1.22.0", "1.24.0"
        )
        if specific_version == "":
            # supported versions do not meet test requirements, skip
            return
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "k8s_version": specific_version,
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--vm-set-type VirtualMachineScaleSets -c 1 "
            "-k {k8s_version} --enable-node-restriction "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.nodeRestriction.enabled", True),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--disable-node-restriction -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.nodeRestriction.enabled", False),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--enable-node-restriction -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.nodeRestriction.enabled", True),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_and_update_with_vpa(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        _, create_version = self._get_versions(resource_group_location)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "k8s_version": create_version,
            }
        )
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--vm-set-type VirtualMachineScaleSets -c 1 "
            "--enable-vpa "
            "--kubernetes-version={k8s_version} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-VPAPreview "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "workloadAutoScalerProfile.verticalPodAutoscaler.enabled", True
                ),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-VPAPreview "
            "--disable-vpa -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "workloadAutoScalerProfile.verticalPodAutoscaler.enabled", False
                ),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-VPAPreview "
            "--enable-vpa -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "workloadAutoScalerProfile.verticalPodAutoscaler.enabled", True
                ),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_addon_autoscaling(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting

        aks_name = self.create_random_name("cliakstest", 16)
        _, create_version = self._get_versions(resource_group_location)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "k8s_version": create_version,
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--vm-set-type VirtualMachineScaleSets -c 1 "
            "--enable-addon-autoscaling "
            "--kubernetes-version={k8s_version} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-AddonAutoscalingPreview "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "workloadAutoScalerProfile.verticalPodAutoscaler.enabled", True
                ),
                self.check(
                    "workloadAutoScalerProfile.verticalPodAutoscaler.addonAutoscaling", "Enabled"
                )
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_update_with_addon_autoscaling(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting

        aks_name = self.create_random_name("cliakstest", 16)
        _, create_version = self._get_versions(resource_group_location)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "k8s_version": create_version,
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--vm-set-type VirtualMachineScaleSets -c 1 "
            "--kubernetes-version={k8s_version} "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # update to enable
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-AddonAutoscalingPreview "
            "--enable-addon-autoscaling -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "workloadAutoScalerProfile.verticalPodAutoscaler.enabled", True
                ),
                self.check(
                    "workloadAutoScalerProfile.verticalPodAutoscaler.addonAutoscaling", "Enabled"
                ),
            ],
        )

        # update to disable
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-AddonAutoscalingPreview "
            "--disable-addon-autoscaling -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                # disable addon autoscaling should not disable VPA
                self.check(
                    "workloadAutoScalerProfile.verticalPodAutoscaler.enabled", True
                ),
                self.check(
                    "workloadAutoScalerProfile.verticalPodAutoscaler.addonAutoscaling", "Disabled"
                ),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_ingress_appgw_addon(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity "
            "-a ingress-appgw --appgw-subnet-cidr 10.232.0.0/16 "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ingressApplicationGateway.enabled", True),
                self.check(
                    "addonProfiles.ingressApplicationGateway.config.subnetCIDR",
                    "10.232.0.0/16",
                ),
            ],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_byo_subnet_with_ingress_appgw_addon(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        vnet_name = self.create_random_name("cliakstest", 16)
        appgw_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "aks_name": aks_name,
                "vnet_name": vnet_name,
                "appgw_name": appgw_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create virtual network
        create_vnet = (
            "network vnet create --resource-group={resource_group} --name={vnet_name} "
            "--address-prefix 11.0.0.0/16 --subnet-name aks-subnet --subnet-prefix 11.0.0.0/24  -o json"
        )
        vnet = self.cmd(
            create_vnet, checks=[self.check("newVNet.provisioningState", "Succeeded")]
        ).get_output_in_json()

        create_subnet = (
            "network vnet subnet create -n appgw-subnet --resource-group={resource_group} --vnet-name {vnet_name} "
            "--address-prefixes 11.0.1.0/24  -o json"
        )
        self.cmd(create_subnet, checks=[self.check("provisioningState", "Succeeded")])

        vnet_id = vnet["newVNet"]["id"]
        assert vnet_id is not None
        self.kwargs.update(
            {
                "vnet_id": vnet_id,
            }
        )

        # create aks cluster
        create_cmd = (
            "aks create --resource-group={resource_group} --name={aks_name} --enable-managed-identity "
            "--vnet-subnet-id {vnet_id}/subnets/aks-subnet -a ingress-appgw "
            "--appgw-name gateway --appgw-subnet-id {vnet_id}/subnets/appgw-subnet "
            "--yes --ssh-key-value={ssh_key_value} -o json"
        )
        aks_cluster = self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ingressApplicationGateway.enabled", True),
                self.check(
                    "addonProfiles.ingressApplicationGateway.config.applicationGatewayName",
                    "gateway",
                ),
                self.check(
                    "addonProfiles.ingressApplicationGateway.config.subnetId",
                    vnet_id + "/subnets/appgw-subnet",
                ),
            ],
        ).get_output_in_json()

        addon_client_id = aks_cluster["addonProfiles"]["ingressApplicationGateway"][
            "identity"
        ]["clientId"]

        self.kwargs.update(
            {
                "addon_client_id": addon_client_id,
            }
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_byo_appgw_with_ingress_appgw_addon(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        vnet_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "aks_name": aks_name,
                "vnet_name": vnet_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create virtual network
        create_vnet = (
            "network vnet create --resource-group={resource_group} --name={vnet_name} "
            "--address-prefix 11.0.0.0/16 --subnet-name aks-subnet --subnet-prefix 11.0.0.0/24 -o json"
        )
        vnet = self.cmd(
            create_vnet, checks=[self.check("newVNet.provisioningState", "Succeeded")]
        ).get_output_in_json()

        create_subnet = (
            "network vnet subnet create -n appgw-subnet --resource-group={resource_group} --vnet-name {vnet_name} "
            "--address-prefixes 11.0.1.0/24  -o json"
        )
        self.cmd(create_subnet, checks=[self.check("provisioningState", "Succeeded")])

        show_subnet = "network vnet subnet show -n appgw-subnet --resource-group={resource_group} --vnet-name {vnet_name} "
        subnet_details = self.cmd(show_subnet).get_output_in_json()
        if subnet_details.get("networkSecurityGroup"):
            # clean up nsg set by policy, otherwise would block creating appgw
            update_subnet = (
                "network vnet subnet update -n appgw-subnet --resource-group={resource_group} --vnet-name {vnet_name} "
                '--nsg ""'
            )
            self.cmd(
                update_subnet,
                checks=[
                    self.check("provisioningState", "Succeeded"),
                    self.check("networkSecurityGroup", None),
                ],
            )

        vnet_id = vnet["newVNet"]["id"]
        assert vnet_id is not None
        self.kwargs.update(
            {
                "vnet_id": vnet_id,
            }
        )

        # create public ip for app gateway
        create_pip = (
            "network public-ip create -n appgw-ip -g {resource_group} "
            "--allocation-method Static --sku Standard  -o json"
        )
        self.cmd(
            create_pip, checks=[self.check("publicIp.provisioningState", "Succeeded")]
        )

        # create app gateway
        # add priority since this is a mandatory parameter since 2021-08-01 API version for network operations
        create_appgw = (
            "network application-gateway create -n appgw -g {resource_group} "
            "--sku Standard_v2 --public-ip-address appgw-ip --subnet {vnet_id}/subnets/appgw-subnet --priority 1001"
        )
        self.cmd(create_appgw)

        # construct group id
        from msrestazure.tools import parse_resource_id, resource_id

        parsed_vnet_id = parse_resource_id(vnet_id)
        group_id = resource_id(
            subscription=parsed_vnet_id["subscription"],
            resource_group=parsed_vnet_id["resource_group"],
        )
        appgw_id = group_id + "/providers/Microsoft.Network/applicationGateways/appgw"

        self.kwargs.update({"appgw_id": appgw_id, "appgw_group_id": group_id})

        # create aks cluster
        create_cmd = (
            "aks create -n {aks_name} -g {resource_group} --enable-managed-identity "
            "--vnet-subnet-id {vnet_id}/subnets/aks-subnet "
            "-a ingress-appgw --appgw-id {appgw_id} --yes "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        aks_cluster = self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ingressApplicationGateway.enabled", True),
                self.check(
                    "addonProfiles.ingressApplicationGateway.config.applicationGatewayId",
                    appgw_id,
                ),
            ],
        ).get_output_in_json()

        addon_client_id = aks_cluster["addonProfiles"]["ingressApplicationGateway"][
            "identity"
        ]["clientId"]

        self.kwargs.update(
            {
                "addon_client_id": addon_client_id,
            }
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_openservicemesh_addon(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-OpenServiceMesh "
            "-a open-service-mesh --ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.openServiceMesh.enabled", True),
            ],
        )

    @live_only()  # live only is required for test environment setup like `az login`
    @AllowLargeResponse()
    def test_aks_addon_list_available(self):
        list_available_cmd = "aks addon list-available -o json"
        addon_list = self.cmd(list_available_cmd).get_output_in_json()
        assert len(addon_list) == 11
        assert addon_list[0]["name"] == "http_application_routing"
        assert addon_list[1]["name"] == "monitoring"
        assert addon_list[2]["name"] == "virtual-node"
        assert addon_list[3]["name"] == "kube-dashboard"
        assert addon_list[4]["name"] == "azure-policy"
        assert addon_list[5]["name"] == "ingress-appgw"
        assert addon_list[6]["name"] == "confcom"
        assert addon_list[7]["name"] == "open-service-mesh"
        assert addon_list[8]["name"] == "azure-keyvault-secrets-provider"
        assert addon_list[9]["name"] == "gitops"
        assert addon_list[10]["name"] == "web_application_routing"

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_addon_list_all_disabled(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = "aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} -o json"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.openServiceMesh", None),
            ],
        )

        list_cmd = (
            "aks addon list --resource-group={resource_group} --name={name} -o json"
        )
        addon_list = self.cmd(list_cmd).get_output_in_json()

        assert len(addon_list) > 0

        for addon in addon_list:
            assert not addon["enabled"]

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_addon_list_confcom_enabled(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} "
            "-a confcom -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ACCSGXDevicePlugin.enabled", True),
                self.check(
                    "addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled",
                    "false",
                ),
            ],
        )

        list_cmd = (
            "aks addon list --resource-group={resource_group} --name={name} -o json"
        )
        addon_list = self.cmd(list_cmd).get_output_in_json()

        assert len(addon_list) > 0

        for addon in addon_list:
            if addon["name"] == "confcom":
                assert addon["enabled"]
            else:
                assert not addon["enabled"]

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_addon_list_openservicemesh_enabled(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} "
            "-a open-service-mesh -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.openServiceMesh.enabled", True),
            ],
        )

        list_cmd = (
            "aks addon list --resource-group={resource_group} --name={name} -o json"
        )
        addon_list = self.cmd(list_cmd).get_output_in_json()

        assert len(addon_list) > 0

        for addon in addon_list:
            if addon["name"] == "open-service-mesh":
                assert addon["enabled"]
            else:
                assert not addon["enabled"]

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_addon_show_all_disabled(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = "aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} -o json"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.openServiceMesh", None),
            ],
        )

        show_cmd = (
            "aks addon show --resource-group={resource_group} --name={name} "
            "-a open-service-mesh -o json"
        )

        with self.assertRaisesRegexp(
            CLIError, 'Addon "open-service-mesh" is not enabled in this cluster.'
        ):
            self.cmd(show_cmd)

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_addon_show_confcom_enabled(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} "
            "-a confcom -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ACCSGXDevicePlugin.enabled", True),
                self.check(
                    "addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled",
                    "false",
                ),
            ],
        )

        show_cmd = (
            "aks addon show --resource-group={resource_group} --name={name} "
            "-a confcom -o json"
        )

        self.cmd(
            show_cmd,
            checks=[
                self.check("api_key", "ACCSGXDevicePlugin"),
                self.check("name", "confcom"),
                self.exists("config"),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_addon_show_openservicemesh_enabled(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} "
            "-a open-service-mesh -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.openServiceMesh.enabled", True),
            ],
        )

        show_cmd = (
            "aks addon show --resource-group={resource_group} --name={name} "
            "-a open-service-mesh -o json"
        )

        self.cmd(
            show_cmd,
            checks=[
                self.check("api_key", "openServiceMesh"),
                self.check("name", "open-service-mesh"),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_addon_enable_with_openservicemesh(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = "aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} -o json"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.openServiceMesh", None),
            ],
        )

        enable_cmd = "aks addon enable --addon open-service-mesh --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            enable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.openServiceMesh.enabled", True),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_addon_disable_openservicemesh(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} "
            "-a open-service-mesh -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.openServiceMesh.enabled", True),
            ],
        )

        disable_cmd = "aks addon disable --addon open-service-mesh --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            disable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.openServiceMesh.enabled", False),
                self.check("addonProfiles.openServiceMesh.config", None),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_addon_enable_with_azurekeyvaultsecretsprovider(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.azureKeyvaultSecretsProvider", None),
            ],
        )

        enable_cmd = "aks addon enable --addon azure-keyvault-secrets-provider --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            enable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", True),
                self.check(
                    "addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation",
                    "false",
                ),
            ],
        )

        disable_cmd = "aks addon disable --addon azure-keyvault-secrets-provider --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            disable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", False),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.config", None),
            ],
        )

        enable_with_secret_rotation_cmd = "aks addon enable --addon azure-keyvault-secrets-provider --enable-secret-rotation --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            enable_with_secret_rotation_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", True),
                self.check(
                    "addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation",
                    "true",
                ),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_addon_enable_confcom_addon(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} "
            "-o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ACCSGXDevicePlugin", None),
            ],
        )

        enable_cmd = "aks addon enable --addon confcom --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            enable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ACCSGXDevicePlugin.enabled", True),
                self.check(
                    "addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled",
                    "false",
                ),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_addon_disable_confcom_addon(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} "
            "-a confcom -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ACCSGXDevicePlugin.enabled", True),
                self.check(
                    "addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled",
                    "false",
                ),
            ],
        )

        disable_cmd = "aks addon disable --addon confcom --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            disable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ACCSGXDevicePlugin.enabled", False),
                self.check("addonProfiles.ACCSGXDevicePlugin.config", None),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_addon_update_all_disabled(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity --ssh-key-value={ssh_key_value} "
            "-o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ACCSGXDevicePlugin", None),
            ],
        )

        update_cmd = "aks addon update --addon confcom --resource-group={resource_group} --name={name} -o json"
        with self.assertRaisesRegexp(
            CLIError, 'Addon "confcom" is not enabled in this cluster.'
        ):
            self.cmd(update_cmd)

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_addon_update_with_confcom(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ACCSGXDevicePlugin", None),
            ],
        )

        enable_cmd = "aks addon enable --addon confcom --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            enable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ACCSGXDevicePlugin.enabled", True),
                self.check(
                    "addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled",
                    "false",
                ),
            ],
        )

        update_cmd = (
            "aks addon update --resource-group={resource_group} --name={name} "
            "-a confcom --enable-sgxquotehelper -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ACCSGXDevicePlugin.enabled", True),
                self.check(
                    "addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled",
                    "true",
                ),
            ],
        )

        delete_cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            delete_cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_addon_update_with_azurekeyvaultsecretsprovider(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.azureKeyvaultSecretsProvider", None),
            ],
        )

        enable_cmd = "aks addon enable --addon azure-keyvault-secrets-provider --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            enable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", True),
                self.check(
                    "addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation",
                    "false",
                ),
            ],
        )

        update_with_secret_rotation_cmd = "aks addon update --addon azure-keyvault-secrets-provider --enable-secret-rotation --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            update_with_secret_rotation_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", True),
                self.check(
                    "addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation",
                    "true",
                ),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_enable_addon_with_openservicemesh(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.openServiceMesh", None),
            ],
        )

        enable_cmd = "aks enable-addons --addons open-service-mesh --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            enable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.openServiceMesh.enabled", True),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_disable_addon_openservicemesh(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity "
            "-a open-service-mesh --ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.openServiceMesh.enabled", True),
            ],
        )

        disable_cmd = "aks disable-addons --addons open-service-mesh --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            disable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.openServiceMesh.enabled", False),
                self.check("addonProfiles.openServiceMesh.config", None),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_azurekeyvaultsecretsprovider_addon(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "-a azure-keyvault-secrets-provider --ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", True),
                self.check(
                    "addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation",
                    "false",
                ),
                self.check(
                    "addonProfiles.azureKeyvaultSecretsProvider.config.rotationPollInterval",
                    "2m",
                ),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_addon_with_azurekeyvaultsecretsprovider_with_secret_rotation(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "-a azure-keyvault-secrets-provider --enable-secret-rotation --rotation-poll-interval 30m "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", True),
                self.check(
                    "addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation",
                    "true",
                ),
                self.check(
                    "addonProfiles.azureKeyvaultSecretsProvider.config.rotationPollInterval",
                    "30m",
                ),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_enable_addon_with_azurekeyvaultsecretsprovider(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.azureKeyvaultSecretsProvider", None),
            ],
        )

        enable_cmd = "aks enable-addons --addons azure-keyvault-secrets-provider --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            enable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", True),
                self.check(
                    "addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation",
                    "false",
                ),
            ],
        )

        update_enable_cmd = "aks update --resource-group={resource_group} --name={name} --enable-secret-rotation --rotation-poll-interval 120s -o json"
        self.cmd(
            update_enable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", True),
                self.check(
                    "addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation",
                    "true",
                ),
                self.check(
                    "addonProfiles.azureKeyvaultSecretsProvider.config.rotationPollInterval",
                    "120s",
                ),
            ],
        )

        update_disable_cmd = "aks update --resource-group={resource_group} --name={name} --disable-secret-rotation -o json"
        self.cmd(
            update_disable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", True),
                self.check(
                    "addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation",
                    "false",
                ),
                self.check(
                    "addonProfiles.azureKeyvaultSecretsProvider.config.rotationPollInterval",
                    "120s",
                ),
            ],
        )

        disable_cmd = "aks disable-addons --addons azure-keyvault-secrets-provider --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            disable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", False),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.config", None),
            ],
        )

        enable_with_secret_rotation_cmd = "aks enable-addons --addons azure-keyvault-secrets-provider --enable-secret-rotation --rotation-poll-interval 1h --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            enable_with_secret_rotation_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", True),
                self.check(
                    "addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation",
                    "true",
                ),
                self.check(
                    "addonProfiles.azureKeyvaultSecretsProvider.config.rotationPollInterval",
                    "1h",
                ),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_confcom_addon(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity "
            "-a confcom --ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ACCSGXDevicePlugin.enabled", True),
                self.check(
                    "addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled",
                    "false",
                ),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_confcom_addon_helper_enabled(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity "
            "-a confcom --enable-sgxquotehelper --ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ACCSGXDevicePlugin.enabled", True),
                self.check(
                    "addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled",
                    "true",
                ),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_enable_addons_confcom_addon(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ACCSGXDevicePlugin", None),
            ],
        )

        enable_cmd = "aks enable-addons --addons confcom --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            enable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ACCSGXDevicePlugin.enabled", True),
                self.check(
                    "addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled",
                    "false",
                ),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_disable_addons_confcom_addon(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity "
            "-a confcom --ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ACCSGXDevicePlugin.enabled", True),
                self.check(
                    "addonProfiles.ACCSGXDevicePlugin.config.ACCSGXQuoteHelperEnabled",
                    "false",
                ),
            ],
        )

        disable_cmd = "aks disable-addons --addons confcom --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            disable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.ACCSGXDevicePlugin.enabled", False),
                self.check("addonProfiles.ACCSGXDevicePlugin.config", None),
            ],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_virtual_node_addon(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        vnet_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "aks_name": aks_name,
                "vnet_name": vnet_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create virtual network
        create_vnet = (
            "network vnet create --resource-group={resource_group} --name={vnet_name} "
            "--address-prefix 11.0.0.0/16 --subnet-name aks-subnet --subnet-prefix 11.0.0.0/24  -o json"
        )
        vnet = self.cmd(
            create_vnet, checks=[self.check("newVNet.provisioningState", "Succeeded")]
        ).get_output_in_json()

        create_subnet = (
            "network vnet subnet create -n aci-subnet --resource-group={resource_group} --vnet-name {vnet_name} "
            "--address-prefixes 11.0.1.0/24  -o json"
        )
        self.cmd(create_subnet, checks=[self.check("provisioningState", "Succeeded")])

        vnet_id = vnet["newVNet"]["id"]
        assert vnet_id is not None
        self.kwargs.update(
            {
                "vnet_id": vnet_id,
            }
        )

        # create aks cluster
        create_cmd = (
            "aks create --resource-group={resource_group} --name={aks_name} --enable-managed-identity "
            "--vnet-subnet-id {vnet_id}/subnets/aks-subnet --network-plugin azure "
            "-a virtual-node --aci-subnet-name aci-subnet --yes "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.aciConnectorLinux.enabled", True),
                self.check(
                    "addonProfiles.aciConnectorLinux.config.SubnetName", "aci-subnet"
                ),
            ],
        )

        # list addons
        list_cmd = (
            "aks addon list --resource-group={resource_group} --name={aks_name} -o json"
        )
        addon_list = self.cmd(list_cmd).get_output_in_json()

        # check virtual node addon
        assert len(addon_list) > 0
        for addon in addon_list:
            if addon["name"] == "virtual-node":
                assert addon["enabled"]
            else:
                assert not addon["enabled"]

        # delete
        cmd = "aks delete --resource-group={resource_group} --name={aks_name} --yes --no-wait"
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_stop_and_start(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        stop_cmd = "aks stop --resource-group={resource_group} --name={name}"
        self.cmd(stop_cmd)

        start_cmd = "aks start --resource-group={resource_group} --name={name}"
        self.cmd(start_cmd)

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_stop_and_start_private_cluster(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value} --enable-private-cluster"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        stop_cmd = "aks stop --resource-group={resource_group} --name={name}"
        self.cmd(stop_cmd)

        start_cmd = "aks start --resource-group={resource_group} --name={name}"
        self.cmd(start_cmd)

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="centraluseuap"
    )
    def test_aks_abort(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value} --no-wait"
        self.cmd(create_cmd)

        abort_cmd = (
            "aks operation-abort --resource-group={resource_group} --name={name}"
        )
        self.cmd(abort_cmd, checks=[self.is_empty()])

        time.sleep(10)
        show_cmd = "aks show --resource-group={resource_group} --name={name}"
        self.cmd(show_cmd, checks=[self.check("provisioningState", "Canceled")])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_nodepool_abort(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        node_pool_name = self.create_random_name("c", 6)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "node_pool_name": node_pool_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--vm-set-type VirtualMachineScaleSets --node-count=1 "
            "--ssh-key-value={ssh_key_value} "
            "-o json"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        # add nodepool
        self.cmd(
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={node_pool_name} --node-count=2",
            checks=[self.check("provisioningState", "Succeeded")],
        )
        # stop nodepool
        self.cmd(
            "aks nodepool stop --no-wait --resource-group={resource_group} --cluster-name={name} --nodepool-name={node_pool_name} --aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/PreviewStartStopAgentPool"
        )

        abort_cmd = "aks nodepool operation-abort --resource-group={resource_group} --cluster-name={name} --nodepool-name={node_pool_name}"
        self.cmd(abort_cmd, checks=[self.is_empty()])

        time.sleep(10)
        get_nodepool_cmd = (
            "aks nodepool show "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "-n {node_pool_name} "
        )
        self.cmd(
            get_nodepool_cmd,
            checks=[
                self.check("provisioningState", "Canceled"),
                self.check("powerState.code", "Running"),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_machine_cmds(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-managed-identity "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.openServiceMesh", None),
            ],
        )

        node_pool_name = self.create_random_name("c", 6)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "node_pool_name": node_pool_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # add nodepool
        self.cmd(
            "aks nodepool add "
            " --resource-group={resource_group} "
            " --cluster-name={name} "
            " --name={node_pool_name} --node-count=2",
            checks=[self.check("provisioningState", "Succeeded")],
        )

        list_cmd = (
            "aks machine list "
            " --resource-group={resource_group} "
            " --cluster-name={name} --nodepool-name={node_pool_name} -o json"
        )
        machine_list = self.cmd(list_cmd).get_output_in_json()
        assert len(machine_list) == 2
        print(aks_machine_list_table_format(machine_list))

        machine_name = machine_list[0]["name"]
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "node_pool_name": node_pool_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "machine_name": machine_name,
            }
        )
        show_cmd = (
            "aks machine show "
            "--resource-group={resource_group} --cluster-name={name} "
            "--nodepool-name={node_pool_name} --machine-name={machine_name} -o json"
        )
        machine_show = self.cmd(show_cmd).get_output_in_json()
        assert machine_show["name"] == machine_name
        print(machine_show)

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westcentralus"
    )
    def test_aks_create_with_safeguards(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            '--safeguards-level Warning --safeguards-version "v1.0.0" '
            "--enable-addons azure-policy --ssh-key-value={ssh_key_value} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/SafeguardsPreview"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("safeguardsProfile.level", "Warning"),
                self.check("safeguardsProfile.version", "v1.0.0"),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westcentralus"
    )
    def test_aks_update_with_safeguards(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value} "
            "--enable-addons azure-policy "
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            '--safeguards-level Warning --safeguards-version "v1.0.0" '
            "--safeguards-excluded-ns test-ns1 "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/SafeguardsPreview"
        )

        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("safeguardsProfile.level", "Warning"),
                self.check("safeguardsProfile.version", "v1.0.0"),
                self.check("safeguardsProfile.excludedNamespaces[0]", "test-ns1"),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_managed_disk(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--vm-set-type VirtualMachineScaleSets -c 1 "
            "--node-osdisk-type=Managed "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("agentPoolProfiles[0].osDiskType", "Managed"),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_ephemeral_disk(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--vm-set-type VirtualMachineScaleSets -c 1 "
            "--node-osdisk-type=Ephemeral --node-osdisk-size 60 "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("agentPoolProfiles[0].osDiskType", "Ephemeral"),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_create_with_ossku(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--vm-set-type VirtualMachineScaleSets -c 1 "
            "--os-sku CBLMariner "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("agentPoolProfiles[0].osSku", "CBLMariner"),
            ],
        )
        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_nodepool_add_with_workload_runtime(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        node_pool_name = self.create_random_name("c", 6)
        node_pool_name_second = self.create_random_name("c", 6)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "node_pool_name": node_pool_name,
                "node_pool_name_second": node_pool_name_second,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--nodepool-name {node_pool_name} -c 1 "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        self.cmd(
            "aks nodepool add "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "--name={node_pool_name_second} "
            "--workload-runtime WasmWasi",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("workloadRuntime", "WasmWasi"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_nodepool_add_with_ossku(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        node_pool_name = self.create_random_name("c", 6)
        node_pool_name_second = self.create_random_name("c", 6)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "node_pool_name": node_pool_name,
                "node_pool_name_second": node_pool_name_second,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--nodepool-name {node_pool_name} -c 1 "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # nodepool get-upgrades
        self.cmd(
            "aks nodepool add "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "--name={node_pool_name_second} "
            "--os-sku CBLMariner",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("osSku", "CBLMariner"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_nodepool_add_with_ossku_windows2022(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        _, create_version = self._get_versions(resource_group_location)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "windows_admin_username": "azureuser1",
                "windows_admin_password": "replace-Password1234$",
                "windows_nodepool_name": "npwin",
                "k8s_version": create_version,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--dns-name-prefix={dns_name_prefix} --node-count=1 "
            "--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} "
            "--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure "
            "--ssh-key-value={ssh_key_value} --kubernetes-version={k8s_version}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check("windowsProfile.adminUsername", "azureuser1"),
            ],
        )

        # add Windows2022 nodepool
        self.cmd(
            "aks nodepool add "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "--name={windows_nodepool_name} "
            "--node-count=1 "
            "--os-type Windows "
            "--os-sku Windows2022 "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKSWindows2022Preview",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("osSku", "Windows2022"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_nodepool_add_with_disable_windows_outbound_nat(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        _, create_version = self._get_versions(resource_group_location)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "windows_admin_username": "azureuser1",
                "windows_admin_password": "replace-Password1234$",
                "windows_nodepool_name": "npwin",
                "k8s_version": create_version,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--dns-name-prefix={dns_name_prefix} --node-count=1 "
            "--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} "
            "--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure "
            "--ssh-key-value={ssh_key_value} --kubernetes-version={k8s_version} "
            "--outbound-type=managedNATGateway "
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check("windowsProfile.adminUsername", "azureuser1"),
            ],
        )

        # add Windows2019 nodepool
        # Windows2022 does not support this feature yet
        self.cmd(
            "aks nodepool add "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "--name={windows_nodepool_name} "
            "--node-count=1 "
            "--os-type Windows "
            "--os-sku Windows2019 "
            "--disable-windows-outbound-nat "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/DisableWindowsOutboundNATPreview",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("windowsProfile.disableOutboundNat", True),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_create_add_nodepool_with_motd(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        node_pool_name = self.create_random_name("c", 6)
        node_pool_name_second = self.create_random_name("c", 6)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "node_pool_name": node_pool_name,
                "node_pool_name_second": node_pool_name_second,
                "ssh_key_value": self.generate_ssh_keys(),
                "message_of_the_day": _get_test_data_file("motd.txt"),
            }
        )
        # 1. create

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--nodepool-name {node_pool_name} -c 1 "
            "--ssh-key-value={ssh_key_value} "
            "--message-of-the-day={message_of_the_day}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "agentPoolProfiles[0].messageOfTheDay",
                    "VU5BVVRIT1JJWkVEIEFDQ0VTUyBUTyBUSElTIERFVklDRSBJUyBQUk9ISUJJVEVECgpZb3UgbXVzdCBoYXZlIGV4cGxpY2l0LCBhdXRob3JpemVkIHBlcm1pc3Npb24gdG8gYWNjZXNzIG9yIGNvbmZpZ3VyZSB0aGlzIGRldmljZS4gVW5hdXRob3JpemVkIGF0dGVtcHRzIGFuZCBhY3Rpb25zIHRvIGFjY2VzcyBvciB1c2UgdGhpcyBzeXN0ZW0gbWF5IHJlc3VsdCBpbiBjaXZpbCBhbmQvb3IgY3JpbWluYWwgcGVuYWx0aWVzLiBBbGwgYWN0aXZpdGllcyBwZXJmb3JtZWQgb24gdGhpcyBkZXZpY2UgYXJlIGxvZ2dlZCBhbmQgbW9uaXRvcmVkLgo=",
                ),
            ],
        )

        # nodepool get-upgrades
        self.cmd(
            "aks nodepool add "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "--name={node_pool_name_second} "
            "--message-of-the-day={message_of_the_day}",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "messageOfTheDay",
                    "VU5BVVRIT1JJWkVEIEFDQ0VTUyBUTyBUSElTIERFVklDRSBJUyBQUk9ISUJJVEVECgpZb3UgbXVzdCBoYXZlIGV4cGxpY2l0LCBhdXRob3JpemVkIHBlcm1pc3Npb24gdG8gYWNjZXNzIG9yIGNvbmZpZ3VyZSB0aGlzIGRldmljZS4gVW5hdXRob3JpemVkIGF0dGVtcHRzIGFuZCBhY3Rpb25zIHRvIGFjY2VzcyBvciB1c2UgdGhpcyBzeXN0ZW0gbWF5IHJlc3VsdCBpbiBjaXZpbCBhbmQvb3IgY3JpbWluYWwgcGVuYWx0aWVzLiBBbGwgYWN0aXZpdGllcyBwZXJmb3JtZWQgb24gdGhpcyBkZXZpY2UgYXJlIGxvZ2dlZCBhbmQgbW9uaXRvcmVkLgo=",
                ),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_custom_ca_trust_flow(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        node_pool_name = self.create_random_name("c", 6)
        node_pool_name_second = self.create_random_name("c", 6)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "node_pool_name": node_pool_name,
                "node_pool_name_second": node_pool_name_second,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # 1. create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--nodepool-name {node_pool_name} -c 1 "
            "--ssh-key-value={ssh_key_value} "
            "--enable-custom-ca-trust"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("agentPoolProfiles[0].enableCustomCaTrust", "True"),
            ],
        )

        # 2. add nodepool
        self.cmd(
            "aks nodepool add "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "--name={node_pool_name_second} "
            "--os-type Linux "
            "--enable-custom-ca-trust",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("enableCustomCaTrust", "True"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_create_add_nodepool_with_custom_ca_trust_certificates(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        node_pool_name = self.create_random_name("c", 6)
        node_pool_name_second = self.create_random_name("c", 6)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "node_pool_name": node_pool_name,
                "node_pool_name_second": node_pool_name_second,
                "ssh_key_value": self.generate_ssh_keys(),
                "custom_ca_trust_certificates": _get_test_data_file("certs.txt"),
            }
        )

        # 1. create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--nodepool-name {node_pool_name} -c 1 "
            "--ssh-key-value={ssh_key_value} "
            "--aks-custom-headers=AKSHTTPCustomFeatures=Microsoft.ContainerService/CustomCATrustPreview "
            "--custom-ca-trust-certificates={custom_ca_trust_certificates}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "securityProfile.customCaTrustCertificates",
                    [CONST_CUSTOM_CA_TEST_CERT for _ in range(2)],
                ),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_nodepool_drain_timeout(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        np_name = self.create_random_name("clinp", 12)
        self.kwargs.update(
            {
                "name": aks_name,
                "resource_group": resource_group,
                "nodepool_name": np_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--ssh-key-value={ssh_key_value} -c 1"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        add_nodepool_cmd = (
            "aks nodepool add -g {resource_group} --cluster-name {name} -n {nodepool_name} "
            "--mode user --drain-timeout 10"
        )
        self.cmd(
            add_nodepool_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("upgradeSettings.drainTimeoutInMinutes", 10),
            ],
        )

        update_nodepool_cmd = (
            "aks nodepool update -g {resource_group} --cluster-name {name} -n {nodepool_name} "
            "--drain-timeout 60"
        )
        self.cmd(
            update_nodepool_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("upgradeSettings.drainTimeoutInMinutes", 60),
            ],
        )

        # actually running an upgrade is too expensive for these tests.

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_nodepool_node_soak_duration(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        np_name = self.create_random_name("clinp", 12)
        self.kwargs.update(
            {
                "name": aks_name,
                "resource_group": resource_group,
                "nodepool_name": np_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--ssh-key-value={ssh_key_value} -c 1"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        add_nodepool_cmd = (
            "aks nodepool add -g {resource_group} --cluster-name {name} -n {nodepool_name} "
            "--mode user --node-soak-duration 5"
        )
        self.cmd(
            add_nodepool_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("upgradeSettings.nodeSoakDurationInMinutes", 5),
            ],
        )

        update_nodepool_cmd = (
            "aks nodepool update -g {resource_group} --cluster-name {name} -n {nodepool_name} "
            "--node-soak-duration 10"
        )
        self.cmd(
            update_nodepool_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("upgradeSettings.nodeSoakDurationInMinutes", 10),
            ],
        )

        # actually running an upgrade is too expensive for these tests.

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="centraluseuap"
    )
    def test_aks_nodepool_stop_and_start(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("c", 6)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "nodepool_name": nodepool_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create aks cluster
        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )
        # add nodepool
        self.cmd(
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool_name} --node-count=2",
            checks=[self.check("provisioningState", "Succeeded")],
        )
        # stop nodepool
        self.cmd(
            "aks nodepool stop --resource-group={resource_group} --cluster-name={name} --nodepool-name={nodepool_name} --aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/PreviewStartStopAgentPool",
            checks=[self.check("powerState.code", "Stopped")],
        )
        # start nodepool
        self.cmd(
            "aks nodepool start --resource-group={resource_group} --cluster-name={name} --nodepool-name={nodepool_name} --aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/PreviewStartStopAgentPool",
            checks=[self.check("powerState.code", "Running")],
        )
        # delete AKS cluster
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_nodepool_add_with_gpu_instance_profile(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        node_pool_name = self.create_random_name("c", 6)
        node_pool_name_second = self.create_random_name("c", 6)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "node_pool_name": node_pool_name,
                "node_pool_name_second": node_pool_name_second,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--nodepool-name {node_pool_name} -c 1 "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # nodepool get-upgrades
        self.cmd(
            "aks nodepool add "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "--name={node_pool_name_second} "
            "--gpu-instance-profile=MIG3g "
            "-c 1 "
            "--aks-custom-headers UseGPUDedicatedVHD=true "
            "--node-vm-size=standard_nd96asr_v4",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("gpuInstanceProfile", "MIG3g"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )


    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_automatic_sku(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        aks_name = self.create_random_name("cliakstest", 16)
        lst_version = self._get_lts_version(resource_group_location)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create an Automatic cluster
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--sku automatic --node-vm-size standard_ds4_v2 "
            "--aks-custom-header AKSHTTPCustomFeatures=Microsoft.ContainerService/AutomaticSKUPreview,"
            "AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableAPIServerVnetIntegrationPreview,"
            "AKSHTTPCustomFeatures=Microsoft.ContainerService/SafeguardsPreview,"
            "AKSHTTPCustomFeatures=Microsoft.ContainerService/NRGLockdownPreview,"
            "AKSHTTPCustomFeatures=Microsoft.ContainerService/NodeAutoProvisioningPreview "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("sku.name", "Automatic"),
                self.check("sku.tier", "Standard"),
            ],
        )
        
        # scale the cluster
        scale_cluster_cmd = (
            "aks scale --resource-group={resource_group} --name={name} "
            "-c 4"
        )
        self.cmd(
            scale_cluster_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("sku.name", "Automatic"),
                self.check("sku.tier", "Standard"),
            ],
        )
        
        # update from sku name Automatic to Base
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--aks-custom-header AKSHTTPCustomFeatures=Microsoft.ContainerService/AutomaticSKUPreview,"
            "AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableAPIServerVnetIntegrationPreview,"
            "AKSHTTPCustomFeatures=Microsoft.ContainerService/SafeguardsPreview,"
            "AKSHTTPCustomFeatures=Microsoft.ContainerService/NRGLockdownPreview,"
            "AKSHTTPCustomFeatures=Microsoft.ContainerService/NodeAutoProvisioningPreview "
            "--sku base "
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("sku.name", "Base"),
                self.check("sku.tier", "Standard"),
            ],
        ) 

        # delete the cluster
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_nodepool_get_upgrades(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        node_pool_name = self.create_random_name("c", 6)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "node_pool_name": node_pool_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--nodepool-name {node_pool_name} -c 1 "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # nodepool get-upgrades
        self.cmd(
            "aks nodepool get-upgrades "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "--nodepool-name={node_pool_name}",
            checks=[
                self.exists("latestNodeImageVersion"),
                self.check(
                    "type",
                    "Microsoft.ContainerService/managedClusters/agentPools/upgradeProfiles",
                ),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus2"
    )
    def test_aks_nodepool_delete_with_ignore_pod_disruption_budget(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        node_pool_name = self.create_random_name("c", 6)
        node_pool_name_second = self.create_random_name("c", 6)
        node_pool_name_third = self.create_random_name("c", 6)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "node_pool_name": node_pool_name,
                "node_pool_name_second": node_pool_name_second,
                "node_pool_name_third": node_pool_name_third,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--nodepool-name {node_pool_name} -c 1 "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        self.cmd(
            "aks nodepool add "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "-c 1 "
            "--name={node_pool_name_second}",
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )
        self.cmd(
            "aks nodepool add "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "-c 1 "
            "--name={node_pool_name_third}",
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # nodepool delete the third
        self.cmd(
            "aks nodepool delete --resource-group={resource_group} --cluster-name={name} --name={node_pool_name_third} --ignore-pod-disruption-budget=false --no-wait",
            checks=[self.is_empty()],
        )
        # nodepool delete the second
        self.cmd(
            "aks nodepool delete --resource-group={resource_group} --cluster-name={name} --name={node_pool_name_second} --ignore-pod-disruption-budget=true",
            checks=[self.is_empty()],
        )

        # delete the cluster
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_nodepool_snapshot(self, resource_group, resource_group_location):
        create_version, upgrade_version = self._get_versions(resource_group_location)
        aks_name = self.create_random_name("cliakstest", 16)
        aks_name2 = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("c", 6)
        nodepool_name2 = self.create_random_name("c", 6)
        snapshot_name = self.create_random_name("s", 16)
        tagVar = "test"
        tagVal = "value"
        tags = tagVar + "=" + tagVal

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "aks_name2": aks_name2,
                "location": resource_group_location,
                "nodepool_name": nodepool_name,
                "nodepool_name2": nodepool_name2,
                "snapshot_name": snapshot_name,
                "k8s_version": create_version,
                "upgrade_k8s_version": upgrade_version,
                "ssh_key_value": self.generate_ssh_keys(),
                "tags": tags,
            }
        )

        # create an aks cluster not using snapshot
        create_cmd = (
            "aks create --resource-group {resource_group} --name {name} --location {location} "
            "--nodepool-name {nodepool_name} "
            "--node-count 1 "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        response = self.cmd(
            create_cmd, checks=[self.check("provisioningState", "Succeeded")]
        ).get_output_in_json()

        cluster_resource_id = response["id"]
        assert cluster_resource_id is not None
        nodepool_resource_id = cluster_resource_id + "/agentPools/" + nodepool_name
        self.kwargs.update(
            {
                "nodepool_resource_id": nodepool_resource_id,
            }
        )
        print("The nodepool resource id %s " % nodepool_resource_id)

        # create snapshot from the nodepool
        create_snapshot_cmd = (
            "aks nodepool snapshot create --resource-group {resource_group} --name {snapshot_name} --location {location} "
            "--nodepool-id {nodepool_resource_id} -o json"
        )
        response = self.cmd(
            create_snapshot_cmd,
            checks=[self.check("creationData.sourceResourceId", nodepool_resource_id)],
        ).get_output_in_json()

        snapshot_resource_id = response["id"]
        assert snapshot_resource_id is not None
        self.kwargs.update(
            {
                "snapshot_resource_id": snapshot_resource_id,
            }
        )
        print("The snapshot resource id %s " % snapshot_resource_id)

        # update tags on nodepool snapshot
        update_snapshot_cmd = "aks nodepool snapshot update --resource-group {resource_group} --name {snapshot_name} --tags {tags} -o json"
        response = self.cmd(
            update_snapshot_cmd, checks=[self.check("tags", {tagVar: tagVal})]
        ).get_output_in_json()

        # delete the original AKS cluster
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

        # show the snapshot
        show_snapshot_cmd = "aks nodepool snapshot show --resource-group {resource_group} --name {snapshot_name} -o json"
        response = self.cmd(
            show_snapshot_cmd,
            checks=[self.check("creationData.sourceResourceId", nodepool_resource_id)],
        ).get_output_in_json()

        # list the snapshots
        list_snapshot_cmd = (
            "aks nodepool snapshot list --resource-group {resource_group} -o json"
        )
        response = self.cmd(list_snapshot_cmd, checks=[]).get_output_in_json()
        assert len(response) > 0

        # create another aks cluster using this snapshot
        create_cmd = (
            "aks create --resource-group {resource_group} --name {aks_name2} --location {location} "
            "--nodepool-name {nodepool_name} "
            "--node-count 1 --snapshot-id {snapshot_resource_id} "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "agentPoolProfiles[0].creationData.sourceResourceId",
                    snapshot_resource_id,
                ),
            ],
        ).get_output_in_json()

        # add a new nodepool to this cluster using this snapshot
        add_nodepool_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={aks_name2} --name={nodepool_name2} --node-count 1 "
            "--snapshot-id {snapshot_resource_id} -o json"
        )
        self.cmd(
            add_nodepool_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("creationData.sourceResourceId", snapshot_resource_id),
            ],
        )

        # upgrade the nodepool2 using this snapshot again
        # upgrade_node_image_only_nodepool_cmd = 'aks nodepool upgrade ' \
        #                                        '--resource-group {resource_group} ' \
        #                                        '--cluster-name {aks_name2} ' \
        #                                        '-n {nodepool_name2} ' \
        #                                        '--node-image-only ' \
        #                                        '--snapshot-id {snapshot_resource_id} -o json'
        # self.cmd(upgrade_node_image_only_nodepool_cmd)

        # get_nodepool_cmd = 'aks nodepool show ' \
        #                    '--resource-group={resource_group} ' \
        #                    '--cluster-name={aks_name2} ' \
        #                    '-n {nodepool_name2} '
        # self.cmd(get_nodepool_cmd, checks=[
        #     self.check('provisioningState', 'Succeeded'),
        #     self.check('creationData.sourceResourceId', snapshot_resource_id)
        # ])

        # delete the 2nd AKS cluster
        self.cmd(
            "aks delete -g {resource_group} -n {aks_name2} --yes --no-wait",
            checks=[self.is_empty()],
        )

        # delete the snapshot
        delete_snapshot_cmd = "aks nodepool snapshot delete --resource-group {resource_group} --name {snapshot_name} --yes --no-wait"
        self.cmd(delete_snapshot_cmd, checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_nodepool_delete_machines(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("c", 6)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "location": resource_group_location,
                "name": aks_name,
                "nodepool_name": nodepool_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create aks cluster
        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )
        # add nodepool
        self.cmd(
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool_name} --node-count=4",
            checks=[self.check("provisioningState", "Succeeded")],
        )
        # list machines
        list_cmd = 'aks machine list ' \
                   ' --resource-group={resource_group} ' \
                   ' --cluster-name={name} --nodepool-name={nodepool_name} -o json'
        machine_list = self.cmd(list_cmd).get_output_in_json()
        assert len(machine_list) == 4
        aks_machine_list_table_format(machine_list)
        # delete machines
        machine_name1 = machine_list[0]["name"]
        machine_name2 = machine_list[2]["name"]
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "location": resource_group_location,
                "name": aks_name,
                "nodepool_name": nodepool_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "machine_name1": machine_name1,
                "machine_name2": machine_name2,
            }
        )
        self.cmd(
            "aks nodepool delete-machines --resource-group={resource_group} --cluster-name={name} --nodepool-name={nodepool_name} --machine-names {machine_name1} {machine_name2}"
        )
        # list machines after deletion
        machine_list_after = self.cmd(list_cmd).get_output_in_json()
        assert len(machine_list_after) == 2
        # delete AKS cluster
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="westcentralus",
        preserve_default_location=True,
    )
    def test_aks_snapshot(self, resource_group, resource_group_location):
        print(resource_group_location)
        create_version, upgrade_version = self._get_versions(resource_group_location)
        aks_name = self.create_random_name("cliakstest", 16)
        aks_name2 = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("c", 6)
        snapshot_name = self.create_random_name("s", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "aks_name2": aks_name2,
                "location": resource_group_location,
                "nodepool_name": nodepool_name,
                "snapshot_name": snapshot_name,
                "k8s_version": create_version,
                "upgrade_k8s_version": upgrade_version,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create an aks cluster not using snapshot
        create_cmd = (
            "aks create --resource-group {resource_group} --name {name} --location {location} "
            "--nodepool-name {nodepool_name} "
            "--node-count 1 "
            "-k {upgrade_k8s_version} "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        response = self.cmd(
            create_cmd, checks=[self.check("provisioningState", "Succeeded")]
        ).get_output_in_json()

        cluster_resource_id = response["id"]
        assert cluster_resource_id is not None
        self.kwargs.update(
            {
                "cluster_resource_id": cluster_resource_id,
            }
        )
        print("The cluster resource id %s " % cluster_resource_id)

        # create snapshot from the cluster
        create_snapshot_cmd = (
            "aks snapshot create --resource-group {resource_group} --name {snapshot_name} --location {location} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/ManagedClusterSnapshotPreview "
            "--cluster-id {cluster_resource_id} -o json"
        )
        response = self.cmd(
            create_snapshot_cmd,
            checks=[self.check("creationData.sourceResourceId", cluster_resource_id)],
        ).get_output_in_json()

        snapshot_resource_id = response["id"]
        assert snapshot_resource_id is not None
        self.kwargs.update(
            {
                "snapshot_resource_id": snapshot_resource_id,
            }
        )
        print("The snapshot resource id %s " % snapshot_resource_id)

        # delete the original AKS cluster
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

        # show the snapshot
        show_snapshot_cmd = "aks snapshot show --resource-group {resource_group} --name {snapshot_name} -o json"
        response = self.cmd(
            show_snapshot_cmd,
            checks=[self.check("creationData.sourceResourceId", cluster_resource_id)],
        ).get_output_in_json()

        # list the snapshots
        list_snapshot_cmd = (
            "aks snapshot list --resource-group {resource_group} -o json"
        )
        response = self.cmd(list_snapshot_cmd, checks=[]).get_output_in_json()
        assert len(response) > 0

        # create another aks cluster using this snapshot
        create_cmd = (
            "aks create --resource-group {resource_group} --name {aks_name2} --location {location} "
            "--nodepool-name {nodepool_name} "
            "--node-count 1 --cluster-snapshot-id {snapshot_resource_id} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/ManagedClusterSnapshotPreview "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("creationData.sourceResourceId", snapshot_resource_id),
                self.check("kubernetesVersion", upgrade_version),
            ],
        ).get_output_in_json()

        # delete the 2nd AKS cluster
        self.cmd(
            "aks delete -g {resource_group} -n {aks_name2} --yes --no-wait",
            checks=[self.is_empty()],
        )

        # delete the snapshot
        delete_snapshot_cmd = "aks snapshot delete --resource-group {resource_group} --name {snapshot_name} --yes --no-wait"
        self.cmd(delete_snapshot_cmd, checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="westcentralus",
        preserve_default_location=True,
    )
    def test_aks_snapshot_upgrade(self, resource_group, resource_group_location):
        print(resource_group_location)
        create_version, upgrade_version = self._get_versions(resource_group_location)
        aks_name = self.create_random_name("cliakstest", 16)
        aks_name2 = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("c", 6)
        snapshot_name = self.create_random_name("s", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "aks_name2": aks_name2,
                "location": resource_group_location,
                "nodepool_name": nodepool_name,
                "snapshot_name": snapshot_name,
                "k8s_version": create_version,
                "upgrade_k8s_version": upgrade_version,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create an aks cluster not using snapshot
        create_cmd = (
            "aks create --resource-group {resource_group} --name {name} --location {location} "
            "--nodepool-name {nodepool_name} "
            "--node-count 1 "
            "-k {upgrade_k8s_version} "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        response = self.cmd(
            create_cmd, checks=[self.check("provisioningState", "Succeeded")]
        ).get_output_in_json()

        cluster_resource_id = response["id"]
        assert cluster_resource_id is not None
        self.kwargs.update(
            {
                "cluster_resource_id": cluster_resource_id,
            }
        )
        print("The cluster resource id %s " % cluster_resource_id)

        # create snapshot from the cluster
        create_snapshot_cmd = (
            "aks snapshot create --resource-group {resource_group} --name {snapshot_name} --location {location} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/ManagedClusterSnapshotPreview "
            "--cluster-id {cluster_resource_id} -o json"
        )
        response = self.cmd(
            create_snapshot_cmd,
            checks=[self.check("creationData.sourceResourceId", cluster_resource_id)],
        ).get_output_in_json()

        snapshot_resource_id = response["id"]
        assert snapshot_resource_id is not None
        self.kwargs.update(
            {
                "snapshot_resource_id": snapshot_resource_id,
            }
        )
        print("The snapshot resource id %s " % snapshot_resource_id)

        # delete the original AKS cluster
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

        # show the snapshot
        show_snapshot_cmd = "aks snapshot show --resource-group {resource_group} --name {snapshot_name} -o json"
        response = self.cmd(
            show_snapshot_cmd,
            checks=[self.check("creationData.sourceResourceId", cluster_resource_id)],
        ).get_output_in_json()

        # list the snapshots
        list_snapshot_cmd = (
            "aks snapshot list --resource-group {resource_group} -o json"
        )
        response = self.cmd(list_snapshot_cmd, checks=[]).get_output_in_json()
        assert len(response) > 0

        # create another aks cluster not using snapshot
        create_cmd = (
            "aks create --resource-group {resource_group} --name {aks_name2} --location {location} "
            "--nodepool-name {nodepool_name} "
            "--node-count 1 "
            "-k {k8s_version} "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("kubernetesVersion", create_version),
            ],
        ).get_output_in_json()

        # upgrade the second aks cluster using this snapshot
        upgrade_cmd = (
            "aks upgrade --resource-group {resource_group} --name {aks_name2} "
            "--cluster-snapshot-id {snapshot_resource_id} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/ManagedClusterSnapshotPreview --yes -o json"
        )
        self.cmd(
            upgrade_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("creationData.sourceResourceId", snapshot_resource_id),
                self.check("kubernetesVersion", upgrade_version),
            ],
        ).get_output_in_json()
        # delete the 2nd AKS cluster
        self.cmd(
            "aks delete -g {resource_group} -n {aks_name2} --yes --no-wait",
            checks=[self.is_empty()],
        )

        # delete the snapshot
        delete_snapshot_cmd = "aks snapshot delete --resource-group {resource_group} --name {snapshot_name} --yes --no-wait"
        self.cmd(delete_snapshot_cmd, checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="westcentralus",
        preserve_default_location=True,
    )
    def test_aks_snapshot_update(self, resource_group, resource_group_location):
        print(resource_group_location)
        create_version, upgrade_version = self._get_versions(resource_group_location)
        aks_name = self.create_random_name("cliakstest", 16)
        aks_name2 = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("c", 6)
        snapshot_name = self.create_random_name("s", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "aks_name2": aks_name2,
                "location": resource_group_location,
                "nodepool_name": nodepool_name,
                "snapshot_name": snapshot_name,
                "k8s_version": upgrade_version,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create an aks cluster not using snapshot
        create_cmd = (
            "aks create --resource-group {resource_group} --name {name} --location {location} "
            "--nodepool-name {nodepool_name} "
            "--node-count 1 "
            "-k {k8s_version} "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        response = self.cmd(
            create_cmd, checks=[self.check("provisioningState", "Succeeded")]
        ).get_output_in_json()

        cluster_resource_id = response["id"]
        assert cluster_resource_id is not None
        self.kwargs.update(
            {
                "cluster_resource_id": cluster_resource_id,
            }
        )
        print("The cluster resource id %s " % cluster_resource_id)

        # create snapshot from the cluster
        create_snapshot_cmd = (
            "aks snapshot create --resource-group {resource_group} --name {snapshot_name} --location {location} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/ManagedClusterSnapshotPreview "
            "--cluster-id {cluster_resource_id} -o json"
        )
        response = self.cmd(
            create_snapshot_cmd,
            checks=[self.check("creationData.sourceResourceId", cluster_resource_id)],
        ).get_output_in_json()

        snapshot_resource_id = response["id"]
        assert snapshot_resource_id is not None
        self.kwargs.update(
            {
                "snapshot_resource_id": snapshot_resource_id,
            }
        )
        print("The snapshot resource id %s " % snapshot_resource_id)

        # delete the original AKS cluster
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

        # show the snapshot
        show_snapshot_cmd = "aks snapshot show --resource-group {resource_group} --name {snapshot_name} -o json"
        response = self.cmd(
            show_snapshot_cmd,
            checks=[self.check("creationData.sourceResourceId", cluster_resource_id)],
        ).get_output_in_json()

        # list the snapshots
        list_snapshot_cmd = (
            "aks snapshot list --resource-group {resource_group} -o json"
        )
        response = self.cmd(list_snapshot_cmd, checks=[]).get_output_in_json()
        assert len(response) > 0

        # create another aks cluster not using snapshot
        create_cmd = (
            "aks create --resource-group {resource_group} --name {aks_name2} --location {location} "
            "--nodepool-name {nodepool_name} "
            "--node-count 1 "
            "-k {k8s_version} "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("kubernetesVersion", upgrade_version),
            ],
        ).get_output_in_json()

        # update the second aks cluster using this snapshot
        update_cmd = (
            "aks update --resource-group {resource_group} --name {aks_name2} "
            "--cluster-snapshot-id {snapshot_resource_id} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/ManagedClusterSnapshotPreview -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("creationData.sourceResourceId", snapshot_resource_id),
            ],
        ).get_output_in_json()
        # delete the 2nd AKS cluster
        self.cmd(
            "aks delete -g {resource_group} -n {aks_name2} --yes --no-wait",
            checks=[self.is_empty()],
        )

        # delete the snapshot
        delete_snapshot_cmd = "aks snapshot delete --resource-group {resource_group} --name {snapshot_name} --yes --no-wait"
        self.cmd(delete_snapshot_cmd, checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_skip_gpu_driver_install(self, resource_group, resource_group_location):
        print(resource_group_location)
        create_version, upgrade_version = self._get_versions(resource_group_location)
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("c", 6)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "nodepool_name": nodepool_name,
                "k8s_version": upgrade_version,
                "ssh_key_value": self.generate_ssh_keys(),
                "windows_admin_username": "azureuser1",
                "windows_admin_password": "replace-Password1234$",
            }
        )

        # create an aks cluster
        create_cmd = (
            "aks create --resource-group {resource_group} --name {name} --location {location} "
            "--node-count 2 "
            "--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} "
            "--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure "
            "-k {k8s_version} "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd, checks=[self.check("provisioningState", "Succeeded")]
        )

        # create nodepool from the cluster without gpu install
        create_nodepool_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool_name} --os-type windows --node-count 1 "
            "--skip-gpu-driver-install "
            "-k {k8s_version} -o json"
        )
        self.cmd(
            create_nodepool_cmd,
            checks=[self.check("provisioningState", "Succeeded"),
                    self.check('gpuProfile.installGpuDriver', False)],
        )

        # delete the original AKS cluster
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    # @AllowLargeResponse()
    # @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    # def test_aks_upgrade_node_image_only_cluster(self, resource_group, resource_group_location):
    # kwargs for string formatting
    #     aks_name = self.create_random_name('cliakstest', 16)
    #     node_pool_name = self.create_random_name('c', 6)
    #     self.kwargs.update({
    #         'resource_group': resource_group,
    #         'name': aks_name,
    #         'node_pool_name': node_pool_name,
    #         'ssh_key_value': self.generate_ssh_keys()
    #     })

    #     create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
    #                  '--nodepool-name {node_pool_name} ' \
    #                  '--vm-set-type VirtualMachineScaleSets --node-count=1 ' \
    #                  '--ssh-key-value={ssh_key_value} -o json'
    #     self.cmd(create_cmd, checks=[
    #         self.check('provisioningState', 'Succeeded')
    #     ])

    #     upgrade_node_image_only_cluster_cmd = 'aks upgrade ' \
    #                                           '-g {resource_group} ' \
    #                                           '-n {name} ' \
    #                                           '--node-image-only ' \
    #                                           '--yes'
    #     self.cmd(upgrade_node_image_only_cluster_cmd, checks=[
    #         self.check(
    #             'agentPoolProfiles[0].provisioningState', 'UpgradingNodeImageVersion')
    #     ])

    # @AllowLargeResponse()
    # @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    # def test_aks_upgrade_node_image_only_nodepool(self, resource_group, resource_group_location):
    # kwargs for string formatting
    #     aks_name = self.create_random_name('cliakstest', 16)
    #     node_pool_name = self.create_random_name('c', 6)
    #     self.kwargs.update({
    #         'resource_group': resource_group,
    #         'name': aks_name,
    #         'node_pool_name': node_pool_name,
    #         'ssh_key_value': self.generate_ssh_keys()
    #     })

    #     create_cmd = 'aks create --resource-group={resource_group} --name={name} ' \
    #                  '--nodepool-name {node_pool_name} ' \
    #                  '--vm-set-type VirtualMachineScaleSets --node-count=1 ' \
    #                  '--ssh-key-value={ssh_key_value} -o json'
    #     self.cmd(create_cmd, checks=[
    #         self.check('provisioningState', 'Succeeded')
    #     ])

    #     upgrade_node_image_only_nodepool_cmd = 'aks nodepool upgrade ' \
    #                                            '--resource-group {resource_group} ' \
    #                                            '--cluster-name {name} ' \
    #                                            '-n {node_pool_name} ' \
    #                                            '--node-image-only ' \
    #                                            '--no-wait'
    #     self.cmd(upgrade_node_image_only_nodepool_cmd)

    #     get_nodepool_cmd = 'aks nodepool show ' \
    #                        '--resource-group={resource_group} ' \
    #                        '--cluster-name={name} ' \
    #                        '-n {node_pool_name} '
    #     self.cmd(get_nodepool_cmd, checks=[
    #         self.check('provisioningState', 'UpgradingNodeImageVersion')
    #     ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_upgrade_nodepool(self, resource_group, resource_group_location):
        create_version, upgrade_version = self._get_versions(resource_group_location)
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "windows_admin_username": "azureuser1",
                "windows_admin_password": "replace-Password1234$",
                "nodepool2_name": "npwin",
                "k8s_version": create_version,
                "upgrade_k8s_version": upgrade_version,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create AKS cluster
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--dns-name-prefix={dns_name_prefix} --node-count=1 "
            "--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} "
            "--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure "
            "--kubernetes-version={k8s_version} --ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check("windowsProfile.adminUsername", "azureuser1"),
            ],
        )

        # add Windows nodepool
        self.cmd(
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --os-type Windows --node-count=1",
            checks=[self.check("provisioningState", "Succeeded")],
        )

        # upgrade cluster control plane only
        self.cmd(
            "aks upgrade --resource-group={resource_group} --name={name} --kubernetes-version={upgrade_k8s_version} --yes",
            checks=[self.check("provisioningState", "Succeeded")],
        )

        # upgrade Windows nodepool
        self.cmd(
            "aks nodepool upgrade --resource-group={resource_group} --cluster-name={name} "
            "--name={nodepool2_name} --kubernetes-version={upgrade_k8s_version} "
            "--aks-custom-headers WindowsContainerRuntime=containerd --yes",
            checks=[self.check("provisioningState", "Succeeded")],
        )

        # delete AKS cluster
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_windows(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "windows_admin_username": "azureuser1",
                "windows_admin_password": "replace-Password1234$",
                "nodepool2_name": "npwin",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--dns-name-prefix={dns_name_prefix} --node-count=1 "
            "--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} "
            "--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check("windowsProfile.adminUsername", "azureuser1"),
            ],
        )

        # nodepool add
        self.cmd(
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --os-type Windows --node-count=1",
            checks=[self.check("provisioningState", "Succeeded")],
        )

        # update Windows license type
        self.cmd(
            "aks update --resource-group={resource_group} --name={name} --enable-ahub",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("windowsProfile.licenseType", "Windows_Server"),
            ],
        )

        # nodepool delete
        self.cmd(
            "aks nodepool delete --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --no-wait",
            checks=[self.is_empty()],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_create_with_fips(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "nodepool2_name": "np2",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-fips-image "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("agentPoolProfiles[0].enableFips", True),
            ],
        )

        # nodepool add
        self.cmd(
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --enable-fips-image",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("enableFips", True),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    # the availability of features is controlled by a toggle and cannot be fully tested yet,
    # however, existing test results show that the client side works as expected, so exclude it at this moment
    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_nodepool_add_with_artifact_streaming(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "nodepool2_name": "np2",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--ssh-key-value={ssh_key_value} "
            "--aks-custom-headers=AKSHTTPCustomFeatures=Microsoft.ContainerService/ArtifactStreamingPreview "
        )

        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # nodepool add
        self.cmd(
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} "
            "--enable-artifact-streaming --aks-custom-headers=AKSHTTPCustomFeatures=Microsoft.ContainerService/ArtifactStreamingPreview",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "agentpoolProfiles[1].ArtifactStreamingProfile.enabled", True
                ),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_create_update_secure_boot_flow(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        aks_name = self.create_random_name("cliakstest", 16)
        node_pool_name = self.create_random_name("c", 6)
        node_pool_name_second = self.create_random_name("c", 6)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "node_pool_name": node_pool_name,
                "node_pool_name_second": node_pool_name_second,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # 1. create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--nodepool-name {node_pool_name} -c 1 --enable-managed-identity "
            "--ssh-key-value={ssh_key_value} "
            '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/TrustedLaunchPreview '
            "--enable-secure-boot"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("agentPoolProfiles[0].securityProfile.enableSecureBoot", True),
            ],
        )

        # 2. add nodepool
        self.cmd(
            "aks nodepool add "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "--name={node_pool_name_second} "
            "--os-type Linux "
            '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/TrustedLaunchPreview '
            "--enable-secure-boot",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.enableSecureBoot", True),
            ],
        )

        # update to disable
        self.cmd(
            "aks nodepool update --resource-group={resource_group} --cluster-name={name} --name={node_pool_name_second} "
            '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/TrustedLaunchPreview '
            "--disable-secure-boot",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.enableSecureBoot", False),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_create_update_vtpm_flow(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        aks_name = self.create_random_name("cliakstest", 16)
        node_pool_name = self.create_random_name("c", 6)
        node_pool_name_second = self.create_random_name("c", 6)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "node_pool_name": node_pool_name,
                "node_pool_name_second": node_pool_name_second,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # 1. create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--nodepool-name {node_pool_name} -c 1 --enable-managed-identity "
            "--ssh-key-value={ssh_key_value} "
            '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/TrustedLaunchPreview '
            "--enable-vtpm"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("agentPoolProfiles[0].securityProfile.enableVtpm", True),
            ],
        )

        # 2. add nodepool
        self.cmd(
            "aks nodepool add "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "--name={node_pool_name_second} "
            "--os-type Linux "
            '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/TrustedLaunchPreview '
            "--enable-vtpm",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.enableVtpm", True),
            ],
        )

        # update to disable
        self.cmd(
            "aks nodepool update --resource-group={resource_group} --cluster-name={name} --name={node_pool_name_second} "
            '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/TrustedLaunchPreview '
            "--disable-vtpm",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.enableVtpm", False),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_ahub(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "windows_admin_username": "azureuser1",
                "windows_admin_password": "replace-Password1234$",
                "nodepool2_name": "npwin",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--dns-name-prefix={dns_name_prefix} --node-count=1 "
            "--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} "
            "--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure --enable-ahub "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check("windowsProfile.adminUsername", "azureuser1"),
                self.check("windowsProfile.licenseType", "Windows_Server"),
            ],
        )

        # nodepool add
        self.cmd(
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --os-type Windows --node-count=1",
            checks=[self.check("provisioningState", "Succeeded")],
        )

        # update Windows license type
        self.cmd(
            "aks update --resource-group={resource_group} --name={name} --disable-ahub",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("windowsProfile.licenseType", "None"),
            ],
        )

        # nodepool delete
        self.cmd(
            "aks nodepool delete --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --no-wait",
            checks=[self.is_empty()],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westeurope"
    )
    def test_aks_update_to_msi_cluster(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # update to MSI cluster
        self.cmd(
            "aks update --resource-group={resource_group} --name={name} --enable-managed-identity --yes",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("identity.type", "SystemAssigned"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_create_with_gitops_addon(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} -a gitops "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.gitops.enabled", True),
            ],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_enable_addon_with_gitops(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.gitops", None),
            ],
        )

        enable_cmd = "aks enable-addons --addons gitops --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            enable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.gitops.enabled", True),
            ],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_disable_addon_gitops(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} -a gitops "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.gitops.enabled", True),
            ],
        )

        disable_cmd = "aks disable-addons --addons gitops --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            disable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.gitops.enabled", False),
                self.check("addonProfiles.gitops.config", None),
            ],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westeurope"
    )
    def test_aks_update_to_msi_cluster_with_addons(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-addons monitoring "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # update to MSI cluster
        self.cmd(
            "aks update --resource-group={resource_group} --name={name} --enable-managed-identity --yes",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("identity.type", "SystemAssigned"),
            ],
        )

        # check egress
        endpoints = self.cmd(
            "aks egress-endpoints list --resource-group={resource_group} --name={name}"
        ).get_output_in_json()
        categories = [e["category"] for e in endpoints]
        assert "addon-monitoring" in categories

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_monitoring_aad_auth_msi(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.create_new_cluster_with_monitoring_aad_auth(
            resource_group,
            resource_group_location,
            aks_name,
            user_assigned_identity=False,
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_monitoring_aad_auth_uai(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.create_new_cluster_with_monitoring_aad_auth(
            resource_group,
            resource_group_location,
            aks_name,
            user_assigned_identity=True,
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_monitoring_aad_auth_msi_with_syslog(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.create_new_cluster_with_monitoring_aad_auth(
            resource_group,
            resource_group_location,
            aks_name,
            user_assigned_identity=False,
            syslog_enabled=True,
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_monitoring_aad_auth_msi_with_datacollectionsettings(
        self,
        resource_group,
        resource_group_location,
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.create_new_cluster_with_monitoring_aad_auth(
            resource_group,
            resource_group_location,
            aks_name,
            user_assigned_identity=False,
            syslog_enabled=False,
            data_collection_settings=_get_test_data_file("datacollectionsettings.json"),
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_monitoring_aad_auth_uai_with_syslog(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.create_new_cluster_with_monitoring_aad_auth(
            resource_group,
            resource_group_location,
            aks_name,
            user_assigned_identity=True,
            syslog_enabled=True,
        )

    def create_new_cluster_with_monitoring_aad_auth(
        self,
        resource_group,
        resource_group_location,
        aks_name,
        user_assigned_identity=False,
        syslog_enabled=False,
        data_collection_settings=None,
    ):
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        if user_assigned_identity:
            uai_cmd = f"identity create -g {resource_group} -n {aks_name}_uai"
            resp = self.cmd(uai_cmd).get_output_in_json()
            identity_id = resp["id"]
            print("********************")
            print(f"identity_id: {identity_id}")
            print("********************")

        # create
        create_cmd = (
            f"aks create --resource-group={resource_group} --name={aks_name} --location={resource_group_location} "
            "--enable-managed-identity "
            "--enable-addons monitoring "
            "--node-count 1 "
            "--ssh-key-value={ssh_key_value} "
        )
        create_cmd += (
            f"--assign-identity {identity_id} " if user_assigned_identity else ""
        )
        create_cmd += "--enable-syslog " if syslog_enabled else ""
        create_cmd += (
            f"--data-collection-settings {data_collection_settings} "
            if data_collection_settings
            else ""
        )

        response = self.cmd(
            create_cmd,
            checks=[
                self.check("addonProfiles.omsagent.enabled", True),
                self.check("addonProfiles.omsagent.config.useAADAuth", "true"),
            ],
        ).get_output_in_json()

        cluster_resource_id = response["id"]
        subscription = cluster_resource_id.split("/")[2]
        workspace_resource_id = response["addonProfiles"]["omsagent"]["config"][
            "logAnalyticsWorkspaceResourceID"
        ]

        # check that the DCR was created
        location = resource_group_location
        dataCollectionRuleName = f"MSCI-{location}-{aks_name}"
        dataCollectionRuleName = dataCollectionRuleName[0:64]
        dcr_resource_id = f"/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Insights/dataCollectionRules/{dataCollectionRuleName}"
        get_cmd = f"rest --method get --url https://management.azure.com{dcr_resource_id}?api-version=2022-06-01"
        self.cmd(
            get_cmd,
            checks=[
                self.check(
                    "properties.destinations.logAnalytics[0].workspaceResourceId",
                    f"{workspace_resource_id}",
                )
            ],
        )

        if syslog_enabled:
            self.cmd(
                get_cmd,
                checks=[
                    self.check(
                        "properties.dataSources.syslog[0].streams[0]",
                        "Microsoft-Syslog",
                    )
                ],
            )

        if data_collection_settings:
            self.cmd(
                get_cmd,
                checks=[
                    self.check(
                        "properties.dataSources.extensions[0].name",
                        "ContainerInsightsExtension",
                    ),
                    self.check(
                        "properties.dataSources.extensions[0].extensionSettings.dataCollectionSettings.interval",
                        "1m",
                    ),
                    self.check(
                        "properties.dataSources.extensions[0].extensionSettings.dataCollectionSettings.namespaceFilteringMode",
                        "Include",
                    ),
                    self.check(
                        "properties.dataSources.extensions[0].extensionSettings.dataCollectionSettings.namespaces[0]",
                        "kube-system",
                    ),
                    self.check(
                        "properties.dataSources.extensions[0].extensionSettings.dataCollectionSettings.streams[0]",
                        "Microsoft-ContainerLogV2",
                    ),
                    self.check(
                        "properties.dataFlows[0].streams[0]",
                        "Microsoft-ContainerLogV2",
                    ),
                    self.check(
                        "properties.dataSources.extensions[0].extensionSettings.dataCollectionSettings.enableContainerLogV2",
                        True,
                    ),
                ],
            )

        # check that the DCR-A was created
        dcra_resource_id = f"{cluster_resource_id}/providers/Microsoft.Insights/dataCollectionRuleAssociations/ContainerInsightsExtension"
        get_cmd = f"rest --method get --url https://management.azure.com{dcra_resource_id}?api-version=2022-06-01"
        self.cmd(
            get_cmd,
            checks=[
                self.check("properties.dataCollectionRuleId", f"{dcr_resource_id}")
            ],
        )

        # make sure monitoring can be smoothly disabled
        self.cmd(f"aks disable-addons -a monitoring -g={resource_group} -n={aks_name}")

        # delete
        self.cmd(
            f"aks delete -g {resource_group} -n {aks_name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_enable_monitoring_with_aad_auth_msi(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.enable_monitoring_existing_cluster_aad_atuh(
            resource_group,
            resource_group_location,
            aks_name,
            user_assigned_identity=False,
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_enable_monitoring_with_aad_auth_uai(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.enable_monitoring_existing_cluster_aad_atuh(
            resource_group,
            resource_group_location,
            aks_name,
            user_assigned_identity=True,
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_enable_monitoring_with_aad_auth_msi_with_syslog(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.enable_monitoring_existing_cluster_aad_atuh(
            resource_group,
            resource_group_location,
            aks_name,
            user_assigned_identity=False,
            syslog_enabled=True,
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_enable_monitoring_with_aad_auth_uai_with_syslog(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.enable_monitoring_existing_cluster_aad_atuh(
            resource_group,
            resource_group_location,
            aks_name,
            user_assigned_identity=True,
            syslog_enabled=True,
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_addon_enable_monitoring_with_aad_auth_msi_with_syslog(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.enable_monitoring_existing_cluster_aad_atuh(
            resource_group,
            resource_group_location,
            aks_name,
            new_addon_cmd=True,
            user_assigned_identity=False,
            syslog_enabled=True,
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_addon_enable_monitoring_with_aad_auth_uai_with_syslog(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.enable_monitoring_existing_cluster_aad_atuh(
            resource_group,
            resource_group_location,
            aks_name,
            new_addon_cmd=True,
            user_assigned_identity=True,
            syslog_enabled=True,
        )

    def enable_monitoring_existing_cluster_aad_atuh(
        self,
        resource_group,
        resource_group_location,
        aks_name,
        new_addon_cmd=False,
        user_assigned_identity=False,
        syslog_enabled=False,
    ):
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        if user_assigned_identity:
            uai_cmd = f"identity create -g {resource_group} -n {aks_name}_uai"
            resp = self.cmd(uai_cmd).get_output_in_json()
            identity_id = resp["id"]
            print("********************")
            print(f"identity_id: {identity_id}")
            print("********************")

        # create
        create_cmd = (
            f"aks create --resource-group={resource_group} --name={aks_name} --location={resource_group_location} "
            "--enable-managed-identity "
            "--node-count 1 "
            "--ssh-key-value={ssh_key_value} "
        )
        create_cmd += (
            f"--assign-identity {identity_id}" if user_assigned_identity else ""
        )
        self.cmd(create_cmd)

        if new_addon_cmd:
            enable_monitoring_cmd = "aks addon enable -a monitoring "
        else:
            enable_monitoring_cmd = "aks enable-addons -a monitoring "
        enable_monitoring_cmd += f"--resource-group={resource_group} --name={aks_name} "
        if syslog_enabled:
            enable_monitoring_cmd += "--enable-syslog "

        response = self.cmd(
            enable_monitoring_cmd,
            checks=[
                self.check("addonProfiles.omsagent.enabled", True),
                self.check("addonProfiles.omsagent.config.useAADAuth", "true"),
            ],
        ).get_output_in_json()

        cluster_resource_id = response["id"]
        subscription = cluster_resource_id.split("/")[2]
        workspace_resource_id = response["addonProfiles"]["omsagent"]["config"][
            "logAnalyticsWorkspaceResourceID"
        ]

        # check that the DCR was created
        location = resource_group_location
        dataCollectionRuleName = f"MSCI-{location}-{aks_name}"
        dataCollectionRuleName = dataCollectionRuleName[0:64]
        dcr_resource_id = f"/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Insights/dataCollectionRules/{dataCollectionRuleName}"
        get_cmd = f"rest --method get --url https://management.azure.com{dcr_resource_id}?api-version=2022-06-01"
        self.cmd(
            get_cmd,
            checks=[
                self.check(
                    "properties.destinations.logAnalytics[0].workspaceResourceId",
                    f"{workspace_resource_id}",
                )
            ],
        )

        if syslog_enabled:
            self.cmd(
                get_cmd,
                checks=[
                    self.check(
                        "properties.dataSources.syslog[0].streams[0]",
                        "Microsoft-Syslog",
                    )
                ],
            )

        # check that the DCR-A was created
        dcra_resource_id = f"{cluster_resource_id}/providers/Microsoft.Insights/dataCollectionRuleAssociations/ContainerInsightsExtension"
        get_cmd = f"rest --method get --url https://management.azure.com{dcra_resource_id}?api-version=2022-06-01"
        self.cmd(
            get_cmd,
            checks=[
                self.check("properties.dataCollectionRuleId", f"{dcr_resource_id}")
            ],
        )

        # make sure monitoring can be smoothly disabled
        self.cmd(f"aks disable-addons -a monitoring -g={resource_group} -n={aks_name}")

        # delete
        self.cmd(
            f"aks delete -g {resource_group} -n {aks_name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_monitoring_legacy_auth(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--enable-managed-identity "
            "--enable-addons monitoring "
            "--node-count 1 "
            "--ssh-key-value={ssh_key_value} "
        )
        response = self.cmd(
            create_cmd,
            checks=[
                self.check("addonProfiles.omsagent.enabled", True),
                self.exists(
                    "addonProfiles.omsagent.config.logAnalyticsWorkspaceResourceID"
                ),
            ],
        ).get_output_in_json()

        # make sure a DCR was not created

        cluster_resource_id = response["id"]
        subscription = cluster_resource_id.split("/")[2]
        workspace_resource_id = response["addonProfiles"]["omsagent"]["config"][
            "logAnalyticsWorkspaceResourceID"
        ]

        try:
            # check that the DCR was created
            location = resource_group_location
            dataCollectionRuleName = f"MSCI-{location}-{aks_name}"
            dataCollectionRuleName = dataCollectionRuleName[0:64]
            dcr_resource_id = f"/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Insights/dataCollectionRules/{dataCollectionRuleName}"
            get_cmd = f"rest --method get --url https://management.azure.com{dcr_resource_id}?api-version=2022-06-01"
            self.cmd(
                get_cmd,
                checks=[
                    self.check(
                        "properties.destinations.logAnalytics[0].workspaceResourceId",
                        f"{workspace_resource_id}",
                    )
                ],
            )

            assert False
        except Exception:
            pass  # this is expected

        # make sure monitoring can be smoothly disabled
        self.cmd(f"aks disable-addons -a monitoring -g={resource_group} -n={aks_name}")

        # delete
        self.cmd(
            f"aks delete -g {resource_group} -n {aks_name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_auto_upgrade_channel(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--enable-managed-identity "
            "--auto-upgrade-channel rapid "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("autoUpgradeProfile.upgradeChannel", "rapid"),
            ],
        )

        # update upgrade channel
        self.cmd(
            "aks update --resource-group={resource_group} --name={name} --auto-upgrade-channel stable",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("autoUpgradeProfile.upgradeChannel", "stable"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_node_os_upgrade_channel(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--enable-managed-identity "
            "--node-os-upgrade-channel NodeImage "
            "--ssh-key-value={ssh_key_value} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/NodeOSUpgradeChannelPreview"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("autoUpgradeProfile.nodeOsUpgradeChannel", "NodeImage"),
            ],
        )

        # update node os upgrade channel
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--node-os-upgrade-channel None "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/NodeOSUpgradeChannelPreview"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("autoUpgradeProfile.nodeOsUpgradeChannel", "None"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_auto_upgrade_channel_and_node_os_upgrade_channel(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--enable-managed-identity "
            "--auto-upgrade-channel rapid "
            "--node-os-upgrade-channel NodeImage "
            "--ssh-key-value={ssh_key_value} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/NodeOSUpgradeChannelPreview"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("autoUpgradeProfile.upgradeChannel", "rapid"),
                self.check("autoUpgradeProfile.nodeOsUpgradeChannel", "NodeImage"),
            ],
        )

        # update auto upgrade channel and node os upgrade channel
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--auto-upgrade-channel stable --node-os-upgrade-channel None "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/NodeOSUpgradeChannelPreview"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("autoUpgradeProfile.upgradeChannel", "stable"),
                self.check("autoUpgradeProfile.nodeOsUpgradeChannel", "None"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_and_update_with_nrg_restriction_level(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--enable-managed-identity "
            "--nrg-lockdown-restriction-level ReadOnly "
            "--ssh-key-value={ssh_key_value} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/NRGLockdownPreview"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("nodeResourceGroupProfile.restrictionLevel", "ReadOnly"),
            ],
        )

        # update the nrg restriction level
        self.cmd(
            "aks update --resource-group={resource_group} --name={name} --nrg-lockdown-restriction-level Unrestricted --aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/NRGLockdownPreview",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("nodeResourceGroupProfile.restrictionLevel", "Unrestricted"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_node_config(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "kc_path": _get_test_data_file("kubeletconfig.json"),
                "oc_path": _get_test_data_file("linuxosconfig.json"),
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # use custom feature so it does not require subscription to regiter the feature
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--kubelet-config={kc_path} --linux-os-config={oc_path} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/CustomNodeConfigPreview "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "agentPoolProfiles[0].kubeletConfig.cpuManagerPolicy", "static"
                ),
                self.check(
                    "agentPoolProfiles[0].kubeletConfig.containerLogMaxSizeMb", 20
                ),
                self.check("agentPoolProfiles[0].linuxOsConfig.swapFileSizeMb", 1500),
                self.check(
                    "agentPoolProfiles[0].linuxOsConfig.sysctls.netIpv4TcpTwReuse", True
                ),
            ],
        )

        # nodepool add
        nodepool_cmd = (
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} --name=nodepool2 --node-count=1 "
            "--kubelet-config={kc_path} --linux-os-config={oc_path} --aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/CustomNodeConfigPreview"
        )
        self.cmd(
            nodepool_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("kubeletConfig.cpuCfsQuotaPeriod", "200ms"),
                self.check("kubeletConfig.podMaxPids", 120),
                self.check("kubeletConfig.containerLogMaxSizeMb", 20),
                self.check("linuxOsConfig.sysctls.netCoreSomaxconn", 163849),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_and_update_with_http_proxy_config(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "http_proxy_path": _get_test_data_file("httpproxyconfig.json"),
                "custom_data_path": _get_test_data_file("setup_proxy.sh"),
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_vnet_cmd = "network vnet create \
            --resource-group={resource_group} \
            --name={name} \
            --address-prefixes 10.42.0.0/16 \
            --subnet-name aks-subnet \
            --subnet-prefix 10.42.1.0/24"

        create_subnet_cmd = "network vnet subnet create \
            --resource-group={resource_group} \
            --vnet-name={name} \
            --name proxy-subnet \
            --address-prefix 10.42.3.0/24"

        show_subnet_cmd = "network vnet subnet show \
            --resource-group={resource_group} \
            --vnet-name={name} \
            --name aks-subnet"

        # name below MUST match the name used in testcerts for httpproxyconfig.json.
        # otherwise the VM will not present a cert with correct hostname
        # else, change the cert to have the correct hostname (harder)
        create_vm_cmd = 'vm create \
            --resource-group={resource_group} \
            --name=cli-proxy-vm \
            --image Canonical:0001-com-ubuntu-server-focal:20_04-lts:latest \
            --ssh-key-values @{ssh_key_value} \
            --public-ip-address "" \
            --custom-data {custom_data_path} \
            --vnet-name {name} \
            --subnet proxy-subnet'

        self.cmd(
            create_vnet_cmd,
            checks=[self.check("newVNet.provisioningState", "Succeeded")],
        )

        self.cmd(
            create_subnet_cmd, checks=[self.check("provisioningState", "Succeeded")]
        )

        subnet_output = self.cmd(show_subnet_cmd).get_output_in_json()
        subnet_id = subnet_output["id"]
        assert subnet_id is not None

        self.cmd(create_vm_cmd)

        self.kwargs.update(
            {
                "vnet_subnet_id": subnet_id,
            }
        )

        # use custom feature so it does not require subscription to regiter the feature
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --http-proxy-config={http_proxy_path} "
            "--ssh-key-value={ssh_key_value} --enable-managed-identity --yes --vnet-subnet-id {vnet_subnet_id} -o json"
        )

        self.cmd(
            create_cmd,
            checks=[
                self.check("httpProxyConfig.httpProxy", "http://cli-proxy-vm:3128/"),
                self.check("httpProxyConfig.httpsProxy", "https://cli-proxy-vm:3129/"),
                self.check(
                    "httpProxyConfig.trustedCa",
                    "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUZHekNDQXdPZ0F3SUJBZ0lVT1FvajhDTFpkc2Vscjk3cnZJd3g1T0xEc3V3d0RRWUpLb1pJaHZjTkFRRUwKQlFBd0Z6RVZNQk1HQTFVRUF3d01ZMnhwTFhCeWIzaDVMWFp0TUI0WERUSXlNRE13T0RFMk5EUTBOMW9YRFRNeQpNRE13TlRFMk5EUTBOMW93RnpFVk1CTUdBMVVFQXd3TVkyeHBMWEJ5YjNoNUxYWnRNSUlDSWpBTkJna3Foa2lHCjl3MEJBUUVGQUFPQ0FnOEFNSUlDQ2dLQ0FnRUEvTVB0VjVCVFB0NmNxaTRSZE1sbXIzeUlzYTJ1anpjaHh2NGgKanNDMUR0blJnb3M1UzQxUEgwcmkrM3RUU1ZYMzJ5cndzWStyRDFZUnVwbTZsbUU3R2hVNUkwR2k5b3prU0YwWgpLS2FKaTJveXBVL0ZCK1FQcXpvQ1JzTUV3R0NibUtGVmw4VnVoeW5kWEs0YjRrYmxyOWJsL2V1d2Q3TThTYnZ6CldVam5lRHJRc2lJc3J6UFQ0S0FaTHFjdHpEZTRsbFBUN1lLYTMzaGlFUE9mdldpWitkcWthUUE5UDY0eFhTeW4KZkhYOHVWQUozdUJWSmVHeEQwcGtOSjdqT3J5YVV1SEh1Y1U4UzltSWpuS2pBQjVhUGpMSDV4QXM2bG1iMzEyMgp5KzF0bkVBbVhNNTBEK1VvRWpmUzZIT2I1cmRpcVhHdmMxS2JvS2p6a1BDUnh4MmE3MmN2ZWdVajZtZ0FKTHpnClRoRTFsbGNtVTRpemd4b0lNa1ZwR1RWT0xMbjFWRkt1TmhNWkN2RnZLZ25Lb0F2M0cwRlVuZldFYVJSalNObUQKTFlhTURUNUg5WnQycERJVWpVR1N0Q2w3Z1J6TUVuWXdKTzN5aURwZzQzbzVkUnlzVXlMOUpmRS9OaDdUZzYxOApuOGNKL1c3K1FZYllsanVyYXA4cjdRRlNyb2wzVkNoRkIrT29yNW5pK3ZvaFNBd0pmMFVsTXBHM3hXbXkxVUk0ClRGS2ZGR1JSVHpyUCs3Yk53WDVoSXZJeTVWdGd5YU9xSndUeGhpL0pkeHRPcjJ0QTVyQ1c3K0N0Z1N2emtxTkUKWHlyN3ZrWWdwNlk1TFpneTR0VWpLMEswT1VnVmRqQk9oRHBFenkvRkY4dzFGRVZnSjBxWS9yV2NMa0JIRFQ4Ugp2SmtoaW84Q0F3RUFBYU5mTUYwd0Z3WURWUjBSQkJBd0RvSU1ZMnhwTFhCeWIzaDVMWFp0TUJJR0ExVWRFd0VCCi93UUlNQVlCQWY4Q0FRQXdEd1lEVlIwUEFRSC9CQVVEQXdmbmdEQWRCZ05WSFNVRUZqQVVCZ2dyQmdFRkJRY0QKQWdZSUt3WUJCUVVIQXdFd0RRWUpLb1pJaHZjTkFRRUxCUUFEZ2dJQkFBb21qQ3lYdmFRT3hnWUs1MHNYTEIyKwp3QWZkc3g1bm5HZGd5Zmc0dXJXMlZtMTVEaEd2STdDL250cTBkWXkyNE4vVWJHN1VEWHZseUxJSkZxMVhQN25mCnBaRzBWQ2paNjlibXhLbTNaOG0wL0F3TXZpOGU5ZWR5OHY5a05CQ3dMR2tIYkE4WW85Q0lpUWdlbGZwcDF2VWgKYm5OQmhhRCtpdTZDZmlDTHdnSmIvaXc3ZW8vQ3lvWnF4K3RqWGFPMnpYdm00cC8rUUlmQU9ndEdRTEZVOGNmWgovZ1VyVHE1Z0ZxMCtQOUd5V3NBVEpGNnE3TDZXWlpqME91VHNlN2Y0Q1NpajZNbk9NTXhBK0pvYWhKejdsc1NpClRKSEl3RXA1ci9SeWhweWVwUXhGWWNVSDVKSmY5cmFoWExXWmkrOVRqeFNNMll5aHhmUlBzaVVFdUdEb2s3OFEKbS9RUGlDaTlKSmIxb2NtVGpBVjh4RFNob2NpdlhPRnlobjZMbjc3dkxqWStBYXZ0V0RoUXRocHVQeHNMdFZ6bQplMFNIMTFkRUxSdGI3NG1xWE9yTzdmdS8rSUJzM0pxTEUvVSt4dXhRdHZHOHZHMXlES0hIU1pxUzJoL1dzNGw0Ck5pQXNoSGdlaFFEUEJjWTl3WVl6ZkJnWnBPVU16ZERmNTB4K0ZTbFk0M1dPSkp6U3VRaDR5WjArM2t5Z3VDRjgKcm5NTFNjZXlTNGNpNExtSi9LQ1N1R2RmNlhWWXo4QkU5Z2pqanBDUDZxeTBVbFJlZldzL2lnL3djSysyYkYxVApuL1l2KzZnWGVDVEhKNzVxRElQbHA3RFJVVWswZmJNajRiSWthb2dXV2s0emYydThteFpMYTBsZVBLTktaTi9tCkdDdkZ3cjNlaSt1LzhjenA1RjdUCi0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K",
                ),
            ],
        )

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "http_proxy_path": _get_test_data_file("httpproxyconfig_update.json"),
            }
        )

        update_cmd = "aks update --resource-group={resource_group} --name={name} --http-proxy-config={http_proxy_path}"

        self.cmd(
            update_cmd,
            checks=[
                self.check("httpProxyConfig.httpProxy", "http://cli-proxy-vm:3128/"),
                self.check("httpProxyConfig.httpsProxy", "https://cli-proxy-vm:3129/"),
                self.check(
                    "httpProxyConfig.trustedCa",
                    "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUZERENDQXZTZ0F3SUJBZ0lVQlJ3cGs1eTh5ckdrNmtYTjhkSHlMRUNvaHBrd0RRWUpLb1pJaHZjTkFRRUwKQlFBd0VqRVFNQTRHQTFVRUF3d0habTl2TFdKaGNqQWVGdzB5TVRFd01UTXdNekU1TlRoYUZ3MHpNVEV3TVRFdwpNekU1TlRoYU1CSXhFREFPQmdOVkJBTU1CMlp2YnkxaVlYSXdnZ0lpTUEwR0NTcUdTSWIzRFFFQkFRVUFBNElDCkR3QXdnZ0lLQW9JQ0FRRFcwRE9sVC9yci9xUEZIUU9lNndBNDkyVGh3VWxZaDhCQkszTW9VWVZLNjEvL2xXekEKeFkrYzlmazlvckUrZXhMSVpwdUg1VnNZR21MNUFyc05sVmNBMkU4MWgwSlBPYUo1eEpiZG40YldpZG9vdXRVVwpXeDNhYUJLSEt0RWdZbUNmTjliWXlZMlNWRWQvNS9HeGh0akVabHJ1aEtRdkZVa3hwR0xKK1JRQ25oNklZakQwCnNpQ0YyTjJhVUJ4RE5KaUdmeHlHSVIrY2p4Vlcrd01md05CQ0l6QVkxMnY4WmpzUXdmUWlhOE5oWEx3M0tuRm0KdzUrcHN2bU1HL1FFUUtZMXNOTnk2dS9DZkI3cmIxQ0EwcjdNNnFsNFMrWHJjZUVRcXpDUWR6NWJueGNYbmFkbwp5MDlhdm5OSGRqbmpvcHNPSkxhd2hzb3RGNWFrL1FLdjYzdU9yVFFlOHlPSWlCZ3JSUzdwejcxbVlhRGNMcXFtCmtmdDVLYnFnMHNZYmo0M09LSm5aZ3crTUtackhoSFJKNi9BcWxOclZML3pFUytHU0ozQ1lSaE5nYXdDQ0Nqd1gKanZYZnkycWFEV2NQbWZaSWVVMVNzdE05THBVRWFQNjJzUVNmb3NEdnZFbUFyUVgwcmd1WGhvZ3pRUFdGWVlEKwo4SUNFYkNFc21hVnN3MzhVUzgzbFlGVCtyTHh3cm5UK1JXSUZ2WFRXbHhCNm5JeWpsOXBhNzlkdU5ocjJxN2RzCjVOU3ZWWHg5UGNqVTQ2VUZ6QnVTbUl0Q0M0Y1NadFRWc3l6ZnpMd2hKbGlqV0czTkp5TnpHUkZQcUpQdTNJUzEKZ3VtKytqdWx4bXZNWm1vM1RqSE5JRm90a0kyd3d3ZUtIcWpYcW9STmwvVnZobE5CaXZRR2gxeGovd0lEQVFBQgpvMW93V0RBU0JnTlZIUkVFQ3pBSmdnZG1iMjh0WW1GeU1CSUdBMVVkRXdFQi93UUlNQVlCQWY4Q0FRQXdEd1lEClZSMFBBUUgvQkFVREF3Zm5nREFkQmdOVkhTVUVGakFVQmdnckJnRUZCUWNEQWdZSUt3WUJCUVVIQXdFd0RRWUoKS29aSWh2Y05BUUVMQlFBRGdnSUJBTDF3RlpTdUw4NTM3aHpUTXhSUWJjcWdEU2F4RUd0ZDJaNTVCcnVWQVloagpxQjR6STd1UVZ2SkNpeXdmQm5BNnZmejh2UDBzdGJJbkVtajh1dS9CSS81NzZqR0tWUWRQSDhqMnQvN1NQWjFKClhBWk9wc1hoVll2RmtpQlhVeW1RMnAvRjFqb2ZRRE1JQ0htdHhRUSthakJQNjBpcnFnVnpsRi95NlQySUgzOHYKbGordndIam52WW5vVmhGNEY0TlE5amp6S3Y1NUhVTk0xUEJKZkFaOTJqeXovczdPMmN2cjhNWlNkT2s5QVk1RQp5RXRlQjBTSjdLS0tUZklBVmVMQzdrRnBHR3FsRkRBNzhPSS9YakNZViswRjk4MHdNOVkxTEVUa3ZMamVSMEFyCnVzZDNIS1Vtd2EwTVEwUTNZNGxma0ZtNjJTclhvcjJURC9WZHpFZWNOTnVmV1VJTVNuaEJDNTVHWjBOTVYvR0QKRXhGZTVWQkhUZEZVNlIwb3JCOVFjVll1Mzk0MEt5NXhkbHNaUHZlMmRJNS9WOXhzY0Zad3cxWWs4K21RK3NVeQp2UVBoL2ZmK0tTQjdVVkdvTVNXUlg3YjFFMGVzZSs4QzZlaVV2OXpDR0VRbkVCcnFIQWxSUDJ2ZzQ0bXFJSnRzCjN2NUt1NW0ySmJoeWNsQVR3VUNQZkN3a2tLRTg0MzZGRitDK0ZUVTJ1OWVpL2t5QTAxYi9zRFl2cWdsS2FWK3MKbEVHRkhjd05Ea2VrS1BFUEZxNkpnZ3R0WlNidE5SMnFadzl3cExIbDVuVlVXdnBGa2hvcW1KVkphK0VBSTQ1LwpqRkh4VG9PMHp1NlBxc1p5SnM2TC84Z3BhbTcwMDV6b0VETVRjcFltMlduMFBKcEg3NE9zUHJVRDVJWVA5ZEt5Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K",
                ),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_none_private_dns_zone(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count=1 --load-balancer-sku=standard "
            "--enable-private-cluster --private-dns-zone none "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("privateFqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check("apiServerAccessProfile.privateDNSZone", "None"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_private_cluster_public_fqdn(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--enable-private-cluster --node-count=1 "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("privateFqdn"),
                self.exists("fqdn"),
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "apiServerAccessProfile.enablePrivateClusterPublicFqdn", True
                ),
            ],
        )

        # update
        update_cmd = "aks update --resource-group={resource_group} --name={name} --disable-public-fqdn"
        self.cmd(
            update_cmd,
            checks=[
                self.exists("privateFqdn"),
                self.check("fqdn", None),
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "apiServerAccessProfile.enablePrivateClusterPublicFqdn", False
                ),
            ],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_fqdn_subdomain(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        identity_name = self.create_random_name("cliakstest", 16)
        subdomain_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "identity_name": identity_name,
                "subdomain_name": subdomain_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create private dns zone
        create_private_dns_zone = 'network private-dns zone create --resource-group={resource_group} --name="privatelink.{location}.azmk8s.io"'
        zone = self.cmd(
            create_private_dns_zone,
            checks=[self.check("provisioningState", "Succeeded")],
        ).get_output_in_json()
        zone_id = zone["id"]
        assert zone_id is not None
        self.kwargs.update(
            {
                "zone_id": zone_id,
            }
        )

        # create identity
        create_identity = (
            "identity create --resource-group={resource_group} --name={identity_name}"
        )
        identity = self.cmd(
            create_identity, checks=[self.check("name", identity_name)]
        ).get_output_in_json()
        identity_id = identity["principalId"]
        identity_resource_id = identity["id"]
        assert identity_id is not None
        self.kwargs.update(
            {
                "identity_id": identity_id,
                "identity_resource_id": identity_resource_id,
            }
        )

        # assign
        from unittest import mock

        with mock.patch(
            "azure.cli.command_modules.role.custom._gen_guid",
            side_effect=self.create_guid,
        ):
            assignment = self.cmd(
                'role assignment create --assignee-object-id={identity_id} --role "Private DNS Zone Contributor" --scope={zone_id} --assignee-principal-type ServicePrincipal'
            ).get_output_in_json()
        assert assignment["roleDefinitionId"] is not None

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count=1 --fqdn-subdomain={subdomain_name} --load-balancer-sku=standard "
            "--enable-private-cluster --private-dns-zone={zone_id} --enable-managed-identity --assign-identity {identity_resource_id} "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("privateFqdn"),
                self.exists("fqdnSubdomain"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check("apiServerAccessProfile.privateDnsZone", zone_id),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_pod_identity_enabled(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--enable-managed-identity "
            "--enable-pod-identity --enable-pod-identity-with-kubenet "
            "--ssh-key-value={ssh_key_value} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnablePodIdentityPreview"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("podIdentityProfile.enabled", True),
                self.check("podIdentityProfile.allowNetworkPluginKubenet", True),
            ],
        )

        # update: disable
        cmd = (
            "aks update --resource-group={resource_group} --name={name} --disable-pod-identity "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnablePodIdentityPreview"
        )
        self.cmd(
            cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("podIdentityProfile.enabled", None),
            ],
        )

        # update: enable
        cmd = (
            "aks update --resource-group={resource_group} --name={name} --enable-pod-identity --enable-pod-identity-with-kubenet "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnablePodIdentityPreview"
        )
        self.cmd(
            cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("podIdentityProfile.enabled", True),
                self.check("podIdentityProfile.allowNetworkPluginKubenet", True),
            ],
        )

        # pod identity exception: add
        cmd = (
            "aks pod-identity exception add --cluster-name={name} --resource-group={resource_group} "
            "--namespace test-namespace --name test-name --pod-labels foo=bar "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnablePodIdentityPreview"
        )
        self.cmd(
            cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("podIdentityProfile.enabled", True),
                self.check(
                    "podIdentityProfile.userAssignedIdentityExceptions[0].name",
                    "test-name",
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentityExceptions[0].namespace",
                    "test-namespace",
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentityExceptions[0].podLabels.foo",
                    "bar",
                ),
            ],
        )

        # pod identity exception: update
        cmd = (
            "aks pod-identity exception update --cluster-name={name} --resource-group={resource_group} "
            "--namespace test-namespace --name test-name --pod-labels foo=bar a=b "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnablePodIdentityPreview"
        )
        self.cmd(
            cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("podIdentityProfile.enabled", True),
                self.check(
                    "podIdentityProfile.userAssignedIdentityExceptions[0].name",
                    "test-name",
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentityExceptions[0].namespace",
                    "test-namespace",
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentityExceptions[0].podLabels.foo",
                    "bar",
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentityExceptions[0].podLabels.a",
                    "b",
                ),
            ],
        )

        # pod identity exception: delete
        cmd = (
            "aks pod-identity exception delete --cluster-name={name} --resource-group={resource_group} "
            "--namespace test-namespace --name test-name "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnablePodIdentityPreview"
        )
        self.cmd(
            cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("podIdentityProfile.enabled", True),
                self.check("podIdentityProfile.userAssignedIdentityExceptions", None),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_using_azurecni_with_pod_identity_enabled(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--enable-managed-identity "
            "--enable-pod-identity --network-plugin azure "
            "--ssh-key-value={ssh_key_value} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnablePodIdentityPreview"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("podIdentityProfile.enabled", True),
            ],
        )

        # update: disable
        cmd = (
            "aks update --resource-group={resource_group} --name={name} --disable-pod-identity "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnablePodIdentityPreview"
        )
        self.cmd(
            cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("podIdentityProfile.enabled", None),
            ],
        )

        # update: enable
        cmd = (
            "aks update --resource-group={resource_group} --name={name} --enable-pod-identity "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnablePodIdentityPreview"
        )
        self.cmd(
            cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("podIdentityProfile.enabled", True),
            ],
        )

        # pod identity exception: add
        cmd = (
            "aks pod-identity exception add --cluster-name={name} --resource-group={resource_group} "
            "--namespace test-namespace --name test-name --pod-labels foo=bar "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnablePodIdentityPreview"
        )
        self.cmd(
            cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("podIdentityProfile.enabled", True),
                self.check(
                    "podIdentityProfile.userAssignedIdentityExceptions[0].name",
                    "test-name",
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentityExceptions[0].namespace",
                    "test-namespace",
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentityExceptions[0].podLabels.foo",
                    "bar",
                ),
            ],
        )

        # pod identity exception: update
        cmd = (
            "aks pod-identity exception update --cluster-name={name} --resource-group={resource_group} "
            "--namespace test-namespace --name test-name --pod-labels foo=bar a=b "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnablePodIdentityPreview"
        )
        self.cmd(
            cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("podIdentityProfile.enabled", True),
                self.check(
                    "podIdentityProfile.userAssignedIdentityExceptions[0].name",
                    "test-name",
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentityExceptions[0].namespace",
                    "test-namespace",
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentityExceptions[0].podLabels.foo",
                    "bar",
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentityExceptions[0].podLabels.a",
                    "b",
                ),
            ],
        )

        # pod identity exception: delete
        cmd = (
            "aks pod-identity exception delete --cluster-name={name} --resource-group={resource_group} "
            "--namespace test-namespace --name test-name "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnablePodIdentityPreview"
        )
        self.cmd(
            cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("podIdentityProfile.enabled", True),
                self.check("podIdentityProfile.userAssignedIdentityExceptions", None),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    # the pod identity add command creates role assignment with random uuid
    # for this case we cannot use recording to capture the fixture, therefore we need to mark it as live_only
    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_pod_identity_usage(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        identity_name = self.create_random_name("id", 6)
        binding_selector_name = "binding_test"
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "identity_name": identity_name,
                "binding_selector": binding_selector_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create identity
        cmd = "identity create --resource-group={resource_group} --name={identity_name} --location={location}"
        application_identity = self.cmd(
            cmd, checks=[self.check("name", identity_name)]
        ).get_output_in_json()
        self.kwargs.update(
            {
                "application_identity_id": application_identity["id"],
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--enable-managed-identity "
            "--enable-pod-identity --enable-pod-identity-with-kubenet "
            "--ssh-key-value={ssh_key_value} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnablePodIdentityPreview"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("podIdentityProfile.enabled", True),
            ],
        )

        # pod identity: add
        cmd = (
            "aks pod-identity add --cluster-name={name} --resource-group={resource_group} "
            "--namespace test-namespace --name test-name --identity-resource-id={application_identity_id} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnablePodIdentityPreview"
        )
        self.cmd(
            cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("podIdentityProfile.enabled", True),
                self.check(
                    "podIdentityProfile.userAssignedIdentities[0].name", "test-name"
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentities[0].namespace",
                    "test-namespace",
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentities[0].provisioningState",
                    "Assigned",
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentities[0].identity.clientId",
                    application_identity["clientId"],
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentities[0].identity.objectId",
                    application_identity["principalId"],
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentities[0].identity.resourceId",
                    application_identity["id"],
                ),
            ],
        )

        # pod identity: delete
        cmd = (
            "aks pod-identity delete --cluster-name={name} --resource-group={resource_group} "
            "--namespace test-namespace --name test-name "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnablePodIdentityPreview"
        )
        self.cmd(
            cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("podIdentityProfile.enabled", True),
                self.check("podIdentityProfile.userAssignedIdentities", None),
            ],
        )

        # pod identity: add with binding selector
        cmd = (
            "aks pod-identity add --cluster-name={name} --resource-group={resource_group} "
            "--namespace test-namespace-binding-selector --name test-name-binding-selector "
            "--identity-resource-id={application_identity_id} --binding-selector={binding_selector} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnablePodIdentityPreview"
        )
        self.cmd(
            cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("podIdentityProfile.enabled", True),
                self.check(
                    "podIdentityProfile.userAssignedIdentities[0].name",
                    "test-name-binding-selector",
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentities[0].namespace",
                    "test-namespace-binding-selector",
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentities[0].provisioningState",
                    "Assigned",
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentities[0].bindingSelector",
                    binding_selector_name,
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentities[0].identity.clientId",
                    application_identity["clientId"],
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentities[0].identity.objectId",
                    application_identity["principalId"],
                ),
                self.check(
                    "podIdentityProfile.userAssignedIdentities[0].identity.resourceId",
                    application_identity["id"],
                ),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_update_with_windows_password(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "windows_admin_username": "azureuser1",
                "windows_admin_password": self.create_random_name("p@0A", 16),
                "nodepool2_name": "npwin",
                "new_windows_admin_password": self.create_random_name("n!C3", 16),
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--dns-name-prefix={dns_name_prefix} --node-count=1 "
            "--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} "
            "--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check("windowsProfile.adminUsername", "azureuser1"),
            ],
        )

        # nodepool add
        self.cmd(
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --os-type Windows --node-count=1",
            checks=[self.check("provisioningState", "Succeeded")],
        )

        # update Windows password
        self.cmd(
            "aks update --resource-group={resource_group} --name={name} --windows-admin-password {new_windows_admin_password}",
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # nodepool delete
        self.cmd(
            "aks nodepool delete --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --no-wait",
            checks=[self.is_empty()],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="centraluseuap"
    )
    def test_aks_custom_kubelet_identity(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        control_plane_identity_name = self.create_random_name("cliakstest", 16)
        kubelet_identity_name = self.create_random_name("cliakstest", 16)
        new_kubelet_identity_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "control_plane_identity_name": control_plane_identity_name,
                "kubelet_identity_name": kubelet_identity_name,
                "new_kubelet_identity_name": new_kubelet_identity_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create control plane identity
        control_plane_identity = "identity create --resource-group={resource_group} --name={control_plane_identity_name}"
        c_identity = self.cmd(
            control_plane_identity,
            checks=[self.check("name", control_plane_identity_name)],
        ).get_output_in_json()
        control_plane_identity_resource_id = c_identity["id"]
        assert control_plane_identity_resource_id is not None
        self.kwargs.update(
            {
                "control_plane_identity_resource_id": control_plane_identity_resource_id,
            }
        )

        # create kubelet identity
        kubelet_identity = "identity create --resource-group={resource_group} --name={kubelet_identity_name}"
        k_identity = self.cmd(
            kubelet_identity, checks=[self.check("name", kubelet_identity_name)]
        ).get_output_in_json()
        kubelet_identity_resource_id = k_identity["id"]
        assert kubelet_identity_resource_id is not None
        self.kwargs.update(
            {
                "kubelet_identity_resource_id": kubelet_identity_resource_id,
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count=1 --enable-managed-identity "
            "--assign-identity {control_plane_identity_resource_id} --assign-kubelet-identity {kubelet_identity_resource_id} "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("identity"),
                self.exists("identityProfile"),
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "identityProfile.kubeletidentity.resourceId",
                    kubelet_identity_resource_id,
                ),
            ],
        )

        # create new kubelet identity
        new_kubelet_identity = "identity create --resource-group={resource_group} --name={new_kubelet_identity_name}"
        new_identity = self.cmd(
            new_kubelet_identity, checks=[self.check("name", new_kubelet_identity_name)]
        ).get_output_in_json()
        new_kubelet_identity_resource_id = new_identity["id"]
        assert new_kubelet_identity_resource_id is not None
        self.kwargs.update(
            {
                "new_kubelet_identity_resource_id": new_kubelet_identity_resource_id,
            }
        )

        # update to new kubelet identity
        self.cmd(
            "aks update --resource-group={resource_group} --name={name} --assign-kubelet-identity {new_kubelet_identity_resource_id} --yes",
            checks=[
                self.exists("identity"),
                self.exists("identityProfile"),
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "identityProfile.kubeletidentity.resourceId",
                    new_kubelet_identity_resource_id,
                ),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_disable_local_accounts(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--enable-aad --aad-admin-group-object-ids 00000000-0000-0000-0000-000000000001 "
            "--disable-local-accounts --ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("disableLocalAccounts", True),
            ],
        )

        # update to enable local accounts
        self.cmd(
            "aks update --resource-group={resource_group} --name={name} --enable-local-accounts",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("disableLocalAccounts", False),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_enable_utlra_ssd(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-vm-size Standard_D2s_v3 --zones 1 2 3 --enable-ultra-ssd "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_maintenancewindow(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "mc_path": _get_test_data_file("maintenancewindow.json"),
                "auto_upgrade_config_name": "aksManagedAutoUpgradeSchedule",
                "node_os_upgrade_config_name": "aksManagedNodeOSUpgradeSchedule",
                "ssh_key_value": self.generate_ssh_keys(),
                "future_date": "2123-01-01",
            }
        )

        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}"
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        # add dedicated maintenanceconfiguration for cluster autoupgrade
        maintenance_configuration_add_cmd = (
            "aks maintenanceconfiguration add "
            "-g {resource_group} --cluster-name {name} "
            "-n {auto_upgrade_config_name} "
            "--schedule-type Weekly "
            "--day-of-week Friday "
            "--interval-weeks 3 "
            "--duration 8 "
            "--utc-offset +05:30 "
            "--start-date {future_date} "
            "--start-time 00:00 "
        )

        self.cmd(
            maintenance_configuration_add_cmd,
            checks=[
                self.exists("maintenanceWindow.schedule.weekly"),
                self.check("maintenanceWindow.schedule.weekly.dayOfWeek", "Friday"),
                self.check("maintenanceWindow.schedule.weekly.intervalWeeks", 3),
                self.check("maintenanceWindow.durationHours", 8),
                self.check("maintenanceWindow.utcOffset", "+05:30"),
                self.check("maintenanceWindow.startDate", "{future_date}"),
                self.check("maintenanceWindow.startTime", "00:00"),
            ],
        )

        # add dedicated maintenanceconfiguration for node os autoupgrade
        maintenance_configuration_add_cmd = (
            "aks maintenanceconfiguration add "
            "-g {resource_group} --cluster-name {name} "
            "-n {node_os_upgrade_config_name} "
            "--schedule-type RelativeMonthly "
            "--day-of-week Tuesday "
            "--week-index Last "
            "--interval-months 1 "
            "--duration 12 "
            "--start-time 09:00 "
            "--utc-offset=-08:00 "
            "--start-date {future_date} "
        )

        self.cmd(
            maintenance_configuration_add_cmd,
            checks=[
                self.exists("maintenanceWindow.schedule.relativeMonthly"),
                self.check(
                    "maintenanceWindow.schedule.relativeMonthly.dayOfWeek", "Tuesday"
                ),
                self.check(
                    "maintenanceWindow.schedule.relativeMonthly.intervalMonths", 1
                ),
                self.check("maintenanceWindow.durationHours", 12),
                self.check("maintenanceWindow.utcOffset", "-08:00"),
                self.check("maintenanceWindow.startDate", "{future_date}"),
                self.check("maintenanceWindow.startTime", "09:00"),
            ],
        )

        # maintenanceconfiguration list
        maintenance_configuration_list_cmd = (
            "aks maintenanceconfiguration list "
            "-g {resource_group} --cluster-name {name}"
        )
        self.cmd(
            maintenance_configuration_list_cmd, checks=[self.check("length(@)", 2)]
        )

        # update maintenanceconfiguration from config file
        maintenance_configuration_update_cmd = (
            "aks maintenanceconfiguration update "
            "-g {resource_group} --cluster-name {name} "
            "-n {auto_upgrade_config_name} "
            "--config-file {mc_path}"
        )

        self.cmd(
            maintenance_configuration_update_cmd,
            checks=[
                self.exists("maintenanceWindow.schedule.absoluteMonthly"),
                self.check("maintenanceWindow.schedule.absoluteMonthly.dayOfMonth", 1),
                self.check(
                    "maintenanceWindow.schedule.absoluteMonthly.intervalMonths", 3
                ),
                self.check("maintenanceWindow.durationHours", 4),
                self.check("maintenanceWindow.utcOffset", "-08:00"),
                self.check("maintenanceWindow.startTime", "09:00"),
                self.check("maintenanceWindow.notAllowedDates | length(@)", 2),
            ],
        )

        # maintenanceconfiguration show
        maintenance_configuration_show_cmd = (
            "aks maintenanceconfiguration show "
            "-g {resource_group} --cluster-name {name} "
            "-n {auto_upgrade_config_name}"
        )
        self.cmd(
            maintenance_configuration_show_cmd,
            checks=[self.check("name == '{auto_upgrade_config_name}'", True)],
        )

        # maintenanceconfiguration delete
        maintenance_configuration_delete_cmd = (
            "aks maintenanceconfiguration delete "
            "-g {resource_group} --cluster-name {name} "
            "-n {auto_upgrade_config_name}"
        )
        self.cmd(maintenance_configuration_delete_cmd, checks=[self.is_empty()])

        maintenance_configuration_delete_cmd = (
            "aks maintenanceconfiguration delete "
            "-g {resource_group} --cluster-name {name} "
            "-n {node_os_upgrade_config_name}"
        )
        self.cmd(maintenance_configuration_delete_cmd, checks=[self.is_empty()])

        # maintenanceconfiguration list
        maintenance_configuration_list_cmd = (
            "aks maintenanceconfiguration list "
            "-g {resource_group} --cluster-name {name}"
        )
        self.cmd(maintenance_configuration_list_cmd, checks=[self.is_empty()])

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_maintenanceconfiguration(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "mc_path": _get_test_data_file("maintenanceconfig.json"),
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}"
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        # maintenanceconfiguration add
        maintenance_configuration_add_cmd = "aks maintenanceconfiguration add -g {resource_group} --cluster-name {name} -n default --weekday Monday --start-hour 1"
        self.cmd(
            maintenance_configuration_add_cmd,
            checks=[
                self.check("timeInWeek[0].day", "Monday"),
                self.check("timeInWeek[0].day", "Monday"),
                self.check("timeInWeek[0].hourSlots | contains(@, `1`)", True),
            ],
        )

        # maintenanceconfiguration update (from config file)
        maintenance_configuration_update_cmd = "aks maintenanceconfiguration update -g {resource_group} --cluster-name {name} -n default --config-file {mc_path}"
        self.cmd(
            maintenance_configuration_update_cmd,
            checks=[
                self.check(
                    "timeInWeek[*].day | contains(@, 'Tuesday') && contains(@, 'Wednesday')",
                    True,
                ),
                self.check(
                    "timeInWeek[*].hourSlots[*] | contains([0], `2`) && contains([1], `6`)",
                    True,
                ),
                self.check("notAllowedTime | length(@) == `2`", True),
            ],
        )

        # maintenanceconfiguration show
        maintenance_configuration_show_cmd = "aks maintenanceconfiguration show -g {resource_group} --cluster-name {name} -n default"
        self.cmd(
            maintenance_configuration_show_cmd,
            checks=[self.check("name == 'default'", True)],
        )

        # maintenanceconfiguration delete
        maintenance_configuration_delete_cmd = "aks maintenanceconfiguration delete -g {resource_group} --cluster-name {name} -n default"
        self.cmd(maintenance_configuration_delete_cmd, checks=[self.is_empty()])

        # maintenanceconfiguration list
        maintenance_configuration_list_cmd = "aks maintenanceconfiguration list -g {resource_group} --cluster-name {name}"
        self.cmd(maintenance_configuration_list_cmd, checks=[self.is_empty()])

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="centraluseuap"
    )
    def test_aks_create_with_windows_gmsa(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "windows_admin_username": "azureuser1",
                "windows_admin_password": "replace-Password1234$",
                "nodepool2_name": "npwin",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--dns-name-prefix={dns_name_prefix} --node-count=1 "
            "--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} "
            "--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure "
            "--ssh-key-value={ssh_key_value} --enable-windows-gmsa --yes "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKSWindowsGmsaPreview"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check("windowsProfile.adminUsername", "azureuser1"),
                self.check("windowsProfile.gmsaProfile.enabled", "True"),
            ],
        )

        # nodepool add
        self.cmd(
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --os-type Windows --node-count=1",
            checks=[self.check("provisioningState", "Succeeded")],
        )

        # nodepool delete
        self.cmd(
            "aks nodepool delete --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --no-wait",
            checks=[self.is_empty()],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="centraluseuap",
        preserve_default_location=True,
    )
    def test_aks_create_with_overlay_network_plugin_mode(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--network-plugin azure --network-plugin-mode overlay --ssh-key-value={ssh_key_value} "
            "--pod-cidr 10.244.0.0/16 --node-count 1 "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AzureOverlayPreview"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.podCidr", "10.244.0.0/16"),
                self.check("networkProfile.networkPluginMode", "overlay"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_create_with_network_dataplane_cilium(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--network-plugin azure --network-plugin-mode overlay --ssh-key-value={ssh_key_value} "
            "--pod-cidr 10.244.0.0/16 --node-count 1 "
            "--network-dataplane=cilium "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/CiliumDataplanePreview,AKSHTTPCustomFeatures=Microsoft.ContainerService/AzureOverlayPreview"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.podCidr", "10.244.0.0/16"),
                self.check("networkProfile.networkPlugin", "azure"),
                self.check("networkProfile.networkPluginMode", "overlay"),
                self.check("networkProfile.networkPolicy", "cilium"),
                self.check("networkProfile.networkDataplane", "cilium"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="centraluseuap",
        preserve_default_location=True,
    )
    def test_aks_create_with_enable_cilium_dataplane(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--network-plugin azure --network-plugin-mode overlay --ssh-key-value={ssh_key_value} "
            "--pod-cidr 10.244.0.0/16 --node-count 1 "
            "--enable-cilium-dataplane "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/CiliumDataplanePreview,AKSHTTPCustomFeatures=Microsoft.ContainerService/AzureOverlayPreview"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.podCidr", "10.244.0.0/16"),
                self.check("networkProfile.networkPluginMode", "overlay"),
                self.check("networkProfile.networkDataplane", "cilium"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="centraluseuap",
        preserve_default_location=True,
    )
    def test_aks_create_dualstack_with_default_network(
        self, resource_group, resource_group_location
    ):
        _, create_version = self._get_versions(resource_group_location)
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "k8s_version": create_version,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--ip-families IPv4,IPv6 --ssh-key-value={ssh_key_value} --kubernetes-version {k8s_version} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-EnableDualStack"
        )

        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.podCidrs[] | length(@)", 2),
                self.check("networkProfile.serviceCidrs[] | length(@)", 2),
                self.check("networkProfile.ipFamilies", ["IPv4", "IPv6"]),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_default_network(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--pod-cidr 172.126.0.0/16 --service-cidr 172.56.0.0/16 --dns-service-ip 172.56.0.10 "
            "--pod-cidrs 172.126.0.0/16 --service-cidrs 172.56.0.0/16 --ip-families IPv4 "
            "--network-plugin kubenet --ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.podCidr", "172.126.0.0/16"),
                self.check("networkProfile.podCidrs", ["172.126.0.0/16"]),
                self.check("networkProfile.serviceCidr", "172.56.0.0/16"),
                self.check("networkProfile.serviceCidrs", ["172.56.0.0/16"]),
                self.check("networkProfile.ipFamilies", ["IPv4"]),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_and_update_outbound_ips(
        self, resource_group, resource_group_location
    ):
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        init_pip_name = self.create_random_name("cliakstest", 16)
        update_pip_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "init_pip_name": init_pip_name,
                "update_pip_name": update_pip_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_init_pip = "network public-ip create -g {resource_group} -n {init_pip_name} --sku Standard"
        # workaround for replay failure in CI
        self.cmd(create_init_pip)
        get_init_pip = "network public-ip show -g {resource_group} -n {init_pip_name}"
        init_pip = self.cmd(
            get_init_pip, checks=[self.check("provisioningState", "Succeeded")]
        ).get_output_in_json()

        create_update_pip = "network public-ip create -g {resource_group} -n {update_pip_name} --sku Standard"
        # workaround for replay failure in CI
        self.cmd(create_update_pip)
        get_update_pip = (
            "network public-ip show -g {resource_group} -n {update_pip_name}"
        )
        update_pip = self.cmd(
            get_update_pip, checks=[self.check("provisioningState", "Succeeded")]
        ).get_output_in_json()

        init_pip_id = init_pip["id"]
        update_pip_id = update_pip["id"]

        assert init_pip_id is not None
        assert update_pip_id is not None
        self.kwargs.update(
            {
                "init_pip_id": init_pip_id,
                "update_pip_id": update_pip_id,
            }
        )

        # create cluster
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--ssh-key-value={ssh_key_value} --load-balancer-outbound-ips {init_pip_id}"
        )

        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "networkProfile.loadBalancerProfile.effectiveOutboundIPs[] | length(@)",
                    1,
                ),
                self.check(
                    "networkProfile.loadBalancerProfile.effectiveOutboundIPs[0].id",
                    init_pip_id,
                ),
            ],
        )

        # update cluster
        update_cmd = "aks update -g {resource_group} -n {name} --load-balancer-outbound-ips {update_pip_id} --load-balancer-outbound-ports 200"

        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "networkProfile.loadBalancerProfile.effectiveOutboundIPs[] | length(@)",
                    1,
                ),
                self.check(
                    "networkProfile.loadBalancerProfile.allocatedOutboundPorts",
                    200,
                ),
            ],
        )

        update_cmd = "aks update -g {resource_group} -n {name} --load-balancer-outbound-ips {update_pip_id} --load-balancer-outbound-ports 0"

        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "networkProfile.loadBalancerProfile.effectiveOutboundIPs[] | length(@)",
                    1,
                ),
                self.check(
                    "networkProfile.loadBalancerProfile.allocatedOutboundPorts",
                    0,
                ),
            ],
        )
        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="centraluseuap",
        preserve_default_location=True,
    )
    def test_aks_create_and_update_ipv6_count(
        self, resource_group, resource_group_location
    ):
        _, create_version = self._get_versions(resource_group_location)
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "k8s_version": create_version,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--pod-cidr 172.126.0.0/16 --service-cidr 172.56.0.0/16 --dns-service-ip 172.56.0.10 "
            "--pod-cidrs 172.126.0.0/16,2001:abcd:1234::/64 --service-cidrs 172.56.0.0/16,2001:ffff::/108 "
            "--ip-families IPv4,IPv6 --load-balancer-managed-outbound-ipv6-count 2 "
            "--network-plugin kubenet --ssh-key-value={ssh_key_value} --kubernetes-version {k8s_version} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-EnableDualStack"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.podCidr", "172.126.0.0/16"),
                self.check(
                    "networkProfile.podCidrs", ["172.126.0.0/16", "2001:abcd:1234::/64"]
                ),
                self.check("networkProfile.serviceCidr", "172.56.0.0/16"),
                self.check(
                    "networkProfile.serviceCidrs", ["172.56.0.0/16", "2001:ffff::/108"]
                ),
                self.check("networkProfile.ipFamilies", ["IPv4", "IPv6"]),
                self.check(
                    "networkProfile.loadBalancerProfile.managedOutboundIPs.countIpv6", 2
                ),
                self.check(
                    "networkProfile.loadBalancerProfile.managedOutboundIPs.count", 1
                ),
                self.check(
                    "networkProfile.loadBalancerProfile.effectiveOutboundIPs[] | length(@)",
                    3,
                ),
            ],
        )

        # update
        update_cmd = "aks update -g {resource_group} -n {name} --load-balancer-managed-outbound-ipv6-count 4"

        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.podCidr", "172.126.0.0/16"),
                self.check(
                    "networkProfile.podCidrs", ["172.126.0.0/16", "2001:abcd:1234::/64"]
                ),
                self.check("networkProfile.serviceCidr", "172.56.0.0/16"),
                self.check(
                    "networkProfile.serviceCidrs", ["172.56.0.0/16", "2001:ffff::/108"]
                ),
                self.check("networkProfile.ipFamilies", ["IPv4", "IPv6"]),
                self.check(
                    "networkProfile.loadBalancerProfile.managedOutboundIPs.countIpv6", 4
                ),
                self.check(
                    "networkProfile.loadBalancerProfile.managedOutboundIPs.count", 1
                ),
                self.check(
                    "networkProfile.loadBalancerProfile.effectiveOutboundIPs[] | length(@)",
                    5,
                ),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="westcentralus",
        preserve_default_location=True,
    )
    def test_aks_azure_cni_overlay_migration(
        self, resource_group, resource_group_location
    ):
        _, create_version = self._get_versions(resource_group_location)
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "k8s_version": create_version,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--network-plugin azure --ssh-key-value={ssh_key_value} --kubernetes-version {k8s_version} "
            "--service-cidr 172.56.0.0/16 --dns-service-ip 172.56.0.10 "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AzureOverlayPreview"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.networkPlugin", "azure"),
                self.check("networkProfile.networkPluginMode", None),
                self.check("networkProfile.podCidr", None),
                self.check("networkProfile.serviceCidr", "172.56.0.0/16"),
            ],
        )

        # update
        update_cmd = (
            "aks update -g {resource_group} -n {name} --network-plugin-mode overlay --pod-cidr 100.64.0.0/10 "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AzureOverlayPreview"
        )

        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.networkPlugin", "azure"),
                self.check("networkProfile.networkPluginMode", "overlay"),
                self.check("networkProfile.podCidr", "100.64.0.0/10"),
                self.check("networkProfile.serviceCidr", "172.56.0.0/16"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_azure_cni_overlay_migration_from_kubenet(
        self, resource_group, resource_group_location
    ):
        _, create_version = self._get_versions(resource_group_location)
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "k8s_version": create_version,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--network-plugin kubenet --ssh-key-value={ssh_key_value} --kubernetes-version {k8s_version} "
            "--service-cidr 172.56.0.0/16 --dns-service-ip 172.56.0.10 --pod-cidr 100.64.0.0/16 -c 1"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.networkPlugin", "kubenet"),
                self.check("networkProfile.networkPluginMode", None),
                self.check("networkProfile.podCidr", "100.64.0.0/16"),
                self.check("networkProfile.serviceCidr", "172.56.0.0/16"),
            ],
        )

        # update
        update_cmd = (
            "aks update -g {resource_group} -n {name} --network-plugin azure --network-plugin-mode overlay "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AzureOverlayPreview"
        )

        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.networkPlugin", "azure"),
                self.check("networkProfile.networkPluginMode", "overlay"),
                self.check("networkProfile.podCidr", "100.64.0.0/16"),
                self.check("networkProfile.serviceCidr", "172.56.0.0/16"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_migrate_cluster_to_cilium_dataplane(
        self, resource_group, resource_group_location
    ):
        _, create_version = self._get_versions(resource_group_location)
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "k8s_version": create_version,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create with Azure CNI overlay
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--network-plugin azure --ssh-key-value={ssh_key_value} --kubernetes-version {k8s_version} "
            "--network-plugin-mode=overlay"
        )

        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.networkPlugin", "azure"),
                self.check("networkProfile.networkPluginMode", "overlay"),
                self.check("networkProfile.networkDataplane", "azure"),
            ],
        )

        # update to enable cilium dataplane
        update_cmd = "aks update -g {resource_group} -n {name} --network-dataplane=cilium --network-policy=cilium"

        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.networkPlugin", "azure"),
                self.check("networkProfile.networkPluginMode", "overlay"),
                self.check("networkProfile.networkDataplane", "cilium"),
                self.check("networkProfile.networkPolicy", "cilium"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="centraluseuap",
        preserve_default_location=True,
    )
    def test_aks_create_or_update_with_load_balancer_backend_pool_type(
        self, resource_group, resource_group_location
    ):
        _, create_version = self._get_versions(resource_group_location)
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "k8s_version": create_version,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--ssh-key-value={ssh_key_value} "
            "--kubernetes-version={k8s_version} "
            "--load-balancer-backend-pool-type=nodeIP "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/IPBasedLoadBalancerPreview"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check(
                    "networkProfile.loadBalancerProfile.backendPoolType", "nodeIP"
                ),
            ],
        )

        # update
        update_cmd = (
            "aks update -g {resource_group} -n {name} --load-balancer-backend-pool-type=nodeIP "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/IPBasedLoadBalancerPreview"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check(
                    "networkProfile.loadBalancerProfile.backendPoolType", "nodeIP"
                ),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="centraluseuap",
        preserve_default_location=True,
    )
    def test_aks_create_or_update_with_health_probe_mode(
        self, resource_group, resource_group_location
    ):
        _, create_version = self._get_versions(resource_group_location)
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "k8s_version": create_version,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--ssh-key-value={ssh_key_value} "
            "--kubernetes-version={k8s_version} "
            "--cluster-service-load-balancer-health-probe-mode=Servicenodeport "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableSLBSharedHealthProbePreview"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check(
                    "networkProfile.loadBalancerProfile.clusterServiceLoadBalancerHealthProbeMode", "Servicenodeport"
                ),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="centraluseuap"
    )
    def test_aks_update_with_windows_gmsa(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "windows_admin_username": "azureuser1",
                "windows_admin_password": "replace-Password1234$",
                "nodepool2_name": "npwin",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--dns-name-prefix={dns_name_prefix} --node-count=1 "
            "--windows-admin-username={windows_admin_username} --windows-admin-password={windows_admin_password} "
            "--load-balancer-sku=standard --vm-set-type=virtualmachinescalesets --network-plugin=azure "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check("windowsProfile.adminUsername", "azureuser1"),
                self.not_exists("windowsProfile.gmsaProfile"),
            ],
        )

        # nodepool add
        self.cmd(
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --os-type Windows --node-count=1",
            checks=[self.check("provisioningState", "Succeeded")],
        )

        # update Windows gmsa
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} --enable-windows-gmsa --yes "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKSWindowsGmsaPreview"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("windowsProfile.gmsaProfile.enabled", "True"),
            ],
        )

        # nodepool delete
        self.cmd(
            "aks nodepool delete --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --no-wait",
            checks=[self.is_empty()],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_nodepool_update_taints_msi(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool1_name = "nodepool1"
        taints = "key1=value1:PreferNoSchedule"
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "ssh_key_value": self.generate_ssh_keys(),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "taints": taints,
                "nodepool1_name": nodepool1_name,
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--dns-name-prefix={dns_name_prefix} --node-count=1 --ssh-key-value={ssh_key_value} "
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # show
        self.cmd(
            "aks show -g {resource_group} -n {name}",
            checks=[
                self.check("type", "{resource_type}"),
                self.check("name", "{name}"),
                self.exists("nodeResourceGroup"),
                self.check("resourceGroup", "{resource_group}"),
                self.check("agentPoolProfiles[0].count", 1),
                self.check("agentPoolProfiles[0].osType", "Linux"),
                self.check("agentPoolProfiles[0].vmSize", "Standard_DS2_v2"),
                self.check("agentPoolProfiles[0].mode", "System"),
                self.check("dnsPrefix", "{dns_name_prefix}"),
                self.exists("kubernetesVersion"),
            ],
        )

        # get-credentials
        fd, temp_path = tempfile.mkstemp()
        self.kwargs.update({"file": temp_path})
        try:
            self.cmd(
                'aks get-credentials -g {resource_group} -n {name} --file "{file}"'
            )
            self.assertGreater(os.path.getsize(temp_path), 0)
        finally:
            os.close(fd)
            os.remove(temp_path)

        # nodepool update nodepool1 taints
        self.cmd(
            "aks nodepool update --resource-group={resource_group} --cluster-name={name} --name={nodepool1_name} --node-taints {taints}",
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # nodepool list
        self.cmd(
            "aks nodepool list --resource-group={resource_group} --cluster-name={name}",
            checks=[
                self.check("[0].mode", "System"),
                self.check("[0].nodeTaints[0]", "key1=value1:PreferNoSchedule"),
            ],
        )

        # nodepool delete nodepool1 label
        self.cmd(
            'aks nodepool update --resource-group={resource_group} --cluster-name={name} --name={nodepool1_name} --node-taints "" '
        )

        # nodepool show
        self.cmd(
            "aks nodepool show --resource-group={resource_group} --cluster-name={name} --name={nodepool1_name} -o json",
            checks=[self.check("nodeTaints", None)],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_nodepool_update_label_msi(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool1_name = "nodepool1"
        nodepool2_name = "nodepool2"
        tags = "key1=value1"
        new_tags = "key2=value2"
        labels = "label1=value1"
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "ssh_key_value": self.generate_ssh_keys(),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "tags": tags,
                "new_tags": new_tags,
                "labels": labels,
                "nodepool1_name": nodepool1_name,
                "nodepool2_name": nodepool2_name,
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--dns-name-prefix={dns_name_prefix} --node-count=1 --ssh-key-value={ssh_key_value} "
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # show
        self.cmd(
            "aks show -g {resource_group} -n {name}",
            checks=[
                self.check("type", "{resource_type}"),
                self.check("name", "{name}"),
                self.exists("nodeResourceGroup"),
                self.check("resourceGroup", "{resource_group}"),
                self.check("agentPoolProfiles[0].count", 1),
                self.check("agentPoolProfiles[0].osType", "Linux"),
                self.check("agentPoolProfiles[0].vmSize", "Standard_DS2_v2"),
                self.check("agentPoolProfiles[0].mode", "System"),
                self.check("dnsPrefix", "{dns_name_prefix}"),
                self.exists("kubernetesVersion"),
            ],
        )

        # get-credentials
        fd, temp_path = tempfile.mkstemp()
        self.kwargs.update({"file": temp_path})
        try:
            self.cmd(
                'aks get-credentials -g {resource_group} -n {name} --file "{file}"'
            )
            self.assertGreater(os.path.getsize(temp_path), 0)
        finally:
            os.close(fd)
            os.remove(temp_path)

        # nodepool update nodepool1 label
        self.cmd(
            "aks nodepool update --resource-group={resource_group} --cluster-name={name} --name={nodepool1_name} --labels {labels}",
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # nodepool list
        self.cmd(
            "aks nodepool list --resource-group={resource_group} --cluster-name={name}",
            checks=[
                self.check("[0].mode", "System"),
                self.check("[0].nodeLabels.label1", "value1"),
            ],
        )

        # nodepool delete nodepool1 label
        self.cmd(
            "aks nodepool update --resource-group={resource_group} --cluster-name={name} --name={nodepool1_name} --labels ",
            checks=[self.check("nodeLabels.label1", None)],
        )

        # nodepool show
        self.cmd(
            "aks nodepool show --resource-group={resource_group} --cluster-name={name} --name={nodepool1_name}",
            checks=[self.check("nodeLabels.label1", None)],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_update_label_msi(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool1_name = "nodepool1"
        nodepool2_name = "nodepool2"
        tags = "key1=value1"
        new_tags = "key2=value2"
        nodepool_labels = "label1=value1 label2=value2"
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "ssh_key_value": self.generate_ssh_keys(),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "tags": tags,
                "new_tags": new_tags,
                "nodepool1_name": nodepool1_name,
                "nodepool2_name": nodepool2_name,
                "nodepool_labels": nodepool_labels,
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--dns-name-prefix={dns_name_prefix} --node-count=1 --ssh-key-value={ssh_key_value} "
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--nodepool-labels {nodepool_labels}"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("agentPoolProfiles[0].nodeLabels.label1", "value1"),
                self.check("agentPoolProfiles[0].nodeLabels.label2", "value2"),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--nodepool-labels "
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("agentPoolProfiles[0].nodeLabels.label1", None),
                self.check("agentPoolProfiles[0].nodeLabels.label2", None),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_update_taint_msi(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool1_name = "nodepool1"
        nodepool2_name = "nodepool2"
        tags = "key1=value1"
        new_tags = "key2=value2"
        nodepool_taints = (
            "taint1=value1:PreferNoSchedule,taint2=value2:PreferNoSchedule"
        )
        nodepool_taints2 = "taint1=value2:PreferNoSchedule"
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "ssh_key_value": self.generate_ssh_keys(),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "tags": tags,
                "new_tags": new_tags,
                "nodepool1_name": nodepool1_name,
                "nodepool2_name": nodepool2_name,
                "nodepool_taints": nodepool_taints,
                "nodepool_taints2": nodepool_taints2,
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--dns-name-prefix={dns_name_prefix} --node-count=1 --ssh-key-value={ssh_key_value} --nodepool-taints {nodepool_taints} "
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "agentPoolProfiles[0].nodeTaints[0]",
                    "taint1=value1:PreferNoSchedule",
                ),
                self.check(
                    "agentPoolProfiles[0].nodeTaints[1]",
                    "taint2=value2:PreferNoSchedule",
                ),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--nodepool-taints {nodepool_taints2}"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "agentPoolProfiles[0].nodeTaints[0]",
                    "taint1=value2:PreferNoSchedule",
                ),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            '--nodepool-taints ""'
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("agentPoolProfiles[0].nodeTaints", None),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="centraluseuap"
    )
    def test_aks_create_with_oidc_issuer_enabled(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--enable-managed-identity "
            "--enable-oidc-issuer "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableOIDCIssuerPreview "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("oidcIssuerProfile.enabled", True),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="centraluseuap"
    )
    def test_aks_update_with_oidc_issuer_enabled(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--enable-managed-identity "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableOIDCIssuerPreview "
            "--enable-oidc-issuer"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("oidcIssuerProfile.enabled", True),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="centraluseuap"
    )
    def test_aks_create_with_workload_identity_enabled(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = " ".join(
            [
                "aks",
                "create",
                "--resource-group={resource_group}",
                "--name={name}",
                "--location={location}",
                "--enable-managed-identity",
                "--enable-oidc-issuer",
                "--enable-workload-identity",
                "--ssh-key-value={ssh_key_value}",
                "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableWorkloadIdentityPreview,AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableOIDCIssuerPreview",
            ]
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("oidcIssuerProfile.enabled", True),
                self.check("securityProfile.workloadIdentity.enabled", True),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="centraluseuap"
    )
    def test_aks_update_with_workload_identity(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = " ".join(
            [
                "aks",
                "create",
                "--resource-group={resource_group}",
                "--name={name}",
                "--location={location}",
                "--enable-managed-identity",
                "--enable-oidc-issuer",
                "--ssh-key-value={ssh_key_value}",
                "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableWorkloadIdentityPreview,AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableOIDCIssuerPreview",
            ]
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        enable_cmd = " ".join(
            [
                "aks",
                "update",
                "--resource-group={resource_group}",
                "--name={name}",
                "--enable-workload-identity",
                "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableWorkloadIdentityPreview,AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableOIDCIssuerPreview",
            ]
        )
        self.cmd(
            enable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.workloadIdentity.enabled", True),
            ],
        )

        disable_cmd = " ".join(
            [
                "aks",
                "update",
                "--resource-group={resource_group}",
                "--name={name}",
                "--disable-workload-identity",
                "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableWorkloadIdentityPreview,AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableOIDCIssuerPreview",
            ]
        )
        self.cmd(
            disable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.workloadIdentity.enabled", False),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_image_cleaner_enabled_with_default_interval_hours(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "vm_size": "Standard_D4s_v3",
                "node_count": 1,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = " ".join(
            [
                "aks",
                "create",
                "--resource-group={resource_group}",
                "--name={name}",
                "--location={location}",
                "--node-vm-size {vm_size}",
                "--node-count {node_count}",
                "--enable-image-cleaner",
                "--ssh-key-value={ssh_key_value}",
                "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableImageCleanerPreview",
            ]
        )

        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.imageCleaner.enabled", True),
                self.check("securityProfile.imageCleaner.intervalHours", 7 * 24),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_image_cleaner_enabled_with_interval_hours(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "vm_size": "Standard_D4s_v3",
                "node_count": 1,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = " ".join(
            [
                "aks",
                "create",
                "--resource-group={resource_group}",
                "--name={name}",
                "--location={location}",
                "--node-vm-size {vm_size}",
                "--node-count {node_count}",
                "--enable-image-cleaner",
                "--image-cleaner-interval-hours 24",
                "--ssh-key-value={ssh_key_value}",
                "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableImageCleanerPreview",
            ]
        )

        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.imageCleaner.enabled", True),
                self.check("securityProfile.imageCleaner.intervalHours", 24),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_update_with_image_cleaner(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "vm_size": "Standard_D4s_v3",
                "node_count": 1,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = " ".join(
            [
                "aks",
                "create",
                "--resource-group={resource_group}",
                "--name={name}",
                "--location={location}",
                "--node-vm-size {vm_size}",
                "--node-count {node_count}",
                "--enable-image-cleaner",
                "--ssh-key-value={ssh_key_value}",
                "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableImageCleanerPreview",
            ]
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.imageCleaner.enabled", True),
                self.check("securityProfile.imageCleaner.intervalHours", 7 * 24),
            ],
        )

        update_interval_cmd = " ".join(
            [
                "aks",
                "update",
                "--resource-group={resource_group}",
                "--name={name}",
                "--image-cleaner-interval-hours 24",
                "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableImageCleanerPreview",
            ]
        )
        self.cmd(
            update_interval_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.imageCleaner.enabled", True),
                self.check("securityProfile.imageCleaner.intervalHours", 24),
            ],
        )

        disable_cmd = " ".join(
            [
                "aks",
                "update",
                "--resource-group={resource_group}",
                "--name={name}",
                "--disable-image-cleaner",
                "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableImageCleanerPreview",
            ]
        )
        self.cmd(
            disable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.imageCleaner.enabled", False),
                self.check("securityProfile.imageCleaner.intervalHours", 24),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_image_integrity_enabled(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "vm_size": "Standard_D4s_v3",
                "node_count": 1,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = " ".join(
            [
                "aks",
                "create",
                "--resource-group={resource_group}",
                "--name={name}",
                "--location={location}",
                "--node-vm-size {vm_size}",
                "--node-count {node_count}",
                "--enable-image-integrity",
                "-a azure-policy",
                "--enable-oidc-issuer",
                "--ssh-key-value={ssh_key_value}",
                "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableImageIntegrityPreview,AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-AzurePolicyExternalData",
            ]
        )

        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.imageIntegrity.enabled", True),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_update_with_image_integrity(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        request_body = (
            '{"type": "Microsoft.ContainerService/managedClusters", "name": "'
            + aks_name
            + '", "location": "'
            + resource_group_location
            + '", "properties": {"securityProfile": {"imageIntegrity": {"enabled": true}}}}'
        )

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "vm_size": "Standard_D4s_v3",
                "node_count": 1,
                "ssh_key_value": self.generate_ssh_keys(),
                "request_body": request_body,
            }
        )

        create_cmd = " ".join(
            [
                "aks",
                "create",
                "--resource-group={resource_group}",
                "--name={name}",
                "--location={location}",
                "--node-vm-size {vm_size}",
                "--node-count {node_count}",
                "-a azure-policy",
                "--enable-oidc-issuer",
                "--ssh-key-value={ssh_key_value}",
                "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-AzurePolicyExternalData",
            ]
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        enable_cmd = " ".join(
            [
                "aks",
                "update",
                "--resource-group={resource_group}",
                "--name={name}",
                "--enable-image-integrity",
                "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableImageIntegrityPreview",
            ]
        )
        self.cmd(
            enable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.imageIntegrity.enabled", True),
            ],
        )

        disable_cmd = " ".join(
            [
                "aks",
                "update",
                "--resource-group={resource_group}",
                "--name={name}",
                "--disable-image-integrity",
            ]
        )
        self.cmd(
            disable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.imageIntegrity.enabled", False),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_crg_id(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        node_pool_name = self.create_random_name("c", 6)
        node_pool_name_second = self.create_random_name("c", 6)
        crg_id = (
            "/subscriptions/26fe00f8-9173-4872-9134-bb1d2e00343a/resourceGroups/STAGING-CRG-RG/providers"
            "/Microsoft.Compute/capacityReservationGroups/crg-3"
        )
        vm_size = "Standard_D4s_v3"
        count = 1
        identity = "/subscriptions/26fe00f8-9173-4872-9134-bb1d2e00343a/resourceGroups/staging-crg-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/crg-rg-id"

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "count": count,
                "location": resource_group_location,
                "crg_id": crg_id,
                "vm_size": vm_size,
                "identity": identity,
                "node_pool_name": node_pool_name,
                "node_pool_name_second": node_pool_name_second,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--node-vm-size {vm_size} "
            "--nodepool-name {node_pool_name} -c 1 "
            "--enable-managed-identity "
            "--assign-identity {identity} "
            "--crg-id={crg_id} "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # nodepool get-upgrades
        self.cmd(
            "aks nodepool add "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "--name={node_pool_name_second} "
            "--node-vm-size {vm_size} "
            "--crg-id={crg_id} "
            "-c 1 ",
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_network_plugin_none(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --network-plugin=none "
            "--location={location} --ssh-key-value={ssh_key_value} -o json"
        )

        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.networkPlugin", "none"),
            ],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="centraluseuap"
    )
    def test_aks_create_with_azurekeyvaultkms_public_key_vault(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        kv_name = self.create_random_name("cliakstestkv", 16)
        identity_name = self.create_random_name("cliakstestidentity", 24)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "kv_name": kv_name,
                "identity_name": identity_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create user-assigned identity
        create_identity = "identity create --resource-group={resource_group} --name={identity_name} -o json"
        identity = self.cmd(create_identity).get_output_in_json()
        identity_id = identity["id"]
        identity_object_id = identity["principalId"]
        assert identity_id is not None
        assert identity_object_id is not None
        self.kwargs.update(
            {
                "identity_id": identity_id,
                "identity_object_id": identity_object_id,
            }
        )

        # create key vault and key
        create_keyvault = (
            "keyvault create --resource-group={resource_group} --name={kv_name} -o json"
        )
        self.cmd(
            create_keyvault,
            checks=[self.check("properties.provisioningState", "Succeeded")],
        )

        create_key = "keyvault key create -n kms --vault-name {kv_name} -o json"
        key = self.cmd(
            create_key, checks=[self.check("attributes.enabled", True)]
        ).get_output_in_json()
        key_id_0 = key["key"]["kid"]
        assert key_id_0 is not None
        self.kwargs.update(
            {
                "key_id": key_id_0,
            }
        )

        # assign access policy
        set_policy = (
            "keyvault set-policy --resource-group={resource_group} --name={kv_name} "
            "--object-id {identity_object_id} --key-permissions encrypt decrypt -o json"
        )
        self.cmd(
            set_policy, checks=[self.check("properties.provisioningState", "Succeeded")]
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--assign-identity {identity_id} "
            "--enable-azure-keyvault-kms --azure-keyvault-kms-key-id={key_id} --azure-keyvault-kms-key-vault-network-access=Public "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.azureKeyVaultKms.enabled", True),
                self.check("securityProfile.azureKeyVaultKms.keyId", key_id_0),
                self.check(
                    "securityProfile.azureKeyVaultKms.keyVaultNetworkAccess", "Public"
                ),
            ],
        )

        key = self.cmd(
            create_key, checks=[self.check("attributes.enabled", True)]
        ).get_output_in_json()
        key_id_1 = key["key"]["kid"]
        assert key_id_1 is not None
        self.kwargs.update(
            {
                "key_id": key_id_1,
            }
        )

        # Rotate key
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--enable-azure-keyvault-kms --azure-keyvault-kms-key-id={key_id} --azure-keyvault-kms-key-vault-network-access=Public "
            "-o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.azureKeyVaultKms.enabled", True),
                self.check("securityProfile.azureKeyVaultKms.keyId", key_id_1),
                self.check(
                    "securityProfile.azureKeyVaultKms.keyVaultNetworkAccess", "Public"
                ),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="centraluseuap"
    )
    def test_aks_update_with_azurekeyvaultkms_public_key_vault(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        kv_name = self.create_random_name("cliakstestkv", 16)
        identity_name = self.create_random_name("cliakstestidentity", 24)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "kv_name": kv_name,
                "identity_name": identity_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create user-assigned identity
        create_identity = "identity create --resource-group={resource_group} --name={identity_name} -o json"
        identity = self.cmd(create_identity).get_output_in_json()
        identity_id = identity["id"]
        identity_object_id = identity["principalId"]
        assert identity_id is not None
        assert identity_object_id is not None
        self.kwargs.update(
            {
                "identity_id": identity_id,
                "identity_object_id": identity_object_id,
            }
        )

        # create key vault and key
        create_keyvault = (
            "keyvault create --resource-group={resource_group} --name={kv_name} -o json"
        )
        self.cmd(
            create_keyvault,
            checks=[self.check("properties.provisioningState", "Succeeded")],
        )

        create_key = "keyvault key create -n kms --vault-name {kv_name} -o json"
        key = self.cmd(
            create_key, checks=[self.check("attributes.enabled", True)]
        ).get_output_in_json()
        key_id = key["key"]["kid"]
        assert key_id is not None
        self.kwargs.update(
            {
                "key_id": key_id,
            }
        )

        # assign access policy
        set_policy = (
            "keyvault set-policy --resource-group={resource_group} --name={kv_name} "
            "--object-id {identity_object_id} --key-permissions encrypt decrypt -o json"
        )
        self.cmd(
            set_policy, checks=[self.check("properties.provisioningState", "Succeeded")]
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--assign-identity {identity_id} "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.not_exists("securityProfile.azureKeyVaultKms"),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--enable-azure-keyvault-kms --azure-keyvault-kms-key-id={key_id} --azure-keyvault-kms-key-vault-network-access=Public "
            "-o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.azureKeyVaultKms.enabled", True),
                self.check("securityProfile.azureKeyVaultKms.keyId", key_id),
                self.check(
                    "securityProfile.azureKeyVaultKms.keyVaultNetworkAccess", "Public"
                ),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="centraluseuap",
        preserve_default_location=True,
    )
    def test_aks_create_with_azurekeyvaultkms_private_key_vault(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        kv_name = self.create_random_name("cliakstestkv", 16)
        identity_name = self.create_random_name("cliakstestidentity", 24)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "kv_name": kv_name,
                "identity_name": identity_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create user-assigned identity
        create_identity = "identity create --resource-group={resource_group} --name={identity_name} -o json"
        identity = self.cmd(create_identity).get_output_in_json()
        identity_id = identity["id"]
        identity_object_id = identity["principalId"]
        assert identity_id is not None
        assert identity_object_id is not None
        self.kwargs.update(
            {
                "identity_id": identity_id,
                "identity_object_id": identity_object_id,
            }
        )

        # create key vault and key
        create_keyvault = (
            "keyvault create --resource-group={resource_group} --name={kv_name} -o json"
        )
        kv = self.cmd(
            create_keyvault,
            checks=[self.check("properties.provisioningState", "Succeeded")],
        ).get_output_in_json()
        kv_resource_id = kv["id"]
        assert kv_resource_id is not None
        self.kwargs.update(
            {
                "kv_resource_id": kv_resource_id,
            }
        )

        create_key = "keyvault key create -n kms --vault-name {kv_name} -o json"
        key = self.cmd(
            create_key, checks=[self.check("attributes.enabled", True)]
        ).get_output_in_json()
        key_id_0 = key["key"]["kid"]
        assert key_id_0 is not None
        self.kwargs.update(
            {
                "key_id": key_id_0,
            }
        )

        # assign access policy
        set_policy = (
            "keyvault set-policy --resource-group={resource_group} --name={kv_name} "
            "--object-id {identity_object_id} --key-permissions encrypt decrypt -o json"
        )
        self.cmd(
            set_policy, checks=[self.check("properties.provisioningState", "Succeeded")]
        )

        # allow the identity approve private endpoint connection (Microsoft.KeyVault/vaults/privateEndpointConnectionsApproval/action)
        create_role_assignment = (
            "role assignment create --role f25e0fa2-a7c8-4377-a976-54943a77a395 "
            '--assignee-object-id {identity_object_id} --assignee-principal-type "ServicePrincipal" '
            "--scope {kv_resource_id}"
        )
        self.cmd(create_role_assignment)

        # disable public network access
        disable_public_network_access = 'keyvault update --resource-group={resource_group} --name={kv_name} --public-network-access "Disabled" -o json'
        kv = self.cmd(
            disable_public_network_access,
            checks=[self.check("properties.provisioningState", "Succeeded")],
        ).get_output_in_json()

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--assign-identity {identity_id} "
            "--enable-azure-keyvault-kms --azure-keyvault-kms-key-id={key_id} "
            "--azure-keyvault-kms-key-vault-network-access=Private --azure-keyvault-kms-key-vault-resource-id {kv_resource_id} "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.azureKeyVaultKms.enabled", True),
                self.check("securityProfile.azureKeyVaultKms.keyId", key_id_0),
                self.check(
                    "securityProfile.azureKeyVaultKms.keyVaultNetworkAccess", "Private"
                ),
                self.check(
                    "securityProfile.azureKeyVaultKms.keyVaultResourceId",
                    kv_resource_id,
                ),
            ],
        )

        # enable public network access
        enable_public_network_access = 'keyvault update --resource-group={resource_group} --name={kv_name} --public-network-access "Enabled" -o json'
        kv = self.cmd(
            enable_public_network_access,
            checks=[self.check("properties.provisioningState", "Succeeded")],
        ).get_output_in_json()

        key = self.cmd(
            create_key, checks=[self.check("attributes.enabled", True)]
        ).get_output_in_json()
        key_id_1 = key["key"]["kid"]
        assert key_id_1 is not None
        self.kwargs.update(
            {
                "key_id": key_id_1,
            }
        )

        # disable public network access
        disable_public_network_access = 'keyvault update --resource-group={resource_group} --name={kv_name} --public-network-access "Disabled" -o json'
        kv = self.cmd(
            disable_public_network_access,
            checks=[self.check("properties.provisioningState", "Succeeded")],
        ).get_output_in_json()

        # Rotate key
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--enable-azure-keyvault-kms --azure-keyvault-kms-key-id={key_id} "
            "--azure-keyvault-kms-key-vault-network-access=Private --azure-keyvault-kms-key-vault-resource-id {kv_resource_id} "
            "-o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.azureKeyVaultKms.enabled", True),
                self.check("securityProfile.azureKeyVaultKms.keyId", key_id_1),
                self.check(
                    "securityProfile.azureKeyVaultKms.keyVaultNetworkAccess", "Private"
                ),
                self.check(
                    "securityProfile.azureKeyVaultKms.keyVaultResourceId",
                    kv_resource_id,
                ),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="centraluseuap",
        preserve_default_location=True,
    )
    def test_aks_update_with_azurekeyvaultkms_private_key_vault(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        kv_name = self.create_random_name("cliakstestkv", 16)
        identity_name = self.create_random_name("cliakstestidentity", 24)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "kv_name": kv_name,
                "identity_name": identity_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create user-assigned identity
        create_identity = "identity create --resource-group={resource_group} --name={identity_name} -o json"
        identity = self.cmd(create_identity).get_output_in_json()
        identity_id = identity["id"]
        identity_object_id = identity["principalId"]
        assert identity_id is not None
        assert identity_object_id is not None
        self.kwargs.update(
            {
                "identity_id": identity_id,
                "identity_object_id": identity_object_id,
            }
        )

        # create key vault and key
        create_keyvault = (
            "keyvault create --resource-group={resource_group} --name={kv_name} -o json"
        )
        kv = self.cmd(
            create_keyvault,
            checks=[self.check("properties.provisioningState", "Succeeded")],
        ).get_output_in_json()
        kv_resource_id = kv["id"]
        assert kv_resource_id is not None
        self.kwargs.update(
            {
                "kv_resource_id": kv_resource_id,
            }
        )

        create_key = "keyvault key create -n kms --vault-name {kv_name} -o json"
        key = self.cmd(
            create_key, checks=[self.check("attributes.enabled", True)]
        ).get_output_in_json()
        key_id = key["key"]["kid"]
        assert key_id is not None
        self.kwargs.update(
            {
                "key_id": key_id,
            }
        )

        # assign access policy
        set_policy = (
            "keyvault set-policy --resource-group={resource_group} --name={kv_name} "
            "--object-id {identity_object_id} --key-permissions encrypt decrypt -o json"
        )
        self.cmd(
            set_policy, checks=[self.check("properties.provisioningState", "Succeeded")]
        )

        # allow the identity approve private endpoint connection (Microsoft.KeyVault/vaults/privateEndpointConnectionsApproval/action)
        create_role_assignment = (
            "role assignment create --role f25e0fa2-a7c8-4377-a976-54943a77a395 "
            '--assignee-object-id {identity_object_id} --assignee-principal-type "ServicePrincipal" '
            "--scope {kv_resource_id}"
        )
        self.cmd(create_role_assignment)

        # disable public network access
        disable_public_network_access = 'keyvault update --resource-group={resource_group} --name={kv_name} --public-network-access "Disabled" -o json'
        kv = self.cmd(
            disable_public_network_access,
            checks=[self.check("properties.provisioningState", "Succeeded")],
        ).get_output_in_json()

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--assign-identity {identity_id} "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.not_exists("securityProfile.azureKeyVaultKms"),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--enable-azure-keyvault-kms --azure-keyvault-kms-key-id={key_id} "
            "--azure-keyvault-kms-key-vault-network-access=Private --azure-keyvault-kms-key-vault-resource-id {kv_resource_id} "
            "-o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.azureKeyVaultKms.enabled", True),
                self.check("securityProfile.azureKeyVaultKms.keyId", key_id),
                self.check(
                    "securityProfile.azureKeyVaultKms.keyVaultNetworkAccess", "Private"
                ),
                self.check(
                    "securityProfile.azureKeyVaultKms.keyVaultResourceId",
                    kv_resource_id,
                ),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="centraluseuap",
        preserve_default_location=True,
    )
    def test_aks_create_with_azurekeyvaultkms_private_cluster_v1_private_key_vault(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        kv_name = self.create_random_name("cliakstestkv", 16)
        identity_name = self.create_random_name("cliakstestidentity", 24)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "kv_name": kv_name,
                "identity_name": identity_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create user-assigned identity
        create_identity = "identity create --resource-group={resource_group} --name={identity_name} -o json"
        identity = self.cmd(create_identity).get_output_in_json()
        identity_id = identity["id"]
        identity_object_id = identity["principalId"]
        assert identity_id is not None
        assert identity_object_id is not None
        self.kwargs.update(
            {
                "identity_id": identity_id,
                "identity_object_id": identity_object_id,
            }
        )

        # create key vault and key
        create_keyvault = (
            "keyvault create --resource-group={resource_group} --name={kv_name} -o json"
        )
        kv = self.cmd(
            create_keyvault,
            checks=[self.check("properties.provisioningState", "Succeeded")],
        ).get_output_in_json()
        kv_resource_id = kv["id"]
        assert kv_resource_id is not None
        self.kwargs.update(
            {
                "kv_resource_id": kv_resource_id,
            }
        )

        create_key = "keyvault key create -n kms --vault-name {kv_name} -o json"
        key = self.cmd(
            create_key, checks=[self.check("attributes.enabled", True)]
        ).get_output_in_json()
        key_id_0 = key["key"]["kid"]
        assert key_id_0 is not None
        self.kwargs.update(
            {
                "key_id": key_id_0,
            }
        )

        # assign access policy
        set_policy = (
            "keyvault set-policy --resource-group={resource_group} --name={kv_name} "
            "--object-id {identity_object_id} --key-permissions encrypt decrypt -o json"
        )
        self.cmd(
            set_policy, checks=[self.check("properties.provisioningState", "Succeeded")]
        )

        # allow the identity approve private endpoint connection (Microsoft.KeyVault/vaults/privateEndpointConnectionsApproval/action)
        create_role_assignment = (
            "role assignment create --role f25e0fa2-a7c8-4377-a976-54943a77a395 "
            '--assignee-object-id {identity_object_id} --assignee-principal-type "ServicePrincipal" '
            "--scope {kv_resource_id}"
        )
        self.cmd(create_role_assignment)

        # disable public network access
        disable_public_network_access = 'keyvault update --resource-group={resource_group} --name={kv_name} --public-network-access "Disabled" -o json'
        kv = self.cmd(
            disable_public_network_access,
            checks=[self.check("properties.provisioningState", "Succeeded")],
        ).get_output_in_json()

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--assign-identity {identity_id} --enable-private-cluster "
            "--enable-azure-keyvault-kms --azure-keyvault-kms-key-id={key_id} "
            "--azure-keyvault-kms-key-vault-network-access=Private --azure-keyvault-kms-key-vault-resource-id {kv_resource_id} "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("apiServerAccessProfile.enablePrivateCluster", "True"),
                self.check("securityProfile.azureKeyVaultKms.enabled", True),
                self.check("securityProfile.azureKeyVaultKms.keyId", key_id_0),
                self.check(
                    "securityProfile.azureKeyVaultKms.keyVaultNetworkAccess", "Private"
                ),
                self.check(
                    "securityProfile.azureKeyVaultKms.keyVaultResourceId",
                    kv_resource_id,
                ),
            ],
        )

        # enable public network access
        enable_public_network_access = 'keyvault update --resource-group={resource_group} --name={kv_name} --public-network-access "Enabled" -o json'
        kv = self.cmd(
            enable_public_network_access,
            checks=[self.check("properties.provisioningState", "Succeeded")],
        ).get_output_in_json()

        key = self.cmd(
            create_key, checks=[self.check("attributes.enabled", True)]
        ).get_output_in_json()
        key_id_1 = key["key"]["kid"]
        assert key_id_1 is not None
        self.kwargs.update(
            {
                "key_id": key_id_1,
            }
        )

        # disable public network access
        disable_public_network_access = 'keyvault update --resource-group={resource_group} --name={kv_name} --public-network-access "Disabled" -o json'
        kv = self.cmd(
            disable_public_network_access,
            checks=[self.check("properties.provisioningState", "Succeeded")],
        ).get_output_in_json()

        # Rotate key
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--enable-azure-keyvault-kms --azure-keyvault-kms-key-id={key_id} "
            "--azure-keyvault-kms-key-vault-network-access=Private --azure-keyvault-kms-key-vault-resource-id {kv_resource_id} "
            "-o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.azureKeyVaultKms.enabled", True),
                self.check("securityProfile.azureKeyVaultKms.keyId", key_id_1),
                self.check(
                    "securityProfile.azureKeyVaultKms.keyVaultNetworkAccess", "Private"
                ),
                self.check(
                    "securityProfile.azureKeyVaultKms.keyVaultResourceId",
                    kv_resource_id,
                ),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="centraluseuap"
    )
    def test_aks_disable_azurekeyvaultkms(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        kv_name = self.create_random_name("cliakstestkv", 16)
        identity_name = self.create_random_name("cliakstestidentity", 24)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "kv_name": kv_name,
                "identity_name": identity_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create user-assigned identity
        create_identity = "identity create --resource-group={resource_group} --name={identity_name} -o json"
        identity = self.cmd(create_identity).get_output_in_json()
        identity_id = identity["id"]
        identity_object_id = identity["principalId"]
        assert identity_id is not None
        assert identity_object_id is not None
        self.kwargs.update(
            {
                "identity_id": identity_id,
                "identity_object_id": identity_object_id,
            }
        )

        # create key vault and key
        create_keyvault = (
            "keyvault create --resource-group={resource_group} --name={kv_name} -o json"
        )
        self.cmd(
            create_keyvault,
            checks=[self.check("properties.provisioningState", "Succeeded")],
        )

        create_key = "keyvault key create -n kms --vault-name {kv_name} -o json"
        key = self.cmd(
            create_key, checks=[self.check("attributes.enabled", True)]
        ).get_output_in_json()
        key_id = key["key"]["kid"]
        assert key_id is not None
        self.kwargs.update(
            {
                "key_id": key_id,
            }
        )

        # assign access policy
        set_policy = (
            "keyvault set-policy --resource-group={resource_group} --name={kv_name} "
            "--object-id {identity_object_id} --key-permissions encrypt decrypt -o json"
        )
        self.cmd(
            set_policy, checks=[self.check("properties.provisioningState", "Succeeded")]
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--assign-identity {identity_id} "
            "--enable-azure-keyvault-kms --azure-keyvault-kms-key-id={key_id} --azure-keyvault-kms-key-vault-network-access=Public "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.azureKeyVaultKms.enabled", True),
                self.check("securityProfile.azureKeyVaultKms.keyId", key_id),
                self.check(
                    "securityProfile.azureKeyVaultKms.keyVaultNetworkAccess", "Public"
                ),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--disable-azure-keyvault-kms "
            "-o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.azureKeyVaultKms.enabled", False),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="westcentralus",
        preserve_default_location=True,
    )
    def test_aks_create_and_update_with_csi_drivers_extensibility(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value} -o json \
                        --disable-disk-driver \
                        --disable-file-driver \
                        --disable-snapshot-controller"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.diskCsiDriver.enabled", False),
                self.check("storageProfile.diskCsiDriver.version", "v1"),
                self.check("storageProfile.fileCsiDriver.enabled", False),
                self.check("storageProfile.snapshotController.enabled", False),
            ],
        )

        # check standard reconcile scenario
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} -y -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.diskCsiDriver.enabled", False),
                self.check("storageProfile.diskCsiDriver.version", "v1"),
                self.check("storageProfile.fileCsiDriver.enabled", False),
                self.check("storageProfile.snapshotController.enabled", False),
            ],
        )

        enable_cmd = "aks update --resource-group={resource_group} --name={name} -o json \
                        --enable-disk-driver \
                        --enable-file-driver \
                        --enable-snapshot-controller"
        self.cmd(
            enable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.diskCsiDriver.enabled", True),
                self.check("storageProfile.diskCsiDriver.version", "v1"),
                self.check("storageProfile.fileCsiDriver.enabled", True),
                self.check("storageProfile.snapshotController.enabled", True),
            ],
        )

        # check standard reconcile scenario
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} -y -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.diskCsiDriver.enabled", True),
                self.check("storageProfile.diskCsiDriver.version", "v1"),
                self.check("storageProfile.fileCsiDriver.enabled", True),
                self.check("storageProfile.snapshotController.enabled", True),
            ],
        )

        disable_cmd = "aks update --resource-group={resource_group} --name={name} -o json \
                        --disable-disk-driver \
                        --disable-file-driver \
                        --disable-snapshot-controller -y"
        self.cmd(
            disable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.diskCsiDriver.enabled", False),
                self.check("storageProfile.diskCsiDriver.version", "v1"),
                self.check("storageProfile.fileCsiDriver.enabled", False),
                self.check("storageProfile.snapshotController.enabled", False),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="westcentralus",
        preserve_default_location=True,
    )
    def test_aks_create_with_standard_csi_drivers(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # check standard creation scenario
        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value} -o json"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.diskCsiDriver.enabled", True),
                self.check("storageProfile.diskCsiDriver.version", "v1"),
                self.check("storageProfile.fileCsiDriver.enabled", True),
                self.check("storageProfile.snapshotController.enabled", True),
            ],
        )

        # check standard reconcile scenario
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} -y -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.diskCsiDriver.enabled", True),
                self.check("storageProfile.diskCsiDriver.version", "v1"),
                self.check("storageProfile.fileCsiDriver.enabled", True),
                self.check("storageProfile.snapshotController.enabled", True),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="centraluseuap",
        preserve_default_location=True,
    )
    def test_aks_create_with_standard_blob_csi_driver(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # check standard creation scenario
        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value} -o json"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.blobCsiDriver.enabled", None),
            ],
        )

        # check standard reconcile scenario
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} -y -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.blobCsiDriver.enabled", None),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="centraluseuap",
        preserve_default_location=True,
    )
    def test_aks_create_and_update_with_blob_csi_driver(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create aks with blob driver
        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value} -o json \
                        --enable-blob-driver \
                        --aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableBlobCSIDriver"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.blobCsiDriver.enabled", True),
            ],
        )

        # check standard reconcile scenario
        update_cmd = "aks update --resource-group={resource_group} --name={name} -y -o json \
                        --aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableBlobCSIDriver"
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.blobCsiDriver.enabled", True),
            ],
        )

        # disable blob driver
        disable_cmd = "aks update --resource-group={resource_group} --name={name} -o json \
                        --disable-blob-driver -y \
                        --aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableBlobCSIDriver"
        self.cmd(
            disable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.blobCsiDriver.enabled", False),
            ],
        )

        # check standard reconcile scenario
        update_cmd = "aks update --resource-group={resource_group} --name={name} -y -o json \
                        --aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableBlobCSIDriver"
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.blobCsiDriver.enabled", False),
            ],
        )

        # enable blob driver
        enable_cmd = "aks update --resource-group={resource_group} --name={name} -o json \
                        --enable-blob-driver -y \
                        --aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableBlobCSIDriver"
        self.cmd(
            enable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.blobCsiDriver.enabled", True),
            ],
        )

        # check standard reconcile scenario
        update_cmd = "aks update --resource-group={resource_group} --name={name} -y -o json \
                        --aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableBlobCSIDriver"
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.blobCsiDriver.enabled", True),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="centraluseuap",
        preserve_default_location=True,
    )
    def test_aks_create_with_csi_driver_v2(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = 'aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value} -o json \
                        --disk-driver-version "v2" \
                        --disable-file-driver \
                        --disable-snapshot-controller'
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.diskCsiDriver.enabled", True),
                self.check("storageProfile.diskCsiDriver.version", "v2"),
                self.check("storageProfile.fileCsiDriver.enabled", False),
                self.check("storageProfile.snapshotController.enabled", False),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="centraluseuap",
        preserve_default_location=True,
    )
    def test_aks_create_and_update_csi_driver_to_v2(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value} -o json \
                        --disable-disk-driver \
                        --disable-file-driver \
                        --disable-snapshot-controller"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.diskCsiDriver.enabled", False),
                self.check("storageProfile.diskCsiDriver.version", "v1"),
                self.check("storageProfile.fileCsiDriver.enabled", False),
                self.check("storageProfile.snapshotController.enabled", False),
            ],
        )

        enable_cmd = 'aks update --resource-group={resource_group} --name={name} -o json \
                        --enable-disk-driver \
                        --disk-driver-version "v2"'
        self.cmd(
            enable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("storageProfile.diskCsiDriver.enabled", True),
                self.check("storageProfile.diskCsiDriver.version", "v2"),
                self.check("storageProfile.fileCsiDriver.enabled", False),
                self.check("storageProfile.snapshotController.enabled", False),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="centraluseuap"
    )
    def test_aks_create_with_apiserver_vnet_integration(
        self, resource_group, resource_group_location
    ):
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-apiserver-vnet-integration "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableAPIServerVnetIntegrationPreview "
            "--enable-private-cluster --location={location} --ssh-key-value={ssh_key_value} -o json"
        )

        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("apiServerAccessProfile.enablePrivateCluster", "True"),
                self.check("apiServerAccessProfile.enableVnetIntegration", "True"),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="centraluseuap",
        preserve_default_location=True,
    )
    def test_aks_create_with_apiserver_vnet_integration_public(
        self, resource_group, resource_group_location
    ):
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --enable-apiserver-vnet-integration "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/EnableAPIServerVnetIntegrationPreview "
            "--location={location} --ssh-key-value={ssh_key_value} -o json"
        )

        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("apiServerAccessProfile.enablePrivateCluster", "False"),
                self.check("apiServerAccessProfile.enableVnetIntegration", "True"),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_web_application_routing(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--enable-addons web_application_routing --ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("ingressProfile.webAppRouting.enabled", True),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_web_application_routing_with_private_dns_zone(
        self, resource_group, resource_group_location
    ):
        # Test creation failure when using an non-existing dns zone resource ID.
        aks_name = self.create_random_name("cliakstest", 16)
        private_dns_zone_name = self.create_random_name("cliakstest", 16) + ".xyz"
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "private_dns_zone_name": private_dns_zone_name,
            }
        )

        create_private_dns_zone_cmd = "network private-dns zone create -g {resource_group} -n {private_dns_zone_name}"
        private_dns_zone_id = self.cmd(
            create_private_dns_zone_cmd,
            checks=[
                self.check("name", private_dns_zone_name),
            ],
        ).get_output_in_json()["id"]

        self.kwargs.update({"private_dns_zone_id": private_dns_zone_id})

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--enable-addons web_application_routing "
            "--dns-zone-resource-ids={private_dns_zone_id} "
            "--ssh-key-value={ssh_key_value} -o json"
        )

        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("ingressProfile.webAppRouting.enabled", True),
                self.check(
                    "ingressProfile.webAppRouting.dnsZoneResourceIds[0]",
                    private_dns_zone_id,
                ),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_disable_addon_web_app_routing(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "-a web_application_routing --ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("ingressProfile.webAppRouting.enabled", True),
            ],
        )

        disable_cmd = "aks disable-addons --addons web_application_routing --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            disable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded")
                # Enable this once the backend bug fix has been rolled out.
                # self.check('ingressProfile.webAppRouting.enabled', False)
            ],
        )

    # graph api is not well mocked
    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_and_update_web_application_routing_dns_zone(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        dns_zone_name = self.create_random_name("cliakstest", 16) + ".xyz"
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_zone_name": dns_zone_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "-a web_application_routing --ssh-key-value={ssh_key_value} -o json"
        )
        mc = self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("ingressProfile.webAppRouting.enabled", True),
            ],
        ).get_output_in_json()
        web_app_routing_identity_obj_id = mc["ingressProfile"]["webAppRouting"][
            "identity"
        ]["objectId"]

        create_dns_zone_cmd = (
            "network dns zone create -g {resource_group} -n {dns_zone_name}"
        )
        dns_zone = self.cmd(
            create_dns_zone_cmd,
            checks=[
                self.check("name", dns_zone_name),
            ],
        ).get_output_in_json()
        dns_zone_id = dns_zone["id"]

        self.kwargs.update(
            {
                "web_app_routing_identity_obj_id": web_app_routing_identity_obj_id,
                "dns_zone_id": dns_zone_id,
            }
        )

        role_assignment_cmd = 'role assignment create --role "DNS Zone Contributor" --assignee {web_app_routing_identity_obj_id} --scope {dns_zone_id}'
        self.cmd(role_assignment_cmd)

        addon_update_cmd = "aks addon update -g {resource_group} -n {name} --addon web_application_routing --dns-zone-resource-ids={dns_zone_id}"
        self.cmd(
            addon_update_cmd, checks=[self.check("provisioningState", "Succeeded")]
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_keda(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create: enable-keda
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} --ssh-key-value={ssh_key_value} --output=json "
            "--aks-custom-headers=AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-KedaPreview "
            "--enable-keda"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("workloadAutoScalerProfile.keda.enabled", True),
            ],
        )

        # delete
        delete_cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            delete_cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_update_with_keda(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create: without enable-keda
        create_cmd = "aks create --resource-group={resource_group} --name={name} --location={location} --ssh-key-value={ssh_key_value} --output=json"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.not_exists("workloadAutoScalerProfile.keda"),
            ],
        )

        # update: enable-keda
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} --yes --output=json "
            "--aks-custom-headers=AKSHTTPCustomFeatures=Microsoft.ContainerService/AKS-KedaPreview "
            "--enable-keda"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("workloadAutoScalerProfile.keda.enabled", True),
            ],
        )

        # update: disable-keda
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} --yes --output=json "
            "--disable-keda"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("workloadAutoScalerProfile.keda.enabled", False),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @live_only()  # this test requires live_only because a binary is downloaded
    def test_aks_draft_with_helm(self):
        import os
        import tempfile

        script_dir = os.path.dirname(__file__)
        create_config = "aks_draft_config/helm.yaml"
        abs_file_path = os.path.join(script_dir, create_config)

        with tempfile.TemporaryDirectory() as tmp_dir:
            # test `create`
            create_cmd = f"aks draft create --path={tmp_dir} --create-config={abs_file_path} --destination={tmp_dir}"
            self.cmd(create_cmd)
            assert os.path.isdir(f"{tmp_dir}/charts") and os.path.isfile(
                f"{tmp_dir}/Dockerfile"
            )

            # test `generate-workflow`
            generate_workflow_cmd = f"aks draft generate-workflow --path={tmp_dir} --branch=main --destination={tmp_dir} --cluster-name=someAksCluster --registry-name=someRegistry --resource-group=someResourceGroup --container-name=someContainer"
            self.cmd(generate_workflow_cmd)
            assert os.path.isfile(
                f"{tmp_dir}/charts/production.yaml"
            ) and os.path.isfile(
                f"{tmp_dir}/.github/workflows/azure-kubernetes-service-helm.yml"
            )

            # test `update`
            update_cmd = f"aks draft update --path={tmp_dir} --destination={tmp_dir} --host=testHost --certificate=testKV"
            self.cmd(update_cmd)
            assert os.path.isfile(f"{tmp_dir}/charts/production.yaml")

    @live_only()  # this test requires live_only because a binary is downloaded
    def test_aks_draft_with_kustomize(self):
        import os
        import tempfile

        script_dir = os.path.dirname(__file__)
        create_config = "aks_draft_config/kustomize.yaml"
        abs_file_path = os.path.join(script_dir, create_config)

        with tempfile.TemporaryDirectory() as tmp_dir:
            # test `create`
            create_cmd = f"aks draft create --path={tmp_dir} --create-config={abs_file_path} --destination={tmp_dir}"
            self.cmd(create_cmd)
            assert (
                os.path.isdir(f"{tmp_dir}/base")
                and os.path.isdir(f"{tmp_dir}/overlays/production")
                and os.path.isfile(f"{tmp_dir}/Dockerfile")
            )

            # test `generate-workflow`
            generate_workflow_cmd = f"aks draft generate-workflow --path={tmp_dir} --branch=main --destination={tmp_dir} --cluster-name=someAksCluster --registry-name=someRegistry --resource-group=someResourceGroup --container-name=someContainer"
            self.cmd(generate_workflow_cmd)
            assert os.path.isfile(
                f"{tmp_dir}/overlays/production/deployment.yaml"
            ) and os.path.isfile(
                f"{tmp_dir}/.github/workflows/azure-kubernetes-service-kustomize.yml"
            )

            # test `update`
            update_cmd = f"aks draft update --path={tmp_dir} --destination={tmp_dir} --host=testHost --certificate=testKV"
            self.cmd(update_cmd)
            assert os.path.isfile(f"{tmp_dir}/overlays/production/service.yaml")

    @live_only()  # this test requires live_only because a binary is downloaded
    def test_aks_draft_with_manifest(self):
        import os
        import tempfile

        script_dir = os.path.dirname(__file__)
        create_config = "aks_draft_config/manifest.yaml"
        abs_file_path = os.path.join(script_dir, create_config)

        with tempfile.TemporaryDirectory() as tmp_dir:
            create_cmd = f"aks draft create --path={tmp_dir} --create-config={abs_file_path} --destination={tmp_dir}"
            self.cmd(create_cmd)
            assert os.path.isdir(f"{tmp_dir}/manifests") and os.path.isfile(
                f"{tmp_dir}/Dockerfile"
            )

            # test `generate-workflow`
            generate_workflow_cmd = f"aks draft generate-workflow --path={tmp_dir} --branch=main --destination={tmp_dir} --cluster-name=someAksCluster --registry-name=someRegistry --resource-group=someResourceGroup --container-name=someContainer"
            self.cmd(generate_workflow_cmd)
            assert os.path.isfile(
                f"{tmp_dir}/.github/workflows/azure-kubernetes-service.yml"
            )

            # test `update`
            update_cmd = f"aks draft update --path={tmp_dir} --destination={tmp_dir} --host=testHost --certificate=testKV"
            self.cmd(update_cmd)
            assert os.path.isfile(f"{tmp_dir}/manifests/service.yaml")

    @live_only()  # because we're downloading a binary, and we're not testing the output of any ARM requests.
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="centraluseuap"
    )
    def test_aks_kollect(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        stg_acct_name = self.create_random_name("cliaksteststg", 24)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "location": resource_group_location,
                "aks_name": aks_name,
                "stg_acct_name": stg_acct_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_aks_cmd = "aks create --resource-group={resource_group} --name={aks_name} --location={location} --ssh-key-value={ssh_key_value} -o json"
        self.cmd(create_aks_cmd, checks=[self.check("provisioningState", "Succeeded")])

        create_stg_cmd = "storage account create --resource-group={resource_group} --name={stg_acct_name} --location={location} -o json"
        self.cmd(create_stg_cmd, checks=[self.check("provisioningState", "Succeeded")])

        # Install kubectl (required by the 'kollect' command).
        try:
            subprocess.call(["az", "aks", "install-cli"])
        except subprocess.CalledProcessError as err:
            raise CliTestError(f"Failed to install kubectl with error: '{err}'")

        self.assert_kollect_deploys_periscope(resource_group, aks_name, stg_acct_name)

    @live_only()  # because we're downloading a binary, and we're not testing the output of any ARM requests.
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="centraluseuap"
    )
    def test_aks_kollect_with_managed_aad(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        stg_acct_name = self.create_random_name("cliaksteststg", 24)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "location": resource_group_location,
                "aks_name": aks_name,
                "stg_acct_name": stg_acct_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # Initially create with local accounts enabled (the default), so that we can use the admin account
        # to grant the necessary k8s permissions to the AD user (the service principal).
        create_aks_cmd = (
            "aks create --resource-group={resource_group} --name={aks_name} "
            "--location={location} --ssh-key-value={ssh_key_value} "
            "--vm-set-type VirtualMachineScaleSets -c 1 "
            "--enable-aad --aad-admin-group-object-ids 00000000-0000-0000-0000-000000000001 "
            "-o json"
        )
        self.cmd(
            create_aks_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("aadProfile.managed", True),
                self.check(
                    "aadProfile.adminGroupObjectIDs[0]",
                    "00000000-0000-0000-0000-000000000001",
                ),
                self.check("disableLocalAccounts", False),
            ],
        )

        # Get the object ID of the service principal
        show_acct_cmd = "account show"
        authenticated_acct = self.cmd(show_acct_cmd).get_output_in_json()
        sp_name = authenticated_acct["user"]["name"]
        show_sp_cmd = f"ad sp show --id {sp_name}"
        sp = self.cmd(
            show_sp_cmd, checks=[self.check("appId", sp_name)]
        ).get_output_in_json()
        sp_oid = sp["id"]
        print(f"objectid of service principal is {sp_oid}")

        # Install kubectl (for setting up service principal permissions, and required by the 'kollect' command).
        try:
            subprocess.call(["az", "aks", "install-cli"])
        except subprocess.CalledProcessError as err:
            raise CliTestError(f"Failed to install kubectl with error: '{err}'")

        # Grant the service principal cluster-admin access using the admin account
        # (it'd be nice if `az aks command invoke` had an --admin option, but it appears not to, so we have to download admin credentials)
        fd, admin_kubeconfig_path = tempfile.mkstemp()
        self.kwargs.update({"kubeconfig_path": admin_kubeconfig_path})
        try:
            get_credential_cmd = "aks get-credentials --resource-group={resource_group} --name={aks_name} --admin -f {kubeconfig_path}"
            self.cmd(get_credential_cmd)
            create_rolebinding_output = subprocess.check_output(
                [
                    "kubectl",
                    "create",
                    "clusterrolebinding",
                    "--kubeconfig",
                    admin_kubeconfig_path,
                    "--clusterrole",
                    "cluster-admin",
                    "--user",
                    sp_oid,
                    "test-clusterrolebinding",
                ]
            )
            print(f"Output of create rolebinding:\n{create_rolebinding_output}")
        except subprocess.CalledProcessError as err:
            raise CliTestError(
                f"Failed to create admin clusterrolebinding for {sp_oid}: '{err}'"
            )
        finally:
            os.close(fd)
            os.remove(admin_kubeconfig_path)

        # Now the current user has the required permissions, we can disable admin access to the cluster
        disable_admin_cmd = "aks update --resource-group={resource_group} --name={aks_name} --disable-local-accounts"
        self.cmd(disable_admin_cmd, checks=[self.check("disableLocalAccounts", True)])

        # Create the storage account to which to upload Periscope output
        create_stg_cmd = "storage account create --resource-group={resource_group} --name={stg_acct_name} --location={location} -o json"
        self.cmd(create_stg_cmd, checks=[self.check("provisioningState", "Succeeded")])

        self.assert_kollect_deploys_periscope(resource_group, aks_name, stg_acct_name)

    def assert_kollect_deploys_periscope(self, resource_group, aks_name, stg_acct_name):
        # The kollect command is interactive, with two prompts requiring 'y|n' followed by newline.
        # The prompting library used by the CLI checks for the presence of a TTY, so just passing these as input is not
        # sufficient and will raise an exception; we also need to attach a pseudo-TTY to the process.
        ptyInFd, ptyOutFd = pty.openpty()
        try:
            with os.fdopen(ptyInFd, "w", closefd=False) as ptyIn:
                kollect_cmd = [
                    "az",
                    "aks",
                    "kollect",
                    "--resource-group",
                    resource_group,
                    "--name",
                    aks_name,
                    "--storage-account",
                    stg_acct_name,
                ]

                # For this test, the first input should be 'y' (to confirm), and the second should be 'n' (to see analysis results).
                # Write these to our PTY (they will be buffered until the command attempts to read them).
                kollect_stdin_responses = ["y\n", "n\n"]
                ptyIn.write("".join(kollect_stdin_responses))

                kollect_output = subprocess.check_output(
                    kollect_cmd, stdin=ptyOutFd, stderr=subprocess.STDOUT, text=True
                )
        except subprocess.CalledProcessError as err:
            raise CliTestError(
                f"Failed to kollect with exit code {err.returncode}. Output:\n{err.output}"
            )
        finally:
            os.close(ptyOutFd)
            os.close(ptyInFd)

        # Check expected output of kollect command
        for pattern in [
            f"This will deploy a daemon set to your cluster to collect logs and diagnostic information and save them to the storage account {stg_acct_name}",
            f"Your logs are being uploaded to storage account {stg_acct_name}",
            f"You can run 'az aks kanalyze -g {resource_group} -n {aks_name}' anytime to check the analysis results",
        ]:
            if pattern not in kollect_output:
                raise CliTestError(
                    f"Output from kollect did not contain '{pattern}'. Output:\n{kollect_output}"
                )

        # Invoke kubectl to get the daemonsets deployed to the cluster
        k_get_daemonset_cmd = [
            "az",
            "aks",
            "command",
            "invoke",
            "--resource-group",
            resource_group,
            "--name",
            aks_name,
            "--command",
            "kubectl get daemonset -n aks-periscope -o name",
        ]
        k_get_daemonset_output = subprocess.check_output(k_get_daemonset_cmd, text=True)

        # Check expected output of 'kubectl get daemonset' command
        for pattern in [
            "daemonset.apps/aks-periscope",
            "daemonset.apps/aks-periscope-win",
        ]:
            if pattern not in k_get_daemonset_output:
                raise CliTestError(
                    f"Output from 'kubectl get daemonset' did not contain '{pattern}'. Output:\n{k_get_daemonset_output}"
                )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_availability_zones(self, resource_group, resource_group_location):
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool2_name = "nodepool2"
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "nodepool2_name": nodepool2_name,
                "zones": "1 2 3",
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--node-count=1 --ssh-key-value={ssh_key_value} --zones {zones}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("agentPoolProfiles[0].availabilityZones[0]", "1"),
                self.check("agentPoolProfiles[0].availabilityZones[1]", "2"),
                self.check("agentPoolProfiles[0].availabilityZones[2]", "3"),
            ],
        )

        # nodepool add
        self.cmd(
            "aks nodepool add --resource-group={resource_group} --cluster-name={name} --name={nodepool2_name} --node-count=1 --zones {zones}",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("availabilityZones[0]", "1"),
                self.check("availabilityZones[1]", "2"),
                self.check("availabilityZones[2]", "3"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    # live only due to workspace is not mocked correctly
    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_defender(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "name": aks_name,
                "resource_group": resource_group,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--ssh-key-value={ssh_key_value} --enable-defender"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.defender.securityMonitoring.enabled", True),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    # live only due to workspace is not mocked correctly
    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_update_with_defender(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = "aks create --resource-group={resource_group} --name={name} --ssh-key-value={ssh_key_value}"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # update to enable defender
        self.cmd(
            "aks update --resource-group={resource_group} --name={name} --enable-defender",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("securityProfile.defender.securityMonitoring.enabled", True),
            ],
        )

        # update to disable defender
        self.cmd(
            "aks update --resource-group={resource_group} --name={name} --disable-defender",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "securityProfile.defender.securityMonitoring.enabled", False
                ),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_azuremonitormetrics(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)

        node_vm_size = "standard_d2s_v3"
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "ssh_key_value": self.generate_ssh_keys(),
                "node_vm_size": node_vm_size,
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} --ssh-key-value={ssh_key_value} --node-vm-size={node_vm_size} "
            "--enable-managed-identity --enable-azure-monitor-metrics --enable-windows-recording-rules --output=json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # azuremonitor metrics will be set to false after initial creation command as its in the
        # postprocessing step that we do an update to enable it. Adding a wait for the second put request
        # in addonput.py which enables the Azure Monitor Metrics addon as all the DC* resources
        # have now been created.
        wait_cmd = " ".join(
            [
                "aks",
                "wait",
                "--resource-group={resource_group}",
                "--name={name}",
                "--updated",
                "--interval 60",
                "--timeout 300",
            ]
        )
        self.cmd(
            wait_cmd,
            checks=[
                self.is_empty(),
            ],
        )

        self.cmd(
            "aks show -g {resource_group} -n {name} --output=json",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("azureMonitorProfile.metrics.enabled", True),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    # live only due to downloading k8s-extension extension
    @live_only()
    @AllowLargeResponse(8192)
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_azurecontainerstorage(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)

        node_vm_size = "standard_d4s_v3"
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "ssh_key_value": self.generate_ssh_keys(),
                "node_vm_size": node_vm_size,
            }
        )

        # add k8s-extension extension for azurecontainerstorage operations.
        self.cmd("extension add --name k8s-extension")

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} --ssh-key-value={ssh_key_value} --node-vm-size={node_vm_size} "
            "--node-count 3 --enable-managed-identity --enable-azure-container-storage azureDisk --output=json"
        )

        # enabling azurecontainerstorage will not affect any field in the cluster.
        # the only check we should perform is to verify that the cluster is provisioned successfully.
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    # live only due to downloading k8s-extension extension
    @live_only()
    @AllowLargeResponse(8192)
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_azurecontainerstorage_with_nodepool_name(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("n", 6)

        node_vm_size = "standard_d4s_v3"
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "ssh_key_value": self.generate_ssh_keys(),
                "node_vm_size": node_vm_size,
                "nodepool_name": nodepool_name,
            }
        )

        # add k8s-extension extension for azurecontainerstorage operations.
        self.cmd("extension add --name k8s-extension")

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} --ssh-key-value={ssh_key_value} --node-vm-size={node_vm_size} "
            "--node-count 3 --nodepool-name {nodepool_name} --enable-managed-identity --enable-azure-container-storage azureDisk --output=json"
        )

        # enabling azurecontainerstorage will not affect any field in the cluster.
        # the only check we should perform is to verify that the cluster is provisioned successfully.
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("agentPoolProfiles[0].name", nodepool_name),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_update_with_azuremonitormetrics(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        node_vm_size = "standard_d2s_v3"
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
                "node_vm_size": node_vm_size,
            }
        )

        # create: without enable-azure-monitor-metrics
        create_cmd = "aks create --resource-group={resource_group} --name={name} --location={location} --ssh-key-value={ssh_key_value} --node-vm-size={node_vm_size} --enable-managed-identity --output=json"
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.not_exists("azureMonitorProfile.metrics"),
            ],
        )

        # update: enable-azure-monitor-metrics
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} --yes --output=json "
            "--enable-azure-monitor-metrics --enable-managed-identity --enable-windows-recording-rules"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("azureMonitorProfile.metrics.enabled", True),
            ],
        )

        # update: disable-azure-monitor-metrics
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} --yes --output=json "
            "--disable-azure-monitor-metrics"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("azureMonitorProfile.metrics.enabled", False),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @live_only()
    @AllowLargeResponse(8192)
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_update_with_azurecontainerstorage(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        node_vm_size = 'standard_d4s_v3'
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'location': resource_group_location,
            'ssh_key_value': self.generate_ssh_keys(),
            'node_vm_size': node_vm_size,
        })

        # add k8s-extension extension for azurecontainerstorage operations.
        self.cmd('extension add --name k8s-extension')

        # create: without enable-azure-container-storage
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} --ssh-key-value={ssh_key_value} --node-vm-size={node_vm_size} --node-count 3 --enable-managed-identity --output=json'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

        # enabling or disabling azurecontainerstorage will not affect any field in the cluster.
        # the only check we should perform is to verify that the cluster is provisioned successfully.

        # update: enable-azure-container-storage
        update_cmd = 'aks update --resource-group={resource_group} --name={name} --yes --output=json ' \
                     '--enable-azure-container-storage azureDisk'
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

        # Sleep for 5 mins before next operation,
        # since azure container storage operations take
        # some time to post process.
        time.sleep(5 * 60)

        # update: disable-azure-container-storage
        update_cmd = 'aks update --resource-group={resource_group} --name={name} --yes --output=json ' \
                     '--disable-azure-container-storage all'
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

        # delete
        cmd = 'aks delete --resource-group={resource_group} --name={name} --yes --no-wait'
        self.cmd(cmd, checks=[
            self.is_empty(),
        ])

    # live only due to workspace is not mocked correctly
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_kube_proxy_config(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "kube_proxy_path": _get_test_data_file("kubeproxyconfig.json"),
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --kube-proxy-config={kube_proxy_path} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/KubeProxyConfigurationPreview "
            "--ssh-key-value={ssh_key_value} --enable-managed-identity --yes -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.kubeProxyConfig.enabled", True),
                self.check("networkProfile.kubeProxyConfig.mode", "IPTABLES"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    # live only due to workspace is not mocked correctly
    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_update_with_kube_proxy_config(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "kube_proxy_path": _get_test_data_file("kubeproxyconfig.json"),
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --kube-proxy-config={kube_proxy_path} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/KubeProxyConfigurationPreview "
            "--ssh-key-value={ssh_key_value} --enable-managed-identity --yes -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.kubeProxyConfig.enabled", True),
                self.check("networkProfile.kubeProxyConfig.mode", "IPTABLES"),
            ],
        )

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "kube_proxy_path": _get_test_data_file("kubeproxyconfig_update.json"),
            }
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} --kube-proxy-config={kube_proxy_path} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/KubeProxyConfigurationPreview"
        )

        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.kubeProxyConfig.enabled", True),
                self.check("networkProfile.kubeProxyConfig.mode", "IPVS"),
                self.check(
                    "networkProfile.kubeProxyConfig.ipvsConfig.scheduler",
                    "LeastConnection",
                ),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_create_with_nsg_control(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
                "node_vm_size": "standard_d2s_v3",
                "asg1": "asg1",
                "asg2": "asg2",
            }
        )

        create_asg1 = (
            "network asg create --name {asg1} --resource-group {resource_group} -o json"
        )
        create_asg2 = (
            "network asg create --name {asg2} --resource-group {resource_group} -o json"
        )
        asg1 = self.cmd(
            create_asg1, checks=[self.check("provisioningState", "Succeeded")]
        ).get_output_in_json()
        asg2 = self.cmd(
            create_asg2, checks=[self.check("provisioningState", "Succeeded")]
        ).get_output_in_json()

        self.kwargs.update(
            {
                "asg_ids": ",".join([asg1["id"], asg2["id"]]),
                "allowed_host_ports": ",".join(
                    ["53/udp", "80/tcp", "443/tcp", "4000-5000/tcp", "4000-6000/udp"]
                ),
            }
        )
        self.cmd(
            "aks create "
            "--resource-group={resource_group} "
            "--name={name} "
            "--location={location} "
            "--ssh-key-value={ssh_key_value} "
            "--node-count=1 "
            "--node-vm-size={node_vm_size} "
            "--nodepool-asg-ids={asg_ids} "
            "--nodepool-allowed-host-ports={allowed_host_ports} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/NodePublicIPNSGControlPreview",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "agentPoolProfiles[0].networkProfile.applicationSecurityGroups",
                    self.kwargs["asg_ids"].split(","),
                ),
                self.check(
                    "agentPoolProfiles[0].networkProfile.allowedHostPorts[] | length(@)",
                    len(self.kwargs["allowed_host_ports"].split(",")),
                ),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_nodepool_create_with_nsg_control(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("n", 6)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
                "node_pool_name": nodepool_name,
                "node_vm_size": "standard_d2s_v3",
                "asg1": "asg1",
                "asg2": "asg2",
            }
        )
        create_asg1 = (
            "network asg create --name {asg1} --resource-group {resource_group} -o json"
        )
        create_asg2 = (
            "network asg create --name {asg2} --resource-group {resource_group} -o json"
        )
        asg1 = self.cmd(
            create_asg1, checks=[self.check("provisioningState", "Succeeded")]
        ).get_output_in_json()
        asg2 = self.cmd(
            create_asg2, checks=[self.check("provisioningState", "Succeeded")]
        ).get_output_in_json()

        self.kwargs.update(
            {
                "asg_ids": ",".join([asg1["id"], asg2["id"]]),
                "allowed_host_ports": ",".join(
                    ["53/udp", "80/tcp", "443/tcp", "4000-5000/tcp", "4000-6000/udp"]
                ),
            }
        )

        self.cmd(
            "aks create "
            "--resource-group={resource_group} "
            "--name={name} "
            "--location={location} "
            "--ssh-key-value={ssh_key_value} "
            "--node-count=1 "
            "--node-vm-size={node_vm_size} ",
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        self.cmd(
            "aks nodepool add "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "--name={node_pool_name} "
            "--node-vm-size={node_vm_size} "
            "--node-count=1 "
            "--asg-ids={asg_ids} "
            "--allowed-host-ports={allowed_host_ports} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/NodePublicIPNSGControlPreview",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "networkProfile.applicationSecurityGroups",
                    self.kwargs["asg_ids"].split(","),
                ),
                self.check(
                    "networkProfile.allowedHostPorts[] | length(@)",
                    len(self.kwargs["allowed_host_ports"].split(",")),
                ),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_nodepool_update_with_nsg_control(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("n", 6)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
                "node_pool_name": nodepool_name,
                "node_vm_size": "standard_d2s_v3",
                "asg1": "asg1",
                "asg2": "asg2",
            }
        )
        create_asg1 = (
            "network asg create --name {asg1} --resource-group {resource_group} -o json"
        )
        create_asg2 = (
            "network asg create --name {asg2} --resource-group {resource_group} -o json"
        )
        asg1 = self.cmd(
            create_asg1, checks=[self.check("provisioningState", "Succeeded")]
        ).get_output_in_json()
        asg2 = self.cmd(
            create_asg2, checks=[self.check("provisioningState", "Succeeded")]
        ).get_output_in_json()

        self.kwargs.update(
            {
                "asg_ids": ",".join([asg1["id"], asg2["id"]]),
                "allowed_host_ports": ",".join(
                    ["53/udp", "80/tcp", "443/tcp", "4000-5000/tcp", "4000-6000/udp"]
                ),
            }
        )

        self.cmd(
            "aks create "
            "--resource-group={resource_group} "
            "--name={name} "
            "--location={location} "
            "--ssh-key-value={ssh_key_value} "
            "--nodepool-name={node_pool_name} "
            "--node-count=1 "
            "--node-vm-size={node_vm_size} ",
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        self.cmd(
            "aks nodepool update "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "--name={node_pool_name} "
            "--asg-ids={asg_ids} "
            "--allowed-host-ports={allowed_host_ports} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/NodePublicIPNSGControlPreview",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "networkProfile.applicationSecurityGroups",
                    self.kwargs["asg_ids"].split(","),
                ),
                self.check(
                    "networkProfile.allowedHostPorts[] | length(@)",
                    len(self.kwargs["allowed_host_ports"].split(",")),
                ),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    # the availability of features is controlled by a toggle and cannot be fully tested yet,
    # however, existing test results show that the client side works as expected, so exclude it at this moment
    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_nodepool_update_with_artifact_streaming(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("n", 6)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
                "node_pool_name": nodepool_name,
                "node_vm_size": "standard_d2s_v3",
            }
        )

        self.cmd(
            "aks create "
            "--resource-group={resource_group} "
            "--name={name} "
            "--location={location} "
            "--ssh-key-value={ssh_key_value} "
            "--nodepool-name={node_pool_name} "
            "--node-count=1 "
            "--node-vm-size={node_vm_size} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/ArtifactStreamingPreview",
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        self.cmd(
            "aks nodepool update "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "--name={node_pool_name} "
            "--enable-artifact-streaming "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/ArtifactStreamingPreview",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "agentPoolProfiles[1].ArtifactStreamingProfile.enabled", True
                ),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_and_update_ssh_public_key(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "-c 1 --ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        TEST_SSH_KEY_PUB = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCYpZoWGqsIbCKOvcrtPi5PpgoaP24pKJ8yk80qBYbqIjyVngCfM8rbgQCZKx4D8emmN7UxjiSt+c4WtV1aUfbT7VA5r4neuhPVgkqgp7CmkKdf0beV/0i5K28J7RojDTktllY9EYRYK6A4olLplaHJiuqbsMYa8amv43ol6IxgM3eE2BiEYm0/uvNKDmZ8AN4w07fFKjz1+wfdkluxC73qhijMY6FCgw+xEvvS1kd2Se6L/M/qV+VVnxW+S/bBT4Yew2dR6KWnauJvxXzdM8WQHyJy52jQ1n5PHxVRMgjRLhWvbcNNgPseFpULxe3a4ATS8kKO2Z9pzpSOgEpW7LVz"  # pylint: disable=line-too-long
        _, pathname = tempfile.mkstemp()
        with open(pathname, "w") as key_file:
            key_file.write(TEST_SSH_KEY_PUB)
        self.kwargs.update({"ssh_key_value": pathname.replace("\\", "\\\\")})

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("linuxProfile.ssh.publicKeys[0].keyData", TEST_SSH_KEY_PUB),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_no_ssh_key_and_update_ssh_public_key(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "-c 1 --no-ssh-key -o json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        TEST_SSH_KEY_PUB = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCYpZoWGqsIbCKOvcrtPi5PpgoaP24pKJ8yk80qBYbqIjyVngCfM8rbgQCZKx4D8emmN7UxjiSt+c4WtV1aUfbT7VA5r4neuhPVgkqgp7CmkKdf0beV/0i5K28J7RojDTktllY9EYRYK6A4olLplaHJiuqbsMYa8amv43ol6IxgM3eE2BiEYm0/uvNKDmZ8AN4w07fFKjz1+wfdkluxC73qhijMY6FCgw+xEvvS1kd2Se6L/M/qV+VVnxW+S/bBT4Yew2dR6KWnauJvxXzdM8WQHyJy52jQ1n5PHxVRMgjRLhWvbcNNgPseFpULxe3a4ATS8kKO2Z9pzpSOgEpW7LVz"  # pylint: disable=line-too-long
        _, pathname = tempfile.mkstemp()
        with open(pathname, "w") as key_file:
            key_file.write(TEST_SSH_KEY_PUB)
        self.kwargs.update({"ssh_key_value": pathname.replace("\\", "\\\\")})

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--ssh-key-value={ssh_key_value} -o json"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("linuxProfile.adminUsername", "azureuser"),
                self.check("linuxProfile.ssh.publicKeys[0].keyData", TEST_SSH_KEY_PUB),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus2euap"
    )
    def test_node_public_ip_tags(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("n", 6)
        nodepool_name_1 = self.create_random_name("n", 6)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
                "node_pool_name": nodepool_name,
                "node_vm_size": "standard_d2a_v4",
                "node_public_ip_tags": "RoutingPreference=Internet",
            }
        )

        self.cmd(
            "aks create "
            "--resource-group={resource_group} "
            "--name={name} "
            "--location={location} "
            "--ssh-key-value={ssh_key_value} "
            "--nodepool-name={node_pool_name} "
            "--node-count=1 "
            "--node-vm-size={node_vm_size} "
            "--enable-node-public-ip "
            "--node-public-ip-tags={node_public_ip_tags} "
            "--aks-custom-headers=AKSHTTPCustomFeatures=Microsoft.ContainerService/NodePublicIPTagsPreview",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "agentPoolProfiles[0].networkProfile.nodePublicIpTags[0].ipTagType",
                    "RoutingPreference",
                ),
                self.check(
                    "agentPoolProfiles[0].networkProfile.nodePublicIpTags[0].tag",
                    "Internet",
                ),
            ],
        )

        self.kwargs.update(
            {
                "node_pool_name": nodepool_name_1,
            }
        )

        self.cmd(
            "aks nodepool add "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "--name={node_pool_name} "
            "--node-vm-size={node_vm_size} "
            "--enable-node-public-ip "
            "--node-public-ip-tags={node_public_ip_tags} "
            "--aks-custom-headers=AKSHTTPCustomFeatures=Microsoft.ContainerService/NodePublicIPTagsPreview",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "networkProfile.nodePublicIpTags[0].ipTagType", "RoutingPreference"
                ),
                self.check("networkProfile.nodePublicIpTags[0].tag", "Internet"),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_vms_agentpool_type(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool_name = self.create_random_name("n", 6)
        nodepool_name_1 = self.create_random_name("n", 6)
        # At 2024.01.18, the two return values are 1.27.x and 1.28.x
        # setting vm type to VirtualMachines requires 1.28.x or higher
        _, k8s_version = self._get_versions(resource_group_location)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
                "node_pool_name": nodepool_name,
                "node_vm_size": "standard_d2a_v4",
                "k8s_version": k8s_version,
            }
        )

        self.cmd(
            "aks create "
            "--resource-group={resource_group} "
            "--name={name} "
            "--location={location} "
            "--ssh-key-value={ssh_key_value} "
            "--nodepool-name={node_pool_name} "
            "--node-count=1 "
            "--node-vm-size={node_vm_size} "
            '--vm-set-type="VirtualMachines" '
            "-k {k8s_version} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/VMsAgentPoolPreview",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("agentPoolProfiles[0].type", "VirtualMachines"),
            ],
        )

        self.kwargs.update(
            {
                "node_pool_name": nodepool_name_1,
            }
        )

        self.cmd(
            "aks nodepool add "
            "--resource-group={resource_group} "
            "--cluster-name={name} "
            "--name={node_pool_name} "
            "--node-vm-size={node_vm_size} "
            "--vm-set-type=VirtualMachines "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/VMsAgentPoolPreview",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("typePropertiesType", "VirtualMachines"),
            ],
        )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    def test_get_trustedaccess_roles(self):
        versions_cmd = "aks trustedaccess role list -l eastus -o json"
        roles = self.cmd(versions_cmd).get_output_in_json()
        assert len(roles) > 0
        role = roles[0]
        assert len(role["rules"]) > 0

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_create_with_trustedaccess_rolebinding(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)

        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'location': resource_group_location,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters',
            'vm_size': 'Standard_D4s_v3',
            'node_count': 1,
            'ssh_key_value': self.generate_ssh_keys(),
        })

        create_cmd = ' '.join([
            'aks', 'create', '--resource-group={resource_group}', '--name={name}', '--location={location}',
            '--node-vm-size {vm_size}',
            '--node-count {node_count}',
            '--ssh-key-value={ssh_key_value}'
        ])

        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
        ])

        list_binding_cmd = 'aks trustedaccess rolebinding list ' \
            '--cluster-name={name} ' \
            '--resource-group={resource_group}'
        self.cmd(list_binding_cmd, checks=[
            self.is_empty(),
        ])

        subscription_id = self.get_subscription_id()
        sid = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/fake_workspace'.format(subscription_id, resource_group)
        self.kwargs.update({
            'sid': sid
        })
        create_binding_cmd = 'aks trustedaccess rolebinding create ' \
            '--resource-group={resource_group} ' \
            '--cluster-name={name} ' \
            '-n testbinding ' \
            '--source-resource-id {sid} ' \
            '--roles Microsoft.MachineLearningServices/workspaces/mlworkload'
        self.cmd(create_binding_cmd)
        self.cmd(list_binding_cmd, checks=[
            self.check('[0].type', 'Microsoft.ContainerService/managedClusters/trustedAccessRoleBindings'),
            self.check('[0].name', 'testbinding'),
        ])

        get_binding_cmd = 'aks trustedaccess rolebinding show ' \
            '-n testbinding ' \
            '--resource-group={resource_group} ' \
            '--cluster-name={name}'
        self.cmd(get_binding_cmd, checks=[
            self.check('type', 'Microsoft.ContainerService/managedClusters/trustedAccessRoleBindings'),
            self.check('name', 'testbinding'),
            self.check('provisioningState', 'Succeeded'),
        ])

        update_binding_cmd = 'aks trustedaccess rolebinding update ' \
            '--cluster-name={name} ' \
            '-n testbinding ' \
            '--resource-group={resource_group} ' \
            '--roles Microsoft.MachineLearningServices/workspaces/mlworkload'
        self.cmd(update_binding_cmd, checks=[
            self.check('roles[0]', 'Microsoft.MachineLearningServices/workspaces/mlworkload'),
        ])

        delete_binding_cmd = 'aks trustedaccess rolebinding delete ' \
            '--cluster-name={name} ' \
            '-n testbinding ' \
            '--resource-group={resource_group} -y'
        self.cmd(delete_binding_cmd)
        self.cmd(list_binding_cmd, checks=[
            self.is_empty(),
        ])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_again_should_fail(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--location={location} --ssh-key-value={ssh_key_value} --output=json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # create again should fail
        create_again_cmd = (
            "aks create --resource-group={resource_group} --name={name} "
            "--location={location} --ssh-key-value={ssh_key_value} --output=json"
        )
        try:
            self.cmd(
                create_again_cmd,
                checks=[
                    self.check("provisioningState", "Succeeded"),
                ],
            )
        except ClientRequestError as ex:
            if "already exists" not in str(ex):
                raise AssertionError(
                    "Actual error '{}' does not contain '{}'".format(
                        ex, "already exists"
                    )
                )

        # delete
        cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_azure_service_mesh_enable_disable(
        self, resource_group, resource_group_location
    ):
        """This test case exercises enabling and disabling service mesh profile.

        It creates a cluster without azure service mesh profile.  Then enable it by
        running `aks mesh enable` followed by disabling by running `aks mesh disable`.
        """

        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
                "revision": self._get_asm_supported_revision(resource_group_location),
            }
        )

        # create cluster without --enable-azure-service-mesh
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--aks-custom-headers=AKSHTTPCustomFeatures=Microsoft.ContainerService/AzureServiceMeshPreview "
            "--ssh-key-value={ssh_key_value} --output=json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # enable azure service mesh again
        update_cmd = "aks mesh enable --resource-group={resource_group} --name={name} --revision={revision}"
        self.cmd(
            update_cmd,
            checks=[
                self.check("serviceMeshProfile.mode", "Istio"),
            ],
        )

        # disable azure service mesh
        update_cmd = (
            "aks mesh disable --resource-group={resource_group} --name={name} --yes"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("serviceMeshProfile.mode", "Disabled"),
            ],
        )

        # delete the cluster
        delete_cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            delete_cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_azure_service_mesh_with_ingress_gateway(
        self, resource_group, resource_group_location
    ):
        """This test case exercises enabling and disabling an ingress gateway.

        It creates a cluster with azure service mesh profile. After that, we enable an ingress
        gateway, then disable it.
        """

        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
                "revision": self._get_asm_supported_revision(resource_group_location),
            }
        )

        # create cluster with --enable-azure-service-mesh
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--aks-custom-headers=AKSHTTPCustomFeatures=Microsoft.ContainerService/AzureServiceMeshPreview "
            "--ssh-key-value={ssh_key_value} "
            "--enable-azure-service-mesh --revision={revision} --output=json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("serviceMeshProfile.mode", "Istio"),
            ],
        )

        # enable ingress gateway
        update_cmd = (
            "aks mesh enable-ingress-gateway --resource-group={resource_group} --name={name} "
            "--ingress-gateway-type Internal"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("serviceMeshProfile.mode", "Istio"),
                self.check(
                    "serviceMeshProfile.istio.components.ingressGateways[0].mode",
                    "Internal",
                ),
                self.check(
                    "serviceMeshProfile.istio.components.ingressGateways[0].enabled",
                    True,
                ),
            ],
        )

        # disable ingress gateway
        update_cmd = (
            "aks mesh disable-ingress-gateway --resource-group={resource_group} --name={name} "
            "--ingress-gateway-type Internal --yes"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("serviceMeshProfile.mode", "Istio"),
                self.check(
                    "serviceMeshProfile.istio.components.ingressGateways[0].mode",
                    "Internal",
                ),
                self.check(
                    "serviceMeshProfile.istio.components.ingressGateways[0].enabled",
                    None,
                ),
            ],
        )

        # delete the cluster
        delete_cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            delete_cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_azure_service_mesh_with_egress_gateway(
        self, resource_group, resource_group_location
    ):
        """This test case exercises enabling and disabling an egress gateway.

        It creates a cluster with azure service mesh profile. After that, we enable an egress
        gateway, then disable it.
        """

        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
                "revision": self._get_asm_supported_revision(resource_group_location)
            }
        )

        # create cluster with --enable-azure-service-mesh
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--aks-custom-headers=AKSHTTPCustomFeatures=Microsoft.ContainerService/AzureServiceMeshPreview "
            "--ssh-key-value={ssh_key_value} "
            "--enable-azure-service-mesh --revision={revision} --output=json"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("serviceMeshProfile.mode", "Istio"),
            ],
        )

        # enable egress gateway
        update_cmd = (
            "aks mesh enable-egress-gateway --resource-group={resource_group} --name={name}"
        )
        try:
            self.cmd(
                update_cmd,
                checks=[
                    self.check("serviceMeshProfile.mode", "Istio"),
                    self.check(
                        "serviceMeshProfile.istio.components.egressGateways[0].enabled",
                        True,
                    ),
                ],
            )
        except HttpResponseError as e:
            # fails because egress gateway has been disabled
            self.assertTrue(e.status_code == 400)

        # disable egress gateway
        try:
            update_cmd = "aks mesh disable-egress-gateway --resource-group={resource_group} --name={name} --yes"
            self.cmd(
                update_cmd,
                checks=[
                    self.check("serviceMeshProfile.mode", "Istio"),
                    self.check(
                        "serviceMeshProfile.istio.components.egressGateways[0].enabled",
                        None,
                    ),
                ],
            )
        except HttpResponseError as e:
            # fails because egress gateway has been disabled
            self.assertTrue(e.status_code == 400)

        # delete the cluster
        delete_cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            delete_cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_azure_service_mesh_with_pluginca(
        self, resource_group, resource_group_location
    ):
        """This test case exercises providing plugin ca params with mesh enable command.

        It creates a cluster, enables azure service mesh with plugica params, then disable it.
        """

        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        akv_resource_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/foo/providers/Microsoft.KeyVault/vaults/foo"
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
                "akv_resource_id": akv_resource_id,
                "revision": self._get_asm_supported_revision(resource_group_location),
            }
        )

        # create cluster
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--aks-custom-headers=AKSHTTPCustomFeatures=Microsoft.ContainerService/AzureServiceMeshPreview "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        # enable azurekeyvaultsecretsprovider addon
        enable_cmd = "aks enable-addons --addons azure-keyvault-secrets-provider --resource-group={resource_group} --name={name} -o json"
        self.cmd(
            enable_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", True),
                self.check(
                    "addonProfiles.azureKeyvaultSecretsProvider.config.enableSecretRotation",
                    "false",
                ),
            ],
        )

        # enable azure service mesh with pluginca
        update_cmd = (
            "aks mesh enable --resource-group={resource_group} --name={name} "
            "--key-vault-id  {akv_resource_id} "
            "--ca-cert-object-name my-ca-cert "
            "--ca-key-object-name my-ca-key "
            "--cert-chain-object-name my-cert-chain "
            "--root-cert-object-name my-root-cert "
            "--revision {revision}"
        )

        self.cmd(
            update_cmd,
            checks=[
                self.check("serviceMeshProfile.mode", "Istio"),
                self.check(
                    "serviceMeshProfile.istio.certificateAuthority.plugin.keyVaultId",
                    akv_resource_id,
                ),
                self.check(
                    "serviceMeshProfile.istio.certificateAuthority.plugin.certObjectName",
                    "my-ca-cert",
                ),
                self.check(
                    "serviceMeshProfile.istio.certificateAuthority.plugin.keyObjectName",
                    "my-ca-key",
                ),
                self.check(
                    "serviceMeshProfile.istio.certificateAuthority.plugin.rootCertObjectName",
                    "my-root-cert",
                ),
                self.check(
                    "serviceMeshProfile.istio.certificateAuthority.plugin.certChainObjectName",
                    "my-cert-chain",
                ),
            ],
        )

        # delete the cluster
        delete_cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            delete_cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_azure_service_mesh_get_revisions(self):
        """This test case exercises getting all the available revisions for the location."""

        revisions_cmd = "aks mesh get-revisions -l westus2"
        revisions = self.cmd(revisions_cmd).get_output_in_json()
        assert len(revisions["meshRevisions"]) > 0

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_azure_service_mesh_get_upgrades(
        self, resource_group, resource_group_location
    ):
        """This test case exercises getting all the possible upgrades for azure service mesh enabled on the cluster.

        It creates a cluster, enables azure service mesh, then gets all the possible upgrades.
        """

        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
                "revision": self._get_asm_supported_revision(resource_group_location),
            }
        )

        # create cluster
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--aks-custom-headers=AKSHTTPCustomFeatures=Microsoft.ContainerService/AzureServiceMeshPreview "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        # enable azure service mesh
        enable_cmd = "aks mesh enable --resource-group={resource_group} --name={name} --revision={revision}"
        self.cmd(
            enable_cmd,
            checks=[
                self.check("serviceMeshProfile.mode", "Istio"),
            ],
        )

        upgrades_cmd = (
            "aks mesh get-upgrades --resource-group={resource_group} --name={name}"
        )
        upgrades = self.cmd(upgrades_cmd).get_output_in_json()
        assert "compatibleWith" in upgrades and len(upgrades["compatibleWith"]) > 0

        # delete the cluster
        delete_cmd = (
            "aks delete --resource-group={resource_group} --name={name} --yes --no-wait"
        )
        self.cmd(
            delete_cmd,
            checks=[
                self.is_empty(),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_standard_sku(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting

        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "location": resource_group_location,
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--ssh-key-value={ssh_key_value} --node-count=1 --tier standard"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check("sku.name", "Base"),
                self.check("sku.tier", "Standard"),
            ],
        )
        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_with_premium_sku(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        aks_name = self.create_random_name("cliakstest", 16)
        lst_version = self._get_lts_version(resource_group_location)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "location": resource_group_location,
                "k8s_version": lst_version,
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--ssh-key-value={ssh_key_value} --tier premium --k8s-support-plan AKSLongTermSupport -k {k8s_version}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check("sku.name", "Base"),
                self.check("sku.tier", "Premium"),
                self.check("supportPlan", "AKSLongTermSupport"),
            ],
        )
        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_update_with_premium_sku(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        lst_version = self._get_lts_version(resource_group_location)
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "location": resource_group_location,
                "k8s_version": lst_version,
            }
        )

        # create a free tier
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--ssh-key-value={ssh_key_value} --node-count=1 --tier free -k {k8s_version}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check("sku.name", "Base"),
                self.check("sku.tier", "Free"),
            ],
        )

        # update to premium tier
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--tier premium --k8s-support-plan AKSLongTermSupport --auto-upgrade-channel patch"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check("sku.name", "Base"),
                self.check("sku.tier", "Premium"),
                self.check("supportPlan", "AKSLongTermSupport"),
            ],
        )

        # update to standard tier
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--tier standard --k8s-support-plan KubernetesOfficial"
        )
        self.cmd(
            update_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check("sku.name", "Base"),
                self.check("sku.tier", "Standard"),
                self.check("supportPlan", "KubernetesOfficial"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_update_upgrade_settings(self, resource_group, resource_group_location):
        """This test case exercises enabling and disabling forceUpgrade override in cluster upgradeSettings."""

        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--enable-managed-identity "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.not_exists("upgradeSettings"),
            ],
        )

        # update upgrade settings
        self.cmd(
            "aks update --resource-group={resource_group} --name={name} --upgrade-override-until 2020-01-01T22:30:17+00:00",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.not_exists("upgradeSettings.overrideSettings.forceUpgrade"),
                self.exists("upgradeSettings.overrideSettings.until"),
            ],
        )
        self.cmd(
            "aks update --resource-group={resource_group} --name={name} --enable-force-upgrade",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("upgradeSettings.overrideSettings.forceUpgrade", True),
                self.exists("upgradeSettings.overrideSettings.until"),
            ],
        )
        self.cmd(
            "aks update --resource-group={resource_group} --name={name} --enable-force-upgrade --upgrade-override-until 2020-02-22T22:30:17+00:00",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("upgradeSettings.overrideSettings.forceUpgrade", True),
                self.check(
                    "upgradeSettings.overrideSettings.until",
                    "2020-02-22T22:30:17+00:00",
                ),
            ],
        )
        self.cmd(
            "aks update --resource-group={resource_group} --name={name} --disable-force-upgrade",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("upgradeSettings.overrideSettings.forceUpgrade", False),
                self.check(
                    "upgradeSettings.overrideSettings.until",
                    "2020-02-22T22:30:17+00:00",
                ),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_update_enable_network_observability(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "location": resource_group_location,
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--ssh-key-value={ssh_key_value} --node-count=1 --tier standard "
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        # update to enable network observability
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} --enable-network-observability "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/NetworkObservabilityPreview "
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.monitoring.enabled", True),
            ],
        )

        # update to disable network observability
        update_cmd_two = (
            "aks update --resource-group={resource_group} --name={name} --disable-network-observability "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/NetworkObservabilityPreview "
        )
        self.cmd(
            update_cmd_two,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.monitoring.enabled", False),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_create_with_enable_network_observability(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting

        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "location": resource_group_location,
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--ssh-key-value={ssh_key_value} --node-count=1 --tier standard --enable-network-observability "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/NetworkObservabilityPreview"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.monitoring.enabled", True),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="westcentralus",
        preserve_default_location=True,
    )
    def test_aks_create_with_enable_cost_analysis(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting

        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "location": resource_group_location,
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--ssh-key-value={ssh_key_value} --node-count=1 --tier standard --enable-cost-analysis "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/ClusterCostAnalysis"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("metricsProfile.costAnalysis.enabled", True),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="westcentralus",
        preserve_default_location=True,
    )
    def test_aks_update_enable_cost_analysis(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting

        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "location": resource_group_location,
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--ssh-key-value={ssh_key_value} --node-count=1 --tier standard "
        )
        self.cmd(create_cmd, checks=[self.check("provisioningState", "Succeeded")])

        # update to enable
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} --enable-cost-analysis "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/ClusterCostAnalysis "
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("metricsProfile.costAnalysis.enabled", True),
            ],
        )

        # update to disable
        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} --disable-cost-analysis "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/ClusterCostAnalysis "
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("metricsProfile.costAnalysis.enabled", False),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="westcentralus",
        preserve_default_location=True,
    )
    def test_aks_create_node_provisioning_mode_manual(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting

        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "location": resource_group_location,
            }
        )

        # create
        # TODO: Use mode Auto instead?
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--ssh-key-value={ssh_key_value} --node-count=1 --enable-managed-identity --node-provisioning-mode=Manual"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("nodeProvisioningProfile.mode", "Manual"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="westcentralus",
        preserve_default_location=True,
    )
    def test_aks_update_node_provisioning_mode_manual(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting

        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "location": resource_group_location,
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--ssh-key-value={ssh_key_value} --node-count=1 --enable-managed-identity"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # update
        update_cmd = "aks update --resource-group={resource_group} --name={name} --node-provisioning-mode=Manual"
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("nodeProvisioningProfile.mode", "Manual"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_create_with_custom_headers(
        self, resource_group, resource_group_location
    ):
        aks_name = self.create_random_name("cliakstest", 16)
        _, create_version = self._get_versions(resource_group_location)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
                "k8s_version": create_version,
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} -k {k8s_version} -c 1 "
            "--ssh-key-value={ssh_key_value} "
            "--aks-custom-headers x-ms-correlation-request-id=12345678-90ab-cdef-1234-567890abcdef"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # scale cluster
        scale_cluster_cmd = (
            "aks scale --resource-group={resource_group} --name={name} "
            "-c 2 --aks-custom-headers x-ms-correlation-request-id=12345678-90ab-cdef-1234-567890abcdef"
        )
        self.cmd(
            scale_cluster_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # scale nodepool
        scale_nodepool_cmd = (
            "aks nodepool scale --resource-group={resource_group} --cluster-name={name} --name=nodepool1 "
            "-c 1 --aks-custom-headers x-ms-correlation-request-id=12345678-90ab-cdef-1234-567890abcdef"
        )
        self.cmd(
            scale_nodepool_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # show
        show_cmd = (
            "aks show --resource-group={resource_group} --name={name} "
            "--aks-custom-headers x-ms-correlation-request-id=12345678-90ab-cdef-1234-567890abcdef"
        )
        self.cmd(
            show_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="eastus"
    )
    def test_aks_create_with_app_routing_enabled(
        self, resource_group, resource_group_location
    ):
        """This test case exercises creating an AKS cluster with app routing addon enabled."""

        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0

        # create cluster with app routing addon enabled
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "aks_name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_cmd = (
            "aks create --resource-group={resource_group} --name={aks_name} --location={location} "
            "--ssh-key-value={ssh_key_value} --enable-app-routing "
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("ingressProfile.webAppRouting.enabled", True),
            ],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_approuting_enable_disable(
        self, resource_group, resource_group_location
    ):
        """This test case exercises enabling and disabling app routing addon in an AKS cluster."""

        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0

        # create cluster without app routing
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "aks_name": aks_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )
        create_cmd = (
            "aks create --resource-group={resource_group} --name={aks_name} --location={location} "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # enable app routing
        enable_app_routing_cmd = (
            "aks approuting enable --resource-group={resource_group} --name={aks_name}"
        )
        self.cmd(
            enable_app_routing_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("ingressProfile.webAppRouting.enabled", True),
            ],
        )

        # disable app routing
        disable_app_routing_cmd = "aks approuting disable --resource-group={resource_group} --name={aks_name} --yes"
        self.cmd(
            disable_app_routing_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("ingressProfile.webAppRouting.enabled", False),
            ],
        )

        # delete cluster
        delete_cmd = "aks delete --resource-group={resource_group} --name={aks_name} --yes --no-wait"
        self.cmd(delete_cmd, checks=[self.is_empty()])

    @AllowLargeResponse(8192)
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_approuting_enable_with_keyvault_secrets_provider_addon_and_keyvault_id(
        self, resource_group, resource_group_location
    ):
        """This test case exercises enabling app routing addon in an AKS cluster along with keyvault secrets provider addon."""

        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0

        # create cluster
        aks_name = self.create_random_name("cliakstest", 16)
        kv_name = self.create_random_name("cliakstestkv", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "aks_name": aks_name,
                "kv_name": kv_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create keyvault with rbac auth enabled
        create_keyvault_cmd = "keyvault create --resource-group={resource_group} --location={location} --name={kv_name} --enable-rbac-authorization=true"
        keyvault = self.cmd(
            create_keyvault_cmd,
            checks=[
                self.check("properties.provisioningState", "Succeeded"),
                self.check("properties.enableRbacAuthorization", True),
                self.check("name", kv_name),
            ],
        ).get_output_in_json()
        keyvault_id = keyvault["id"]
        self.kwargs.update({"keyvault_id": keyvault_id})

        create_cmd = (
            "aks create --resource-group={resource_group} --name={aks_name} --location={location} "
            "--ssh-key-value={ssh_key_value} "
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # enable app routing with keyvault secrets provider addon enabled
        enable_app_routing_cmd = "aks approuting enable --enable-kv --attach-kv {keyvault_id} --resource-group={resource_group} --name={aks_name}"
        self.cmd(
            enable_app_routing_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("ingressProfile.webAppRouting.enabled", True),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", True),
            ],
        )

        # delete cluster
        delete_cmd = "aks delete --resource-group={resource_group} --name={aks_name} --yes --no-wait"
        self.cmd(delete_cmd, checks=[self.is_empty()])

    @live_only()
    @AllowLargeResponse(8192)
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_approuting_update(self, resource_group, resource_group_location):
        """This test case exercises updating app routing addon in an AKS cluster."""

        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0

        aks_name = self.create_random_name("cliakstest", 16)
        kv_name = self.create_random_name("cliakstestkv", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "aks_name": aks_name,
                "kv_name": kv_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create keyvault with rbac auth enabled
        create_keyvault_cmd = "keyvault create --resource-group={resource_group} --location={location} --name={kv_name} --enable-rbac-authorization=true"
        keyvault = self.cmd(
            create_keyvault_cmd,
            checks=[
                self.check("properties.provisioningState", "Succeeded"),
                self.check("properties.enableRbacAuthorization", True),
                self.check("name", kv_name),
            ],
        ).get_output_in_json()
        keyvault_id = keyvault["id"]

        self.kwargs.update({"keyvault_id": keyvault_id})

        # create cluster with app routing enabled
        create_cmd = (
            "aks create --resource-group={resource_group} --name={aks_name} --location={location} "
            "--ssh-key-value={ssh_key_value} --enable-app-routing"
        )
        result = self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("ingressProfile.webAppRouting.enabled", True),
            ],
        ).get_output_in_json()
        object_id = result["ingressProfile"]["webAppRouting"]["identity"]["objectId"]
        self.kwargs.update({"object_id": object_id})

        # update with enable_rbac_authorization flag in keyvault set to true
        update_cmd = (
            "aks approuting update --resource-group={resource_group} --name={aks_name} --enable-kv "
            "--attach-kv {keyvault_id}"
        )

        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("ingressProfile.webAppRouting.enabled", True),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", True),
            ],
        )

        # update keyvault with rbac auth disabled
        update_keyvault_cmd = "keyvault update --resource-group={resource_group} --name={kv_name} --enable-rbac-authorization=false"
        self.cmd(
            update_keyvault_cmd,
            checks=[
                self.check("properties.provisioningState", "Succeeded"),
                self.check("properties.enableRbacAuthorization", False),
                self.check("name", kv_name),
            ],
        )

        # update with enable_rbac_authorization flag in keyvault set to false
        update_cmd = (
            "aks approuting update --resource-group={resource_group} --name={aks_name} "
            "--attach-kv {keyvault_id}"
        )

        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("ingressProfile.webAppRouting.enabled", True),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", True),
            ],
        )

        check_access_policy_cmd = "az keyvault show --resource-group={resource_group} --name={kv_name} --query \"properties.accessPolicies[?objectId=='{object_id}']\" -o json"
        self.cmd(
            check_access_policy_cmd,
            checks=[
                self.check("length(@)", 1),
                self.check("[0].objectId", "{object_id}"),
                self.check("[0].permissions.certificates", ["Get"]),
                self.check("[0].permissions.keys", None),
                self.check("[0].permissions.secrets", ["Get"]),
                self.check("[0].permissions.storage", None),
            ],
        )

        # delete cluster
        delete_cmd = "aks delete --resource-group={resource_group} --name={aks_name} --yes --no-wait"
        self.cmd(delete_cmd, checks=[self.is_empty()])

    @live_only()
    @AllowLargeResponse(8192)
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_approuting_update_with_monitoring_addon_enabled(self, resource_group, resource_group_location):
        """This test case exercises updating app routing addon in an AKS cluster with monitoring addon enabled."""

        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0

        aks_name = self.create_random_name("cliakstest", 16)
        kv_name = self.create_random_name("cliakstestkv", 16)

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "aks_name": aks_name,
                "kv_name": kv_name,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create keyvault with rbac auth enabled
        create_keyvault_cmd = "keyvault create --resource-group={resource_group} --location={location} --name={kv_name} --enable-rbac-authorization=true"
        keyvault = self.cmd(
            create_keyvault_cmd,
            checks=[
                self.check("properties.provisioningState", "Succeeded"),
                self.check("properties.enableRbacAuthorization", True),
                self.check("name", kv_name),
            ],
        ).get_output_in_json()
        keyvault_id = keyvault["id"]

        self.kwargs.update({"keyvault_id": keyvault_id})

        # create cluster with app routing and monitoring addon enabled
        create_cmd = (
            "aks create --resource-group={resource_group} --name={aks_name} --location={location} "
            "--ssh-key-value={ssh_key_value} --enable-app-routing --enable-addons monitoring"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("addonProfiles.omsagent.enabled", True),
                self.check("ingressProfile.webAppRouting.enabled", True),
            ],
        ).get_output_in_json()

        # update with enable_rbac_authroization flag in keyvault set to true
        update_cmd = (
            "aks approuting update --resource-group={resource_group} --name={aks_name} --enable-kv "
            "--attach-kv {keyvault_id}"
        )

        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("ingressProfile.webAppRouting.enabled", True),
                self.check("addonProfiles.azureKeyvaultSecretsProvider.enabled", True),
            ],
        )

        # delete cluster
        delete_cmd = "aks delete --resource-group={resource_group} --name={aks_name} --yes --no-wait"
        self.cmd(delete_cmd, checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_approuting_zone_add_delete_list(
        self, resource_group, resource_group_location
    ):
        """This test case exercises adding, deleting and listing zones to app routing addon in an AKS cluster."""
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0

        aks_name = self.create_random_name("cliakstest", 16)
        dns_zone_1 = self.create_random_name("cliakstest", 16) + ".com"
        dns_zone_2 = self.create_random_name("cliakstest", 16) + ".com"

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "aks_name": aks_name,
                "dns_zone_1": dns_zone_1,
                "dns_zone_2": dns_zone_2,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_dns_zone_cmd_1 = "network dns zone create --resource-group={resource_group} --name {dns_zone_1}"
        dns_zone_result = self.cmd(
            create_dns_zone_cmd_1,
            checks=[
                self.check("name", dns_zone_1),
            ],
        ).get_output_in_json()
        dns_zone_id_1 = dns_zone_result["id"]

        create_dns_zone_cmd_2 = "network dns zone create --resource-group={resource_group} --name {dns_zone_2}"
        dns_zone_result = self.cmd(
            create_dns_zone_cmd_2,
            checks=[
                self.check("name", dns_zone_2),
            ],
        ).get_output_in_json()
        dns_zone_id_2 = dns_zone_result["id"]

        self.kwargs.update(
            {"dns_zone_id_1": dns_zone_id_1, "dns_zone_id_2": dns_zone_id_2}
        )

        # create cluster with app routing enabled
        create_cmd = (
            "aks create --resource-group={resource_group} --name={aks_name} --location={location} "
            "--ssh-key-value={ssh_key_value} --enable-app-routing"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("ingressProfile.webAppRouting.enabled", True),
                self.check("ingressProfile.webAppRouting.dnsZoneResourceIds", None),
            ],
        )

        # add dns zone
        add_dns_zone_cmd = "aks approuting zone add --resource-group={resource_group} --name={aks_name} --ids {dns_zone_id_1}"
        self.cmd(
            add_dns_zone_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "ingressProfile.webAppRouting.dnsZoneResourceIds[0]", dns_zone_id_1
                ),
            ],
        )

        # add dns zone with --atach-zones flag
        add_dns_zone_cmd = "aks approuting zone add --resource-group={resource_group} --name={aks_name} --ids {dns_zone_id_2} --attach-zones"
        self.cmd(
            add_dns_zone_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "ingressProfile.webAppRouting.dnsZoneResourceIds[0]", dns_zone_id_1
                ),
                self.check(
                    "ingressProfile.webAppRouting.dnsZoneResourceIds[1]", dns_zone_id_2
                ),
            ],
        )

        # list dns zone
        list_dns_zone_cmd = "aks approuting zone list --resource-group={resource_group} --name={aks_name}"
        self.cmd(
            list_dns_zone_cmd,
            checks=[
                self.check("length(@)", 2),
                self.check("[0].resource_group", resource_group),
                self.check("[0].type", "dnszones"),
                self.check("[0].name", dns_zone_1),
                self.check("[1].resource_group", resource_group),
                self.check("[1].type", "dnszones"),
                self.check("[1].name", dns_zone_2),
            ],
        )

        # delete dns zone
        delete_dns_zone_cmd = "aks approuting zone delete --resource-group={resource_group} --name={aks_name} --ids {dns_zone_id_1} --yes"
        self.cmd(
            delete_dns_zone_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "ingressProfile.webAppRouting.dnsZoneResourceIds[0]", dns_zone_id_2
                ),
            ],
        )

        # delete cluster
        delete_cmd = "aks delete --resource-group={resource_group} --name={aks_name} --yes --no-wait"
        self.cmd(delete_cmd, checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="eastus",
        preserve_default_location=True,
    )
    def test_aks_approuting_zone_update(self, resource_group, resource_group_location):
        """This test case exercises updating zones to app routing addon in an AKS cluster."""

        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0

        aks_name = self.create_random_name("cliakstest", 16)
        dns_zone_1 = self.create_random_name("cliakstest", 16) + ".com"
        dns_zone_2 = self.create_random_name("cliakstest", 16) + ".com"

        self.kwargs.update(
            {
                "resource_group": resource_group,
                "aks_name": aks_name,
                "dns_zone_1": dns_zone_1,
                "dns_zone_2": dns_zone_2,
                "location": resource_group_location,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        create_dns_zone_cmd_1 = "network dns zone create --resource-group={resource_group} --name {dns_zone_1}"
        dns_zone_1 = self.cmd(
            create_dns_zone_cmd_1,
            checks=[
                self.check("name", dns_zone_1),
            ],
        ).get_output_in_json()
        dns_zone_id_1 = dns_zone_1["id"]

        create_dns_zone_cmd_2 = "network dns zone create --resource-group={resource_group} --name {dns_zone_2}"
        dns_zone_2 = self.cmd(
            create_dns_zone_cmd_2,
            checks=[
                self.check("name", dns_zone_2),
            ],
        ).get_output_in_json()
        dns_zone_id_2 = dns_zone_2["id"]

        self.kwargs.update(
            {"dns_zone_id_1": dns_zone_id_1, "dns_zone_id_2": dns_zone_id_2}
        )

        # create cluster with app routing enabled
        create_cmd = (
            "aks create --resource-group={resource_group} --name={aks_name} --location={location} "
            "--ssh-key-value={ssh_key_value} --enable-app-routing"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("ingressProfile.webAppRouting.enabled", True),
                self.check("ingressProfile.webAppRouting.dnsZoneResourceIds", None),
            ],
        )

        # add dns zone
        add_dns_zone_cmd = "aks approuting zone add --resource-group={resource_group} --name={aks_name} --ids {dns_zone_id_1}"
        self.cmd(
            add_dns_zone_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "ingressProfile.webAppRouting.dnsZoneResourceIds[0]", dns_zone_id_1
                ),
            ],
        )

        # update dns zone
        update_dns_zone_cmd = "aks approuting zone update --resource-group={resource_group} --name={aks_name} --ids {dns_zone_id_2}"
        self.cmd(
            update_dns_zone_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "ingressProfile.webAppRouting.dnsZoneResourceIds[0]", dns_zone_id_2
                ),
            ],
        )

        # delete cluster
        delete_cmd = "aks delete --resource-group={resource_group} --name={aks_name} --yes --no-wait"
        self.cmd(delete_cmd, checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_update_agentpool_os_sku(self, resource_group, resource_group_location):
        aks_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} -c 1 "
            "--ssh-key-value={ssh_key_value}"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
            ],
        )

        # update nodepool
        update_nodepool_cmd = (
            "aks nodepool update --resource-group={resource_group} --cluster-name={name} "
            "--name=nodepool1 --os-sku AzureLinux "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/OSSKUMigrationPreview"
        )
        self.cmd(
            update_nodepool_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("osSku", "AzureLinux"),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest',
                                    location='westus2', preserve_default_location=True)
    def test_aks_create_with_enable_ai_toolchain_operator(self, resource_group,
                                                          resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting

        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys(),
            'location': resource_group_location,
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--ssh-key-value={ssh_key_value} --node-count=1 --enable-managed-identity ' \
                     '--enable-oidc-issuer --enable-ai-toolchain-operator ' \
                     '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AIToolchainOperatorPreview '
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aiToolchainOperatorProfile.enabled', True),
        ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest',
                                    location='westus2', preserve_default_location=True)
    def test_aks_update_with_enable_ai_toolchain_operator(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting

        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys(),
            'location': resource_group_location,
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--ssh-key-value={ssh_key_value} --node-count=1 --enable-managed-identity ' \
                     '--enable-oidc-issuer '
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # update to enable
        update_cmd = 'aks update --resource-group={resource_group} --name={name} --enable-ai-toolchain-operator ' \
                     '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AIToolchainOperatorPreview '
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aiToolchainOperatorProfile.enabled', True),
        ])

        # update to disable
        update_cmd = 'aks update --resource-group={resource_group} --name={name} --disable-ai-toolchain-operator ' \
                     '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AIToolchainOperatorPreview '

        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('aiToolchainOperatorProfile.enabled', False),
        ])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='westus2')
    def test_aks_disable_ssh(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'resource_group_location': resource_group_location,
            'ssh_key_value': self.generate_ssh_keys(),
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} -c 1 ' \
                     '--ssh-key-value={ssh_key_value} --location={resource_group_location} ' \
                     '--ssh-access disabled ' \
                     '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/DisableSSHPreview'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('agentPoolProfiles[0].securityProfile.sshAccess', 'Disabled'),
        ])

        # update nodepool
        update_nodepool_cmd = 'aks nodepool update --resource-group={resource_group} --cluster-name={name} ' \
                              '--name=nodepool1 --ssh-access localuser --yes ' \
                              '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/DisableSSHPreview'
        self.cmd(update_nodepool_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('securityProfile.sshAccess', 'LocalUser'),
        ])

        # create new nodepool
        add_nodepool_cmd = 'aks nodepool add -g {resource_group} --cluster-name {name} -n nodepool2 ' \
                           '--ssh-access localuser ' \
                           '--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/DisableSSHPreview'
        self.cmd(add_nodepool_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('securityProfile.sshAccess', 'LocalUser'),
        ])

        # update cluster
        update_cmd = 'aks update --resource-group={resource_group} --name={name} ' \
                     '--ssh-access disabled --yes ' \
                     '--aks-custom-header AKSHTTPCustomFeatures=Microsoft.ContainerService/DisableSSHPreview'
        self.cmd(update_cmd, checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('agentPoolProfiles[0].securityProfile.sshAccess', 'Disabled'),
            self.check('agentPoolProfiles[1].securityProfile.sshAccess', 'Disabled'),
        ])

        # delete
        self.cmd('aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="centraluseuap",
        preserve_default_location=True,
    )
    def test_aks_create_with_pod_ip_allocation_mode_static_block(
        self, resource_group, resource_group_location
    ):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        vnet_name = self.create_random_name("cliakstest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "aks_name": aks_name,
                "vnet_name": vnet_name,
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create virtual network
        create_vnet = (
            "network vnet create --resource-group={resource_group} --name={vnet_name} "
            "--address-prefix 10.0.0.0/8 -o json"
        )
        vnet = self.cmd(
            create_vnet, checks=[self.check("newVNet.provisioningState", "Succeeded")]
        ).get_output_in_json()
        vnet_id = vnet["newVNet"]["id"]
        assert vnet_id is not None

        # create node subnet
        create_node_subnet = (
            "network vnet subnet create -n nodeSubnet --resource-group={resource_group} --vnet-name {vnet_name} "
            "--address-prefixes 10.240.0.0/16"
        )
        show_node_subnet_cmd = "network vnet subnet show \
            --resource-group={resource_group} \
            --vnet-name={vnet_name} \
            --name nodeSubnet"
        self.cmd(create_node_subnet, checks=[self.check("provisioningState", "Succeeded")])
        node_subnet_output = self.cmd(show_node_subnet_cmd).get_output_in_json()
        node_subnet_id = node_subnet_output["id"]
        assert node_subnet_id is not None

        # create pod subnet
        create_pod_subnet = (
            "network vnet subnet create -n podSubnet --resource-group={resource_group} --vnet-name {vnet_name} "
            "--address-prefixes 10.40.0.0/13"
        )
        show_pod_subnet_cmd = "network vnet subnet show \
            --resource-group={resource_group} \
            --vnet-name={vnet_name} \
            --name podSubnet"
        self.cmd(create_pod_subnet, checks=[self.check("provisioningState", "Succeeded")])
        pod_subnet_output = self.cmd(show_pod_subnet_cmd).get_output_in_json()
        pod_subnet_id = pod_subnet_output["id"]
        assert pod_subnet_id is not None

        pod_ip_allocation_mode = "StaticBlock"
        self.kwargs.update(
            {
                "vnet_id": vnet_id,
                "node_subnet_id": node_subnet_id,
                "pod_subnet_id": pod_subnet_id,
                "pod_ip_allocation_mode": pod_ip_allocation_mode,
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={aks_name} --location={location} "
            "--network-plugin azure --ssh-key-value={ssh_key_value} --max-pods 80 "
            "--vnet-subnet-id {node_subnet_id} --pod-subnet-id {pod_subnet_id} --node-count 3 "
            "--pod-ip-allocation-mode={pod_ip_allocation_mode} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/AzureVnetScalePreview"
        )
        self.cmd(
            create_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("networkProfile.networkPlugin", "azure"),
                self.check("agentPoolProfiles[0].podSubnetId", pod_subnet_id),
                self.check("agentPoolProfiles[0].podIpAllocationMode", pod_ip_allocation_mode),
            ],
        )

        # delete
        self.cmd(
            "aks delete -g {resource_group} -n {aks_name} --yes --no-wait",
            checks=[self.is_empty()],
        )

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix='clitest',
                                    location='westus2', preserve_default_location=True)
    def test_aks_check_network(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting

        aks_name = self.create_random_name('cliakstest', 16)
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'ssh_key_value': self.generate_ssh_keys(),
            'location': resource_group_location,
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--ssh-key-value={ssh_key_value} --node-count=2 --os-sku Ubuntu'
        self.cmd(create_cmd, checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        # check network to a random node
        check_cmd = 'aks check-network outbound --resource-group={resource_group} --name={name}'
        self.cmd(check_cmd, checks=[self.is_empty()])

        # get node name
        managed_resource_group = 'MC_' + resource_group + '_' + aks_name + '_' + resource_group_location
        self.kwargs.update({"managed_resource_group": managed_resource_group})

        list_vmss_cmd = 'vmss list --resource-group={managed_resource_group}'
        vmss_list = self.cmd(list_vmss_cmd).get_output_in_json()

        assert len(vmss_list) == 1
        assert vmss_list[0]['provisioningState'] == 'Succeeded'

        vmss_name = vmss_list[0]['name']
        node_name = vmss_name + '000001'
        self.kwargs.update({"node_name": node_name})

        # check network to a specific node
        check_cmd = 'aks check-network outbound --resource-group={resource_group} --name={name} ' \
            '--node-name={node_name}'
        self.cmd(check_cmd, checks=[self.is_empty()])

        # delete
        self.cmd(
            'aks delete -g {resource_group} -n {name} --yes --no-wait', checks=[self.is_empty()])

    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17, name_prefix="clitest", location="westus2"
    )
    def test_aks_create_cluster_with_taints(self, resource_group, resource_group_location):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name("cliakstest", 16)
        nodepool1_name = "nodepool1"
        nodepool2_name = "nodepool2"
        tags = "key1=value1"
        new_tags = "key2=value2"
        nodepool_taints = (
            "taint1=value1:PreferNoSchedule,taint2=value2:PreferNoSchedule"
        )
        nodepool_init_taints = (
            "initTaint1=value1:PreferNoSchedule,initTaint2=value2:PreferNoSchedule"
        )
        nodepool_taints2 = "taint1=value2:PreferNoSchedule"
        nodepool_init_taints2 = "initTaint1=value2:PreferNoSchedule"
        self.kwargs.update(
            {
                "resource_group": resource_group,
                "name": aks_name,
                "dns_name_prefix": self.create_random_name("cliaksdns", 16),
                "ssh_key_value": self.generate_ssh_keys(),
                "location": resource_group_location,
                "resource_type": "Microsoft.ContainerService/ManagedClusters",
                "tags": tags,
                "new_tags": new_tags,
                "nodepool1_name": nodepool1_name,
                "nodepool2_name": nodepool2_name,
                "nodepool_taints": nodepool_taints,
                "nodepool_initialization_taints": nodepool_init_taints,
                "nodepool_taints2": nodepool_taints2,
                "nodepool_initialization_taints2": nodepool_init_taints2,
            }
        )

        # create
        create_cmd = (
            "aks create --resource-group={resource_group} --name={name} --location={location} "
            "--dns-name-prefix={dns_name_prefix} --node-count=1 "
            "--ssh-key-value={ssh_key_value} --nodepool-taints {nodepool_taints} "
            "--nodepool-initialization-taints {nodepool_initialization_taints} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/NodeInitializationTaintsPreview "
        )
        self.cmd(
            create_cmd,
            checks=[
                self.exists("fqdn"),
                self.exists("nodeResourceGroup"),
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "agentPoolProfiles[0].nodeTaints[0]",
                    "taint1=value1:PreferNoSchedule",
                ),
                self.check(
                    "agentPoolProfiles[0].nodeTaints[1]",
                    "taint2=value2:PreferNoSchedule",
                ),
                self.check(
                    "agentPoolProfiles[0].nodeInitializationTaints[0]",
                    "initTaint1=value1:PreferNoSchedule",
                ),
                self.check(
                    "agentPoolProfiles[0].nodeInitializationTaints[1]",
                    "initTaint2=value2:PreferNoSchedule",
                ),
            ],
        )


        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            "--nodepool-taints {nodepool_taints2} "
            "--nodepool-initialization-taints {nodepool_initialization_taints2} " 
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/NodeInitializationTaintsPreview "
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check(
                    "agentPoolProfiles[0].nodeTaints[0]",
                    "taint1=value2:PreferNoSchedule",
                ),
                self.check(
                    "agentPoolProfiles[0].nodeInitializationTaints[0]",
                    "initTaint1=value2:PreferNoSchedule",
                ),
            ],
        )

        update_cmd = (
            "aks update --resource-group={resource_group} --name={name} "
            '--nodepool-taints "" '
            '--nodepool-initialization-taints ""'
        )
        self.cmd(
            update_cmd,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("agentPoolProfiles[0].nodeTaints", None),
                self.check("agentPoolProfiles[0].nodeInitializationTaints", None),
            ],
        )

    # live only due to role assignment is not mocked
    @live_only()
    @AllowLargeResponse()
    @AKSCustomResourceGroupPreparer(
        random_name_length=17,
        name_prefix="clitest",
        location="westcentralus",
    )
    def test_aks_artifact_source(self, resource_group, resource_group_location):
        aks_name = self.create_random_name('cliakstest', 16)
        vnet_name = self.create_random_name("clitest", 16)
        aks_subnet_name = "aks-subnet"
        acr_subnet_name = "acr-subnet"
        cluster_identity_name = self.create_random_name("clitest", 16)
        kubelet_identity_name = self.create_random_name("clitest", 16)
        acr_name = self.create_random_name("clitest", 16)
        self.kwargs.update(
            {
                "resource_group": resource_group,
                'location': resource_group_location,
                "aks_name": aks_name,
                "vnet_name": vnet_name,
                "aks_subnet_name": aks_subnet_name,
                "acr_subnet_name": acr_subnet_name,
                "cluster_identity_name": cluster_identity_name,
                "kubelet_identity_name": kubelet_identity_name,
                "acr_name": acr_name,
                "ssh_key_value": self.generate_ssh_keys(),
            }
        )

        # create virtual network and subnets
        create_vnet = (
            "network vnet create --resource-group {resource_group} --name {vnet_name} "
            "--address-prefixes 192.168.0.0/16 "
            "--subnet-name {aks_subnet_name} "
            "--subnet-prefix 192.168.1.0/24 -o json"
        )
        vnet = self.cmd(
            create_vnet, checks=[self.check("newVNet.provisioningState", "Succeeded")]
        ).get_output_in_json()
        vnet_id = vnet["newVNet"]["id"]
        assert vnet_id is not None
        self.kwargs.update(
            {
                "vnet_id": vnet_id,
            }
        )
        create_acr_subnet = (
            "network vnet subnet create -n {acr_subnet_name} --resource-group {resource_group} --vnet-name {vnet_name} "
            "--address-prefixes 192.168.2.0/24 --private-endpoint-network-policies Disabled -o json"
        )
        self.cmd(create_acr_subnet, checks=[self.check("provisioningState", "Succeeded")])

        # create ACR
        create_acr_cmd = (
            "acr create --resource-group {resource_group} --name {acr_name} "
            "--sku Premium --public-network-enabled false -o json"
        )
        acr = self.cmd(
            create_acr_cmd, checks=[self.check("provisioningState", "Succeeded")]
        ).get_output_in_json()
        acr_id = acr["id"]
        assert acr_id is not None
        self.kwargs.update(
            {
                "acr_id": acr_id,
            }
        )

        # enable acr artifact cache
        enable_acr_artifact_cache_cmd = (
            "acr cache create -n aks-mcr -r {acr_name} "
            "--source-repo \"mcr.microsoft.com/*\" --target-repo \"aks-addon-mcr/*\" -o json"
        )
        self.cmd(enable_acr_artifact_cache_cmd, checks=[self.check("provisioningState", "Succeeded")])

        # create private endpoint
        create_private_endpoint_cmd = (
            "network private-endpoint create --resource-group {resource_group} --name myPrivateEndpoint "
            "--vnet-name {vnet_name} --subnet {acr_subnet_name} "
            "--private-connection-resource-id {acr_id} --group-id registry --connection-name myConnection -o json"
        )
        private_endpoint = self.cmd(
            create_private_endpoint_cmd, checks=[self.check("provisioningState", "Succeeded")]
        ).get_output_in_json()
        nic_id = private_endpoint["networkInterfaces"][0]["id"]
        assert nic_id is not None
        self.kwargs.update(
            {
                "nic_id": nic_id,
            }
        )
        get_acr_private_ip_cmd = (
            "network nic show --ids {nic_id} "
            "--query \"ipConfigurations[?privateLinkConnectionProperties.requiredMemberName=='registry'].privateIPAddress\" "
            "-o tsv"
        )
        acr_private_ip = self.cmd(get_acr_private_ip_cmd).output.strip()
        assert acr_private_ip is not None
        self.kwargs.update(
            {
                "acr_private_ip": acr_private_ip,
            }
        )
        get_acr_data_endpoint_private_ip_cmd = (
            "network nic show --ids {nic_id} "
            "--query \"ipConfigurations[?privateLinkConnectionProperties.requiredMemberName=='registry_data_{location}'].privateIPAddress\" "
            "-o tsv"
        )
        acr_data_endpoint_private_ip = self.cmd(get_acr_data_endpoint_private_ip_cmd).output.strip()
        assert acr_data_endpoint_private_ip is not None
        self.kwargs.update(
            {
                "acr_data_endpoint_private_ip": acr_data_endpoint_private_ip,
            }
        )

        # create private dns zone
        create_private_dns_zone_cmd = (
            "network private-dns zone create --resource-group {resource_group} "
            "--name privatelink.azurecr.io -o json"
        )
        private_dns_zone = self.cmd(
            create_private_dns_zone_cmd, checks=[self.check("provisioningState", "Succeeded")]
        ).get_output_in_json()
        create_private_dns_link_vnet_cmd = (
            "network private-dns link vnet create --resource-group {resource_group} "
            "--zone-name privatelink.azurecr.io "
            "--name MyDNSLink --virtual-network {vnet_name} --registration-enabled false -o json"
        )
        self.cmd(create_private_dns_link_vnet_cmd, checks=[self.check("provisioningState", "Succeeded")])

        # create record for ACR
        create_record_set_cmd = (
            "network private-dns record-set a create --resource-group {resource_group} --zone-name privatelink.azurecr.io "
            "--name {acr_name} -o json"
        )
        self.cmd(create_record_set_cmd)
        create_dns_record_cmd = (
            "network private-dns record-set a add-record --resource-group {resource_group} --zone-name privatelink.azurecr.io "
            "--record-set-name {acr_name} --ipv4-address {acr_private_ip} -o json"
        )
        self.cmd(create_dns_record_cmd)

        # create record for ACR data endpoint
        create_record_set_cmd = (
            "network private-dns record-set a create --resource-group {resource_group} --zone-name privatelink.azurecr.io "
            "--name {acr_name}.{location}.data -o json"
        )
        self.cmd(create_record_set_cmd)
        create_dns_record_cmd = (
            "network private-dns record-set a add-record --resource-group {resource_group} --zone-name privatelink.azurecr.io "
            "--record-set-name {acr_name}.{location}.data --ipv4-address {acr_data_endpoint_private_ip} -o json"
        )
        self.cmd(create_dns_record_cmd)

        # create identity
        create_cluster_idenity_cmd = (
            "identity create --name {cluster_identity_name} --resource-group {resource_group} -o json"
        )
        cluster_idenity = self.cmd(create_cluster_idenity_cmd).get_output_in_json()
        cluster_identity_id = cluster_idenity["id"]
        assert cluster_identity_id is not None
        self.kwargs.update(
            {
                "cluster_identity_id": cluster_identity_id,
            }
        )
        create_kubelet_idenity_cmd = (
            "identity create --name {kubelet_identity_name} --resource-group {resource_group} -o json"
        )
        kubelet_identity = self.cmd(create_kubelet_idenity_cmd).get_output_in_json()
        kubelet_identity_id = kubelet_identity["id"]
        kubelet_identity_principal_id = kubelet_identity["principalId"]
        assert kubelet_identity_id is not None
        assert kubelet_identity_principal_id is not None
        self.kwargs.update(
            {
                "kubelet_identity_id": kubelet_identity_id,
                "kubelet_identity_principal_id": kubelet_identity_principal_id,
            }
        )

        # create role assignment
        create_role_assignment_cmd = (
            "role assignment create --role AcrPull --scope {acr_id} --assignee-object-id {kubelet_identity_principal_id} "
            "--assignee-principal-type ServicePrincipal -o json"
        )
        self.cmd(create_role_assignment_cmd)

        # create AKS cluster
        create_cmd = (
            "aks create --resource-group {resource_group} --name {aks_name} -c 1 --ssh-key-value={ssh_key_value} "
            "--network-plugin kubenet --vnet-subnet-id {vnet_id}/subnets/{aks_subnet_name} "
            "--assign-identity {cluster_identity_id} "
            "--assign-kubelet-identity {kubelet_identity_id} "
            "--bootstrap-artifact-source Cache --bootstrap-container-registry-resource-id {acr_id} "
            "--aks-custom-headers AKSHTTPCustomFeatures=Microsoft.ContainerService/BootstrapProfilePreview "
            "-o json"
        )
        self.cmd(create_cmd, checks=[
            self.check("provisioningState", "Succeeded"),
            self.check("bootstrapProfile.artifactSource", "Cache"),
            self.check("bootstrapProfile.containerRegistryId", acr_id),
        ])

        # delete
        self.cmd("aks delete -g {resource_group} -n {aks_name} --yes --no-wait", checks=[self.is_empty()])
