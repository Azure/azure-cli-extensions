# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import time

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class SubscriptionClientScenarioTest(ScenarioTest):

    # @ResourceGroupPreparer(name_prefix='cli_test_account')
    def test_account(self):
        self.kwargs.update({
            'alias_name': self.create_random_name(prefix='cli_alias', length=24),
            'new_alias_name': self.create_random_name(prefix='cli_alias_new', length=24),
            'display_name': "My Subscription",
            'new_display_name': "My Big Subscription",
            'billing_scope': "/providers/Microsoft.Billing/billingAccounts/9147924/enrollmentAccounts/253727"
        })

        self.cmd('az account alias create --name {alias_name} --billing-scope "{billing_scope}" --display-name "{display_name}" --workload "Production"',
                 checks=[self.check('name', '{alias_name}'),
                         self.check('properties.provisioningState', 'Succeeded')])

        alias_sub = self.cmd('az account alias show -n {alias_name}',
                             checks=[self.check('name', '{alias_name}'),
                                     self.check('properties.provisioningState', 'Succeeded')]).get_output_in_json()
        sub_id = alias_sub['properties']['subscriptionId']
        self.kwargs.update({'subscription_id': sub_id})

        # response different from swagger, causing deserialization error
        # self.cmd('az account alias list',
        #          checks=[])

        self.cmd('az account subscription list',
                 checks=[self.greater_than('length(@)', 0)])

        self.cmd('az account subscription show --subscription-id {subscription_id}',
                 checks=[self.check('displayName', '{display_name}'),
                         self.check('state', 'Enabled'),
                         self.check('subscriptionId', sub_id)])

        self.cmd('az account subscription list-location --subscription-id {subscription_id}',
                 checks=[self.greater_than('length(@)', 0)])

        self.cmd('az account subscription cancel --subscription-id {subscription_id} --yes',
                 checks=[self.check('subscriptionId', '{subscription_id}')])
        time.sleep(300)
        self.cmd('az account subscription show --subscription-id {subscription_id}',
                 checks=[self.check('displayName', '{display_name}'),
                         self.check('state', 'Warned'),
                         self.check('subscriptionId', sub_id)])

        self.cmd('az account subscription enable --subscription-id {subscription_id}',
                 checks=[self.check('subscriptionId', '{subscription_id}')])
        time.sleep(300)
        self.cmd('az account subscription show --subscription-id {subscription_id}',
                 checks=[self.check('displayName', '{display_name}'),
                         self.check('state', 'Enabled'),
                         self.check('subscriptionId', sub_id)])

        self.cmd('az account subscription rename --subscription-id {subscription_id} --name "{new_display_name}"',
                 checks=[self.check('subscriptionId', '{subscription_id}')])
        # uncomment when request body match is supported in playback tests
        # time.sleep(600)
        # self.cmd('az account subscription show --subscription-id {subscription_id}',
        #          checks=[
        #          self.check('displayName', '{new_display_name}'),
        #          self.check('state', 'Enabled'),
        #          self.check('subscriptionId', sub_id)])

        self.cmd('az account tenant list',
                 checks=[self.exists('[0].tenantId')])

        self.cmd('az account alias delete -n {alias_name}',
                 checks=[])

        self.cmd('az account alias create --name {new_alias_name} --workload "Production" --subscription-id {subscription_id}',
                 checks=[self.check('name', '{new_alias_name}'),
                         self.check('properties.provisioningState', 'Succeeded')])

        time.sleep(600)
        self.cmd('az account alias delete -n {new_alias_name}',
                 checks=[])
