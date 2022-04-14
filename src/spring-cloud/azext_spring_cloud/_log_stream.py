# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re


class LogStream:
    def __init__(self, client, resource_group, service):
        test_keys = client.services.list_test_keys(resource_group, service)
        self.primary_key = test_keys.primary_key
        # https://primary:xxxx[key]@servicename.test.azuremicrosoervice.io -> servicename.azuremicroservice.io
        test_url = test_keys.primary_test_endpoint
        base_url = test_url.replace('.test.', '.')
        self.base_url = re.sub('https://.+?\@', '', base_url)
