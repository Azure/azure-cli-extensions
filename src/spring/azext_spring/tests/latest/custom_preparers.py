# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from datetime import datetime
from azure.cli.testsdk.preparers import (
    NoTrafficRecordingPreparer,
    ResourceGroupPreparer
)
from azure.cli.testsdk.scenario_tests import (
    SingleValueReplacer,
)
from azure.cli.testsdk.exceptions import (
    CliTestError,
)
from azure.cli.testsdk.reverse_dependency import (
    get_dummy_cli,
)


class SpringPreparer(NoTrafficRecordingPreparer, SingleValueReplacer):
    """
    Prepare a Spring instance before testing and distroy it when finishing.
    It runs `az spring create -n {} -g {} {addtional_params}` to create the instance
    """
    def __init__(self, name_prefix='clitest',
                 parameter_name='spring',
                 dev_setting_name='AZURE_CLI_TEST_DEV_SPRING_NAME',
                 resource_group_parameter_name='resource_group',
                 location='uksouth',
                 random_name_length=15, key='asa', additional_params=None):
        if ' ' in name_prefix:
            raise CliTestError('Error: Space character in Spring name prefix \'%s\'' % name_prefix)
        super(SpringPreparer, self).__init__(name_prefix, random_name_length)
        self.cli_ctx = get_dummy_cli()
        self.parameter_name = parameter_name
        self.key = key
        self.additional_params = additional_params
        self.location = location
        self.resource_group_parameter_name = resource_group_parameter_name

        self.dev_setting_name = os.environ.get(dev_setting_name, None)

    def create_resource(self, name, **kwargs):
        if self.dev_setting_name:
            self.test_class_instance.kwargs[self.key] = self.dev_setting_name
            return {self.parameter_name: self.dev_setting_name}
        group = self._get_resource_group(**kwargs)
        template = 'az spring create -n {} -g {} -l {} {}'.format(name, group, self.location, self.additional_params)
        self.live_only_execute(self.cli_ctx, template)

        self.test_class_instance.kwargs[self.key] = name
        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        if not self.dev_setting_name:
            group = self._get_resource_group(**kwargs)
            template = 'az spring delete -n {} -g {} --no-wait'.format(name, group)
            self.live_only_execute(self.cli_ctx, template)

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create a Spring a resource group is required. Please add ' \
                       'decorator @{} in front of this Spring preparer.'
            raise CliTestError(template.format(ResourceGroupPreparer.__name__))