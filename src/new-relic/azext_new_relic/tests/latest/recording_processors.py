# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re

from azure.cli.testsdk.scenario_tests import RecordingProcessor
from azure.cli.testsdk.scenario_tests.utilities import is_text_payload


MOCK_INGESTION_KEY = "fake-ingestion-key"
_INGESTION_KEY_RE = re.compile(
    r'("ingestionKey"\s*:\s*")[^"]+(")',
    re.IGNORECASE,
)


class NewRelicSecretScrubber(RecordingProcessor):

    def process_request(self, request):
        return self._scrub(request)

    def process_response(self, response):
        return self._scrub(response)

    @staticmethod
    def _scrub(entity):
        body = entity.get("body")
        if not isinstance(body, dict):
            return entity

        if is_text_payload(entity) and body.get("string"):
            entity["body"]["string"] = _INGESTION_KEY_RE.sub(
                rf"\g<1>{MOCK_INGESTION_KEY}\g<2>",
                entity["body"]["string"],
            )
        return entity
