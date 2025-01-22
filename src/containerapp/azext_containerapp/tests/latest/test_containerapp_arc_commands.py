# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, live_only)
from azure.cli.testsdk.decorators import serial_test
from .custom_preparers import ConnectedClusterPreparer


class ContainerAppArcTest(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    def test_containerapp_arc_invalid_command(self):
        with self.assertRaises(SystemExit) as cm:
            self.cmd('containerapp arc setup-core-dns --yes')
        self.assertNotEqual(cm.exception.code, 0)

        with self.assertRaises(SystemExit) as cm:
            self.cmd('containerapp arc setup-core-dns --distro Aks-Hci --yes')
        self.assertNotEqual(cm.exception.code, 0)

    @serial_test()
    @live_only()
    @ResourceGroupPreparer(location="southcentralus", random_name_length=15)
    @ConnectedClusterPreparer(location="southcentralus", skip_connected_cluster=True)
    def test_containerapp_arc_setup_core_dns_e2e(self, resource_group, connected_cluster_name):
        self.cmd('containerapp arc setup-core-dns --distro AksAzureLocal --yes', expect_failure=False)