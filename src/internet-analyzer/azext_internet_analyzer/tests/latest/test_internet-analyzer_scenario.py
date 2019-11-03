# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class FrontDoorScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_internet_analyzer')
    def test_internet_analyzer(self, resource_group):

        self.kwargs.update({
            'name': 'test1'
        })

        self.cmd('az internet-analyzer profile create '
                 '--resource-group {rg} '
                 '--name "MyProfile" '
                 '--enabled-state "Enabled" '
                 '--location "WestUs"',
                 checks=[])

        self.cmd('az internet-analyzer test create '
                 '--resource-group {rg} '
                 '--profile-name "MyProfile" '
                 '--name "MyExperiment" '
                 '--description "this is my first experiment!" '
                 '--endpoint-a-name "endpoint A" '
                 '--endpoint-a-endpoint "endpointA.net" '
                 '--endpoint-b-name "endpoint B" '
                 '--endpoint-b-endpoint "endpointB.net" '
                 '--enabled-state "Enabled"',
                 checks=[])

        # EXAMPLE NOT FOUND: List NetworkExperiment Profiles in a Resource Group

        # EXAMPLE NOT FOUND: Gets an NetworkExperiment Profile by Profile Id

        # EXAMPLE NOT FOUND: Gets an Experiment by ExperimentName

        # EXAMPLE NOT FOUND: Gets a list of Preconfigured Endpoints

        # EXAMPLE NOT FOUND: Gets a list of Experiments

        # EXAMPLE NOT FOUND: Gets a Latency Scorecard for a given Experiment

        # EXAMPLE NOT FOUND: Gets a Timeseries for a given Experiment

        self.cmd('az internet-analyzer profile delete '
                 '--name "MyResourceGroup" '
                 '--profile-name "MyProfile"',
                 checks=[])

        self.cmd('az internet-analyzer test delete '
                 '--resource-group {rg} '
                 '--profile-name "MyProfile" '
                 '--name "MyExperiment"',
                 checks=[])
