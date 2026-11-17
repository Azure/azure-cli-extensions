# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest
from azure.core.exceptions import HttpResponseError


class AiinfraoptimizationScenario(ScenarioTest):

    def __init__(self, method_name, *args, **kwargs):
        super().__init__(method_name, *args, **kwargs)
        # Playback only matches the HTTP method, URL and query by default, so also match the serialized request body.
        self.vcr.match_on = (*self.vcr.match_on, 'body')

    def test_aiinfraoptimization_recommendvmsku(self):
        # Mirrors the documented command example, which sets every argument.
        self.kwargs.update({
            'location': 'eastus2',
            'model': '{hugging-face-model-id:meta-llama/Llama-3.1-70B-Instruct,parameter-count:70553706496,'
                     'weight-precision:FP16,num-layers:80,num-key-value-heads:8,head-dim:128,'
                     'max-context-length:131072}',
            'workload': '{max-concurrent-requests-per-replica:1,'
                        'token-budget:{prompt-tokens:8000,max-output-tokens:1024}}',
            'deployment': '{replica-count:1,procurement-option:OnDemand}',
            'optimization': '{ranking-preference:Cost,max-deployment-cost-per-hour:{amount:50,currency-code:USD}}',
            'target_vm_sizes': '[Standard_NC48ads_A100_v4,Standard_ND96asr_v4]',
            'subscription_options': '{include-quota:True,include-placement:True,include-pricing:True}',
        })

        self.cmd('aiinfraoptimization recommendvmsku --location {location} --model "{model}" '
                 '--workload "{workload}" --deployment "{deployment}" --optimization "{optimization}" '
                 '--target-vm-sizes "{target_vm_sizes}" --subscription-options "{subscription_options}"',
                 checks=[
                     self.check('sizing.model.huggingFaceModelId', 'meta-llama/Llama-3.1-70B-Instruct'),
                     self.check('sizing.model.parameterCount', 70553706496),
                     self.check('sizing.model.weightPrecision', 'FP16'),
                     self.check('sizing.workload.maxConcurrentRequestsPerReplica', 1),
                     self.check('sizing.workload.contextLength', 9024),
                     self.greater_than('length(options)', 0),
                     self.check('options[0].recommendationRank', 1),
                     self.check("length(options[?vmSize != 'Standard_NC48ads_A100_v4' && "
                                "vmSize != 'Standard_ND96asr_v4'])", 0),
                     self.check("length(options[?cost.currencyCode != 'USD'])", 0),
                     # Quota and placement are evaluated for every option when requested.
                     self.check('length(options[?!quota || !placement])', 0),
                 ])

    def test_aiinfraoptimization_recommendvmsku_boundary_values(self):
        # Covers the alternate enum values and the 0 and False boundaries, for a model without a Hugging Face ID.
        self.kwargs.update({
            'location': 'eastus2',
            'model': '{parameter-count:8000000000,weight-precision:BF16,'
                     'num-layers:32,num-key-value-heads:8,head-dim:128}',
            'workload': '{max-concurrent-requests-per-replica:4,'
                        'token-budget:{prompt-tokens:4096,max-output-tokens:0}}',
            'deployment': '{replica-count:2,procurement-option:Spot}',
            'optimization': '{ranking-preference:Latency}',
            'target_vm_sizes': '[Standard_NC24ads_A100_v4,Standard_NC40ads_H100_v5]',
            'subscription_options': '{include-quota:False,include-placement:False,include-pricing:False}',
        })

        self.cmd('aiinfraoptimization recommendvmsku --location {location} --model "{model}" '
                 '--workload "{workload}" --deployment "{deployment}" --optimization "{optimization}" '
                 '--target-vm-sizes "{target_vm_sizes}" --subscription-options "{subscription_options}"',
                 checks=[
                     self.check('sizing.model.huggingFaceModelId', None),
                     self.check('sizing.model.parameterCount', 8000000000),
                     self.check('sizing.model.weightPrecision', 'BF16'),
                     self.check('sizing.workload.maxConcurrentRequestsPerReplica', 4),
                     self.check('sizing.workload.contextLength', 4096),
                     self.greater_than('length(options)', 0),
                     self.check("length(options[?vmSize != 'Standard_NC24ads_A100_v4' && "
                                "vmSize != 'Standard_NC40ads_H100_v5'])", 0),
                     # Disabled subscription lookups skip quota and placement and fall back to retail pricing.
                     self.check('length(options[?quota || placement])', 0),
                     self.check("length(options[?cost.source != 'AzureRetail'])", 0),
                 ])

    def test_aiinfraoptimization_recommendvmsku_service_error(self):
        # The service reads Hugging Face anonymously, so it can't size a gated model without its architecture fields.
        self.kwargs.update({
            'location': 'eastus2',
            'model': '{hugging-face-model-id:meta-llama/Llama-3.1-8B-Instruct}',
        })

        with self.assertRaisesRegex(HttpResponseError, 'is gated on HuggingFace') as cm:
            self.cmd('aiinfraoptimization recommendvmsku --location {location} --model "{model}"')
        self.assertEqual(cm.exception.status_code, 400)
        self.assertEqual(cm.exception.error.code, 'InvalidArgument')
        self.assertEqual(cm.exception.error.target, 'model')
