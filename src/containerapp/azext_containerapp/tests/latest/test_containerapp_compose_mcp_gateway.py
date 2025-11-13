# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, live_only)
from azure.cli.core.azclierror import (
    ResourceNotFoundError,
    InvalidArgumentValueError,
    UnauthorizedError
)


class ContainerAppComposeMCPGatewayScenarioTest(ScenarioTest):
    """
    Test scenarios for MCP Gateway detection and configuration.
    Per Constitution Principle III: These tests are written BEFORE implementation.
    They MUST FAIL until the implementation is complete.
    """

    @ResourceGroupPreparer(location='eastus')
    @live_only()
    def test_mcp_gateway_deployment(self, resource_group):
        """
        Test US2 Acceptance Scenario 1: Deploy compose file with MCP gateway.

        Expected: MCP gateway service is created without being assigned to GPU profile.

        This test MUST FAIL until T032-T043 are implemented.
        """
        self.kwargs.update({
            'env_name': self.create_random_name(prefix='env', length=24),
            'compose_file': os.path.join(os.path.dirname(__file__), '../../../../../../test-resources/compose-files/mcp-gateway.yml')
        })

        self.cmd('containerapp env create -g {rg} -n {env_name} --location eastus')
        self.cmd('containerapp compose create -g {rg} --environment {env_name} '
                '--compose-file-path {compose_file}')

        # Verify MCP gateway app was created
        mcp_gateway = self.cmd('containerapp show -g {rg} -n mcp-gateway').get_output_in_json()
        self.assertIsNotNone(mcp_gateway)

        # Verify MCP gateway is NOT on GPU profile
        workload_profile = mcp_gateway['properties'].get('workloadProfileName')
        if workload_profile:
            self.assertNotIn('GPU', workload_profile.upper())

    @ResourceGroupPreparer(location='eastus')
    @live_only()
    def test_managed_identity_enablement(self, resource_group):
        """
        Test US2 Acceptance Scenario 2: System-assigned managed identity enabled for MCP gateway.

        Expected: MCP gateway container app has system-assigned managed identity enabled.

        This test MUST FAIL until T034-T037 are implemented.
        """
        self.kwargs.update({
            'env_name': self.create_random_name(prefix='env', length=24),
            'compose_file': os.path.join(os.path.dirname(__file__), '../../../../../../test-resources/compose-files/mcp-gateway.yml')
        })

        self.cmd('containerapp env create -g {rg} -n {env_name} --location eastus')
        self.cmd('containerapp compose create -g {rg} --environment {env_name} '
                '--compose-file-path {compose_file}')

        # Verify system-assigned managed identity is enabled
        mcp_gateway = self.cmd('containerapp show -g {rg} -n mcp-gateway').get_output_in_json()
        identity = mcp_gateway['identity']
        self.assertEqual(identity['type'], 'SystemAssigned')
        self.assertIsNotNone(identity.get('principalId'))

    @ResourceGroupPreparer(location='eastus')
    @live_only()
    def test_role_assignment(self, resource_group):
        """
        Test US2 Acceptance Scenario 3: Azure AI Developer role assigned to MCP gateway identity.

        Expected: MCP gateway managed identity has "Azure AI Developer" role on resource group.

        This test MUST FAIL until T038-T043 are implemented.
        """
        self.kwargs.update({
            'env_name': self.create_random_name(prefix='env', length=24),
            'compose_file': os.path.join(os.path.dirname(__file__), '../../../../../../test-resources/compose-files/mcp-gateway.yml')
        })

        self.cmd('containerapp env create -g {rg} -n {env_name} --location eastus')
        self.cmd('containerapp compose create -g {rg} --environment {env_name} '
                '--compose-file-path {compose_file}')

        # Get MCP gateway identity
        mcp_gateway = self.cmd('containerapp show -g {rg} -n mcp-gateway').get_output_in_json()
        principal_id = mcp_gateway['identity']['principalId']

        # Verify role assignment exists (would need az role assignment list)
        # This is a placeholder - actual implementation would check Azure RBAC
        self.assertIsNotNone(principal_id)

    @ResourceGroupPreparer(location='eastus')
    @live_only()
    def test_mcp_environment_injection(self, resource_group):
        """
        Test US2 Acceptance Scenario 4: Environment variable injection for MCP gateway dependencies.

        Expected: Services that depend on MCP gateway receive MCP_ENDPOINT environment variable.

        This test MUST FAIL until T040-T043 are implemented.
        """
        self.kwargs.update({
            'env_name': self.create_random_name(prefix='env', length=24),
            'compose_file': os.path.join(os.path.dirname(__file__), '../../../../../../test-resources/compose-files/models-and-mcp.yml')
        })

        self.cmd('containerapp env create -g {rg} -n {env_name} --location eastus --enable-workload-profiles')
        self.cmd('containerapp compose create -g {rg} --environment {env_name} '
                '--compose-file-path {compose_file}')

        # Check web service has MCP_ENDPOINT
        web_app = self.cmd('containerapp show -g {rg} -n web').get_output_in_json()
        env_vars = {e['name']: e.get('value', '') for e in web_app['properties']['template']['containers'][0].get('env', [])}

        self.assertIn('MCP_ENDPOINT', env_vars)
        self.assertIn('mcp-gateway', env_vars['MCP_ENDPOINT'].lower())
