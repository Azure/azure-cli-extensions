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

    @ResourceGroupPreparer(name_prefix='cli_test_imagebuilder')
    def test_imagebuilder(self, resource_group):

        self.kwargs.update({
            'name': 'test1'
        })

        self.cmd('az imagebuilder create '
                 '--resource-group {rg} '
                 '--image-template-name "myImageTemplate" '
                 '--location "westus" '
                 '--customize-name "Shell Customizer Example" '
                 '--distribute-run-output-name "image_it_pir_1" '
                 '--vm-profile-vm-size "Standard_D2s_v3"',
                 checks=[])

        self.cmd('az imagebuilder create '
                 '--resource-group {rg} '
                 '--image-template-name "myImageTemplate" '
                 '--location "westus" '
                 '--customize-name "Shell Customizer Example" '
                 '--distribute-run-output-name "image_it_pir_1" '
                 '--vm-profile-vm-size "Standard_D2s_v3" '
                 '--type "UserAssigned"',
                 checks=[])

        self.cmd('az imagebuilder show '
                 '--resource-group {rg} '
                 '--image-template-name "myImageTemplate"',
                 checks=[])

        self.cmd('az imagebuilder list '
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

        self.cmd('az imagebuilder Run '
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
