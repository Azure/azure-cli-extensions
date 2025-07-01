# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import time
import unittest


from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, MSGraphNameReplacer, MOCKED_USER_NAME)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .test_definitions import (test_data_source, test_dashboard)
from .recording_processors import ApiKeyServiceAccountTokenReplacer

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AmgScenarioTest(ScenarioTest):
    def __init__(self, method_name):
        super().__init__(method_name, recording_processors=[
            ApiKeyServiceAccountTokenReplacer()
        ])


    @ResourceGroupPreparer(name_prefix='cli_test_amg')
    def test_amg_crud(self, resource_group):

        self.kwargs.update({
            'name': self.create_random_name(prefix='clitestamg', length=23),
            'location': 'westcentralus'
        })

        self.cmd('grafana create -g {rg} -n {name} -l {location} --tags foo=doo --skip-role-assignments True', checks=[
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
            self.check('properties.deterministicOutboundIP', 'Enabled'),
            self.check('properties.apiKey', 'Enabled'),
            self.check('length(properties.outboundIPs)', 2)
        ])

        self.cmd('grafana show -g {rg} -n {name}', checks=[
            self.check('properties.deterministicOutboundIP', 'Enabled'),
            self.check('properties.apiKey', 'Enabled'),
            self.check('length(properties.outboundIPs)', 2)
        ])

        self.cmd('grafana update -g {rg} -n {name} --deterministic-outbound-ip Disabled --api-key Disabled --public-network-access Disabled')
        self.cmd('grafana show -g {rg} -n {name}', checks=[
            self.check('properties.deterministicOutboundIP', 'Disabled'),
            self.check('properties.apiKey', 'Disabled'),
            self.check('properties.publicNetworkAccess', 'Disabled'),
            self.check('properties.outboundIPs', None)
        ])

        self.cmd('grafana delete -g {rg} -n {name} --yes')
        final_count = len(self.cmd('grafana list').get_output_in_json())
        self.assertTrue(final_count, count - 1)


    @ResourceGroupPreparer(name_prefix='cli_test_amg')
    def test_amg_api_key_e2e(self, resource_group):

        self.kwargs.update({
            'name': self.create_random_name(prefix='clitestamgapikey', length=23),
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
    def test_amg_service_account_e2e(self, resource_group):

        self.kwargs.update({
            'name': self.create_random_name(prefix='clitestamgsvcacct', length=23),
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
            'name': self.create_random_name(prefix='clitestamge2e', length=23),
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
            'name': self.create_random_name(prefix='clitestamgbackup', length=23),
            'location': 'westcentralus',
            'name2': self.create_random_name(prefix='clitestamgbackup', length=23)
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

            # Close-out Instance
            self.cmd('grafana delete -g {rg} -n {name} --yes')
            self.cmd('grafana delete -g {rg} -n {name2} --yes')
            final_count = len(self.cmd('grafana list').get_output_in_json())
            self.assertTrue(final_count, 0)


    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='cli_test_amg')
    def test_amg_private_endpoint(self, resource_group):

        self.kwargs.update({
            'name': self.create_random_name(prefix='clitestamgmpe', length=23),
            'location': 'westcentralus',
            'monitor_name': self.create_random_name(prefix='clitestmon', length=20),
            'mpe_name': self.create_random_name(prefix='clitestmpe', length=20),
            'pe_name': self.create_random_name(prefix='clitestpe', length=20),
            'vnet_name': self.create_random_name(prefix='clitestvnet', length=20),
            'subnet_name': self.create_random_name(prefix='clitestsubnet', length=20),
            'conn_name': self.create_random_name(prefix='clitestconn', length=20),
            'sub': self.get_subscription_id(),
        })

        owner = self._get_signed_in_user()
        self.recording_processors.append(MSGraphNameReplacer(owner, MOCKED_USER_NAME))

        with unittest.mock.patch('azext_amg.custom._gen_guid', side_effect=self.create_guid):

            self.cmd('grafana create -g {rg} -n {name} -l {location}')

            self.cmd('monitor account create -n {monitor_name} -g {rg} -l {location}')

            self.cmd('grafana mpe create -g {rg} --workspace-name {name} -n {mpe_name} -l {location} --group-ids prometheusMetrics --private-link-resource-region {location} --private-link-resource-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Monitor/accounts/{monitor_name}', checks=[
                self.check('name', '{mpe_name}'),
                self.check('connectionState.status', 'Pending')
            ])

            self.cmd('grafana mpe list -g {rg} --workspace-name {name}', checks=[
                self.check('length([])', 1)
            ])

            self.cmd('grafana mpe show -g {rg} --workspace-name {name} -n {mpe_name}', checks=[
                self.check('name', '{mpe_name}')
            ])

            out = self.cmd('network private-endpoint-connection list -g {rg} -n {monitor_name} --type Microsoft.Monitor/accounts', checks=[
                self.check('length([])', 1)
            ]).get_output_in_json()

            self.kwargs.update({
                'mpe_id': out[0]['id']
            })

            self.cmd('network private-endpoint-connection approve --id {mpe_id} -d "Approved" ')

            self.cmd('grafana mpe show -g {rg} --workspace-name {name} -n {mpe_name}', checks=[
                self.check('connectionState.status', 'Pending')
            ])

            self.cmd('grafana mpe refresh -g {rg} --workspace-name {name}')

            self.cmd('grafana mpe show -g {rg} --workspace-name {name} -n {mpe_name}', checks=[
                self.check('connectionState.status', 'Approved')
            ])

            self.cmd('grafana mpe delete -g {rg} --workspace-name {name} -n {mpe_name} --yes')

            self.cmd('grafana mpe list -g {rg} --workspace-name {name}', checks=[
                self.check('length([])', 0)
            ])

            self.cmd('network vnet create -g {rg} -n {vnet_name} -l {location} --subnet-name {subnet_name}')

            self.cmd('network private-endpoint create -g {rg} -n {pe_name} --vnet-name {vnet_name} --subnet {subnet_name} --private-connection-resource-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Dashboard/grafana/{name} -l {location} --connection-name {conn_name} --group-id grafana') 

            self.cmd('grafana private-endpoint-connection list -g {rg} --workspace-name {name}', checks=[
                self.check('length([])', 1)
            ])

            self.cmd('grafana private-endpoint-connection update --private-link-service-connection-state description="Rejection Message" status="Rejected" -g {rg} --workspace-name {name} -n {conn_name}')

            self.cmd('grafana private-endpoint-connection show -g {rg} --workspace-name {name} -n {conn_name}', checks=[
                self.check('name', '{conn_name}'),
                self.check('privateLinkServiceConnectionState.status', 'Rejected'),
                self.check('privateLinkServiceConnectionState.description', 'Rejection Message')
            ])

            self.cmd('grafana private-endpoint-connection delete -g {rg} --workspace-name {name} -n {conn_name} --yes')

            self.cmd('grafana private-endpoint-connection list -g {rg} --workspace-name {name}', checks=[
                self.check('length([])', 0)
            ])


    @AllowLargeResponse(size_kb=3072)
    @ResourceGroupPreparer(name_prefix='cli_test_amg')
    def test_amg_integrations_monitor(self, resource_group):
        self.kwargs.update({
            'name': self.create_random_name(prefix='clitestamginteg', length=23),
            'location': 'westcentralus',
            'monitor_name': self.create_random_name(prefix='clitestamwinteg', length=23),
            'sub': self.get_subscription_id()
        })

        owner = self._get_signed_in_user()
        self.recording_processors.append(MSGraphNameReplacer(owner, MOCKED_USER_NAME))

        with unittest.mock.patch('azext_amg.custom._gen_guid', side_effect=self.create_guid):

            self.cmd('grafana create -g {rg} -n {name} -l {location}')

            self.cmd('monitor account create -n {monitor_name} -g {rg} -l {location}')

            self.cmd('grafana integrations monitor add -g {rg} -n {name} --monitor-sub-id {sub} --monitor-rg-name {rg} --monitor-name {monitor_name}')

            monitor_integrations = self.cmd('grafana integrations monitor list -g {rg} -n {name}', checks=[
                self.check('length([])', 1)
            ]).get_output_in_json()

            self.cmd(f'role assignment list --scope {monitor_integrations[0]} --role "Monitoring Data Reader"', checks=[
                self.check('length([])', 1)
            ])

            self._poll_for_amg_succeeded_state('{rg}', '{name}', timeout=500)  # Wait for workspace to complete 'Updating' provisioning state
            self.cmd('grafana integrations monitor delete -g {rg} -n {name} --monitor-sub-id {sub} --monitor-rg-name {rg} --monitor-name {monitor_name}')

            self.cmd('grafana integrations monitor list -g {rg} -n {name}', checks=[
                self.check('length([])', 0)
            ])

            self.cmd(f'role assignment list --scope {monitor_integrations[0]} --role "Monitoring Data Reader"', checks=[
                self.check('length([])', 0)
            ])


    def _get_signed_in_user(self):
        account_info = self.cmd('account show').get_output_in_json()
        if account_info['user']['type'] == 'user':
            return account_info['user']['name']
        return None
    

    def _poll_for_amg_succeeded_state(self, rg, name, timeout):
        start_time = time.time()
        interval = 10
        while time.time() - start_time < timeout:
            try:
                result = self.cmd('grafana show -g {rg} -n {name}').get_output_in_json()
                if result["properties"]['provisioningState'] == 'Succeeded':
                    return
                time.sleep(interval)
                interval *= 2
            except Exception:
                raise Exception('Failed to retrieve the AMG provisioning state')
        raise Exception('Timed out waiting for the AMG to reach the Succeeded provisioning state')
