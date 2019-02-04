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

    def _Create_VirtualNetwork(self):
        GenerateVirtualNetworkName(self)
        # return self.cmd('az network vnet create -g {rg} -n {vnet}', checks=[
        #     self.check('name', '{vnet}')
        # ]).get_output_in_json()

    def _Validate_Links(self, expectedLinks, actualLinks):
        result = all(link in actualLinks for link in expectedLinks)
        self.check(result, True)

    def _Create_VirtualNetworkLinks(self, numOfLinks=2):
        self._Create_PrivateZone()
        createdLinks = list()
        for num in range(numOfLinks):
            createdLinks.append(
                self._Create_VirtualNetworkLink(createZone = False))
        createdLinks.sort(key=lambda x: x['name'])
        return createdLinks

    def _Create_VirtualNetworkLink(self, registrationEnabled = False, createZone = True):
        self.kwargs['registrationEnabled'] = registrationEnabled
        if createZone is True:
            self._Create_PrivateZone()
        self._Create_VirtualNetwork()
        GenerateVirtualNetworkLinkName(self)
        return self.cmd('az network privatedns link create -g {rg} -n {link} -z {zone} -v {vnet} -e {registrationEnabled}', checks=[
            self.check('name', '{link}'),
            self.check_pattern('id', GenerateVirtualNetworkLinkArmId(self)),
            self.check('location', 'global'),
            self.check('type', 'Microsoft.Network/privateDnsZones/virtualNetworkLinks'),
            self.exists('etag'),
            self.check('tags', None),
            self.check_pattern('virtualNetwork.id', GenerateVirtualNetworkArmId(self)),
            self.check('registrationEnabled', '{registrationEnabled}'),
            self.check('provisioningState', 'Succeeded'),
            self.check_pattern('virtualNetworkLinkState', 'InProgress|Succeeded')
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
            self.check('tags.{}'.format(tagKey), tagVal),
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
            self.check('tags.{}'.format(tagKey), tagVal),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchZone_ZoneExistsChangeTags_ExpectTagsChanged(self, resource_group):
        GeneratePrivateZoneName(self)
        tagKey, tagVal = GenerateTags(self)
        self.cmd('az network privatedns zone create -g {rg} -n {zone} --tags {tags}', checks=[
            self.check('name', '{zone}'),
            self.check('tags.{}'.format(tagKey), tagVal),
            self.check('provisioningState', 'Succeeded')
        ])
        tagKey, tagVal = GenerateTags(self)
        self.cmd('az network privatedns zone update -g {rg} -n {zone} --tags {tags}', checks=[
            self.check('name', '{zone}'),
            self.check('tags.{}'.format(tagKey), tagVal),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchZone_ZoneExistsRemoveTags_ExpectTagsRemoved(self, resource_group):
        GeneratePrivateZoneName(self)
        tagKey, tagVal = GenerateTags(self)
        self.cmd('az network privatedns zone create -g {rg} -n {zone} --tags {tags}', checks=[
            self.check('name', '{zone}'),
            self.check('tags.{}'.format(tagKey), tagVal),
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
        with self.assertRaisesRegexp(SystemExit, '3'):
            self.cmd('az network privatedns zone show -g {rg} -n {zone}')

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


class PrivateDnsLinksTests(BaseScenarioTests):

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PutLink_LinkNotExistsWithoutRegistration_ExpectLinkCreated(self, resource_group):
        self._Create_VirtualNetworkLink()

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PutLink_LinkNotExistsWithRegistration_ExpectLinkCreated(self, resource_group):
        self._Create_VirtualNetworkLink(registrationEnabled=True)

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PutLink_LinkExistsIfNoneMatchFailure_ExpectError(self, resource_group):
        self._Create_VirtualNetworkLink()
        with self.assertRaisesRegexp(CLIError, 'exists already' ):
            self.cmd('az network privatedns link create -g {rg} -n {link} -z {zone} -v {vnet}')

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchLink_LinkExistsIfMatchSuccess_ExpectLinkUpdated(self, resource_group):
        linkCreated = self._Create_VirtualNetworkLink()
        self.kwargs['etag'] = linkCreated['etag']
        self.cmd('az network privatedns link update -g {rg} -n {link} -z {zone} --if-match {etag}', checks=[
            self.check('name', '{link}'),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchLink_LinkExistsIfMatchFailure_ExpectError(self, resource_group):
        linkCreated = self._Create_VirtualNetworkLink()
        self.kwargs['etag'] = self.create_guid()
        with self.assertRaisesRegexp(CLIError, 'etag mismatch'):
            self.cmd('az network privatedns link update -g {rg} -n {link} -z {zone} --if-match {etag}')

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchLink_ZoneNotExists_ExpectError(self, resource_group):
        GeneratePrivateZoneName(self)
        GenerateVirtualNetworkLinkName(self)
        with self.assertRaisesRegexp(CloudError, 'ResourceNotFound'):
            self.cmd('az network privatedns link update -g {rg} -n {link} -z {zone}')

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchLink_LinkNotExists_ExpectError(self, resource_group):
        self._Create_PrivateZone()
        GenerateVirtualNetworkLinkName(self)
        with self.assertRaisesRegexp(CloudError, 'ResourceNotFound'):
            self.cmd('az network privatedns link update -g {rg} -n {link} -z {zone}')

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchLink_LinkExistsEmptyRequest_ExpectNoError(self, resource_group):
        self._Create_VirtualNetworkLink()
        self.cmd('az network privatedns link update -g {rg} -n {link} -z {zone}', checks=[
            self.check('name', '{link}'),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchLink_EnableRegistration_ExpectRegistrationEnabled(self, resource_group):
        self._Create_VirtualNetworkLink()
        self.kwargs['registrationEnabled'] = True
        self.cmd('az network privatedns link update -g {rg} -n {link} -z {zone} -e {registrationEnabled}', checks=[
            self.check('name', '{link}'),
            self.check('registrationEnabled', '{registrationEnabled}'),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchLink_DisableRegistration_ExpectRegistrationDisabled(self, resource_group):
        self._Create_VirtualNetworkLink(registrationEnabled = True)
        self.kwargs['registrationEnabled'] = False
        self.cmd('az network privatedns link update -g {rg} -n {link} -z {zone} -e {registrationEnabled}', checks=[
            self.check('name', '{link}'),
            self.check('registrationEnabled', '{registrationEnabled}'),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchLink_LinkExistsAddTags_ExpectTagsAdded(self, resource_group):
        self._Create_VirtualNetworkLink()
        tagKey, tagVal = GenerateTags(self)
        self.cmd('az network privatedns link update -g {rg} -n {link} -z {zone} --tags {tags}', checks=[
            self.check('name', '{link}'),
            self.check('tags.{}'.format(tagKey), tagVal),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchLink_LinkExistsChangeTags_ExpectTagsChanged(self, resource_group):
        self._Create_VirtualNetworkLink()
        tagKey, tagVal = GenerateTags(self)
        self.cmd('az network privatedns link update -g {rg} -n {link} -z {zone} --tags {tags}', checks=[
            self.check('name', '{link}'),
            self.check('tags.{}'.format(tagKey), tagVal),
            self.check('provisioningState', 'Succeeded')
        ])
        tagKey, tagVal = GenerateTags(self)
        self.cmd('az network privatedns link update -g {rg} -n {link} -z {zone} --tags {tags}', checks=[
            self.check('name', '{link}'),
            self.check('tags.{}'.format(tagKey), tagVal),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_PatchLink_LinkExistsRemoveTags_ExpectTagsRemoved(self, resource_group):
        self._Create_VirtualNetworkLink()
        tagKey, tagVal = GenerateTags(self)
        self.cmd('az network privatedns link update -g {rg} -n {link} -z {zone} --tags {tags}', checks=[
            self.check('name', '{link}'),
            self.check('tags.{}'.format(tagKey), tagVal),
            self.check('provisioningState', 'Succeeded')
        ])
        self.cmd('az network privatedns link update -g {rg} -n {link} -z {zone} --tags ""', checks=[
            self.check('name', '{link}'),
            self.check('tags', '{{}}'),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_GetLink_ZoneNotExists_ExpectError(self, resource_group):
        GeneratePrivateZoneName(self)
        GenerateVirtualNetworkLinkName(self)
        with self.assertRaisesRegexp(SystemExit, '3'):
            self.cmd('az network privatedns link show -g {rg} -n {link} -z {zone}')

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_GetLink_LinkNotExists_ExpectError(self, resource_group):
        self._Create_PrivateZone()
        GenerateVirtualNetworkLinkName(self)
        with self.assertRaisesRegexp(SystemExit, '3'):
            self.cmd('az network privatedns link show -g {rg} -n {link} -z {zone}')

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_GetLink_LinkExists_ExpectLinkRetrieved(self, resource_group):
        self._Create_VirtualNetworkLink()
        self.cmd('az network privatedns link show -g {rg} -n {link} -z {zone}', checks=[
            self.check('name', '{link}'),
            self.check_pattern('id', GenerateVirtualNetworkLinkArmId(self)),
            self.check('provisioningState', 'Succeeded')
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_ListLinks_NoLinksPresent_ExpectNoLinksRetrieved(self, resource_group):
        self.cmd('az network privatedns link list -g {rg} -z {zone}', checks=[
            self.is_empty()
        ])

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_ListLinks_MultipleLinksPresent_ExpectMultipleLinksRetrieved(self, resource_group):
        expectedLinks = self._Create_VirtualNetworkLinks(numOfLinks=2)
        returnedLinks = self.cmd('az network privatedns link list -g {rg} -z {zone}', checks=[
            self.check('length(@)', 2)
        ]).get_output_in_json()
        self._Validate_Links(expectedLinks, returnedLinks)

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_DeleteLink_ZoneNotExists_ExpectNoError(self, resource_group):
        GeneratePrivateZoneName(self)
        GenerateVirtualNetworkLinkName(self)
        self.cmd('az network privatedns link delete -g {rg} -n {link} -z {zone} -y')

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_DeleteLink_LinkNotExists_ExpectNoError(self, resource_group):
        self._Create_PrivateZone()
        GenerateVirtualNetworkLinkName(self)
        self.cmd('az network privatedns link delete -g {rg} -n {link} -z {zone} -y')

    @ResourceGroupPreparer(name_prefix='clitest_privatedns')
    def test_DeleteLink_LinkExists_ExpectLinkDeleted(self, resource_group):
        self._Create_VirtualNetworkLink()
        self.cmd('az network privatedns link delete -g {rg} -n {link} -z {zone} -y')


if __name__ == '__main__':
    unittest.main()
