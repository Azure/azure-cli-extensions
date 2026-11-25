# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re

from azure.cli.testsdk.scenario_tests import RecordingProcessor


_ARM_HOST = re.compile(r"https?://(?:armmanagement|management)\.autonomous\.cloud\.private", re.IGNORECASE)


class PrivateAuthRequestFilter(RecordingProcessor):

    def process_request(self, request):
        if "autonomous.cloud.private" in request.uri and "microsoft.edgeoperator" not in request.uri.lower():
            return None
        return request


class ArmEndpointNormalizer(RecordingProcessor):
    """Keep private-cloud recordings playable against the default CI cloud."""

    def process_request(self, request):
        request.uri = _ARM_HOST.sub("https://management.azure.com", request.uri)
        return request

    def process_response(self, response):
        for name, values in response.get("headers", {}).items():
            if name.lower() in ("azure-asyncoperation", "location"):
                response["headers"][name] = [
                    _ARM_HOST.sub("https://management.azure.com", value) for value in values
                ]
        body = response.get("body", {}).get("string")
        if body:
            is_bytes = isinstance(body, bytes)
            if is_bytes:
                body = body.decode("utf-8")
            body = _ARM_HOST.sub("https://management.azure.com", body)
            response["body"]["string"] = body.encode("utf-8") if is_bytes else body
        return response
