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
            'query': '"Manifests | limit 1"',
            'username': 'user',
            'password': 'password',
            'password_name': 'password'
        })

        # Query with bearer auth and filter by count
        credentials = self.cmd(
            'acr credential show -n {registry_name} -g {resource_group}').get_output_in_json()

        self.kwargs['username'] = credentials['username']
        self.kwargs['password'] = credentials['passwords'][0]['value']

        self.cmd(
            'acr query -n {registry_name} -q {query} --username {username} --password {password} ',
            checks=[self.check('count', 1)])

        # Query with basic auth and filter by repository
        token = self.cmd('acr login -n {registry_name} --expose-token').get_output_in_json()
        self.kwargs['username'] = EMPTY_GUID
        self.kwargs['password'] = token["accessToken"]
        self.kwargs['query'] = '"Manifests"'
        self.kwargs['repository_name'] = 'test/new'

        self.cmd(
            'acr query -n {registry_name} --repository {repository_name} -q {query} --username {username} --password {password} ',
            checks=[self.check('count', 12)])

        # Renew credentials
        self.cmd(
            'acr credential renew -n {registry_name} --password-name {password_name} ')

        # Filter by size 
        self.kwargs['query'] = '"Manifests | where imageSize > 100000000"'
        self.cmd(
            'acr query -n {registry_name} -q {query}', checks=[self.check('count', 3)])
