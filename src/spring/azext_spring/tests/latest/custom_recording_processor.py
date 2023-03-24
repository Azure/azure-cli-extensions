# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import re
from azure.cli.testsdk.scenario_tests import RecordingProcessor
from azure.cli.testsdk.scenario_tests.utilities import is_text_payload


class RegexSingleValueReplacer(RecordingProcessor):
    def __init__(self, pattern, anchor, moniker):
        super(RegexSingleValueReplacer, self).__init__()
        self.pattern = pattern
        self.moniker = moniker
        self.anchor = anchor

    # pylint: disable=no-member
    def process_request(self, request):
        from urllib.parse import quote_plus
        if self.anchor in request.uri:
            request.uri = self.pattern.sub(self.moniker, request.uri)
        elif quote_plus(self.anchor) in request.uri:
            request.uri = request.uri.replace(quote_plus(self.anchor),
                                              quote_plus(self.moniker))

        if is_text_payload(request) and request.body:
            body = str(request.body, 'utf-8') if isinstance(request.body, bytes) else str(request.body)
            if self.anchor in body:
                request.body = self.pattern.sub(self.moniker, request.body)
        return request

    def process_response(self, response):
        if is_text_payload(response) and response['body']['string']:
            response['body']['string'] = self.pattern.sub(self.moniker, response['body']['string'])
        self.replace_header(response, 'location', self.anchor, self.moniker)
        self.replace_header(response, 'azure-asyncoperation', self.anchor, self.moniker)

        return response


class TestEndpointReplacer(RegexSingleValueReplacer):
    def __init__(self):
        super(TestEndpointReplacer, self).__init__(re.compile(f'(?<="primaryKey":")[^"]+|(?<="secondaryKey":")[^"]+|(?<="primaryTestEndpoint":")[^"]+|(?<="secondaryTestEndpoint":")[^"]+', re.IGNORECASE),
                                                   'primary', 'fake')