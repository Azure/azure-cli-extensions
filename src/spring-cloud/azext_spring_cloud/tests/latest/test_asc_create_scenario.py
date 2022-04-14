# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time

from azure.cli.testsdk import (ScenarioTest, record_only)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

'''
Since the scenarios covered here involves a lot of Azure Spring Cloud service creation. 
It will take around 5~10 minutes to create one. And may take 1~2 hours to finish all.
So as a trade-off, mark it as record_only. It will run against the requests and responses
in yaml files under recordings fold. If the yaml file is not here, it will call to backend 
and generate the yaml file again.
'''


@record_only()
class AzureSpringCloudCreateScenarioTests(ScenarioTest):

    def test_az_asc_create_with_ingress_config(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest-ingress1',
            'location': 'eastus2euap',
            'rg': 'cli'
        })
        self.cmd('spring-cloud create -n {serviceName} -g {rg} -l {location} '
                 '--disable-app-insights=true --ingress-read-timeout=600',
                 checks=[self.check('properties.networkProfile.ingressConfig.readTimeoutInSeconds', 600)])
        self._clean_service(self.kwargs['rg'], self.kwargs['serviceName'])

    def _clean_service(self, rg, service_name):
        self.cmd('spring-cloud delete -n {} -g {} --no-wait'
                 .format(service_name, rg))
