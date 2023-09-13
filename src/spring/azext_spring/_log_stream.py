# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


class LogStream:
    def __init__(self, client, resource_group, service):
        test_keys = client.services.list_test_keys(resource_group, service)
        self.primary_key = test_keys.primary_key

        resource = client.services.get(resource_group, service)
        self.base_url = resource.properties.fqdn
