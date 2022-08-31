# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class StaticwebappScenarioTest(ScenarioTest):

    # TODO
    @ResourceGroupPreparer(name_prefix='cli_test_staticwebapp')
    def test_staticwebapp(self, resource_group):
        pass