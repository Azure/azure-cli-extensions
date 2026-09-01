# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from types import SimpleNamespace

from azure.cli.testsdk.scenario_tests import live_only
from azure.cli.testsdk import ScenarioTest

from ...commands import transform_suite_offers, transform_suite_offer_quotas
from ..._client_factory import base_url_v2
from ...operations.suite_offers import _merge_suite_offer_quotas
from ...vendored_sdks.azure_quantum_python._client.models import QuotaUsage
from ...vendored_sdks.azure_quantum_python._client._utils.model_base import _deserialize
from ...vendored_sdks.azure_quantum_python._client.operations._operations import (
    build_services_suite_offers_list_quota_usages_request,
)


def _allocation(standard=None, high=None, target_id=None):
    ns = SimpleNamespace(standard_minutes_lifetime=standard, high_minutes_lifetime=high)
    if target_id is not None:
        ns.target_id = target_id
    return ns


def _offer(provider_id='ionq', location='eastus', quotas=None, target_quotas=None):
    properties = SimpleNamespace(
        provider_id=provider_id,
        location=location,
        quotas=quotas,
        target_quotas=target_quotas or [],
    )
    return SimpleNamespace(properties=properties)


def _usage(target_id=None, standard=None, high=None, last_modified_time=None):
    return SimpleNamespace(
        target_id=target_id,
        usage=SimpleNamespace(standard_minutes_lifetime=standard, high_minutes_lifetime=high),
        last_modified_time=last_modified_time,
    )


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

    def test_transform_suite_offer_quotas(self):
        quotas = [
            {
                'providerId': 'ionq',
                'scope': 'Subscription',
                'standardMinutesLifetime': {'allocated': 100, 'used': 40, 'remaining': 60},
                'highMinutesLifetime': {'allocated': 50, 'used': 10, 'remaining': 40},
            }
        ]

        table = transform_suite_offer_quotas(quotas)

        self.assertEqual(len(table), 1)
        row = table[0]
        self.assertEqual(list(row.keys()), [
            'Scope', 'Target', 'Std Allocated', 'Std Used', 'Std Remaining',
            'High Allocated', 'High Used', 'High Remaining'
        ])
        self.assertEqual(row['Scope'], 'Subscription')
        self.assertEqual(row['Target'], '')
        self.assertEqual(row['Std Allocated'], 100)
        self.assertEqual(row['Std Used'], 40)
        self.assertEqual(row['Std Remaining'], 60)
        self.assertEqual(row['High Allocated'], 50)

    def test_base_url_v2(self):
        self.assertEqual(base_url_v2('East US'), 'https://eastus-v2.quantum.azure.com/')

    def test_build_suite_offers_list_quota_usages_request(self):
        request = build_services_suite_offers_list_quota_usages_request(
            subscription_id='00000000-0000-0000-0000-000000000000',
            provider_id='ionq',
        )
        self.assertEqual(request.method, 'GET')
        self.assertIn(
            '/subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Quantum/suiteOffers/ionq/quotaUsages',
            request.url,
        )
        self.assertIn('api-version=2026-01-15-preview', request.url)

    def test_deserialize_quota_usages_bare_array(self):
        data = [
            {
                'id': 'usage-1',
                'providerId': 'ionq',
                'scope': 'Subscription',
                'usage': {'standardMinutesLifetime': 40.0, 'highMinutesLifetime': 10.0},
                'lastModifiedTime': '2026-01-15T00:00:00Z',
            },
            {
                'id': 'usage-2',
                'providerId': 'ionq',
                'scope': 'SubscriptionTarget',
                'targetId': 'ionq.qpu',
                'usage': {'standardMinutesLifetime': 5.0, 'highMinutesLifetime': 1.0},
            },
        ]

        usages = _deserialize(list[QuotaUsage], data)

        self.assertEqual(len(usages), 2)
        self.assertEqual(usages[0].scope, 'Subscription')
        self.assertIsNone(usages[0].target_id)
        self.assertEqual(usages[0].usage.standard_minutes_lifetime, 40.0)
        self.assertEqual(usages[1].scope, 'SubscriptionTarget')
        self.assertEqual(usages[1].target_id, 'ionq.qpu')

    def test_merge_quotas_allocation_and_usage(self):
        offer = _offer(
            quotas=_allocation(standard=100, high=50),
            target_quotas=[_allocation(standard=30, high=None, target_id='ionq.qpu')],
        )
        usages = [
            _usage(target_id=None, standard=40, high=10),
            _usage(target_id='ionq.qpu', standard=5),
        ]

        rows = _merge_suite_offer_quotas(offer, usages, 'ionq')

        self.assertEqual(len(rows), 2)
        sub = rows[0]
        self.assertEqual(sub['scope'], 'Subscription')
        self.assertNotIn('targetId', sub)
        self.assertEqual(sub['standardMinutesLifetime'], {'allocated': 100, 'used': 40, 'remaining': 60})
        self.assertEqual(sub['highMinutesLifetime'], {'allocated': 50, 'used': 10, 'remaining': 40})

        target = rows[1]
        self.assertEqual(target['scope'], 'SubscriptionTarget')
        self.assertEqual(target['targetId'], 'ionq.qpu')
        self.assertEqual(target['standardMinutesLifetime'], {'allocated': 30, 'used': 5, 'remaining': 25})
        # High allocation absent, high usage absent -> omitted entirely.
        self.assertNotIn('highMinutesLifetime', target)

    def test_merge_quotas_allocation_only(self):
        offer = _offer(quotas=_allocation(standard=100, high=50))

        rows = _merge_suite_offer_quotas(offer, [], 'ionq')

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['standardMinutesLifetime'], {'allocated': 100, 'used': None, 'remaining': None})
        self.assertNotIn('lastModifiedTime', rows[0])

    def test_merge_quotas_usage_only(self):
        offer = _offer(quotas=None)
        usages = [_usage(target_id=None, standard=40, high=10, last_modified_time='2026-01-15T00:00:00Z')]

        rows = _merge_suite_offer_quotas(offer, usages, 'ionq')

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['standardMinutesLifetime'], {'allocated': None, 'used': 40, 'remaining': None})
        self.assertEqual(rows[0]['lastModifiedTime'], '2026-01-15T00:00:00Z')

    @live_only()
    def test_quantum_suite_offer_list(self):
        offers = self.cmd('az quantum suite-offer list').get_output_in_json()
        assert isinstance(offers, list)
