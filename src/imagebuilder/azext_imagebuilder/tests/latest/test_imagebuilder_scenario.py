# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import mock

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ImageBuilderClientScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_imagebuilder1', location='westus')
    def test_imagebuilder1(self, resource_group):

        # Create a Custom Image from an Azure Platform Vanilla OS Image

        self.kwargs.update({
            'it': 'it1',
            'img': 'img1',
            'vm': 'vm1'
        })

        # az feature register --namespace Microsoft.VirtualMachineImages --name VirtualMachineTemplatePreview

        rg_id = self.cmd('az group show -g {rg}').get_output_in_json()['id']

        self.kwargs.update({
            'rg_id': rg_id
        })

        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd('az role assignment create --assignee cf32a0cc-373c-47c9-9156-0db11f6a6dfc '
                     '--role Contributor --scope {rg_id}')

        self.cmd('az imagebuilder create '
                 '--resource-group {rg} '
                 '--name {it} '
                 '--source-type PlatformImage '
                 '--source-urn Canonical:UbuntuServer:18.04-LTS:18.04.201903060 '
                 '--customize @cus.json '
                 '--distribute-type ManagedImage '
                 '--distribute-location westus '
                 '--distribute-image {img}',
                 checks=[self.check('name', '{it}')])

        self.cmd('az imagebuilder run -g {rg} -n {it}')

        self.cmd('az vm create -g {rg} -n {vm} --image {img}')

    @ResourceGroupPreparer(name_prefix='cli_test_imagebuilder2', location='westus')
    def test_imagebuilder2(self, resource_group):

        # Creating_a_Custom_Linux_Shared_Image_Gallery_Image

        self.kwargs.update({
            'it': 'it1',
            'img': 'img1',
            'vm': 'vm1',
            'sig': self.create_random_name(prefix='sig1', length=20),
            'imgd': 'imgd1'
        })

        # az feature register --namespace Microsoft.VirtualMachineImages --name VirtualMachineTemplatePreview

        rg_id = self.cmd('az group show -g {rg}').get_output_in_json()['id']

        self.kwargs.update({
            'rg_id': rg_id
        })

        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd('az role assignment create --assignee cf32a0cc-373c-47c9-9156-0db11f6a6dfc '
                     '--role Contributor --scope {rg_id}')

        self.cmd('az sig create -g {rg} --gallery-name {sig}')

        imgd_id = self.cmd('az sig image-definition create -g {rg} --gallery-name {sig} '
                           '--gallery-image-definition {imgd} '
                           '--publisher corpIT --offer myOffer --sku 18.04-LTS --os-type Linux'
                           ).get_output_in_json()['id']

        self.kwargs.update({
            'imgd_id': imgd_id
        })

        self.cmd('az imagebuilder create '
                 '--resource-group {rg} '
                 '--name {it} '
                 '--source-type PlatformImage '
                 '--source-urn Canonical:UbuntuServer:18.04-LTS:18.04.201903060 '
                 '--distribute-type SharedImage '
                 '--distribute-location westus eastus '
                 '--distribute-image {imgd_id}',
                 checks=[self.check('name', '{it}')])

        self.cmd('az imagebuilder run -g {rg} -n {it}')

        self.cmd('az vm create -g {rg} -n {vm} --image {imgd_id}/versions/latest')
