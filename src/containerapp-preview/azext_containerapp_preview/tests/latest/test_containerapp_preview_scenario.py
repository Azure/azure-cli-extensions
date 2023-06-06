# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class containerappScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview')
    def test_containerapp_preview(self, resource_group):

        self.kwargs.update({
            'name': 'test1'
        })

        self.cmd('az containerapp create --name "ghrunnersacajobstest" --resource-group "arc-appint-forxinyu12-rg0" --environment "my-environment" --image "mcr.microsoft.com/k8se/quickstart:latest"')