# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from datetime import datetime
from azure.cli.testsdk.preparers import NoTrafficRecordingPreparer
from azure_devtools.scenario_tests import SingleValueReplacer
from azure.cli.testsdk.exceptions import CliTestError
from azure.cli.testsdk.reverse_dependency import get_dummy_cli


KEY_RESOURCE_GROUP = 'rg'
KEY_VIRTUAL_NETWORK = 'vnet'
KEY_VNET_SUBNET = 'subnet'


class VirtualNetworkPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest.vn',
                 parameter_name='virtual_network',
                 resource_group_name=None,
                 resource_group_key=KEY_RESOURCE_GROUP,
                 dev_setting_name='AZURE_CLI_TEST_DEV_VIRTUAL_NETWORK_NAME',
                 random_name_length=24, key=KEY_VIRTUAL_NETWORK):
        if ' ' in name_prefix:
            raise CliTestError(
                'Error: Space character in name prefix \'%s\'' % name_prefix)
        super(VirtualNetworkPreparer, self).__init__(
            name_prefix, random_name_length)
        self.cli_ctx = get_dummy_cli()
        self.parameter_name = parameter_name
        self.key = key
        self.resource_group_name = resource_group_name
        self.resource_group_key = resource_group_key
        self.dev_setting_name = os.environ.get(dev_setting_name, None)

    def create_resource(self, name, **kwargs):
        if self.dev_setting_name:
            return {self.parameter_name: self.dev_setting_name, }

        if not self.resource_group_name:
            self.resource_group_name = self.test_class_instance.kwargs.get(
                self.resource_group_key)
            if not self.resource_group_name:
                raise CliTestError("Error: No resource group configured!")

        tags = {'product': 'azurecli', 'cause': 'automation',
                'date': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}
        if 'ENV_JOB_NAME' in os.environ:
            tags['job'] = os.environ['ENV_JOB_NAME']
        tags = ' '.join(['{}={}'.format(key, value)
                         for key, value in tags.items()])
        template = 'az network vnet create --resource-group {} --name {} --tag ' + tags
        self.live_only_execute(self.cli_ctx, template.format(
            self.resource_group_name, name))

        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        # delete vnet if test is being recorded and if the vnet is not a dev rg
        if not self.dev_setting_name:
            self.live_only_execute(
                self.cli_ctx, 'az network vnet delete --name {} --resource-group {}'.format(name, self.resource_group_name))


class VnetSubnetPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    def __init__(self, name_prefix='clitest.vn',
                 parameter_name='subnet',
                 resource_group_name=None,
                 resource_group_key=KEY_RESOURCE_GROUP,
                 vnet_name=None,
                 vnet_key=KEY_VIRTUAL_NETWORK,
                 address_prefixes="11.0.0.0/24",
                 dev_setting_name='AZURE_CLI_TEST_DEV_VNET_SUBNET_NAME',
                 random_name_length=24, key=KEY_VNET_SUBNET):
        if ' ' in name_prefix:
            raise CliTestError(
                'Error: Space character in name prefix \'%s\'' % name_prefix)
        super(VnetSubnetPreparer, self).__init__(
            name_prefix, random_name_length)
        self.cli_ctx = get_dummy_cli()
        self.parameter_name = parameter_name
        self.key = key
        self.resource_group_name = resource_group_name
        self.resource_group_key = resource_group_key
        self.vnet_name = vnet_name
        self.vnet_key = vnet_key
        self.address_prefixes = address_prefixes
        self.dev_setting_name = os.environ.get(dev_setting_name, None)

    def create_resource(self, name, **kwargs):
        if self.dev_setting_name:
            return {self.parameter_name: self.dev_setting_name, }

        if not self.resource_group_name:
            self.resource_group_name = self.test_class_instance.kwargs.get(
                self.resource_group_key)
            if not self.resource_group_name:
                raise CliTestError("Error: No resource group configured!")
        if not self.vnet_name:
            self.vnet_name = self.test_class_instance.kwargs.get(self.vnet_key)
            if not self.vnet_name:
                raise CliTestError("Error: No vnet configured!")

        self.test_class_instance.kwargs[self.key] = 'default'
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        pass
