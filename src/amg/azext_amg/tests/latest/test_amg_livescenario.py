# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ResourceGroupPreparer, LiveScenarioTest)
from azure.cli.testsdk .scenario_tests import AllowLargeResponse
from .test_definitions import (test_data_source, test_notification_channel, test_dashboard)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AmgLiveScenarioTest(LiveScenarioTest):

    @AllowLargeResponse(size_kb=3072)
    @ResourceGroupPreparer(name_prefix='cli_test_amg', location='westeurope')
    def test_amg_e2e(self, resource_group):

        # Test Instance
        self.kwargs.update({
            'name': 'clitestamg',
            'location': 'westeurope'
        })

        self.cmd('grafana create -g {rg} -n {name} -l {location} --tags foo=doo', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])

        self.cmd('grafana list -g {rg}')
        count = len(self.cmd('grafana list').get_output_in_json())

        self.cmd('grafana show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'doo')
        ])

        # Test User      
        response_list = self.cmd('grafana user list -g {rg} -n {name}').get_output_in_json()
        self.assertTrue(len(response_list) > 0)
        
        response_actual_user = self.cmd('grafana user actual-user -g {rg} -n {name}').get_output_in_json()
        self.assertTrue(len(response_actual_user) > 0)

        # Test Folder
        self.kwargs.update({
            'title': 'Test Folder',
            'update_title': 'Test Folder Update'
        })
        
        response_create = self.cmd('grafana folder create -g {rg} -n {name} --title "{title}"', checks=[
            self.check("[title]", "['{title}']")]).get_output_in_json()
        
        self.kwargs.update({
            'folder_uid': response_create["uid"]
        })

        self.cmd('grafana folder show -g {rg} -n {name} --folder "{title}"', checks=[
            self.check("[title]", "['{title}']")])

        self.cmd('grafana folder update -g {rg} -n {name} --folder "{folder_uid}" --title "{update_title}"', checks=[
            self.check("[title]", "['{update_title}']")])
            
        response_list = self.cmd('grafana folder list -g {rg} -n {name}').get_output_in_json()
        self.assertTrue(len(response_list) > 0)

        self.cmd('grafana folder delete -g {rg} -n {name} --folder "{update_title}"')
        response_delete = self.cmd('grafana folder list -g {rg} -n {name}').get_output_in_json()
        self.assertTrue(len(response_delete) == len(response_list) - 1)


        # Test Data Source
        self.kwargs.update({
            'definition': test_data_source,
            'definition_name': test_data_source["name"]
        })
        
        self.cmd('grafana data-source create -g {rg} -n {name} --definition "{definition}"', checks=[
            self.check("[name]", "['{definition_name}']")])

        self.cmd('grafana data-source show -g {rg} -n {name} --data-source "{definition_name}"', checks=[
            self.check("[name]", "['{definition_name}']")])

        self.cmd('grafana data-source update -g {rg} -n {name} --data-source "{definition_name}" --definition "{definition}"', checks=[
            self.check("[name]", "['{definition_name}']")])
            
        response_list = self.cmd('grafana data-source list -g {rg} -n {name}').get_output_in_json()
        self.assertTrue(len(response_list) > 0)

        self.cmd('grafana data-source delete -g {rg} -n {name} --data-source "{definition_name}"')
        response_delete = self.cmd('grafana data-source list -g {rg} -n {name}').get_output_in_json()
        self.assertTrue(len(response_delete) == len(response_list) - 1)


        # Test Notification Channel
        self.kwargs.update({
            'definition': test_notification_channel,
            'definition_name': test_notification_channel["name"]
        })
        
        response_create = self.cmd('grafana notification-channel create -g {rg} -n {name} --definition "{definition}"', checks=[
            self.check("[name]", "['{definition_name}']")]).get_output_in_json()

        self.kwargs.update({
            'notification_channel_uid': response_create["uid"]
        })

        self.cmd('grafana notification-channel show -g {rg} -n {name} --notification-channel "{notification_channel_uid}"', checks=[
            self.check("[name]", "['{definition_name}']")])

        self.cmd('grafana notification-channel update -g {rg} -n {name} --notification-channel "{notification_channel_uid}" --definition "{definition}"', checks=[
            self.check("[name]", "['{definition_name}']")])
            
        response_list = self.cmd('grafana notification-channel list -g {rg} -n {name}').get_output_in_json()
        self.assertTrue(len(response_list) > 0)

        self.cmd('grafana notification-channel delete -g {rg} -n {name} --notification-channel "{notification_channel_uid}"')
        response_delete = self.cmd('grafana notification-channel list -g {rg} -n {name}').get_output_in_json()
        self.assertTrue(len(response_delete) == len(response_list) - 1)

    
        # Test Dashboard
        definition_name = test_dashboard["dashboard"]["title"]
        slug = definition_name.lower().replace(' ', '-')

        self.kwargs.update({
            'definition': test_dashboard,
            'definition_name': definition_name,
            'definition_slug': slug,
        })
        
        response_create = self.cmd('grafana dashboard create -g {rg} -n {name} --definition "{definition}" --title "{definition_name}"', checks=[
            self.check("[slug]", "['{definition_slug}']")]).get_output_in_json()

        test_definition_update = test_dashboard
        test_definition_update["dashboard"]["uid"] = response_create["uid"]
        test_definition_update["dashboard"]["id"] = response_create["id"]
        test_definition_update["dashboard"]["version"] = response_create["version"]

        self.kwargs.update({
            'dashboard_uid': response_create["uid"],
            'test_definition_update': test_definition_update
        })

        self.cmd('grafana dashboard show -g {rg} -n {name} --dashboard "{dashboard_uid}"', checks=[
            self.check("[dashboard.title]", "['{definition_name}']")])

        response_update = self.cmd('grafana dashboard update -g {rg} -n {name} --definition "{test_definition_update}" --overwrite true', checks=[
            self.check("[slug]", "['{definition_slug}']")]).get_output_in_json()
        self.assertTrue(response_update["version"] == response_create["version"] + 1)

        response_list = self.cmd('grafana dashboard list -g {rg} -n {name}').get_output_in_json()
        self.assertTrue(len(response_list) > 0)

        self.cmd('grafana dashboard delete -g {rg} -n {name} --dashboard "{dashboard_uid}"')
        response_delete = self.cmd('grafana dashboard list -g {rg} -n {name}').get_output_in_json()
        self.assertTrue(len(response_delete) == len(response_list) - 1)

        # Close-out Instance
        self.cmd('grafana delete -g {rg} -n {name} --yes')
        final_count = len(self.cmd('grafana list').get_output_in_json())
        self.assertTrue(final_count, count - 1)
