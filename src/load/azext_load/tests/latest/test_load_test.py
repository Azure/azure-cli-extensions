from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer, KeyVaultPreparer, JMESPathCheck


class LoadScenario(ScenarioTest):
    
    def testcase_load_test_list(self):
        self.kwargs.update({
            'load-test-resource': "hbisht-cli-testing",
            'resource-group': "hbisht-rg"
        })
        self.cmd('az load test list --load-test-resource {load-test-resource} '
                 '--resource-group {resource-group} '
                 )
        