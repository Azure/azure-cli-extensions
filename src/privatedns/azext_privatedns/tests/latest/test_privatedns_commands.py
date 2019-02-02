# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from ._test_data_generator import *
from knack.log import get_logger

logger = get_logger(__name__)

class PrivateDnsZonesTests(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PutZone_ZoneNotExists_ExpectZoneCreated(self, resource_group):

        GeneratePrivateZoneName(self)

        self.cmd('az network privatedns zone create -g {rg} -n {zone}', checks=[
            self.check('name', '{zone}'),
            self.check('id', GeneratePrivateZoneArmId(self)),
            self.check('location', 'global'),
            self.check('type', 'Microsoft.Network/privateDnsZones'),
            self.exists('etag'),
            self.check('tags', None),
            self.check('provisioningState', 'Succeeded'),
            self.greater_than('maxNumberOfRecordSets', 0),
            self.greater_than('maxNumberOfVirtualNetworkLinks', 0),
            self.greater_than('maxNumberOfVirtualNetworkLinksWithRegistration', 0),
            self.check('numberOfRecordSets', 1),
            self.check('numberOfVirtualNetworkLinks', 0),
            self.check('numberOfVirtualNetworkLinksWithRegistration', 0),
        ])


    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PutZone_ZoneNotExistsWithTags_ExpectZoneCreatedWithTags(self, resource_group):

        GeneratePrivateZoneName(self)
        tagKey, tagVal = GenerateTags(self)

        self.cmd('az network privatedns zone create -g {rg} -n {zone} --tags {tags}', checks=[
            self.check('name', '{zone}'),
            self.check('id', GeneratePrivateZoneArmId(self)),
            self.check('location', 'global'),
            self.check('type', 'Microsoft.Network/privateDnsZones'),
            self.exists('etag'),
            self.check('tags', '{{\'' + tagKey + '\': \'' + tagVal + '\'}}'),
            self.check('provisioningState', 'Succeeded'),
            self.greater_than('maxNumberOfRecordSets', 0),
            self.greater_than('maxNumberOfVirtualNetworkLinks', 0),
            self.greater_than('maxNumberOfVirtualNetworkLinksWithRegistration', 0),
            self.check('numberOfRecordSets', 1),
            self.check('numberOfVirtualNetworkLinks', 0),
            self.check('numberOfVirtualNetworkLinksWithRegistration', 0),
        ])



if __name__ == '__main__':
    unittest.main()
