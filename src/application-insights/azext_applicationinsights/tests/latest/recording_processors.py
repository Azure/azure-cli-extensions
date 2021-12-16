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


class StorageAccountSASReplacer(RecordingProcessor):
    SAS_REPLACEMENT = 'se=2020-10-27&sp=w&sv=2018-11-09&sr=c'

    def __init__(self):
        self._activated = False
        self._sas_tokens = []

    def reset(self):
        self._activated = False
        self._sas_tokens = []

    def add_sas_token(self, sas_token):
        self._sas_tokens.append(sas_token)

    def process_request(self, request):
        import re
        try:
            pattern = r"/providers/Microsoft\.Insights/components/[^/]+/exportconfiguration$"
            if re.search(pattern, request.path, re.I):
                self._activated = True
        except AttributeError:
            pass

        if self._activated and request.body:
            for sas_token in self._sas_tokens:
                body_string = _py3_byte_to_str(request.body)
                request.body = body_string.replace(sas_token, self.SAS_REPLACEMENT)
        return request
