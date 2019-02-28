# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer

# No tidy up of tests required. The resource group is automatically removed


class AzureNetAppFilesExtAccountServiceScenarioTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_tests_rg')
    def test_ext_create_delete_account(self):
        account_name = self.create_random_name(prefix='cli', length=24)
        tags = 'Tag1=Value1 Tag2=Value2'

        # create and check
        account = self.cmd("az anf account create --resource-group {rg} --account-name '%s' -l 'westus2' --tags '%s'" % (account_name, tags)).get_output_in_json()
        assert account['name'] == account_name
        assert account['tags']['Tag1'] == 'Value1'
        assert account['tags']['Tag2'] == 'Value2'

        account_list = self.cmd("anf account list --resource-group {rg}").get_output_in_json()
        assert len(account_list) > 0

        # delete and recheck
        self.cmd("az anf account delete --resource-group {rg} --account-name '%s'" % account_name)
        account_list = self.cmd("anf account list --resource-group {rg}").get_output_in_json()
        assert len(account_list) == 0

        # and again with short forms and also unquoted
        account = self.cmd("az anf account create -g {rg} -a %s -l westus2 --tags '%s'" % (account_name, tags)).get_output_in_json()
        assert account['name'] == account_name
        account_list = self.cmd("anf account list --resource-group {rg}").get_output_in_json()
        assert len(account_list) > 0

        self.cmd("az anf account delete --resource-group {rg} -a %s" % account_name)
        account_list = self.cmd("anf account list --resource-group {rg}").get_output_in_json()
        assert len(account_list) == 0

    @ResourceGroupPreparer(name_prefix='cli_tests_rg')
    def test_ext_list_accounts_ext(self):
        accounts = [self.create_random_name(prefix='cli', length=24), self.create_random_name(prefix='cli', length=24)]

        for account_name in accounts:
            self.cmd("az anf account create -g {rg} -a %s -l 'westus2' --tags 'Tag1=Value1'" % account_name).get_output_in_json()

        account_list = self.cmd("anf account list -g {rg}").get_output_in_json()
        assert len(account_list) == 2

        for account_name in accounts:
            self.cmd("az anf account delete -g {rg} -a %s" % account_name)

        account_list = self.cmd("anf account list --resource-group {rg}").get_output_in_json()
        assert len(account_list) == 0

    @ResourceGroupPreparer(name_prefix='cli_tests_rg')
    def test_ext_get_account_by_name_ext(self):
        account_name = self.create_random_name(prefix='cli', length=24)
        account = self.cmd("az anf account create -g {rg} -a %s -l 'westus2'" % account_name).get_output_in_json()
        account = self.cmd("az anf account show --resource-group {rg} -a %s" % account_name).get_output_in_json()
        assert account['name'] == account_name
        account_from_id = self.cmd("az anf account show --ids %s" % account['id']).get_output_in_json()
        assert account_from_id['name'] == account_name

    @ResourceGroupPreparer(name_prefix='cli_tests_rg')
    def test_ext_update_account_ext(self):
        account_name = self.create_random_name(prefix='cli', length=24)
        tag = "Tag1=Value1"

        account = self.cmd("az anf account create -g {rg} -a %s -l 'westus2'" % account_name).get_output_in_json()
        account = self.cmd("az anf account update --resource-group {rg} -a %s --tags %s" % (account_name, tag)).get_output_in_json()
        assert account['name'] == account_name
        assert account['tags']['Tag1'] == 'Value1'
