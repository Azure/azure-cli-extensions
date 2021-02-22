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
        # Get a pre-created iSCSI datastore
        self.cmd('az vmware datastore show --name rasivagu-iscsi-datastore --resource-group rasivagu-cloudsan-rg --cluster Cluster-1 --private-cloud rasivagu-sddc')

        # List all existing datastores
        self.cmd('az vmware datastore list --resource-group rasivagu-cloudsan-rg --cluster Cluster-1 --private-cloud rasivagu-sddc')

        # Create a new ANF based datastore
        self.cmd('az vmware datastore create --name ANFDatastore1 --resource-group rasivagu-cloudsan-rg --cluster Cluster-1 --private-cloud rasivagu-sddc --nfs-file-path ANFVol1FilePath --nfs-provider-ip 10.50.1.4')

        # Get the newly created ANF based datastore
        self.cmd('az vmware datastore show --name ANFDatastore1 --resource-group rasivagu-cloudsan-rg --cluster Cluster-1 --private-cloud rasivagu-sddc')

        # Delete the newly created ANF based datastore
        self.cmd('az vmware datastore delete --name ANFDatastore1 --resource-group rasivagu-cloudsan-rg --cluster Cluster-1 --private-cloud rasivagu-sddc')
