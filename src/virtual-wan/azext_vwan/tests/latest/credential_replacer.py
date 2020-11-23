# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re

from azure_devtools.scenario_tests import RecordingProcessor


class VpnClientGeneratedURLReplacer(RecordingProcessor):
    def __init__(self):
        # self.credential_url_pattern = r'https://nfvprodsuppbl\.blob\.core\.windows\.net/vpnprofileimmutable/(.*)/vpnprofile/(.*)/vpnclientconfiguration\.zip'  # pylint: disable=line-too-long
        self.credential_url_pattern = r'sig=(.*)&'

    def process_response(self, response):

        body = response['body']['string']

        m = re.search(self.credential_url_pattern, body, re.M)

        if 'profileUrl' in body and m is not None:
            for sub in m.groups():
                response['body']['string'] = body = body.replace(sub, '00000000-0000-0000-0000-000000000000')

        response['body']['string'] = body

        return response
