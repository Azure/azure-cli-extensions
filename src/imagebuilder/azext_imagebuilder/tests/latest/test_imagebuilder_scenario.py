# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ImageBuilderClientScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_imagebuilder', location='westus2')
    def test_imagebuilder(self, resource_group):

        self.kwargs.update({
            'it': 'it1'
        })

        # az feature register --namespace Microsoft.VirtualMachineImages --name VirtualMachineTemplatePreview

        rg_id = self.cmd('az group show -g {rg}').get_output_in_json()['id']

        self.kwargs.update({
            'rg_id': rg_id
        })

        self.cmd('az role assignment create --assignee cf32a0cc-373c-47c9-9156-0db11f6a6dfc --role Contributor --scope {rg_id}')

        self.cmd('az imagebuilder create '
                 '--resource-group {rg} '
                 '--name {it} '
                 '--source '
                 '--location westus '
                 '--distribute-type ManagedImage '
                 '--distribute-location westus '
                 '--distribute-image image1',
                 checks=[])

        self.cmd('az imagebuilder create '
                 '--resource-group {rg} '
                 '--image-template-name "myImageTemplate" '
                 '--location "westus" '
                 '--vm-profile-vm-size "Standard_D2s_v3" '
                 '--type "UserAssigned"',
                 checks=[])

        self.cmd('az imagebuilder get_run_output '
                 '--resource-group {rg} '
                 '--image-template-name "myImageTemplate"',
                 checks=[])

        self.cmd('az imagebuilder list_run_outputs '
                 '--resource-group {rg} '
                 '--image-template-name "myImageTemplate"',
                 checks=[])

        self.cmd('az imagebuilder show '
                 '--resource-group {rg} '
                 '--image-template-name "myImageTemplate"',
                 checks=[])

        self.cmd('az imagebuilder list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az imagebuilder list',
                 checks=[])

        self.cmd('az imagebuilder run '
                 '--resource-group {rg} '
                 '--image-template-name "myImageTemplate"',
                 checks=[])

        self.cmd('az imagebuilder update '
                 '--resource-group {rg} '
                 '--image-template-name "myImageTemplate" '
                 '--type "None"',
                 checks=[])

        self.cmd('az imagebuilder update '
                 '--resource-group {rg} '
                 '--image-template-name "myImageTemplate"',
                 checks=[])

        self.cmd('az imagebuilder delete '
                 '--resource-group {rg} '
                 '--image-template-name "myImageTemplate"',
                 checks=[])
