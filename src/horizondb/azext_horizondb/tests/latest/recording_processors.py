# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import hashlib
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from azure.cli.testsdk.scenario_tests import RecordingProcessor


class ArmOperationResultsRecordingProcessor(RecordingProcessor):
    """Scrub opaque ARM operation identifiers and signed polling parameters."""

    @staticmethod
    def _scrub_uri(uri):
        parsed = urlsplit(uri)
        match = re.search(r'/(?:operationresults|azureasyncoperation)/([^/]+)', parsed.path, flags=re.IGNORECASE)
        if not match:
            return uri

        operation = match.group(1)
        if not operation.startswith('recorded-operation-'):
            digest = hashlib.sha256(operation.casefold().encode('utf-8')).hexdigest()[:16]
            operation = 'recorded-operation-' + digest
        path = parsed.path[:match.start(1)] + operation + parsed.path[match.end(1):]
        query = [(key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True)
                 if key.lower() not in {'c', 'h', 's', 't'}]
        return urlunsplit(parsed._replace(path=path, query=urlencode(query)))

    def process_request(self, request):
        request.uri = self._scrub_uri(request.uri)
        return request

    def process_response(self, response):
        for header in ['x-ms-operation-identifier', 'x-msedge-ref']:
            response['headers'].pop(header, None)
        for header in ['location', 'azure-asyncoperation', 'operation-location']:
            self.replace_header_fn(response, header, self._scrub_uri)
        return response
