# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk.scenario_tests import live_only
from azure.cli.testsdk import ScenarioTest

from ...commands import transform_suite_offers


class QuantumSuiteOffersScenarioTest(ScenarioTest):

    def test_transform_suite_offers(self):
        suite_offers = [
            {
                'id': '/subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Quantum/suiteOffers/ionq',
                'name': 'ionq',
                'properties': {
                    'providerId': 'ionq',
                    'providerName': 'IonQ',
                    'companyName': 'IonQ, Inc.',
                    'location': 'eastus',
                    'description': 'IonQ quantum computing offer.'
                }
            }
        ]

        table = transform_suite_offers(suite_offers)

        self.assertEqual(len(table), 1)
        row = table[0]
        self.assertEqual(list(row.keys()), ['Provider ID', 'Provider Name', 'Company', 'Location'])
        self.assertEqual(row['Provider ID'], 'ionq')
        self.assertEqual(row['Provider Name'], 'IonQ')
        self.assertEqual(row['Company'], 'IonQ, Inc.')
        self.assertEqual(row['Location'], 'eastus')

    @live_only()
    def test_quantum_suite_offer_list(self):
        offers = self.cmd('az quantum suite-offer list').get_output_in_json()
        assert isinstance(offers, list)
