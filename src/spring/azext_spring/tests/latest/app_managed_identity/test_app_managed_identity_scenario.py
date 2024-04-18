# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.testsdk import (ScenarioTest, record_only)
from ....vendored_sdks.appplatform.v2024_05_01_preview.models import ManagedIdentityType

"""
In order to re-run this scenario test,
1. Choose a subscription ID in which you'll create user-assigned managed identities, and fill in ${USER_IDENTITY_SUB_ID}
2. Create a resource group ${USER_IDENTITY_RESOURCE_GROUP} in ${USER_IDENTITY_SUB_ID}
3. Manually create 2 user-assigned managed identities for USER_IDENTITY_NAME_1 and USER_IDENTITY_NAME_2 in \
   group ${USER_IDENTITY_RESOURCE_GROUP} under subscription ${USER_IDENTITY_SUB_ID}.
4. After successfully re-run, Set ${USER_IDENTITY_SUB_ID} back to "00000000-0000-0000-0000-000000000000"
"""
USER_IDENTITY_SUB_ID = "00000000-0000-0000-0000-000000000000"

MASKED_SUB = "00000000-0000-0000-0000-000000000000"
USER_IDENTITY_RESOURCE_GROUP = "cli"
USER_IDENTITY_NAME_1 = "managed-identity-1"
USER_IDENTITY_NAME_2 = "managed-identity-2"
USER_IDENTITY_RESOURCE_ID_TEMPLATE = "/subscriptions/{}/resourcegroups/{}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{}"
MASKED_USER_IDENTITY_RESOURCE_ID_1 = USER_IDENTITY_RESOURCE_ID_TEMPLATE.format(MASKED_SUB, USER_IDENTITY_RESOURCE_GROUP,
                                                                               USER_IDENTITY_NAME_1)
MASKED_USER_IDENTITY_RESOURCE_ID_2 = USER_IDENTITY_RESOURCE_ID_TEMPLATE.format(MASKED_SUB, USER_IDENTITY_RESOURCE_GROUP,
                                                                               USER_IDENTITY_NAME_2)
USER_IDENTITY_RESOURCE_ID_1 = USER_IDENTITY_RESOURCE_ID_TEMPLATE.format(USER_IDENTITY_SUB_ID,
                                                                        USER_IDENTITY_RESOURCE_GROUP,
                                                                        USER_IDENTITY_NAME_1)
USER_IDENTITY_RESOURCE_ID_2 = USER_IDENTITY_RESOURCE_ID_TEMPLATE.format(USER_IDENTITY_SUB_ID,
                                                                        USER_IDENTITY_RESOURCE_GROUP,
                                                                        USER_IDENTITY_NAME_2)


@record_only()
class AppIdentityAssign(ScenarioTest):

    def test_app_identity_crud(self):
        self.kwargs.update({
            'app': 'test-msi-app-1',
            'serviceName': 'cli-unittest',
            'rg': 'cli',
            'ua1': USER_IDENTITY_RESOURCE_ID_1,
            'ua2': USER_IDENTITY_RESOURCE_ID_2
        })

        self.cmd('spring app identity remove -n {app} -g {rg} -s {serviceName} --system-assigned --user-assigned',
                 checks=[
                     self.check('identity.type', None)
                 ])

        self.cmd('spring app identity show -n {app} -g {rg} -s {serviceName}', checks=[
            self.is_empty()
        ])

        self.cmd('spring app identity assign -n {app} -g {rg} -s {serviceName} --system-assigned', checks=[
            self.check('identity.type', ManagedIdentityType.SYSTEM_ASSIGNED, case_sensitive=False),
            self.exists('identity.tenantId'),
            self.exists('identity.principalId')
        ])

        app = self.cmd('spring app identity assign -n {app} -g {rg} -s {serviceName} --user-assigned {ua1} {ua2}',
                       checks=[
                           self.check('identity.type', ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED,
                                      case_sensitive=False),
                           self.exists('identity.tenantId'),
                           self.exists('identity.principalId'),
                           self.exists('identity.userAssignedIdentities')
                       ]).json_value
        user_identity_dict = self._to_lower(app['identity']['userAssignedIdentities'])
        self.assertTrue(isinstance(user_identity_dict, dict))
        self.assertTrue(self._contains_user_id_1(user_identity_dict.keys()))
        self.assertTrue(self._contains_user_id_2(user_identity_dict.keys()))

        app = self.cmd('spring app identity remove -n {app} -g {rg} -s {serviceName} --user-assigned {ua1}', checks=[
            self.check('identity.type', ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED, case_sensitive=False),
            self.exists('identity.tenantId'),
            self.exists('identity.principalId'),
            self.exists('identity.userAssignedIdentities')
        ]).json_value
        user_identity_dict = self._to_lower(app['identity']['userAssignedIdentities'])
        self.assertTrue(isinstance(user_identity_dict, dict))
        self.assertTrue(len(user_identity_dict) == 1)
        self.assertTrue(self._contains_user_id_2(user_identity_dict.keys()))

        self.cmd('spring app identity remove -n {app} -g {rg} -s {serviceName} --user-assigned {ua2}', checks=[
            self.check('identity.type', ManagedIdentityType.SYSTEM_ASSIGNED, case_sensitive=False),
            self.exists('identity.tenantId'),
            self.exists('identity.principalId'),
            self.check('identity.userAssignedIdentities', None)
        ])

        self.cmd('spring app identity remove -n {app} -g {rg} -s {serviceName} --system-assigned',
                 checks=[self.check('identity', None)])

        app = self.cmd(
            'spring app identity assign -n {app} -g {rg} -s {serviceName} --system-assigned --user-assigned {ua1} {ua2}',
            checks=[
                self.check('identity.type', ManagedIdentityType.SYSTEM_ASSIGNED_USER_ASSIGNED, case_sensitive=False),
                self.exists('identity.tenantId'),
                self.exists('identity.principalId'),
                self.exists('identity.userAssignedIdentities')
            ]).json_value
        user_identity_dict = self._to_lower(app['identity']['userAssignedIdentities'])
        self.assertTrue(isinstance(user_identity_dict, dict))
        self.assertTrue(self._contains_user_id_1(user_identity_dict.keys()))
        self.assertTrue(self._contains_user_id_2(user_identity_dict.keys()))

        self.cmd(
            'spring app identity remove -n {app} -g {rg} -s {serviceName} --system-assigned --user-assigned {ua1} {ua2}',
            checks=[self.check('identity', None)])

    def _contains_user_id_1(self, keys):
        return MASKED_USER_IDENTITY_RESOURCE_ID_1.lower() in keys or USER_IDENTITY_RESOURCE_ID_1.lower() in keys

    def _contains_user_id_2(self, keys):
        return MASKED_USER_IDENTITY_RESOURCE_ID_2.lower() in keys or USER_IDENTITY_RESOURCE_ID_2.lower() in keys

    def _to_lower(self, str_dict):
        new_dict = {}
        for key in str_dict.keys():
            new_dict[key.lower()] = str_dict[key]
        return new_dict
