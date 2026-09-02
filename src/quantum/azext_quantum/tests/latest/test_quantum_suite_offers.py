# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from types import SimpleNamespace

from azure.cli.testsdk.scenario_tests import live_only
from azure.cli.testsdk import ScenarioTest

from ...commands import transform_suite_offers, transform_suite_offer_quotas, transform_targets
from ..._client_factory import base_url_v2
from ...operations.suite_offers import _merge_suite_offer_quotas
from ...vendored_sdks.azure_quantum_python._client.models import QuotaUsage, ProviderStatus
from ...vendored_sdks.azure_quantum_python._client._utils.model_base import _deserialize
from ...vendored_sdks.azure_quantum_python._client.operations._operations import (
    build_services_suite_offers_list_quota_usages_request,
    build_services_suite_offers_list_provider_status_request,
    ServicesSuiteOffersOperations,
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
                'scope': 'SubscriptionTarget',
                'targetId': 'ionq.qpu',
                'allocation': {'standardMinutesLifetime': 100, 'highMinutesLifetime': 50},
                'usage': {'standardMinutesLifetime': 40, 'highMinutesLifetime': 10},
            }
        ]

        table = transform_suite_offer_quotas(quotas)

        self.assertEqual(len(table), 1)
        row = table[0]
        self.assertEqual(list(row.keys()), [
            'Target', 'Std Allocated', 'Std Used', 'High Allocated', 'High Used'
        ])
        self.assertEqual(row['Target'], 'ionq.qpu')
        self.assertEqual(row['Std Allocated'], 100)
        self.assertEqual(row['Std Used'], 40)
        self.assertEqual(row['High Allocated'], 50)
        self.assertEqual(row['High Used'], 10)

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

    def test_build_suite_offers_list_provider_status_request(self):
        request = build_services_suite_offers_list_provider_status_request(
            subscription_id='00000000-0000-0000-0000-000000000000',
            provider_id='ionq',
        )
        self.assertEqual(request.method, 'GET')
        self.assertIn(
            '/subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Quantum/suiteOffers/ionq/providerStatus',
            request.url,
        )
        self.assertIn('api-version=2026-01-15-preview', request.url)

    def test_deserialize_provider_status_bare_array(self):
        data = [
            {
                'id': 'ionq',
                'currentAvailability': 'Available',
                'targets': [
                    {'id': 'ionq.qpu', 'currentAvailability': 'Available', 'averageQueueTime': 42},
                ],
            }
        ]

        providers = _deserialize(list[ProviderStatus], data)

        self.assertEqual(len(providers), 1)
        self.assertEqual(providers[0].id, 'ionq')
        self.assertEqual(providers[0].current_availability, 'Available')
        self.assertEqual(len(providers[0].targets), 1)
        self.assertEqual(providers[0].targets[0].id, 'ionq.qpu')
        self.assertEqual(providers[0].targets[0].average_queue_time, 42)

    def test_list_provider_status_wraps_single_object(self):
        # The service returns a single ProviderStatus object, not a paged envelope or array.
        single = {
            'id': 'ionq',
            'currentAvailability': 'Available',
            'targets': [
                {'id': 'ionq.qpu', 'currentAvailability': 'Available', 'averageQueueTime': 7},
            ],
        }
        http_response = SimpleNamespace(status_code=200, json=lambda: single)
        pipeline_response = SimpleNamespace(http_response=http_response)
        fake_client = SimpleNamespace(
            _pipeline=SimpleNamespace(run=lambda request, **kwargs: pipeline_response),
            format_url=lambda url, **kwargs: url,
        )
        fake_config = SimpleNamespace(api_version='2026-01-15-preview', endpoint='https://example')
        fake_serialize = SimpleNamespace(url=lambda name, value, kind, **kwargs: value)

        operations = ServicesSuiteOffersOperations(
            fake_client, fake_config, fake_serialize, object()
        )

        result = operations.list_provider_status(
            '00000000-0000-0000-0000-000000000000', 'ionq'
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 'ionq')
        self.assertEqual(result[0].current_availability, 'Available')
        self.assertEqual(result[0].targets[0].id, 'ionq.qpu')
        self.assertEqual(result[0].targets[0].average_queue_time, 7)

    def test_transform_targets_suite_offer_shape(self):
        providers = [
            {
                'id': 'ionq',
                'currentAvailability': 'Available',
                'targets': [
                    {'id': 'ionq.qpu', 'currentAvailability': 'Available', 'averageQueueTime': 42},
                ],
            }
        ]

        table = transform_targets(providers)

        self.assertEqual(len(table), 1)
        row = table[0]
        self.assertEqual(list(row.keys()), [
            'Provider', 'Target-id', 'Current Availability', 'Average Queue Time (seconds)'
        ])
        self.assertEqual(row['Provider'], 'ionq')
        self.assertEqual(row['Target-id'], 'ionq.qpu')
        self.assertEqual(row['Current Availability'], 'Available')
        self.assertEqual(row['Average Queue Time (seconds)'], 42)

    def test_merge_quotas_target_with_usage(self):
        offer = _offer(
            quotas=_allocation(standard=100, high=50),  # subscription-level allocation is ignored
            target_quotas=[_allocation(standard=30, high=15, target_id='ionq.qpu')],
        )
        usages = [
            _usage(target_id=None, standard=40, high=10),        # subscription-scope usage ignored
            _usage(target_id='ionq.qpu', standard=5, high=2),
        ]

        rows = _merge_suite_offer_quotas(offer, usages, 'ionq')

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(list(row.keys()), ['providerId', 'scope', 'targetId', 'allocation', 'usage'])
        self.assertEqual(row['providerId'], 'ionq')
        self.assertEqual(row['scope'], 'SubscriptionTarget')
        self.assertEqual(row['targetId'], 'ionq.qpu')
        self.assertEqual(row['allocation'], {'standardMinutesLifetime': 30, 'highMinutesLifetime': 15})
        self.assertEqual(row['usage'], {'standardMinutesLifetime': 5, 'highMinutesLifetime': 2})

    def test_merge_quotas_target_without_usage(self):
        offer = _offer(
            target_quotas=[_allocation(standard=30, high=None, target_id='ionq.qpu')],
        )

        rows = _merge_suite_offer_quotas(offer, [], 'ionq')

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row['allocation'], {'standardMinutesLifetime': 30, 'highMinutesLifetime': None})
        self.assertEqual(row['usage'], {'standardMinutesLifetime': None, 'highMinutesLifetime': None})

    def test_merge_quotas_ignores_subscription_and_unmatched_usage(self):
        offer = _offer(
            quotas=_allocation(standard=100, high=50),
            target_quotas=[_allocation(standard=30, high=15, target_id='ionq.qpu')],
        )
        usages = [
            _usage(target_id=None, standard=40, high=10),           # subscription scope -> ignored
            _usage(target_id='other.target', standard=7, high=3),   # no matching allocation -> ignored
        ]

        rows = _merge_suite_offer_quotas(offer, usages, 'ionq')

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['targetId'], 'ionq.qpu')
        self.assertEqual(rows[0]['usage'], {'standardMinutesLifetime': None, 'highMinutesLifetime': None})

    @live_only()
    def test_quantum_suite_offer_list(self):
        offers = self.cmd('az quantum suite-offer list').get_output_in_json()
        assert isinstance(offers, list)

    @live_only()
    def test_quantum_suite_offer_quotas(self):
        offers = self.cmd('az quantum suite-offer list').get_output_in_json()
        if not offers:
            self.skipTest('No suite offers available in the subscription.')

        provider_id = offers[0]['properties']['providerId']
        quotas = self.cmd(f'az quantum suite-offer quotas -p {provider_id}').get_output_in_json()

        assert isinstance(quotas, list)
        for row in quotas:
            self.assertEqual(set(row.keys()), {'providerId', 'scope', 'targetId', 'allocation', 'usage'})
            self.assertEqual(row['scope'], 'SubscriptionTarget')
            self.assertEqual(row['providerId'], provider_id)
            self.assertEqual(set(row['allocation'].keys()), {'standardMinutesLifetime', 'highMinutesLifetime'})
            self.assertEqual(set(row['usage'].keys()), {'standardMinutesLifetime', 'highMinutesLifetime'})

    @live_only()
    def test_quantum_suite_offer_target_list(self):
        offers = self.cmd('az quantum suite-offer list').get_output_in_json()
        if not offers:
            self.skipTest('No suite offers available in the subscription.')

        provider_id = offers[0]['properties']['providerId']
        providers = self.cmd(f'az quantum suite-offer target list -p {provider_id}').get_output_in_json()

        assert isinstance(providers, list)
        for provider in providers:
            self.assertIn('id', provider)
            self.assertIn('targets', provider)
            for target in provider['targets']:
                self.assertIn('id', target)
                self.assertIn('currentAvailability', target)
                self.assertIn('averageQueueTime', target)
