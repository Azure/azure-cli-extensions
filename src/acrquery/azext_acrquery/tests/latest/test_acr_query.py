# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest
from azure.cli.command_modules.acr._docker_utils import (
    EMPTY_GUID
)

REGISTRY_NAME = "metadataunittest"
RESOURCE_GROUP = "cabarker"
REPOSITORY_NAME = "nginx"


class AcrQueryTests(ScenarioTest):

    def test_acrquery(self):
        # Query with bearer auth and filter by count
        credentials = self.cmd(
            'acr credential show -n {} -g {}'.format(REGISTRY_NAME, RESOURCE_GROUP)).get_output_in_json()

        username = credentials['username']
        password = credentials['passwords'][0]['value']

        self.cmd(
            'acr query -n {} -q {} --username {} --password {} '.format(REGISTRY_NAME, '"Manifests | limit 1"', username, password),
            checks=[self.check('count', 1)])

        # Query with basic auth and filter by repository
        token = self.cmd('acr login -n {} --expose-token'.format(REGISTRY_NAME)).get_output_in_json()
        bearer = token["accessToken"]

        self.cmd(
            'acr query -n {} --repository {} -q {} --username {} --password {} '.format(REGISTRY_NAME, REPOSITORY_NAME, '"Manifests | limit 1"', EMPTY_GUID, bearer),
            checks=[self.check('count', 1)])

        # Renew credentials
        self.cmd(
            'acr credential renew -n {} --password-name {} '.format(REGISTRY_NAME, 'password'))

        # Filter by size
        manifests = self.cmd(
            'acr query -n {} -q {}'.format(REGISTRY_NAME, '"Manifests | where imageSize > 500"')).get_output_in_json()

        for manifest in manifests["data"]:
            assert manifest["size"] > 500
