# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class HealthcareApisScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_healthcareapis')
    def test_healthcareapis(self, resource_group):

        self.cmd('az healthcareapis create '
                 '--resource-group {rg} '
                 '--name hcservicernd652 '
                 '--kind "fhir-R4" '
                 '--location "westus2" '
                 '--access-policies-object-id "c487e7d1-3210-41a3-8ccc-e9372b78da47,5b307da8-43d4-492b-8b66-b0294ade872f" '
                 '--cosmos-db-offer-throughput "1000" '
                 '--authentication-authority "https://login.microsoftonline.com/abfde7b2-df0f-47e6-aabf-2462b07508dc" '
                 '--authentication-audience "https://azurehealthcareapis.com" '
                 '--authentication-smart-proxy-enabled true '
                 '--cors-origins "*" '
                 '--cors-headers "*" '
                 '--cors-methods "DELETE,GET,OPTIONS,PATCH,POST,PUT" '
                 '--cors-max-age "1440" '
                 '--cors-allow-credentials false',
                 checks=[])

        self.cmd('az healthcareapis delete '
                 '--resource-group {rg} '
                 '--name hcservicernd652',
                 checks=[])

        self.cmd('az healthcareapis create '
                 '--resource-group {rg} '
                 '--name hcservicernd653 '
                 '--kind "fhir-R4" '
                 '--location "westus2" '
                 '--access-policies-object-id "c487e7d1-3210-41a3-8ccc-e9372b78da47"',
                 checks=[])

        self.cmd('az healthcareapis show '
                 '--resource-group {rg} '
                 '--name hcservicernd653',
                 checks=[])

        self.cmd('az healthcareapis list',
                 checks=[])

        self.cmd('az healthcareapis list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az healthcareapis delete '
                 '--resource-group {rg} '
                 '--name hcservicernd653',
                 checks=[])
