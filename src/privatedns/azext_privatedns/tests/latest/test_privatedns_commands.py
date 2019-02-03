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
from knack.util import CLIError
from msrestazure.azure_exceptions import CloudError

logger = get_logger(__name__)

class BaseScenarioTests(ScenarioTest):

    def _Validate_Zones(self, expectedZones, actualZones):
        result = all(zone in actualZones for zone in expectedZones)
        self.check(result, True)

    def _Create_PrivateZones(self, numOfZones = 2):
        createdZones = list()
        for num in range(numOfZones):
            createdZones.append(self._Create_PrivateZone())
        createdZones.sort(key=lambda x: x['name'])
        return createdZones

    def _Create_PrivateZone(self):
        GeneratePrivateZoneName(self)
        return self.cmd('az network privatedns zone create -g {rg} -n {zone}', checks=[
            self.check('name', '{zone}'),
            self.check_pattern('id', GeneratePrivateZoneArmId(self)),
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
        ]).get_output_in_json()


class PrivateDnsZonesTests(BaseScenarioTests):

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PutZone_ZoneNotExists_ExpectZoneCreated(self, resource_group):
        self._Create_PrivateZone()

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PutZone_ZoneNotExistsWithTags_ExpectZoneCreatedWithTags(self, resource_group):
        GeneratePrivateZoneName(self)
        tagKey, tagVal = GenerateTags(self)
        self.cmd('az network privatedns zone create -g {rg} -n {zone} --tags {tags}', checks=[
            self.check('name', '{zone}'),
            self.check('tags', '{{\'' + tagKey + '\': \'' + tagVal + '\'}}'),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PutZone_ZoneExistsIfNoneMatchFailure_ExpectError(self, resource_group):
        self._Create_PrivateZone()
        with self.assertRaisesRegexp(CLIError, 'exists already'):
            self.cmd('az network privatedns zone create -g {rg} -n {zone}')

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchZone_ZoneExistsIfMatchSuccess_ExpectZoneUpdated(self, resource_group):
        zoneCreated = self._Create_PrivateZone()
        self.kwargs['etag'] = zoneCreated['etag']
        self.cmd('az network privatedns zone update -g {rg} -n {zone} --if-match {etag}', checks=[
            self.check('name', '{zone}'),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchZone_ZoneExistsIfMatchFailure_ExpectError(self, resource_group):
        zoneCreated = self._Create_PrivateZone()
        self.kwargs['etag'] = self.create_guid()
        with self.assertRaisesRegexp(CLIError, 'etag mismatch'):
            self.cmd('az network privatedns zone update -g {rg} -n {zone} --if-match {etag}')

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchZone_ZoneExistsAddTags_ExpectTagsAdded(self, resource_group):
        self._Create_PrivateZone()
        tagKey, tagVal = GenerateTags(self)
        self.cmd('az network privatedns zone update -g {rg} -n {zone} --tags {tags}', checks=[
            self.check('name', '{zone}'),
            self.check('tags', '{{\'' + tagKey + '\': \'' + tagVal + '\'}}'),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchZone_ZoneExistsChangeTags_ExpectTagsChanged(self, resource_group):
        GeneratePrivateZoneName(self)
        tagKey, tagVal = GenerateTags(self)
        self.cmd('az network privatedns zone create -g {rg} -n {zone} --tags {tags}', checks=[
            self.check('name', '{zone}'),
            self.check('tags', '{{\'' + tagKey + '\': \'' + tagVal + '\'}}'),
            self.check('provisioningState', 'Succeeded')
        ])
        tagKey, tagVal = GenerateTags(self)
        self.cmd('az network privatedns zone update -g {rg} -n {zone} --tags {tags}', checks=[
            self.check('name', '{zone}'),
            self.check('tags', '{{\'' + tagKey + '\': \'' + tagVal + '\'}}'),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchZone_ZoneExistsRemoveTags_ExpectTagsRemoved(self, resource_group):
        GeneratePrivateZoneName(self)
        tagKey, tagVal = GenerateTags(self)
        self.cmd('az network privatedns zone create -g {rg} -n {zone} --tags {tags}', checks=[
            self.check('name', '{zone}'),
            self.check('tags', '{{\'' + tagKey + '\': \'' + tagVal + '\'}}'),
            self.check('provisioningState', 'Succeeded')
        ])
        self.cmd('az network privatedns zone update -g {rg} -n {zone} --tags ""', checks=[
            self.check('name', '{zone}'),
            self.check('tags', '{{}}'),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchZone_ZoneNotExists_ExpectError(self, resource_group):
        GeneratePrivateZoneName(self)
        with self.assertRaisesRegexp(CloudError, 'ResourceNotFound'):
            self.cmd('az network privatedns zone update -g {rg} -n {zone}')


    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchZone_ZoneExistsEmptyRequest_ExpectNoError(self, resource_group):
        self._Create_PrivateZone()
        self.cmd('az network privatedns zone update -g {rg} -n {zone}', checks=[
            self.check('name', '{zone}'),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_GetZone_ZoneExists_ExpectZoneRetrieved(self, resource_group):
        self._Create_PrivateZone()
        self.cmd('az network privatedns zone show -g {rg} -n {zone}', checks=[
            self.check('name', '{zone}'),
            self.check_pattern('id', GeneratePrivateZoneArmId(self)),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_GetZone_ZoneNotExists_ExpectError(self, resource_group):
        GeneratePrivateZoneName(self)
        self.cmd('az network privatedns zone show -g {rg} -n {zone}', expect_failure=True)

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_ListZonesInSubscription_MultipleZonesPresent_ExpectMultipleZonesRetrieved(self, resource_group):
        expectedZones = self._Create_PrivateZones(numOfZones=2)
        returnedZones = self.cmd('az network privatedns zone list', checks=[
            self.greater_than('length(@)', 1)
        ]).get_output_in_json()
        self._Validate_Zones(expectedZones, returnedZones)

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_ListZonesInResourceGroup_MultipleZonesPresent_ExpectMultipleZonesRetrieved(self, resource_group):
        expectedZones = self._Create_PrivateZones(numOfZones=2)
        returnedZones = self.cmd('az network privatedns zone list -g {rg}', checks=[
            self.check('length(@)', 2)
        ]).get_output_in_json()
        self._Validate_Zones(expectedZones, returnedZones)

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_ListZonesInResourceGroup_NoZonesPresent_ExpectNoZonesRetrieved(self, resource_group):
        self.cmd('az network privatedns zone list -g {rg}', checks=[
            self.is_empty()
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_DeleteZone_ZoneExists_ExpectZoneDeleted(self, resource_group):
        self._Create_PrivateZone()
        self.cmd('az network privatedns zone delete -g {rg} -n {zone} -y')

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_DeleteZone_ZoneNotExists_ExpectNoError(self, resource_group):
        GeneratePrivateZoneName(self)
        self.cmd('az network privatedns zone delete -g {rg} -n {zone} -y')

if __name__ == '__main__':
    unittest.main()
