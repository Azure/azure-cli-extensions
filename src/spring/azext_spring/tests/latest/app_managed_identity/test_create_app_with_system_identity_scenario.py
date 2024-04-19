# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.testsdk import (ScenarioTest, record_only)
from ....vendored_sdks.appplatform.v2024_05_01_preview.models import ManagedIdentityType


@record_only()
class CreateAppWithSystemIdentity(ScenarioTest):

    def test_create_app_with_assign_identity(self):
        self.kwargs.update({
            'app': 'create-app-system-identity-1',
            'serviceName': 'cli-unittest',
            'rg': 'cli'
        })

        self.cmd('spring app create -n {app} -g {rg} -s {serviceName} --assign-identity', checks=[
            self.check('identity.type', ManagedIdentityType.SYSTEM_ASSIGNED, case_sensitive=False),
            self.exists('identity.principalId'),
            self.exists('identity.tenantId'),
            self.check('identity.userAssignedIdentities', None)
        ])

    def test_create_app_with_system_assigned(self):
        self.kwargs.update({
            'app': 'create-app-system-identity-2',
            'serviceName': 'cli-unittest',
            'rg': 'cli'
        })

        self.cmd('spring app create -n {app} -g {rg} -s {serviceName} --system-assigned', checks=[
            self.check('identity.type', ManagedIdentityType.SYSTEM_ASSIGNED, case_sensitive=False),
            self.exists('identity.principalId'),
            self.exists('identity.tenantId'),
            self.check('identity.userAssignedIdentities', None)
        ])
