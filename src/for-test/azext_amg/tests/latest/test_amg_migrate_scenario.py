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

from .test_definitions import (test_data_source, test_data_source_different_uid, test_dashboard, test_dashboard_with_datasource, test_dashboard_with_datasource_short_uid, test_data_source_long_uid2, test_data_source_short_uid2)
from .recording_processors import ApiKeyServiceAccountTokenReplacer

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AmgMigrateScenarioTest(ScenarioTest):

    def __init__(self, method_name):
        super().__init__(method_name, recording_processors=[
            ApiKeyServiceAccountTokenReplacer()
        ])

    def _setup_migrate_instances(self):
        # migrate from amg1 to amg2
        amg1 = self.cmd('grafana create -g {rg} -n {name} -l {location}').get_output_in_json()
        amg2 = self.cmd('grafana create -g {rg} -n {name2} -l {location}').get_output_in_json()

        # Ensure RBAC changes are propagated
        time.sleep(120)

        # enable service accounts so I can create service tokens
        self.cmd('grafana update -g {rg} -n {name} --service-account Enabled')

        # set up folder
        self.kwargs.update({
            'folderTitle': 'Test Folder',
            'id': amg1['id'],
            'id2': amg2['id']
        })
        self.cmd('grafana folder create -g {rg} -n {name} --title "{folderTitle}"')
        self.cmd('grafana folder list -g {rg} -n {name}').get_output_in_json()

        # set up data source
        self.kwargs.update({
            'dataSourceDefinition': test_data_source,
            'dataSourceName': test_data_source["name"]
        })
        ds1 = self.cmd('grafana data-source create -g {rg} -n {name} --definition "{dataSourceDefinition}"').get_output_in_json()
        self.kwargs.update({
            'amg1_datasource_uid': ds1['datasource']['uid']
        })

        # create dashboard
        dashboard_title = test_dashboard["dashboard"]["title"]
        slug = dashboard_title.lower().replace(' ', '-')

        self.kwargs.update({
            'dashboardDefinition': test_dashboard,
            'dashboardTitle': dashboard_title,
            'dashboardTitle2': dashboard_title + '2',
            'dashboardTitle3': dashboard_title + '3',
            'dashboardSlug': slug,
        })
        self.kwargs['dashboardDefinition']['dashboard']['uid'] = 'mg2OAlTVa'  # control the uid to prevent auto generated uid with possible '-' that breaks the command

        # dashboard under own folder
        response_create = self.cmd('grafana dashboard create -g {rg} -n {name} --folder "{folderTitle}"  --definition "{dashboardDefinition}" --title "{dashboardTitle}"').get_output_in_json()
        self.kwargs.update({
            'dashboardUid': response_create["uid"],
        })

        # 2nd dashboard under "General"
        self.kwargs['dashboardDefinition']['dashboard']['uid'] = 'mg2OAlTVb'
        response_create = self.cmd('grafana dashboard create -g {rg} -n {name}  --definition "{dashboardDefinition}" --title "{dashboardTitle2}"').get_output_in_json()
        self.kwargs.update({
            'dashboardUid2': response_create["uid"],
        })

        # 3rd dashboard under own folder
        self.kwargs['dashboardDefinition']['dashboard']['uid'] = 'mg2OAlTVc'
        response_create = self.cmd('grafana dashboard create -g {rg} -n {name} --folder "{folderTitle}"  --definition "{dashboardDefinition}" --title "{dashboardTitle3}"').get_output_in_json()
        self.kwargs.update({
            'dashboardUid3': response_create["uid"],
        })

        return amg1, amg2

    @AllowLargeResponse(size_kb=3072)
    @ResourceGroupPreparer(name_prefix='cli_test_amg', location='westcentralus')
    def test_amg_migrate_dry_run(self, resource_group):
        # Simple E2E test for migration where we create a new AMG instance, create a folder, data source, and dashboard, then migrate to a new AMG instance
        self.kwargs.update({
            'name': self.create_random_name(prefix='clitestamgmigrate', length=23),
            'location': 'westcentralus',
            'name2': self.create_random_name(prefix='clitestamgmigrate', length=23)
        })

        owner = self._get_signed_in_user()
        self.recording_processors.append(MSGraphNameReplacer(owner, MOCKED_USER_NAME))

        with unittest.mock.patch('azext_amg.custom._gen_guid', side_effect=self.create_guid):
            amg1, amg2 = self._setup_migrate_instances()
           
            # prepare to migrate
            # get the service account token:
            self.kwargs.update({
                'serviceAccountName': self.create_random_name(prefix='clitestamgmigrate', length=23)
            })

            # Note: admin is needed since we need admin permisisons to access folder permissions
            self.cmd('az grafana service-account create -g {rg} -n {name} --service-account {serviceAccountName} --role admin')
            service_account_token = self.cmd('az grafana service-account token create -g {rg} -n {name} --service-account {serviceAccountName} --token {serviceAccountName}_token --time-to-live 1d').get_output_in_json()

            self.kwargs.update({
                'srcUrl': amg1['properties']['endpoint'],
                'serviceAccountToken': service_account_token['key']
            })

            data_source_list_output = self.cmd('grafana data-source list -g {rg} -n {name2}').get_output_in_json()
            folder_list_output = self.cmd('grafana folder list -g {rg} -n {name2}').get_output_in_json()
            dashboard_list_output = self.cmd('grafana dashboard list -g {rg} -n {name2}').get_output_in_json()

            with unittest.mock.patch('azext_amg.utils.search_annotations', side_effect=self._return_200_and_empty_list):
                # now migrate to new instance 2.
                self.cmd('grafana migrate -g {rg} -n {name2} -s {srcUrl} -t {serviceAccountToken} --dry-run')

            data_source_list_output_after = self.cmd('grafana data-source list -g {rg} -n {name2}').get_output_in_json()
            folder_list_output_after = self.cmd('grafana folder list -g {rg} -n {name2}').get_output_in_json()
            dashboard_list_output_after = self.cmd('grafana dashboard list -g {rg} -n {name2}').get_output_in_json()

            self.assertTrue(data_source_list_output == data_source_list_output_after)
            self.assertTrue(folder_list_output == folder_list_output_after)
            self.assertTrue(dashboard_list_output == dashboard_list_output_after)

            # Close-out Instance
            self.cmd('grafana delete -g {rg} -n {name} --yes')
            self.cmd('grafana delete -g {rg} -n {name2} --yes')
            final_count = len(self.cmd('grafana list').get_output_in_json())
            self.assertTrue(final_count, 0)


    @AllowLargeResponse(size_kb=3072)
    @ResourceGroupPreparer(name_prefix='cli_test_amg', location='westcentralus')
    def test_amg_migrate_override(self, resource_group):
        # Simple E2E test for migration where we create a new AMG instance, create a folder, data source, and dashboard, then migrate to a new AMG instance
        self.kwargs.update({
            'name': self.create_random_name(prefix='clitestamgmigrate', length=23),
            'location': 'westcentralus',
            'name2': self.create_random_name(prefix='clitestamgmigrate', length=23)
        })

        owner = self._get_signed_in_user()
        self.recording_processors.append(MSGraphNameReplacer(owner, MOCKED_USER_NAME))

        with unittest.mock.patch('azext_amg.custom._gen_guid', side_effect=self.create_guid):
            amg1, amg2 = self._setup_migrate_instances()

            test_dashboard2 = test_dashboard
            test_dashboard2["dashboard"]["title"] = test_dashboard2["dashboard"]["title"] + '2_amg'
            dashboard_title = test_dashboard["dashboard"]["title"]
            self.kwargs.update({
                'dashboardTitle2_amg': dashboard_title,
                'dashboardDefinition2': test_dashboard2
            })

            # recreate the second dashboard in amg2: keeping the same uid
            self.kwargs['dashboardDefinition']['dashboard']['uid'] = 'mg2OAlTVb'
            response_create = self.cmd('grafana dashboard create -g {rg} -n {name2}  --definition "{dashboardDefinition2}" --title "{dashboardTitle2_amg}"').get_output_in_json()
            self.kwargs.update({
                'dashboardUid2_amg2': response_create["uid"],
            })
           
            # prepare to migrate
            # get the service account token:
            self.kwargs.update({
                'serviceAccountName': self.create_random_name(prefix='clitestamgmigrate', length=23)
            })

            # Note: admin is needed since we need admin permisisons to access folder permissions
            self.cmd('az grafana service-account create -g {rg} -n {name} --service-account {serviceAccountName} --role admin')
            service_account_token = self.cmd('az grafana service-account token create -g {rg} -n {name} --service-account {serviceAccountName} --token {serviceAccountName}_token --time-to-live 1d').get_output_in_json()

            self.kwargs.update({
                'srcUrl': amg1['properties']['endpoint'],
                'serviceAccountToken': service_account_token['key']
            })

            self.cmd('grafana dashboard show -g {rg} -n {name2} --dashboard "{dashboardUid2_amg2}"', checks=[
                self.check("[dashboard.title]", "['{dashboardTitle2_amg}']"),
                self.check("[dashboard.uid]", "['{dashboardUid2_amg2}']"),
                self.check("[meta.folderTitle]", "['General']")])

            with unittest.mock.patch('azext_amg.utils.search_annotations', side_effect=self._return_200_and_empty_list):
                # now migrate to new instance 2.
                self.cmd('grafana migrate -g {rg} -n {name2} -s {srcUrl} -t {serviceAccountToken}')

            # the uid shouldn't be updated since we didn't overwrite.
            self.cmd('grafana dashboard show -g {rg} -n {name2} --dashboard "{dashboardUid2_amg2}"', checks=[
                self.check("[dashboard.title]", "['{dashboardTitle2_amg}']"),
                self.check("[dashboard.uid]", "['{dashboardUid2_amg2}']"),
                self.check("[meta.folderTitle]", "['General']")])

            with unittest.mock.patch('azext_amg.utils.search_annotations', side_effect=self._return_200_and_empty_list):
                self.cmd('grafana migrate -g {rg} -n {name2} -s {srcUrl} -t {serviceAccountToken} --overwrite')

            # the uid should stay the same, but the title & other properies should be updated.
            self.cmd('grafana dashboard show -g {rg} -n {name2} --dashboard "{dashboardUid2_amg2}"', checks=[
                self.check("[dashboard.title]", "['{dashboardTitle2}']"),
                self.check("[dashboard.uid]", "['{dashboardUid2_amg2}']"),
                self.check("[meta.folderTitle]", "['General']")])
            
            # Close-out Instance
            self.cmd('grafana delete -g {rg} -n {name} --yes')
            self.cmd('grafana delete -g {rg} -n {name2} --yes')
            final_count = len(self.cmd('grafana list').get_output_in_json())
            self.assertTrue(final_count, 0)


    @AllowLargeResponse(size_kb=3072)
    @ResourceGroupPreparer(name_prefix='cli_test_amg', location='westcentralus')
    def test_amg_migrate_remapping(self, resource_group):
        # Simple E2E test for migration where we create a new AMG instance, create a folder, data source, and dashboard, then migrate to a new AMG instance
        self.kwargs.update({
            'name': self.create_random_name(prefix='clitestamgmigrate', length=23),
            'location': 'westcentralus',
            'name2': self.create_random_name(prefix='clitestamgmigrate', length=23)
        })

        owner = self._get_signed_in_user()
        self.recording_processors.append(MSGraphNameReplacer(owner, MOCKED_USER_NAME))

        with unittest.mock.patch('azext_amg.custom._gen_guid', side_effect=self.create_guid):
            amg1, amg2 = self._setup_migrate_instances()

            dashboard_title = test_dashboard_with_datasource["dashboard"]["title"]
            self.kwargs.update({
                'dashboardDefinitionDatasource': test_dashboard_with_datasource,
                'dashboardTitle4': dashboard_title + '4',
                'dataSourceDefinitionDifferentUid': test_data_source_different_uid,
                'dashboardDefinitionDatasourceShortUid': test_dashboard_with_datasource_short_uid,
                'dashboardTitle5': dashboard_title + '5',
                'dataSourceDefinitionLongUid2': test_data_source_long_uid2,
                'dataSourceDefinitionShortUid2': test_data_source_short_uid2,
            })
            self.kwargs['dashboardDefinitionDatasource']['dashboard']['uid'] = 'mg2OAlTVd'  # control the uid to prevent auto generated uid with possible '-' that breaks the command
            self.kwargs['dashboardDefinitionDatasourceShortUid']['dashboard']['uid'] = 'mg2OAlTVe'  # control the uid to prevent auto generated uid with possible '-' that breaks the command

            response_create = self.cmd('grafana dashboard create -g {rg} -n {name}  --definition "{dashboardDefinitionDatasource}" --title "{dashboardTitle4}"').get_output_in_json()
            self.kwargs.update({
                'dashboardUid4': response_create["uid"],
            })

            ds2 = self.cmd('grafana data-source create -g {rg} -n {name2} --definition "{dataSourceDefinitionDifferentUid}"').get_output_in_json()
            self.kwargs.update({
                'amg2_datasource_uid': ds2['datasource']['uid']
            })

            # create short uid in amg 1 (to do shortuid -> longuid remapping test)
            self.cmd('grafana data-source create -g {rg} -n {name} --definition "{dataSourceDefinitionShortUid2}"').get_output_in_json()

            # Create the dashboard
            response_create2 = self.cmd('grafana dashboard create -g {rg} -n {name}  --definition "{dashboardDefinitionDatasourceShortUid}" --title "{dashboardTitle5}"').get_output_in_json()
            self.kwargs.update({
                'dashboardUid5': response_create2["uid"],
            })

            # create the long data source for amg2.
            ds2 = self.cmd('grafana data-source create -g {rg} -n {name2} --definition "{dataSourceDefinitionLongUid2}"').get_output_in_json()
            self.kwargs.update({
                'amg2_datasource_uid_long': ds2['datasource']['uid']
            })

            # prepare to migrate
            # get the service account token:
            self.kwargs.update({
                'serviceAccountName': self.create_random_name(prefix='clitestamgmigrate', length=23)
            })

            # Note: admin is needed since we need admin permisisons to access folder permissions
            self.cmd('az grafana service-account create -g {rg} -n {name} --service-account {serviceAccountName} --role admin')
            service_account_token = self.cmd('az grafana service-account token create -g {rg} -n {name} --service-account {serviceAccountName} --token {serviceAccountName}_token --time-to-live 1d').get_output_in_json()

            self.kwargs.update({
                'srcUrl': amg1['properties']['endpoint'],
                'serviceAccountToken': service_account_token['key']
            })

            with unittest.mock.patch('azext_amg.utils.search_annotations', side_effect=self._return_200_and_empty_list):
                # now migrate to new instance 2.
                self.cmd('grafana migrate -g {rg} -n {name2} -s {srcUrl} -t {serviceAccountToken}')

            self.cmd('grafana dashboard show -g {rg} -n {name2} --dashboard "{dashboardUid4}"', checks=[
                self.check("[dashboard.title]", "['{dashboardTitle4}']"),
                self.check("[dashboard.panels[0].datasource.uid]", "['{amg2_datasource_uid}']"),
                self.check("[meta.folderTitle]", "['General']")])
            
            self.cmd('grafana dashboard show -g {rg} -n {name2} --dashboard "{dashboardUid5}"', checks=[
                self.check("[dashboard.title]", "['{dashboardTitle5}']"),
                self.check("[dashboard.panels[0].datasource.uid]", "['{amg2_datasource_uid_long}']"),
                self.check("[meta.folderTitle]", "['General']")])
            
            # Close-out Instance
            self.cmd('grafana delete -g {rg} -n {name} --yes')
            self.cmd('grafana delete -g {rg} -n {name2} --yes')
            final_count = len(self.cmd('grafana list').get_output_in_json())
            self.assertTrue(final_count, 0)


    @AllowLargeResponse(size_kb=3072)
    @ResourceGroupPreparer(name_prefix='cli_test_amg', location='westcentralus')
    def test_amg_migrate_simple_e2e(self, resource_group):
        # Simple E2E test for migration where we create a new AMG instance, create a folder, data source, and dashboard, then migrate to a new AMG instance
        self.kwargs.update({
            'name': self.create_random_name(prefix='clitestamgmigrate', length=23),
            'location': 'westcentralus',
            'name2': self.create_random_name(prefix='clitestamgmigrate', length=23)
        })

        owner = self._get_signed_in_user()
        self.recording_processors.append(MSGraphNameReplacer(owner, MOCKED_USER_NAME))

        with unittest.mock.patch('azext_amg.custom._gen_guid', side_effect=self.create_guid):
            # migrate from amg1 to amg2
            amg1, amg2 = self._setup_migrate_instances()
         
            # prepare to migrate
            # get the service account token:
            self.kwargs.update({
                'serviceAccountName': self.create_random_name(prefix='clitestamgmigrate', length=23)
            })

            # Note: admin is needed since we need admin permisisons to access folder permissions
            self.cmd('az grafana service-account create -g {rg} -n {name} --service-account {serviceAccountName} --role admin')
            service_account_token = self.cmd('az grafana service-account token create -g {rg} -n {name} --service-account {serviceAccountName} --token {serviceAccountName}_token --time-to-live 1d').get_output_in_json()

            self.kwargs.update({
                'srcUrl': amg1['properties']['endpoint'],
                'serviceAccountToken': service_account_token['key']
            })

            with unittest.mock.patch('azext_amg.utils.search_annotations', side_effect=self._return_200_and_empty_list):
                # now migrate to new instance 2.
                self.cmd('grafana migrate -g {rg} -n {name2} -s {srcUrl} -t {serviceAccountToken}')

            # check that the migrate worked.
            # migrate shouldn't have modified the first instance.
            self.cmd('grafana data-source show -g {rg} -n {name} --data-source "{dataSourceName}"')
            self.cmd('grafana folder show -g {rg} -n {name} --folder "{folderTitle}"')
            self.cmd('grafana dashboard show -g {rg} -n {name} --dashboard "{dashboardUid}"', checks=[
                self.check("[dashboard.title]", "['{dashboardTitle}']"),
                self.check("[meta.folderTitle]", "['{folderTitle}']")])
            self.cmd('grafana dashboard show -g {rg} -n {name} --dashboard "{dashboardUid2}"', checks=[
                self.check("[dashboard.title]", "['{dashboardTitle2}']"),
                self.check("[meta.folderTitle]", "['General']")])
            self.cmd('grafana dashboard show -g {rg} -n {name} --dashboard "{dashboardUid3}"', checks=[
                self.check("[dashboard.title]", "['{dashboardTitle3}']"),
                self.check("[meta.folderTitle]", "['{folderTitle}']")])

            # the new things should exist.
            self.cmd('grafana data-source show -g {rg} -n {name2} --data-source "{dataSourceName}"')
            self.cmd('grafana folder show -g {rg} -n {name2} --folder "{folderTitle}"')
            self.cmd('grafana dashboard show -g {rg} -n {name2} --dashboard "{dashboardUid}"', checks=[
                self.check("[dashboard.title]", "['{dashboardTitle}']"),
                self.check("[meta.folderTitle]", "['{folderTitle}']")])
            self.cmd('grafana dashboard show -g {rg} -n {name2} --dashboard "{dashboardUid2}"', checks=[
                self.check("[dashboard.title]", "['{dashboardTitle2}']"),
                self.check("[meta.folderTitle]", "['General']")])
            self.cmd('grafana dashboard show -g {rg} -n {name2} --dashboard "{dashboardUid3}"', checks=[
                self.check("[dashboard.title]", "['{dashboardTitle3}']"),
                self.check("[meta.folderTitle]", "['{folderTitle}']")])

            # TODO: Add snapshot / annotation testing when creating them via the CLI is supported.

            # Close-out Instance
            self.cmd('grafana delete -g {rg} -n {name} --yes')
            self.cmd('grafana delete -g {rg} -n {name2} --yes')
            final_count = len(self.cmd('grafana list').get_output_in_json())
            self.assertTrue(final_count, 0)

    def _get_signed_in_user(self):
        account_info = self.cmd('account show').get_output_in_json()
        if account_info['user']['type'] == 'user':
            return account_info['user']['name']
        return None

    def _return_200_and_empty_list(self, grafana_url, ts_from, ts_to, http_get_headers):
        return 200, []
