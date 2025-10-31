import unittest
from azure.cli.testsdk import *

class DatadogTermsTestScenario(ScenarioTest):
    test_options = {
        "subscription": "00000000-0000-0000-0000-000000000000",
        "rg": "bhanu-rg",
        "monitor": "datadogtestresource",
        "terms_name": "default"
    }

    @ResourceGroupPreparer(name_prefix='cli_test_datadog_terms', location='centraluseuap')
    def test_datadog_monitor_terms(self, resource_group):
        email = self.cmd('account show').get_output_in_json()['user']['name']
        self.kwargs.update({
            'monitor': self.test_options["monitor"],
            'rg': self.test_options["rg"],
            'email': email,
            'subscription': self.test_options["subscription"],
            'terms_name': self.test_options["terms_name"]
        })

        # Create terms
        self.cmd('datadog terms create --subscription {subscription} --accepted true', checks=[
            self.check('properties.accepted', True)
        ])

        # List terms
        self.cmd('datadog terms list --subscription {subscription}', checks=[
            self.check('[0].type', "Microsoft.Datadog/agreements")
        ])