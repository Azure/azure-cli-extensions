# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from msrestazure.azure_exceptions import CloudError


class VmwareDatastoresScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwareDatastoresScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_vmware_datastores')
    def test_vmware_datastores(self):
        self.kwargs.update({
            'loc': 'centralus',
            'privatecloud': 'cloud1',
            'cluster': 'pycluster1',
            'volume_id:': '/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/ResourceGroup1/providers/Microsoft.NetApp/netAppAccounts/NetAppAccount1/capacityPools/CapacityPool1/volumes/NFSVol1'
        })

        # # Get a pre-created iSCSI datastore
        # self.cmd('az vmware datastore show --name rasivagu-iscsi-datastore --resource-group {rg} --cluster {cluster} --private-cloud {privatecloud}')

        # # List all existing datastores
        # self.cmd('az vmware datastore list --resource-group {rg} --cluster {cluster} --private-cloud {privatecloud}')

        # Create a new ANF based datastore
        self.cmd('az vmware datastore net-app-volume create --name ANFDatastore1 --resource-group {rg} --cluster {cluster} --private-cloud {privatecloud} --volume-id {volume_id}')

        # # Get the newly created ANF based datastore
        # self.cmd('az vmware datastore show --name ANFDatastore1 --resource-group {rg} --cluster {cluster} --private-cloud {privatecloud}')

        # # Delete the newly created ANF based datastore
        # self.cmd('az vmware datastore delete --name ANFDatastore1 --resource-group {rg} --cluster {cluster} --private-cloud {privatecloud}')
