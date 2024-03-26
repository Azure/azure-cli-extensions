# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import *
from azure.core.exceptions import HttpResponseError

@record_only()
class MdpScenario(ScenarioTest):

    def __init__(self, *args, **kwargs):
        super(MdpScenario, self).__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "subscriptionId": self.get_subscription_id(),
                "location": "eastus2",
            }
        )

    @ResourceGroupPreparer(
        name_prefix="clitest_mdp", key="rg", parameter_name="rg"
    )
    def test_mdp_scenario(self):
        self.kwargs.update(
            {
                "poolName": self.create_random_name(prefix="cli", length=24),
                "identityName": self.create_random_name(prefix="testid_", length=24),
            }
        )

        self.cmd(
            "az mdp pool list " '--resource-group "{rg}" ',
            checks=[
                self.check("length(@)", 0),
            ],
        )

        # Add more


    @ResourceGroupPreparer(
        name_prefix="clitest_mdp", key="rg", parameter_name="rg"
    )
    def test_mdp_create_error_scenario(self):
        self.kwargs.update(
            {
                "poolName": self.create_random_name(prefix="cli", length=24),
                "identityName": self.create_random_name(prefix="testid_", length=24),
            }
        )

        with self.assertRaises(HttpResponseError) as raises:
            self.cmd(
                "az mdp pool create "
                '--name "{poolName}" '
                '--location "{location}" '
                '--resource-group "{rg}"',
            ).get_output_in_json()

        assert 'Bad Request' in str(raises.exception.reason)
        assert raises.exception.status_code == 400
        assert 'ResourceCreationValidateFailed' in str(raises.exception)
