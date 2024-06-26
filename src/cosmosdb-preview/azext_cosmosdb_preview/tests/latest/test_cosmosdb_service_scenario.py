# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from knack.util import CLIError
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from datetime import datetime, timedelta, timezone
from dateutil import parser

class Cosmosdb_previewServiceScenarioTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_test_cosmosdb_service', location='eastus2')
    def test_cosmosdb_service(self, resource_group):
        self.kwargs.update({
            'acc': self.create_random_name(prefix='cli', length=15)
        })

        # Create account
        self.cmd('az cosmosdb create -n {acc} -g {rg} --locations regionName=eastus2 failoverPriority=0 isZoneRedundant=False')

        service_create = self.cmd('az cosmosdb service create -a {acc} -g {rg} --name "sqlDedicatedGateway" --kind SqlDedicatedGateway --gateway-type IntegratedCache --count 1 --size "Cosmos.D4s" ').get_output_in_json()
        assert service_create["name"] == "sqlDedicatedGateway"

        service_update = self.cmd('az cosmosdb service update -a {acc} -g {rg} --name "sqlDedicatedGateway" --kind SqlDedicatedGateway --count 2 --size "Cosmos.D4s" ').get_output_in_json()
        assert service_update["name"] == "sqlDedicatedGateway"

        self.cmd('az cosmosdb service show  -a {acc} -g {rg} --name "sqlDedicatedGateway"')

        service_list = self.cmd('az cosmosdb service list -a {acc} -g {rg}').get_output_in_json()
        assert len(service_list) == 1
