# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import base64

from knack import log

logger = log.get_logger(__name__)


def format_relay_info_string(relay_info):
    relay_info_string = json.dumps(
        {
            "relay": {
                "namespaceName": relay_info['namespaceName'],
                "namespaceNameSuffix": relay_info['namespaceNameSuffix'],
                "hybridConnectionName": relay_info['hybridConnectionName'],
                "accessKey": relay_info['accessKey'],
                "expiresOn": relay_info['expiresOn'],
                "serviceConfigurationToken": relay_info['serviceConfigurationToken']
            }
        })
    result_bytes = relay_info_string.encode("ascii")
    enc = base64.b64encode(result_bytes)
    base64_result_string = enc.decode("ascii")
    return base64_result_string
