# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

# pylint: disable=unused-argument,too-few-public-methods


class VMAEM(ScenarioTest):

    @ResourceGroupPreparer()
    def test_vm_aem_configure(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1',
        })
        self.cmd('vm create -g {rg} -n {vm} --image centos --generate-ssh-keys')
        self.cmd('vm aem set -g {rg} -n {vm}')
        self.cmd('vm aem verify -g {rg} -n {vm}')
        self.cmd('vm aem delete -g {rg} -n {vm}')
        self.cmd('vm aem verify -g {rg} -n {vm}')
