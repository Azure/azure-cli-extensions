# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappScenarioTest(ScenarioTest):

    @AllowLargeResponse(8192)
    def test_containerapp_preview(self):
        self.cmd('az containerapp create --name "ghrunnersaca" --resource-group "arc-appint-forxinyu12-rg0" --environment "my-environment2" --image "mcr.microsoft.com/k8se/quickstart:latest" --bind postgres:postgres_binding redis')
        return

