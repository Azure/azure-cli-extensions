# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk import ResourceGroupPreparer


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class OperationsManagementClientScenarioTest(ScenarioTest):

    def current_subscription(self):
        subs = self.cmd('az account show').get_output_in_json()
        return subs['id']

    @ResourceGroupPreparer(name_prefix='cli_test_operationsmanagement_rg2'[:9], key='rg')
    @ResourceGroupPreparer(name_prefix='cli_test_operationsmanagement_rg1'[:9], key='rg_2')
    def test_operationsmanagement(self, resource_group):

        self.kwargs.update({
            'subscription_id': self.current_subscription()
        })

        self.kwargs.update({
            'solution1': self.create_random_name(prefix='cli_test_solutions'[:9], length=24),
            'managementAssociation1': self.create_random_name(prefix='cli_test_management_associations'[:9],
                                                              length=24),
            'ManagementAssociations_2': self.create_random_name(prefix='cli_test_management_associations'[:9],
                                                                length=24),
            'managementConfiguration1': self.create_random_name(prefix='cli_test_management_configurations'[:9],
                                                                length=24),
            'ManagementConfigurations_2': self.create_random_name(prefix='cli_test_management_configurations'[:9],
                                                                  length=24),
        })

        # EXAMPLE: Solutions/resource-group-name/SolutionCreate
        self.cmd('az operationsmanagement solution create '
                 '--location "East US" '
                 '--plan name=name1 product=product1 promotion-code=promocode1 publisher=publisher1 '
                 '--properties contained-resources=["/subscriptions/sub2/resourceGroups/rg2/providers/provider1/resourc'
                 'es/resource1","/subscriptions/sub2/resourceGroups/rg2/providers/provider2/resources/resource2"] refer'
                 'enced-resources=["/subscriptions/sub2/resourceGroups/rg2/providers/provider1/resources/resource2","/s'
                 'ubscriptions/sub2/resourceGroups/rg2/providers/provider2/resources/resource3"] workspace-resource-id='
                 '/subscriptions/{subscription_id}/resourceGroups/{rg}/providers/Microsoft.OperationalInsights/workspac'
                 'es/ws1 '
                 '--resource-group "{rg_2}" '
                 '--solution-name "{solution1}"',
                 checks=[])

        # EXAMPLE: ManagementConfigurations/resource-group-name/ManagementConfigurationCreate
        self.cmd('az operationsmanagement management-configuration create '
                 '--management-configuration-name "{managementConfiguration1}" '
                 '--location "East US" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        # EXAMPLE: ManagementAssociations/resource-group-name/SolutionCreate
        self.cmd('az operationsmanagement management-association create '
                 '--management-association-name "{managementAssociation1}" '
                 '--location "East US" '
                 '--properties application-id=/subscriptions/{subscription_id}/resourcegroups/{rg_2}/providers/Microsof'
                 't.Appliance/Appliances/appliance1 '
                 '--resource-group "{rg_2}"',
                 checks=[])

        # EXAMPLE: ManagementAssociations/resource-group-name/SolutionGet
        self.cmd('az operationsmanagement management-association show '
                 '--management-association-name "{managementAssociation1}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        # EXAMPLE: ManagementConfigurations/resource-group-name/SolutionGet
        self.cmd('az operationsmanagement management-configuration show '
                 '--management-configuration-name "{ManagementConfigurations_2}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        # EXAMPLE: Solutions/resource-group-name/SolutionGet
        self.cmd('az operationsmanagement solution show '
                 '--resource-group "{rg_2}" '
                 '--solution-name "{solution1}"',
                 checks=[])

        # EXAMPLE: Solutions/resource-group-name/SolutionList
        self.cmd('az operationsmanagement solution list '
                 '--resource-group "{rg_2}"',
                 checks=[])

        # EXAMPLE: ManagementConfigurations/api-version/SolutionList
        self.cmd('az operationsmanagement management-configuration list',
                 checks=[])

        # EXAMPLE: ManagementAssociations/api-version/SolutionList
        self.cmd('az operationsmanagement management-association list',
                 checks=[])

        # EXAMPLE: Solutions/api-version/SolutionList
        self.cmd('az operationsmanagement solution list',
                 checks=[])

        # EXAMPLE: Solutions/resource-group-name/SolutionUpdate
        self.cmd('az operationsmanagement solution update '
                 '--tags Dept=IT Environment=Test '
                 '--resource-group "{rg_2}" '
                 '--solution-name "{solution1}"',
                 checks=[])

        # EXAMPLE: ManagementAssociations/resource-group-name/SolutionDelete
        self.cmd('az operationsmanagement management-association delete '
                 '--management-association-name "{ManagementAssociations_2}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        # EXAMPLE: ManagementConfigurations/resource-group-name/ManagementConfigurationDelete
        self.cmd('az operationsmanagement management-configuration delete '
                 '--management-configuration-name "{ManagementConfigurations_2}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        # EXAMPLE: Solutions/resource-group-name/SolutionDelete
        self.cmd('az operationsmanagement solution delete '
                 '--resource-group "{rg_2}" '
                 '--solution-name "{solution1}"',
                 checks=[])
