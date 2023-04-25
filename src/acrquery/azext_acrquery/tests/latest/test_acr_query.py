# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest
from azure.cli.command_modules.acr._docker_utils import (
    EMPTY_GUID
)


class AcrQueryTests(ScenarioTest):

    def test_acrquery(self):
        self.kwargs.update({
            'registry_name': 'metadataunittest',
            'resource_group': 'cabarker',
            'repository_name': 'nginx',
            'password': 'password'
        })
        # Query with bearer auth and filter by count
        credentials = self.cmd(
            'acr credential show -n {registry_name} -g {resource_group}').get_output_in_json()

        username = credentials['username']
        password = credentials['passwords'][0]['value']

        self.cmd(
            'acr query -n {} -q {} --username {} --password {} '.format('metadataunittest', '"Manifests | limit 1"', username, password),
            checks=[self.check('count', 1)])

        # Query with basic auth and filter by repository
        token = self.cmd('acr login -n {registry_name} --expose-token').get_output_in_json()
        bearer = token["accessToken"]

        self.cmd(
            'acr query -n {} --repository {} -q {} --username {} --password {} '.format('metadataunittest', 'nginx', '"Manifests | limit 1"', EMPTY_GUID, bearer),
            checks=[self.check('count', 1)])

        # Renew credentials
        self.cmd(
            'acr credential renew -n {registry_name} --password-name {password} ')

        # Filter by size
        manifests = self.cmd('acr query -n {} -q {}'.format('metadataunittest', '"Manifests | where imageSize > 500"')).get_output_in_json()

        for manifest in manifests["data"]:
            assert manifest["size"] > 500