# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from azure.cli.testsdk import (ScenarioTest)
from azure.cli.testsdk.reverse_dependency import (
    get_dummy_cli,
)

from .custom_dev_setting_constant import SpringTestEnvironmentEnum
from .custom_preparers import (SpringPreparer, SpringResourceGroupPreparer, SpringSubResourceWrapper)


class TearDown(SpringSubResourceWrapper):
    def __init__(self,
                 resource_group_parameter_name='resource_group',
                 spring_parameter_name='spring'):
        super(TearDown, self).__init__()
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.spring_parameter_name = spring_parameter_name

    def create_resource(self, *_, **kwargs):
        self.resource_group = self._get_resource_group(**kwargs)
        self.spring = self._get_spring(**kwargs)


class ServerVersionTest(ScenarioTest):

    @SpringResourceGroupPreparer(
        dev_setting_name=SpringTestEnvironmentEnum.STANDARD['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.STANDARD['spring'])
    @TearDown()
    def test_list_support_server_versions(self, resource_group, spring):

        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group,
        })
        results = self.cmd('spring list-support-server-versions -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(results) > 0)
