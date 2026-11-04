# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import JMESPathCheck, ResourceGroupPreparer, ScenarioTest

from .afdx_scenario_mixin import CdnAfdScenarioMixin, _json_arg


class CdnAfdAuthPolicyScenarioTest(CdnAfdScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer(additional_tags={'owner': 'zhefeng'})
    def test_afd_auth_policy_crud(self, resource_group):
        profile_name = self.create_random_name(prefix='profile', length=16)
        profile = self.afd_nonproduction_profile_create_cmd(
            resource_group, profile_name, sku='Premium_AzureFrontDoor').get_output_in_json()
        profile_args = f'-g {resource_group} --profile-name {profile_name}'
        # Public Microsoft tenant fixture; no local account lookup is needed during playback.
        issuer = 'https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47/v2.0'
        # ARM is an existing Entra resource audience; no app registration or token is required.
        audiences = ['https://management.azure.com/']
        auth_configs = [{
            'entra-id': {
                'issuer': issuer,
                'audiences': audiences,
                'auth-location': 'Header',
                'auth-location-selector': 'Authorization',
            },
        }]
        self.cmd(f'afd auth-policy list {profile_args}', checks=[JMESPathCheck('length(@)', 0)])

        policy_name = self.create_random_name(prefix='authpolicy', length=24)
        policy_args = f'{profile_args} --auth-policy-name {policy_name}'
        policy_id = f"{profile['id']}/authpolicies/{policy_name}"
        preserved_checks = [
            JMESPathCheck('id', policy_id, case_sensitive=False),
            JMESPathCheck('name', policy_name),
            JMESPathCheck('type', 'Microsoft.Cdn/profiles/authpolicies'),
            JMESPathCheck('properties.associations.isProfileLevel', True),
            JMESPathCheck('length(properties.authConfigs)', 1),
            JMESPathCheck('properties.authConfigs[0].identityProvider', 'EntraID'),
            JMESPathCheck('properties.authConfigs[0].issuer', issuer),
            JMESPathCheck('properties.authConfigs[0].audiences', audiences),
            JMESPathCheck('properties.authConfigs[0].authLocation', 'Header'),
            JMESPathCheck('properties.authConfigs[0].authLocationSelector', 'Authorization'),
            JMESPathCheck('properties.provisioningState', 'Succeeded'),
        ]
        create_checks = preserved_checks + [
            JMESPathCheck('properties.action', 'Block'),
            JMESPathCheck('properties.forwardTokenToOrigin', True),
        ]
        self.cmd(
            f'afd auth-policy create {policy_args} --action Block --forward-token-to-origin true '
            f'--associations {_json_arg({"is-profile-level": True})} '
            f'--auth-configs {_json_arg(auth_configs)}',
            checks=create_checks)
        self.cmd(f'afd auth-policy show {policy_args}', checks=create_checks)
        self.cmd(f'afd auth-policy list {profile_args}', checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].id', policy_id, case_sensitive=False),
            JMESPathCheck('[0].type', 'Microsoft.Cdn/profiles/authpolicies'),
            JMESPathCheck('[0].properties.associations.isProfileLevel', True),
            JMESPathCheck('[0].properties.authConfigs[0].identityProvider', 'EntraID'),
            JMESPathCheck('[0].properties.authConfigs[0].issuer', issuer),
            JMESPathCheck('[0].properties.authConfigs[0].audiences', audiences),
            JMESPathCheck('[0].properties.action', 'Block'),
            JMESPathCheck('[0].properties.forwardTokenToOrigin', True),
        ])

        update_checks = preserved_checks + [
            JMESPathCheck('properties.action', 'Log'),
            JMESPathCheck('properties.forwardTokenToOrigin', True),
        ]
        self.cmd(f'afd auth-policy update {policy_args} --action Log', checks=update_checks)
        self.cmd(f'afd auth-policy show {policy_args}', checks=update_checks)
        update_checks = preserved_checks + [
            JMESPathCheck('properties.action', 'Log'),
            JMESPathCheck('properties.forwardTokenToOrigin', False),
        ]
        self.cmd(f'afd auth-policy update {policy_args} --forward-token false', checks=update_checks)
        self.cmd(f'afd auth-policy show {policy_args}', checks=update_checks)
        self.cmd(f'afd auth-policy list {profile_args}', checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', policy_name),
            JMESPathCheck('[0].properties.action', 'Log'),
            JMESPathCheck('[0].properties.forwardTokenToOrigin', False),
            JMESPathCheck('[0].properties.associations.isProfileLevel', True),
            JMESPathCheck('[0].properties.authConfigs[0].issuer', issuer),
            JMESPathCheck('[0].properties.authConfigs[0].audiences', audiences),
        ])

        self.cmd(f'afd auth-policy delete {policy_args} --yes')
        self.cmd(f'afd auth-policy list {profile_args}', checks=[JMESPathCheck('length(@)', 0)])
        self.cmd(f'afd auth-policy show {policy_args}', expect_failure=True)
