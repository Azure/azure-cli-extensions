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

        self.cmd('az internet-analyzer profile list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az internet-analyzer profile show '
                 '--resource-group {rg} '
                 '--name "MyProfile"',
                 checks=[])

        self.cmd('az internet-analyzer test show '
                 '--resource-group {rg} '
                 '--profile-name "MyProfile" '
                 '--name "MyExperiment"',
                 checks=[])

        self.cmd('az internet-analyzer test list '
                 '--resource-group {rg} '
                 '--profile-name "MyProfile"',
                 checks=[])

        self.cmd('az internet-analyzer preconfigured-endpoint list '
                 '--resource-group {rg} '
                 '--profile-name "MyProfile"',
                 checks=[])

        self.cmd('az internet-analyzer show-scorecard '
                 '--resource-group {rg} '
                 '--profile-name "MyProfile" '
                 '--test-name "MyExperiment" '
                 '--aggregation-interval "Daily" '
                 '--end-date-time-utc "2019-09-21T17:32:28Z" ',
                 checks=[])

        self.cmd('az internet-analyzer show-timeseries '
                 '--resource-group {rg} '
                 '--profile-name "MyProfile" '
                 '--test-name "MyExperiment" '
                 '--aggregation-interval "Hourly" '
                 '--start-date-time-utc "2019-07-21T17:32:28Z" '
                 '--end-date-time-utc "2019-09-21T17:32:28Z" '
                 '--timeseries-type "MeasurementCounts" '
                 '--endpoint "endpoint1.net"',
                 checks=[])

        self.cmd('az internet-analyzer test delete '
                 '--resource-group {rg} '
                 '--profile-name "MyProfile" '
                 '--name "MyExperiment"',
                 checks=[])

        self.cmd('az internet-analyzer profile delete '
                 '--resource-group {rg} '
                 '--name "MyProfile"',
                 checks=[])
