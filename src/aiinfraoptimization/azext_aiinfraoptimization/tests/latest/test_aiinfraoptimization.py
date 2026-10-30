# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
from types import SimpleNamespace
from unittest import mock
from urllib.parse import parse_qs, urlsplit

from azure.cli.core.aaz._client import AAZMgmtClient
from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.patches import patch_load_cached_subscriptions
from azure.core.pipeline.policies import ContentDecodePolicy


SUBSCRIPTION_ID = '00000000-0000-0000-0000-000000000000'

# The request and response mirror the Recommendations_RecommendVmSku example in the
# Microsoft.AIInfraOptimization 2026-06-01-preview REST API specification.
RECOMMEND_VM_SKU_REQUEST = {
    'model': {
        'huggingFaceModelId': 'meta-llama/Llama-3.1-70B-Instruct',
        'parameterCount': 70000000000,
        'weightPrecision': 'FP16',
        'numLayers': 80,
        'numKeyValueHeads': 8,
        'headDim': 128,
        'maxContextLength': 131072,
    },
    'workload': {
        'maxConcurrentRequestsPerReplica': 1,
        'tokenBudget': {'promptTokens': 8000, 'maxOutputTokens': 1024},
    },
    'deployment': {'replicaCount': 1, 'procurementOption': 'OnDemand'},
    'optimization': {
        'rankingPreference': 'Cost',
        'maxDeploymentCostPerHour': {'amount': 50, 'currencyCode': 'USD'},
    },
    'targetVmSizes': ['Standard_NC48ads_A100_v4', 'Standard_ND96asr_v4'],
    'subscriptionOptions': {'includeQuota': True, 'includePlacement': True, 'includePricing': True},
}

RECOMMEND_VM_SKU_RESPONSE = {
    'options': [
        {
            'vmSize': 'Standard_NC48ads_A100_v4',
            'recommendationRank': 1,
            'readiness': {
                'status': 'ReadyToAttempt',
                'reason': 'Quota is available for the requested replica count in eastus2.',
            },
            'topology': {
                'estimatedNodeCountPerReplica': 1,
                'estimatedTotalNodeCount': 1,
                'accelerator': {'model': 'A100', 'countPerVm': 2, 'memoryGiBPerAccelerator': 80},
            },
            'cost': {
                'currencyCode': 'USD',
                'vmHourly': 7.35,
                'deploymentHourly': 7.35,
                'source': 'AzureSubscription',
                'priceAsOf': '2026-08-27T00:00:00Z',
            },
            'quota': {
                'status': 'Available',
                'reason': 'The subscription has sufficient quota for 1 replica.',
                'maxAvailableReplicaCount': 4,
            },
            'placement': {'status': 'Evaluated', 'recommendedAvailabilityZones': ['1', '3']},
            'azureMlRecommended': True,
            'benchmark': {
                'level': 'TopologyMatched',
                'modelClass': '70b',
                'scenario': 'Server',
                'submitterCount': 3,
                'submissionId': '3.1-0093',
                'benchmarkModel': 'llama2-70b',
                'submitter': 'Contoso',
                'system': '2xA100-SXM-80GB',
                'throughput': 2140.5,
                'throughputUnit': 'Tokens/s',
                'software': 'vLLM 0.6.2',
                'operatingSystem': 'Ubuntu 22.04',
                'weightDataTypes': 'float16',
                'p99TtftMs': 385.2,
                'p99TpotMs': 42.7,
            },
            'documentationUrl': 'https://learn.microsoft.com/azure/virtual-machines/nc-a100-v4-series',
        },
        {
            'vmSize': 'Standard_ND96asr_v4',
            'recommendationRank': 2,
            'readiness': {
                'status': 'QuotaIncreaseRequired',
                'reason': 'The subscription must raise its quota before this size can be deployed.',
            },
            'topology': {
                'estimatedNodeCountPerReplica': 1,
                'estimatedTotalNodeCount': 1,
                'accelerator': {'model': 'A100', 'countPerVm': 8, 'memoryGiBPerAccelerator': 40},
            },
            'cost': {
                'currencyCode': 'USD',
                'vmHourly': 27.2,
                'deploymentHourly': 27.2,
                'source': 'AzureRetail',
                'priceAsOf': '2026-08-26T00:00:00Z',
                'error': {
                    'code': 'DataUnavailable',
                    'message': 'Subscription-scoped pricing was unavailable, so retail pricing was used.',
                },
            },
            'quota': {
                'status': 'Unavailable',
                'reason': 'The subscription has 0 of the 96 cores required in eastus2.',
                'maxAvailableReplicaCount': 0,
                'increase': {
                    'limits': [{
                        'name': 'standardNDASv4_A100Family',
                        'currentUsage': 0,
                        'currentLimit': 0,
                        'requiredLimit': 96,
                    }],
                    'portalUrl': 'https://portal.azure.com/#view/Microsoft_Azure_Support/NewSupportRequestV3Blade',
                },
            },
            'placement': {
                'status': 'NotEvaluated',
                'reason': 'Placement is queried only for sizes with available quota.',
            },
            'azureMlRecommended': False,
            'benchmark': {'level': 'Benchmarked', 'modelClass': '70b', 'scenario': 'Server', 'submitterCount': 1},
            'documentationUrl': 'https://learn.microsoft.com/azure/virtual-machines/nda100-v4-series',
        },
    ],
    'sizing': {
        'model': {
            'parameterCount': 70000000000,
            'weightPrecision': 'FP16',
            'huggingFaceModelId': 'meta-llama/Llama-3.1-70B-Instruct',
        },
        'workload': {'maxConcurrentRequestsPerReplica': 1, 'contextLength': 9024},
        'memory': {
            'modelWeightsGiB': 130.39,
            'kvCacheGiBPerRequest': 2.75,
            'kvCacheGiBTotal': 2.75,
            'modelAndKvCacheGiB': 133.14,
        },
        'basis': {
            'parameterCountSource': 'Request',
            'modelWeightsCalculation': 'EstimatedFromParameterCount',
            'contextLengthSource': 'Request',
        },
    },
}


class AiinfraoptimizationScenario(ScenarioTest):
    """Runs commands end to end through the CLI with only the HTTP send mocked, so no login or network is needed."""

    def setUp(self):
        super().setUp()
        patch_load_cached_subscriptions(self)
        for patcher in (
            mock.patch.object(AAZCommandCtx, 'get_login_credential', return_value=mock.Mock()),
            # Fail fast, instead of calling the live service or recording a cassette, if a request escapes the mocks.
            mock.patch('requests.sessions.Session.request', side_effect=AssertionError('Unexpected network request')),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    @staticmethod
    def _mock_response(status_code, body):
        # Mirrors the pipeline response that generated AAZ operations read the status code and JSON body from.
        return SimpleNamespace(
            http_response=SimpleNamespace(status_code=status_code),
            context={ContentDecodePolicy.CONTEXT_NAME: copy.deepcopy(body)},
        )

    def test_aiinfraoptimization_recommendvmsku(self):
        self.kwargs.update({
            'subscription': SUBSCRIPTION_ID,
            'location': 'eastus2',
            'model': '{hugging-face-model-id:meta-llama/Llama-3.1-70B-Instruct,parameter-count:70000000000,'
                     'weight-precision:FP16,num-layers:80,num-key-value-heads:8,head-dim:128,'
                     'max-context-length:131072}',
            'workload': '{max-concurrent-requests-per-replica:1,'
                        'token-budget:{prompt-tokens:8000,max-output-tokens:1024}}',
            'deployment': '{replica-count:1,procurement-option:OnDemand}',
            'optimization': '{ranking-preference:Cost,max-deployment-cost-per-hour:{amount:50,currency-code:USD}}',
            'target_vm_sizes': '[Standard_NC48ads_A100_v4,Standard_ND96asr_v4]',
            'subscription_options': '{include-quota:True,include-placement:True,include-pricing:True}',
        })

        with mock.patch.object(AAZMgmtClient, 'send_request',
                               return_value=self._mock_response(200, RECOMMEND_VM_SKU_RESPONSE)) as send_request:
            result = self.cmd(
                'aiinfraoptimization recommendvmsku --subscription {subscription} --location {location} '
                '--model "{model}" --workload "{workload}" --deployment "{deployment}" '
                '--optimization "{optimization}" --target-vm-sizes "{target_vm_sizes}" '
                '--subscription-options "{subscription_options}"',
                checks=[
                    self.check('length(options)', 2),
                    self.check('options[0].vmSize', 'Standard_NC48ads_A100_v4'),
                    self.check('options[0].recommendationRank', 1),
                    self.check('options[0].readiness.status', 'ReadyToAttempt'),
                    self.check('options[0].topology.accelerator.countPerVm', 2),
                    self.check('options[0].cost.deploymentHourly', 7.35),
                    self.check('options[0].placement.recommendedAvailabilityZones', ['1', '3']),
                    self.check('options[1].cost.error.code', 'DataUnavailable'),
                    self.check('options[1].quota.increase.limits[0].requiredLimit', 96),
                    self.check('sizing.memory.modelAndKvCacheGiB', 133.14),
                    self.check('sizing.basis.modelWeightsCalculation', 'EstimatedFromParameterCount'),
                ])
        # Comparing the full output catches response-schema regressions that would silently drop fields.
        self.assertEqual(result.get_output_in_json(), RECOMMEND_VM_SKU_RESPONSE)

        send_request.assert_called_once()
        request = send_request.call_args.kwargs['request']
        url = urlsplit(request.url)
        self.assertEqual(request.method, 'POST')
        self.assertEqual(
            url.path,
            f'/subscriptions/{SUBSCRIPTION_ID}/providers/Microsoft.AIInfraOptimization'
            '/locations/eastus2/recommendVmSku')
        self.assertEqual(parse_qs(url.query), {'api-version': ['2026-06-01-preview']})
        self.assertEqual(json.loads(request.body), RECOMMEND_VM_SKU_REQUEST)
