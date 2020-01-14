# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class SubscriptionClientScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_account')
    def test_account(self, resource_group):

        self.cmd('az account subscription-operation get '
                 '--operation-id "e4b8d068-f574-462a-a76f-6fa0afc613c9"',
                 checks=[])

        self.cmd('az account subscription-operation get '
                 '--operation-id "e4b8d068-f574-462a-a76f-6fa0afc613c9"',
                 checks=[])

        self.cmd('az account operation list',
                 checks=[])

        self.cmd('az account subscription-factory create-subscription-in-enrollment-account '
                 '--display-name "Test Ea Azure Sub" '
                 '--offer-type "MS-AZR-0017P"',
                 checks=[])

        self.cmd('az account subscription-factory create-subscription-in-enrollment-account '
                 '--display-name "Test Ea Azure Sub" '
                 '--offer-type "MS-AZR-0017P"',
                 checks=[])

        self.cmd('az account subscription-factory create-subscription-in-enrollment-account '
                 '--display-name "Test Ea Azure Sub" '
                 '--offer-type "MS-AZR-0017P"',
                 checks=[])

        self.cmd('az account subscription enable',
                 checks=[])

        self.cmd('az account subscription rename',
                 checks=[])

        self.cmd('az account subscription cancel',
                 checks=[])
