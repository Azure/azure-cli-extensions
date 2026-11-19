# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import ScenarioTest, live_only
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class OracleDatabasePrivateIpAddressScenario(ScenarioTest):

    # @live_only()
    @AllowLargeResponse(size_kb=10240)
    def test_oracledatabase_cloud_vm_cluster_list_private_ip_address(self):
        # Populate the existing cluster details and set its OCI subnet/VNIC environment variables.
        resource_group = 'advancedNetworkingTest'
        cloud_vm_cluster_name = 'DataGuardTest0504'
        subnet_id = os.environ.get('AZURE_ORACLE_DATABASE_SUBNET_ID', '<subnet-ocid>')
        vnic_id = os.environ.get('AZURE_ORACLE_DATABASE_VNIC_ID', '<vnic-ocid>')

        result = self.cmd(
            'az oracle-database cloud-vm-cluster list-private-ip-address '
            '--resource-group {} '
            '--cloudvmclustername {} '
            '--subnet-id {} '
            '--vnic-id {}'.format(
                resource_group,
                cloud_vm_cluster_name,
                subnet_id,
                vnic_id,
            )
        ).get_output_in_json()
        self.assertIsInstance(result, list)
        self.assertTrue(result)
        self.assertTrue(all('ipAddress' in address for address in result))
