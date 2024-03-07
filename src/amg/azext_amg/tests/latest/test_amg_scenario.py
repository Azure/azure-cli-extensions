# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import time
import unittest


from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, MSGraphNameReplacer, MOCKED_USER_NAME)
from azure.cli.testsdk .scenario_tests import AllowLargeResponse
from .test_definitions import (test_data_source, test_notification_channel, test_dashboard)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AmgScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_amg')
    def test_amg_crud(self, resource_group):

        self.kwargs.update({
            'name': 'clitestamg2',
            'location': 'westcentralus'
        })

        self.cmd('grafana create -g {rg} -n {name} -l {location} --tags foo=doo --skip-role-assignments', checks=[
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

        self.cmd('grafana update -g {rg} -n {name} --deterministic-outbound-ip Enabled --api-key Enabled', checks=[
            self.check('properties.deterministicOutboundIp', 'Enabled'),
            self.check('properties.apiKey', 'Enabled'),
            self.check('length(properties.outboundIPs)', 2)
        ])

        self.cmd('grafana show -g {rg} -n {name}', checks=[
            self.check('properties.deterministicOutboundIp', 'Enabled'),
            self.check('properties.apiKey', 'Enabled'),
            self.check('length(properties.outboundIPs)', 2)
        ])

        self.cmd('grafana update -g {rg} -n {name} --deterministic-outbound-ip Disabled --api-key Disabled --public-network-access Disabled')
        self.cmd('grafana show -g {rg} -n {name}', checks=[
            self.check('properties.deterministicOutboundIp', 'Disabled'),
            self.check('properties.apiKey', 'Disabled'),
            self.check('properties.publicNetworkAccess', 'Disabled'),
            self.check('properties.outboundIPs', None)
        ])

        self.cmd('grafana delete -g {rg} -n {name} --yes')
        final_count = len(self.cmd('grafana list').get_output_in_json())
        self.assertTrue(final_count, count - 1)

    @ResourceGroupPreparer(name_prefix='cli_test_amg')
    def test_api_key_e2e(self, resource_group):

        self.kwargs.update({
            'name': 'clitestamgapikey',
            'location': 'westcentralus',
            "key": "apikey1",
            "key2": "apikey2"
        })

        owner = self._get_signed_in_user()
        self.recording_processors.append(MSGraphNameReplacer(owner, MOCKED_USER_NAME))

        with unittest.mock.patch('azext_amg.custom._gen_guid', side_effect=self.create_guid):
            self.cmd('grafana create -g {rg} -n {name} -l {location}')
            # Ensure RBAC changes are propagated
            time.sleep(120)
            self.cmd('grafana update -g {rg} -n {name} --api-key Enabled')
            self.cmd('grafana api-key list -g {rg} -n {name}', checks=[
                self.check('length([])', 0)
            ])
            result = self.cmd('grafana api-key create -g {rg} -n {name} --key {key} --role Admin --time-to-live 3d').get_output_in_json()
            api_key = result["key"]
            self.cmd('grafana api-key create -g {rg} -n {name} --key {key2}')
            self.cmd('grafana api-key list -g {rg} -n {name}', checks=[
                self.check('length([])', 2)
            ])
            self.cmd('grafana api-key delete -g {rg} -n {name} --key {key2}')
            number = len(self.cmd('grafana dashboard list -g {rg} -n {name} --api-key ' + api_key).get_output_in_json())
            self.assertTrue(number > 0)

    @ResourceGroupPreparer(name_prefix='cli_test_amg')
    def test_service_account_e2e(self, resource_group):

        self.kwargs.update({
            'name': 'clitestserviceaccount',
            'location': 'westcentralus',
            "account": "myServiceAccount",
            "token": "myToken"
        })

        owner = self._get_signed_in_user()
        self.recording_processors.append(MSGraphNameReplacer(owner, MOCKED_USER_NAME))

        with unittest.mock.patch('azext_amg.custom._gen_guid', side_effect=self.create_guid):
            self.cmd('grafana create -g {rg} -n {name} -l {location}')
            # Ensure RBAC changes are propagated
            time.sleep(120)
            self.cmd('grafana update -g {rg} -n {name} --service-account Enabled')
            self.cmd('grafana service-account list -g {rg} -n {name}', checks=[
                self.check('length([])', 0)
            ])
            self.cmd('grafana service-account create -g {rg} -n {name} --service-account oldName --role viewer --is-disabled true', checks=[
                self.check('isDisabled', True)
            ])
            self.cmd('grafana service-account update -g {rg} -n {name} --service-account oldName --new-name {account} --role Admin --is-disabled false', checks=[
                # self.check('isDisabled', False)
            ])
            self.cmd('grafana service-account show -g {rg} -n {name} --service-account {account}')
            self.cmd('grafana service-account list -g {rg} -n {name}')
            result = self.cmd('grafana service-account token create -g {rg} -n {name} --service-account {account} --token {token} --time-to-live 1d').get_output_in_json()
            key = result["key"]
            self.cmd('grafana service-account token list -g {rg} -n {name} --service-account {account}', checks=[
                self.check('length([])', 1)
            ])
            number = len(self.cmd('grafana dashboard list -g {rg} -n {name} --token ' + key).get_output_in_json())
            self.assertTrue(number > 0)
            self.cmd('grafana service-account token delete -g {rg} -n {name} --service-account {account} --token {token}')
            self.cmd('grafana service-account token list -g {rg} -n {name} --service-account {account}', checks=[
                self.check('length([])', 0)
            ])
            self.cmd('grafana service-account delete -g {rg} -n {name} --service-account {account}')

    @AllowLargeResponse(size_kb=3072)
    @ResourceGroupPreparer(name_prefix='cli_test_amg', location='westeurope')
    def test_amg_e2e(self, resource_group):

        # Test Instance
        self.kwargs.update({
            'name': 'clitestamge2e',
            'location': 'westeurope'
        })

        owner = self._get_signed_in_user()
        self.recording_processors.append(MSGraphNameReplacer(owner, MOCKED_USER_NAME))

        with unittest.mock.patch('azext_amg.custom._gen_guid', side_effect=self.create_guid):

            self.cmd('grafana create -g {rg} -n {name} -l {location} --tags foo=doo', checks=[
                self.check('tags.foo', 'doo'),
                self.check('name', '{name}')
            ])
            # Ensure RBAC changes are propagated
            time.sleep(120)

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

    @AllowLargeResponse(size_kb=3072)
    @ResourceGroupPreparer(name_prefix='cli_test_amg', location='westcentralus')
    def test_amg_backup_restore(self, resource_group):

        # Test Instance
        self.kwargs.update({
            'name': 'clitestbackup',
            'location': 'westcentralus',
            'name2': 'clitestbackup2'
        })

        owner = self._get_signed_in_user()
        self.recording_processors.append(MSGraphNameReplacer(owner, MOCKED_USER_NAME))

        with unittest.mock.patch('azext_amg.custom._gen_guid', side_effect=self.create_guid):

            amg1 = self.cmd('grafana create -g {rg} -n {name} -l {location}').get_output_in_json()
            amg2 = self.cmd('grafana create -g {rg} -n {name2} -l {location}').get_output_in_json()
            # Ensure RBAC changes are propagated
            time.sleep(120)

            # set up folder
            self.kwargs.update({
                'folderTitle': 'Test Folder',
                'id': amg1['id'],
                'id2': amg2['id']
            })
            self.cmd('grafana folder create -g {rg} -n {name} --title "{folderTitle}"')

            # set up data source
            self.kwargs.update({
                'dataSourceDefinition': test_data_source,
                'dataSourceName': test_data_source["name"]
            })
            self.cmd('grafana data-source create -g {rg} -n {name} --definition "{dataSourceDefinition}"')

            # create dashboard
            dashboard_title = test_dashboard["dashboard"]["title"]
            slug = dashboard_title.lower().replace(' ', '-')

            self.kwargs.update({
                'dashboardDefinition': test_dashboard,
                'dashboardTitle': dashboard_title,
                'dashboardTitle2': dashboard_title + '2',
                'dashboardSlug': slug,
            })
            self.kwargs['dashboardDefinition']['dashboard']['uid'] = 'mg2OAlTVa'  # control the uid to prevent auto generated uid with possible '-' that breaks the command
            # dashboard under own folder
            response_create = self.cmd('grafana dashboard create -g {rg} -n {name} --folder "{folderTitle}"  --definition "{dashboardDefinition}" --title "{dashboardTitle}"').get_output_in_json()

            self.kwargs.update({
                'dashboardUid': response_create["uid"],
            })

            # dashboard under "General"
            self.kwargs['dashboardDefinition']['dashboard']['uid'] = 'mg2OAlTVb'
            response_create = self.cmd('grafana dashboard create -g {rg} -n {name}  --definition "{dashboardDefinition}" --title "{dashboardTitle}"').get_output_in_json()
            self.kwargs.update({
                'dashboardUid2': response_create["uid"],
            })

            # 2nd dashboard under own folder
            self.kwargs['dashboardDefinition']['dashboard']['uid'] = 'mg2OAlTVc'
            response_create = self.cmd('grafana dashboard create -g {rg} -n {name} --folder "{folderTitle}"  --definition "{dashboardDefinition}" --title "{dashboardTitle2}"').get_output_in_json()

            self.kwargs.update({
                'dashboardUid3': response_create["uid"],
            })

            with tempfile.TemporaryDirectory() as temp_dir:
                self.kwargs.update({
                    'tempDir': temp_dir
                })
                # test exclude scenarios
                self.cmd('grafana backup -g {rg} -n {name} -d "{tempDir}" --folders-to-include "{folderTitle}" General --components datasources dashboards folders')

                filenames = next(os.walk(temp_dir), (None, None, []))[2]
                self.assertTrue(len(filenames) == 1)
                self.assertTrue(filenames[0].endswith('.tar.gz'))

                self.kwargs.update({
                    'archiveFile': os.path.join(temp_dir, filenames[0])
                })

                self.cmd('grafana folder delete -g {rg} -n {name} --folder "{folderTitle}"')
                self.cmd('grafana data-source delete -g {rg} -n {name} --data-source "{dataSourceName}"')

                self.cmd('grafana restore -g {rg} -n {name} --archive-file "{archiveFile}"')

            self.cmd('grafana data-source show -g {rg} -n {name} --data-source "{dataSourceName}"')
            self.cmd('grafana folder show -g {rg} -n {name} --folder "{folderTitle}"')

            self.cmd('grafana dashboard show -g {rg} -n {name} --dashboard "{dashboardUid}"', checks=[
                self.check("[dashboard.title]", "['{dashboardTitle}']"),
                self.check("[meta.folderTitle]", "['{folderTitle}']")])
            self.cmd('grafana dashboard show -g {rg} -n {name} --dashboard "{dashboardUid2}"', checks=[
                self.check("[dashboard.title]", "['{dashboardTitle}']"),
                self.check("[meta.folderTitle]", "['General']")])

            with tempfile.TemporaryDirectory() as temp_dir:
                self.kwargs.update({
                    'tempDir': temp_dir
                })
                self.cmd('grafana backup -g {rg} -n {name} -d "{tempDir}" --folders-to-exclude General "Azure Monitor" Geneva --components dashboards folders')

                filenames = next(os.walk(temp_dir), (None, None, []))[2]
                self.assertTrue(len(filenames) == 1)
                self.assertTrue(filenames[0].endswith('.tar.gz'))

                self.kwargs.update({
                    'archiveFile': os.path.join(temp_dir, filenames[0])
                })

                self.cmd('grafana dashboard delete -g {rg} -n {name} --dashboard "{dashboardUid2}"')
                self.cmd('grafana restore -g {rg} -n {name} --archive-file "{archiveFile}"')

            self.cmd('grafana dashboard list -g {rg} -n {name}', checks=[
                self.check("length([?uid == '{dashboardUid2}'])", 0),
                self.check("length([?uid == '{dashboardUid}'])", 1)])

            self.kwargs['dashboardDefinition']['dashboard']['uid'] = 'mg2OAlTVd'
            response_create = self.cmd('grafana dashboard create -g {rg} -n {name}  --definition "{dashboardDefinition}" --title "{dashboardTitle}"').get_output_in_json()
            print(response_create)
            self.kwargs.update({
                'dashboardUid4': response_create["uid"],
            })

            self.cmd('grafana dashboard sync --source {id} --destination {id2} --folders-to-include "{folderTitle}" general')
            self.cmd('grafana folder show -g {rg} -n {name2} --folder "{folderTitle}"')
            self.cmd('grafana dashboard show -g {rg} -n {name2} --dashboard "{dashboardUid}"', checks=[
                self.check("[dashboard.title]", "['{dashboardTitle}']"),
                self.check("[meta.folderTitle]", "['{folderTitle}']")])
            self.cmd('grafana dashboard show -g {rg} -n {name2} --dashboard "{dashboardUid4}"', checks=[
                self.check("[dashboard.title]", "['{dashboardTitle}']"),
                self.check("[meta.folderTitle]", "['General']")])

            self.cmd('grafana dashboard delete -g {rg} -n {name2} --dashboard "{dashboardUid}"')
            self.cmd('grafana dashboard delete -g {rg} -n {name2} --dashboard "{dashboardUid3}"')
            self.cmd('grafana dashboard sync --source {id} --destination {id2} --folders-to-include "{folderTitle}" --dashboards-to-include "{dashboardTitle}"')
            self.cmd('grafana dashboard list -g {rg} -n {name2}', checks=[
                self.check("length([?uid == '{dashboardUid3}'])", 0),
                self.check("length([?uid == '{dashboardUid}'])", 1)
            ])

    def _get_signed_in_user(self):
        account_info = self.cmd('account show').get_output_in_json()
        if account_info['user']['type'] == 'user':
            return account_info['user']['name']
        return None
