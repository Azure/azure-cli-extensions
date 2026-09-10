# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from .recording_processors import MOCK_INGESTION_KEY, NewRelicSecretScrubber


def test_new_relic_secret_scrubber():
    processor = NewRelicSecretScrubber()
    expected = f'{{"ingestionKey":"{MOCK_INGESTION_KEY}"}}'

    for process in (processor.process_request, processor.process_response):
        entity = {
            "headers": {"content-type": ["application/json"]},
            "body": {"string": '{"ingestionKey":"live-key-value"}'},
        }

        scrubbed = process(entity)

        assert scrubbed["body"]["string"] == expected


def test_new_relic_secret_scrubber_ignores_unsupported_body():
    processor = NewRelicSecretScrubber()

    for process in (processor.process_request, processor.process_response):
        for entity in (
            {"headers": {}},
            {"headers": {}, "body": None},
            {"headers": {}, "body": "not-a-dictionary"},
        ):
            assert process(entity) == entity
