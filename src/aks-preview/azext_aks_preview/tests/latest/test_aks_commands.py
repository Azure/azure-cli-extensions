# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import unittest

from knack.util import CLIError

from azure.cli.testsdk import (
    ResourceGroupPreparer, RoleBasedServicePrincipalPreparer, ScenarioTest, live_only)
from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk.checkers import (StringContainCheck, StringContainCheckIgnoreCase)

# flake8: noqa


class AzureKubernetesServiceScenarioTest(ScenarioTest):

    @AllowLargeResponse()
    @ResourceGroupPreparer(random_name_length=17, name_prefix='clitest', location='eastus')
    @RoleBasedServicePrincipalPreparer()
    def test_aks_create_default_service(self, resource_group, resource_group_location, sp_name, sp_password):
        # reset the count so in replay mode the random names will start with 0
        self.test_resources_count = 0
        # kwargs for string formatting
        aks_name = self.create_random_name('cliakstest', 16)
        tags = "key1=value1"
        nodepool_labels = "label1=value1 label2=value2"
        self.kwargs.update({
            'resource_group': resource_group,
            'name': aks_name,
            'dns_name_prefix': self.create_random_name('cliaksdns', 16),
            'ssh_key_value': self.generate_ssh_keys().replace('\\', '\\\\'),
            'location': resource_group_location,
            'service_principal': sp_name,
            'client_secret': sp_password,
            'tags': tags,
            'nodepool_labels': nodepool_labels,
            'resource_type': 'Microsoft.ContainerService/ManagedClusters'
        })

        # create
        create_cmd = 'aks create --resource-group={resource_group} --name={name} --location={location} ' \
                     '--dns-name-prefix={dns_name_prefix} --node-count=1 --ssh-key-value={ssh_key_value} ' \
                     '--service-principal={service_principal} --client-secret={client_secret} --tags {tags} ' \
                     '--nodepool-labels {nodepool_labels}'
        self.cmd(create_cmd, checks=[
            self.exists('fqdn'),
            self.exists('nodeResourceGroup'),
            self.check('provisioningState', 'Succeeded'),
            self.check('tags.key2', 'value1')
        ])
