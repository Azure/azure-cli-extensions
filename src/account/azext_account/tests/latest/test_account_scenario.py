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

        self.cmd('az account subscription create '
                 '--billing-account-name "0aa27f2b-ec7f-5a65-71f6-a5ff0897bd55:ae0dae1e-de9a-41f6-8257-76b055d98372_2019-05-31" '
                 '--billing-profile-name "27VR-HDWX-BG7-TGB" '
                 '--cost-center "135366376" '
                 '--display-name "Contoso MCA subscription" '
                 '--sku-id "0001" '
                 '--invoice-section-name "JGF7-NSBG-PJA-TGB"',
                 checks=[])

        self.cmd('az account subscription create-subscription-in-enrollment-account '
                 '--display-name "Test Ea Azure Sub" '
                 '--offer-type "MS-AZR-0017P" '
                 '--enrollment-account-name "73f8ab6e-cfa0-42be-b886-be6e77c2980c"',
                 checks=[])

        self.cmd('az account subscription create-csp-subscription '
                 '--billing-account-name "2bc54a6f-8d8a-5be1-5bff-bb4f285f512b:11a72812-d9a4-446e-9a1e-70c8bcadf5c0_2019-05-31" '
                 '--display-name "Contoso MCA subscription" '
                 '--sku-id "0001" '
                 '--customer-name "e33ba30d-3718-4b15-bfaa-5627a57cda6f"',
                 checks=[])

        self.cmd('az account subscription create '
                 '--billing-account-name "0aa27f2b-ec7f-5a65-71f6-a5ff0897bd55:ae0dae1e-de9a-41f6-8257-76b055d98372_2019-05-31" '
                 '--billing-profile-name "27VR-HDWX-BG7-TGB" '
                 '--cost-center "135366376" '
                 '--display-name "Contoso MCA subscription" '
                 '--sku-id "0001" '
                 '--invoice-section-name "JGF7-NSBG-PJA-TGB"',
                 checks=[])

        self.cmd('az account subscription create-subscription-in-enrollment-account '
                 '--display-name "Test Ea Azure Sub" '
                 '--offer-type "MS-AZR-0017P" '
                 '--enrollment-account-name "73f8ab6e-cfa0-42be-b886-be6e77c2980c"',
                 checks=[])

        self.cmd('az account subscription create-csp-subscription '
                 '--billing-account-name "2bc54a6f-8d8a-5be1-5bff-bb4f285f512b:11a72812-d9a4-446e-9a1e-70c8bcadf5c0_2019-05-31" '
                 '--display-name "Contoso MCA subscription" '
                 '--sku-id "0001" '
                 '--customer-name "e33ba30d-3718-4b15-bfaa-5627a57cda6f"',
                 checks=[])

        self.cmd('az account subscription create '
                 '--billing-account-name "0aa27f2b-ec7f-5a65-71f6-a5ff0897bd55:ae0dae1e-de9a-41f6-8257-76b055d98372_2019-05-31" '
                 '--billing-profile-name "27VR-HDWX-BG7-TGB" '
                 '--cost-center "135366376" '
                 '--display-name "Contoso MCA subscription" '
                 '--sku-id "0001" '
                 '--invoice-section-name "JGF7-NSBG-PJA-TGB"',
                 checks=[])

        self.cmd('az account subscription create-subscription-in-enrollment-account '
                 '--display-name "Test Ea Azure Sub" '
                 '--offer-type "MS-AZR-0017P" '
                 '--enrollment-account-name "73f8ab6e-cfa0-42be-b886-be6e77c2980c"',
                 checks=[])

        self.cmd('az account subscription create-csp-subscription '
                 '--billing-account-name "2bc54a6f-8d8a-5be1-5bff-bb4f285f512b:11a72812-d9a4-446e-9a1e-70c8bcadf5c0_2019-05-31" '
                 '--display-name "Contoso MCA subscription" '
                 '--sku-id "0001" '
                 '--customer-name "e33ba30d-3718-4b15-bfaa-5627a57cda6f"',
                 checks=[])

        self.cmd('az account subscription enable',
                 checks=[])

        self.cmd('az account subscription cancel',
                 checks=[])

        self.cmd('az account subscription rename',
                 checks=[])

        self.cmd('az account subscription-operation show '
                 '--operation-id "e4b8d068-f574-462a-a76f-6fa0afc613c9"',
                 checks=[])

        self.cmd('az account operation list',
                 checks=[])
