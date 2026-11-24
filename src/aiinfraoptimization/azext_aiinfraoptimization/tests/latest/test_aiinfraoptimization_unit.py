# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest
from types import SimpleNamespace
from unittest import mock

from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.mock import DummyCli
from azure.core import PipelineClient
from azure.core.pipeline.policies import ContentDecodePolicy

from azext_aiinfraoptimization.aaz.latest.aiinfraoptimization import Recommendvmsku


class RecommendvmskuTokenBudgetTest(unittest.TestCase):
    # Checks the CLI's own token budget limits with the HTTP call stubbed, so it needs no recording.

    @staticmethod
    def _send(prompt_tokens, max_output_tokens):
        client = PipelineClient(base_url='https://management.azure.com')
        session = SimpleNamespace(http_response=SimpleNamespace(status_code=200),
                                  context={ContentDecodePolicy.CONTEXT_NAME: {}})
        with mock.patch.object(AAZCommandCtx, 'get_http_client', return_value=client), \
                mock.patch.object(client, 'send_request', return_value=session) as send_request:
            Recommendvmsku(cli_ctx=DummyCli())({
                'subscription': '00000000-0000-0000-0000-000000000000',
                'location': 'eastus2',
                'workload': {'token_budget': {'prompt_tokens': prompt_tokens,
                                              'max_output_tokens': max_output_tokens}},
            })
        return json.loads(send_request.call_args.kwargs['request'].body)

    def test_accepts_maximum_token_budget(self):
        for prompt_tokens, max_output_tokens in ((2147483647, 0), (0, 2147483647)):
            with self.subTest(prompt_tokens=prompt_tokens, max_output_tokens=max_output_tokens):
                self.assertEqual(self._send(prompt_tokens, max_output_tokens)['workload']['tokenBudget'],
                                 {'promptTokens': prompt_tokens, 'maxOutputTokens': max_output_tokens})

    def test_rejects_token_budget_above_maximum(self):
        for option, prompt_tokens, max_output_tokens in (('prompt-tokens', 2147483648, 0),
                                                         ('max-output-tokens', 0, 2147483648)):
            with self.subTest(option=option):
                with self.assertRaisesRegex(InvalidArgumentValueError,
                                            f"{option}: Invalid format: '2147483648' is greater than 2147483647"):
                    self._send(prompt_tokens, max_output_tokens)
