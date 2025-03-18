# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, record_only)
from .custom_preparers import (SpringPreparer, SpringResourceGroupPreparer)
from .custom_dev_setting_constant import SpringTestEnvironmentEnum
from knack.log import get_logger

logger = get_logger(__name__)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
'''
Since the scenarios covered here depend on a Azure Spring service instance creation.
It cannot support live run. So mark it as record_only.
'''

@record_only()
class ApidExportTest(ScenarioTest):
    
    @SpringResourceGroupPreparer(
        dev_setting_name=SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['spring'])
    def test_asa_export(self, resource_group, spring):
        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group,
        })

        self.cmd('spring export -g {rg} -s {serviceName} --output-folder .\\output')


