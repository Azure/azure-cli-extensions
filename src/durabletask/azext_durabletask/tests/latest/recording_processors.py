# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re

from azure.cli.testsdk.scenario_tests import RecordingProcessor


class IdentityRecordingProcessor(RecordingProcessor):
    """Remove account and managed-identity details from ARM recordings."""

    @staticmethod
    def _sanitize(value):
        value = re.sub(
            r'("(?:subscription|subscriptionId|tenantId|clientId|principalId|objectId|createdBy|updatedBy|'
            r'lastModifiedBy)"\s*:\s*")[^"]*(")',
            r'\g<1>00000000-0000-0000-0000-000000000000\2',
            value, flags=re.IGNORECASE)
        value = re.sub(
            r'("id"\s*:\s*")[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}(")',
            r'\g<1>00000000-0000-0000-0000-000000000000\2',
            value, flags=re.IGNORECASE)
        value = re.sub(
            r'((?:tenantId|objectId|clientId|principalId)(?:=|%3d))[0-9a-f-]{36}',
            r'\g<1>00000000-0000-0000-0000-000000000000',
            value, flags=re.IGNORECASE)
        value = re.sub(
            r'(https://(?:login\.microsoftonline\.com|login\.windows\.net|sts\.windows\.net)/)'
            r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',
            r'\g<1>00000000-0000-0000-0000-000000000000',
            value, flags=re.IGNORECASE)
        value = re.sub(r'([?&](?:c|s|h|t)=)[^&"\s]+', r'\g<1>redacted', value)
        return re.sub(
            r'[a-z0-9-]+\.([a-z0-9]+)\.durabletask\.io',
            r'scheduler.\1.durabletask.io', value, flags=re.IGNORECASE)

    def process_request(self, request):
        request.uri = re.sub(
            r'(/roleAssignments/)[0-9a-f-]{36}',
            r'\g<1>00000000-0000-0000-0000-000000000000',
            self._sanitize(request.uri), flags=re.IGNORECASE)
        if request.body:
            body = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
            request.body = self._sanitize(body).encode('utf-8')
        return request

    def process_response(self, response):
        body = response['body'].get('string')
        if body:
            text = body.decode('utf-8') if isinstance(body, bytes) else body
            sanitized = self._sanitize(text)
            response['body']['string'] = sanitized.encode('utf-8') if isinstance(body, bytes) else sanitized
        for header in list(response['headers']):
            if header.lower() in (
                'x-ms-client-object-id', 'x-ms-client-principal-id', 'x-ms-client-tenant-id',
                'x-ms-home-tenant-id',
            ):
                del response['headers'][header]
            else:
                response['headers'][header] = [
                    self._sanitize(value) for value in response['headers'][header]
                ]
        return response
