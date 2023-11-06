# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class CommunityGalleryScenarioTest(ScenarioTest):

    # At present, due to the relevant Python SDK is not released to public,
    # the relevant commands in the test are only used through local build and are not released.
    # Related PR: https://github.com/Azure/azure-cli/pull/20129
    # So skip this test in CI first
    @ResourceGroupPreparer(location='CentralUSEUAP')
    @unittest.skip('Relevant commands in main repo have not been released')
    def test_community_gallery_operations(self, resource_group, resource_group_location):
        self.kwargs.update({
            'vm': self.create_random_name('vm', 16),
            'gallery': self.create_random_name('gellery', 16),
            'image': self.create_random_name('image', 16),
            'version': '1.1.2',
            'captured': 'managedImage1',
            'location': resource_group_location,
        })

        self.cmd('sig create -g {rg} --gallery-name {gallery} --permissions Community --publisher-uri puburi --publisher-email abc@123.com --eula eula --public-name-prefix pubname')
        self.cmd('sig share enable-community -r {gallery} -g {rg}')

        self.cmd('sig image-definition create -g {rg} --gallery-name {gallery} --gallery-image-definition {image} --os-type linux -p publisher1 -f offer1 -s sku1')
        self.cmd('vm create -g {rg} -n {vm} --image ubuntults --nsg-rule None')
        self.cmd('vm deallocate -g {rg} -n {vm}')
        self.cmd('vm generalize -g {rg} -n {vm}')

        self.cmd('image create -g {rg} -n {captured} --source {vm}')
        self.cmd('sig image-version create -g {rg} --gallery-name {gallery} --gallery-image-definition {image} --gallery-image-version {version} --managed-image {captured} --replica-count 1')
        self.kwargs['public_name'] = self.cmd('sig show --gallery-name {gallery} --resource-group {rg} --select Permissions').get_output_in_json()['sharingProfile']['communityGalleryInfo']['publicNames'][0]

        self.cmd('sig show-community --location {location} --public-gallery-name {public_name}', checks=[
            self.check('location', '{location}'),
            self.check('name', '{public_name}'),
            self.check('uniqueId', '/CommunityGalleries/{public_name}')
        ])

        self.cmd('sig image-definition show-community --gallery-image-definition {image} '
                 '--public-gallery-name {public_name} --location {location}', checks=[
            self.check('location', '{location}'),
            self.check('name', '{image}'),
            self.check('uniqueId', '/CommunityGalleries/{public_name}/Images/{image}')
        ])

        self.cmd('sig image-definition list-community --public-gallery-name {public_name} --location {location}', checks=[
            self.check('[0].location', '{location}'),
            self.check('[0].name', '{image}'),
            self.check('[0].uniqueId', '/CommunityGalleries/{public_name}/Images/{image}')
        ])

        self.kwargs['community_gallery_image_version'] = self.cmd('sig image-version show-community --gallery-image-definition {image} --public-gallery-name {public_name} --location {location} --gallery-image-version {version}', checks=[
            self.check('location', '{location}'),
            self.check('name', '{version}'),
            self.check('uniqueId', '/CommunityGalleries/{public_name}/Images/{image}/Versions/{version}')
        ]).get_output_in_json()['uniqueId']

        self.cmd('sig image-version list-community --gallery-image-definition {image} --public-gallery-name {public_name} '
                 '--location {location}', checks=[
            self.check('[0].location', '{location}'),
            self.check('[0].name', '{version}'),
            self.check('[0].uniqueId', '/CommunityGalleries/{public_name}/Images/{image}/Versions/{version}')
        ])

        # gallery permissions must be reset, or the resource group can't be deleted
        self.cmd('sig share reset --gallery-name {gallery} -g {rg}')
        self.cmd('sig show --gallery-name {gallery} --resource-group {rg} --select Permissions', checks=[
            self.check('sharingProfile.permissions', 'Private')
        ])

    # At present, due to the relevant Python SDK is not released to public,
    # the relevant commands in the test are only used through local build and are not released.
    # Related PR: https://github.com/Azure/azure-cli/pull/20129
    # So skip this test in CI first
    @ResourceGroupPreparer(location='CentralUSEUAP')
    @unittest.skip('Relevant commands in main repo have not been released')
    def test_create_vm_with_community_gallery_image(self, resource_group, resource_group_location):
        self.kwargs.update({
            'vm': self.create_random_name('vm', 16),
            'vm_with_community_gallery': self.create_random_name('vm_sg', 16),
            'vm_with_community_gallery_version': self.create_random_name('vm_sgv', 16),
            'vm_with_community_gallery_version2': self.create_random_name('vm_sgv2', 16),
            'vmss_with_community_gallery_version': self.create_random_name('vmss', 16),
            'gallery': self.create_random_name('gellery', 16),
            'image': self.create_random_name('image', 16),
            'version': '1.1.2',
            'captured': 'managedImage1',
            'location': resource_group_location,
            'subId': '0b1f6471-1bf0-4dda-aec3-cb9272f09590',  # share the gallery to tester's subscription, so the tester can get community galleries
            'tenantId': '2f4a9838-26b7-47ee-be60-ccc1fdec5953',
        })

        self.cmd('sig create -g {rg} --gallery-name {gallery} --permissions Community --publisher-uri puburi --publisher-email abc@123.com --eula eula --public-name-prefix pubname')
        self.cmd('sig share enable-community -r {gallery} -g {rg}')

        self.cmd('sig image-definition create -g {rg} --gallery-name {gallery} --gallery-image-definition {image} --os-type linux -p publisher1 -f offer1 -s sku1')
        self.cmd('vm create -g {rg} -n {vm} --image ubuntults --nsg-rule None')
        self.cmd('vm deallocate -g {rg} -n {vm}')
        self.cmd('vm generalize -g {rg} -n {vm}')

        self.cmd('image create -g {rg} -n {captured} --source {vm}')
        self.cmd('sig image-version create -g {rg} --gallery-name {gallery} --gallery-image-definition {image} --gallery-image-version {version} --managed-image {captured} --replica-count 1')
        self.kwargs['public_name'] = self.cmd('sig show --gallery-name {gallery} --resource-group {rg} --select Permissions').get_output_in_json()['sharingProfile']['communityGalleryInfo']['publicNames'][0]

        self.kwargs['community_gallery_image_version'] = self.cmd('sig image-version show-community --gallery-image-definition {image} --public-gallery-name {public_name} --location {location} --gallery-image-version {version}', checks=[
            self.check('location', '{location}'),
            self.check('name', '{version}'),
            self.check('uniqueId', '/CommunityGalleries/{public_name}/Images/{image}/Versions/{version}')
        ]).get_output_in_json()['uniqueId']

        self.cmd('vm create -g {rg} -n {vm_with_community_gallery_version} --image {community_gallery_image_version} --nsg-rule None')

        self.cmd('vm show -g {rg} -n {vm_with_community_gallery_version}', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('storageProfile.imageReference.communityGalleryImageId', '{community_gallery_image_version}'),
        ])

        from azure.cli.core.azclierror import ArgumentUsageError
        with self.assertRaises(ArgumentUsageError):
            self.cmd('vm create -g {rg} -n {vm_with_community_gallery_version2} --image {community_gallery_image_version} --nsg-rule None --os-type windows')

        self.cmd('vmss create -g {rg} -n {vmss_with_community_gallery_version} --image {community_gallery_image_version} ')

        self.cmd('vmss show -g {rg} -n {vmss_with_community_gallery_version}', checks=[
            self.check('provisioningState', 'Succeeded'),
            self.check('virtualMachineProfile.storageProfile.imageReference.communityGalleryImageId', '{community_gallery_image_version}'),
        ])

        # gallery permissions must be reset, or the resource group can't be deleted
        self.cmd('sig share reset --gallery-name {gallery} -g {rg}')
        self.cmd('sig show --gallery-name {gallery} --resource-group {rg} --select Permissions', checks=[
            self.check('sharingProfile.permissions', 'Private')
        ])

    @ResourceGroupPreparer(location='eastus')
    def test_shared_gallery_community(self, resource_group):
        self.kwargs.update({
            'gallery': self.create_random_name('gellery', 16),
        })
        self.cmd(
            'sig create -r {gallery} -g{rg} --permissions Community --publisher-uri puburi --publisher-email abc@123.com --eula eula --public-name-prefix pubname',
            checks=[
                self.check('name', '{gallery}'),
                self.check('resourceGroup', '{rg}'),
                self.check('sharingProfile.permissions', 'Community'),
                self.check('sharingProfile.communityGalleryInfo.publisherUri', 'puburi'),
                self.check('sharingProfile.communityGalleryInfo.publisherContact', 'abc@123.com'),
                self.check('sharingProfile.communityGalleryInfo.eula', 'eula'),
                self.check("sharingProfile.communityGalleryInfo.publicNames[0].starts_with(@, 'pubname')", True),
                self.check('sharingProfile.communityGalleryInfo.communityGalleryEnabled', False)
            ])
        self.cmd('sig share enable-community -r {gallery} -g {rg}')
        self.cmd('sig show -r {gallery} -g {rg}', checks=[
            self.check('sharingProfile.communityGalleryInfo.communityGalleryEnabled', True)
        ])
        self.cmd('sig share reset -r {gallery} -g {rg}')
        self.cmd('sig delete -r {gallery} -g {rg}')
