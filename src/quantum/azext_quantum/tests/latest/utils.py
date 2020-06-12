# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

TEST_SUBS = "677fc922-91d0-4bf6-9b06-4274d319a0fa"
TEST_RG = 'aqua-provider-validator'
TEST_WORKSPACE = 'validator-workspace-westus'


def is_private_preview_subscription(scenario):
    """ Returns True if running in AzureQuantum-test """

    # Since azure quantum is still in private preview, we require
    # tests to run in a specific subscription (AzureQuantum-test)
    # this method checks if running in such subscription:
    account = scenario.cmd('az account show -o json').get_output_in_json()
    return account['id'] == TEST_SUBS
