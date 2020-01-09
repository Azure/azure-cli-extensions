# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure_devtools.scenario_tests import RecordingProcessor


def _py3_byte_to_str(byte_or_str):
    import logging
    logger = logging.getLogger()
    logger.warning(type(byte_or_str))
    try:
        return str(byte_or_str, 'utf-8') if isinstance(byte_or_str, bytes) else byte_or_str
    except TypeError:  # python 2 doesn't allow decoding through str
        return str(byte_or_str)


class PowerBIKeyReplacer(RecordingProcessor):
    """Replace the access token for service principal authentication in a response body."""

    KEY_REPLACEMENT = 'veryFakedPowerBIKey=='

    def __init__(self):
        self._activated = False
        self._candidates = []

    def reset(self):
        self._activated = False
        self._candidates = []

    def process_request(self, request):  # pylint: disable=no-self-use
        import re
        try:
            pattern = r"/providers/Microsoft\.PowerBI/workspaceCollections/[^/]+/listKeys$"
            if re.search(pattern, request.path, re.I):
                self._activated = True
            pattern = r"/providers/Microsoft\.PowerBI/workspaceCollections/[^/]+/regenerateKey$"
            if re.search(pattern, request.path, re.I):
                self._activated = True
        except AttributeError:
            pass
        for candidate in self._candidates:
            if request.body:
                body_string = _py3_byte_to_str(request.body)
                request.body = body_string.replace(candidate, self.KEY_REPLACEMENT)
        return request

    def process_response(self, response):
        if self._activated:
            import json
            try:
                body = json.loads(response['body']['string'])
                self._candidates.append(body['key1'])
                self._candidates.append(body['key2'])
                self._activated = False
            except (KeyError, ValueError, TypeError):
                pass
        for candidate in self._candidates:
            if response['body']['string']:
                body = response['body']['string']
                response['body']['string'] = _py3_byte_to_str(body)
                response['body']['string'] = response['body']['string'].replace(candidate, self.KEY_REPLACEMENT)
        return response
