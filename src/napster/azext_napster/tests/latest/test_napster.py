# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import *


class NapsterScenario(ScenarioTest):
    def test_napster_scenario(self):
        self.kwargs.update({
            'resource_group': 'acctest0001',
            'name': 'napster-test-saml',
            'location': 'eastus2euap',
            'marketplace_subscription_id': '09fffd7d-d000-4467-cc23-d82b97e9431d',
            'publisher_id': 'touchcastinc1655995956899',
            'offer_id': 'napster_companion_api',
            'plan_id': 'napster_companion_api_feb_2026',
            'plan_name': 'Pay As You Go',
            'term_unit': 'P1M',
            'term_id': 'n7ja87drquhy',
            'saas_resource_id': '/subscriptions/61641157-140c-4b97-b365-30ff76d9f82e/resourceGroups/acctest0001/providers/Microsoft.SaaS/resources/shr-test-1',
            'user_first_name': 'Yashika',
            'user_last_name': 'Jain',
            'user_email': 'yashikajain@microsoft.com',
            'user_upn': 'yashikajain@microsoft.com',
            'user_phone_number': '+1-425-555-1234',
            'application': 'dsaf',
            'enterprise_app_id': 'b2c3d4e5-f6a7-4b5c-8d9e-0f1a2b3c4d5e',
        })

        # Create organization
        self.cmd(
            'az napster companion-api organization create '
            '--resource-group {resource_group} '
            '--organizationname {name} '
            '--marketplace "{{subscription-id:{marketplace_subscription_id},offer-details:{{publisher-id:{publisher_id},offer-id:{offer_id},plan-id:{plan_id},plan-name:\'Pay As You Go\',term-unit:{term_unit},term-id:{term_id}}},saas-resource-id:{saas_resource_id}}}" '
            '--user "{{first-name:{user_first_name},last-name:{user_last_name},email-address:{user_email},upn:{user_upn},phone-number:{user_phone_number}}}" '
            '--partner-properties "{{application:{application}}}" '
            '--single-sign-on-properties "{{type:Saml,state:Initial,enterprise-app-id:{enterprise_app_id},url:\'https://companion-api.napsterai.dev/admin/ms-auth\',aad-domains:[MicrosoftCustomerLed.onmicrosoft.com]}}" '
            '--location {location}',
            checks=[
                self.check('name', '{name}'),
            ]
        )

        # List organizations
        self.cmd(
            'az napster companion-api organization list --resource-group {resource_group}',
            checks=[
                self.greater_than('length(@)', 0),
            ]
        )

        # Show organization
        self.cmd(
            'az napster companion-api organization show '
            '--resource-group {resource_group} '
            '--organizationname {name}',
            checks=[
                self.check('name', '{name}'),
            ]
        )

        # Update organization
        self.cmd(
            'az napster companion-api organization update '
            '--resource-group {resource_group} '
            '--organizationname {name}',
            checks=[
                self.check('name', '{name}'),
            ]
        )

        # Delete organization at the end
        self.cmd(
            'az napster companion-api organization delete '
            '--resource-group {resource_group} '
            '--organizationname {name} -y',
            checks=[]
        )
