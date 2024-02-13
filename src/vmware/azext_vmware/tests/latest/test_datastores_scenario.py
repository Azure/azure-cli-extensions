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
            # 'loc': 'centralus',
            # 'privatecloud': 'cloud1',
            # 'cluster': 'pycluster1',
            'rg': 'rasivagu-sddc-rg',
            'privatecloud': 'rasivagu-mock-sddc',
            'cluster': 'Cluster-1',
            'volume_id': '/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/ResourceGroup1/providers/Microsoft.NetApp/netAppAccounts/NetAppAccount1/capacityPools/CapacityPool1/volumes/NFSVol1',
            'target_id': '/subscriptions/ba75e79b-dd95-4025-9dbf-3a7ae8dff2b5/resourceGroups/rasivagu-df-rg/providers/Microsoft.StoragePool/diskPools/rasivagu-df-diskpool/iscsiTargets/rasivagu-df-target'
        })
        
        # Create a new iSCSI based datastore
        self.cmd('az vmware datastore disk-pool-volume create --name iSCSIDatastore1 --resource-group {rg} --private-cloud {privatecloud} --cluster {cluster} --target-id {target_id} --lun-name lun0')
        # "The subscription '11111111-1111-1111-1111-111111111111' could not be found.

        # Get a iSCSI datastore
        self.cmd('az vmware datastore show --name iSCSIDatastore1 --resource-group {rg} --private-cloud {privatecloud} --cluster {cluster}')

        # # List all existing datastores
        self.cmd('az vmware datastore list --resource-group {rg} --private-cloud {privatecloud} --cluster {cluster}')

        # Create a new ANF based datastore
        self.cmd('az vmware datastore netapp-volume create --name ANFDatastore1 --resource-group {rg} --private-cloud {privatecloud} --cluster {cluster} --volume-id {volume_id}')
        # "ANF datastore is not enabled for the cloud SAN version 'v1'

        # Get the newly created ANF based datastore
        self.cmd('az vmware datastore show --name ANFDatastore1 --resource-group {rg} --private-cloud {privatecloud} --cluster {cluster}')

        # Delete the newly created ANF based datastore
        self.cmd('az vmware datastore delete --name iSCSIDatastore1 --resource-group {rg} --private-cloud {privatecloud} --cluster {cluster} --yes')

        # Create a new iSCSI based datastore with --mount-option as ATTACH
        self.cmd('az vmware datastore disk-pool-volume create --name iSCSIDatastore1 --resource-group {rg} --private-cloud {privatecloud} --cluster {cluster} --target-id {target_id} --lun-name lun0 --mount-option ATTACH')
