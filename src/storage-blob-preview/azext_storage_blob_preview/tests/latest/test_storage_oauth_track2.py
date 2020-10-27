# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
from azure.cli.testsdk import (ScenarioTest, JMESPathCheck, JMESPathCheckExists, ResourceGroupPreparer,
                               StorageAccountPreparer, api_version_constraint, live_only)
from azure.cli.core.profiles import ResourceType
from ..storage_test_util import StorageScenarioMixin
from knack.util import CLIError


class StorageOauthTests(StorageScenarioMixin, ScenarioTest):
    def oauth_cmd(self, cmd, *args, **kwargs):
        return self.cmd(cmd + ' --auth-mode login', *args, **kwargs)

    @live_only()
    @ResourceGroupPreparer()
    @StorageAccountPreparer()
    def test_storage_blob_sas_oauth(self, resource_group, storage_account):
        """
        Test user delegaiton SAS.
        A user delegation SAS is secured with Azure Active Directory (Azure AD) credentials and also by the
        permissions specified for the SAS. A user delegation SAS applies to Blob storage only.

        """
        from datetime import datetime, timedelta
        expiry = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%MZ')

        account_info = self.get_account_info(resource_group, storage_account)
        container = self.create_container(account_info)
        local_file = self.create_temp_file(128, full_random=False)
        blob_name = self.create_random_name('blob', 16)

        self.kwargs.update({
            'expiry': expiry,
            'account': storage_account,
            'container': container,
            'local_file': local_file,
            'blob': blob_name
        })

        # ----user delegation key----
        with self.assertRaisesRegexp(CLIError, "incorrect usage: specify --as-user when --auth-mode login"):
            self.oauth_cmd('storage blob generate-sas --account-name {account} -n {blob} -c {container} '
                           '--expiry {expiry} --permissions r --https-only ')

        # test sas-token for a container
        sas = self.oauth_cmd('storage container generate-sas -n {container} --https-only --permissions dlrw '
                             '--expiry {expiry} --as-user --account-name {account} -otsv').output.strip()
        self.kwargs['container_sas'] = sas
        self.cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} '
                 '--account-name {account} --sas-token "{container_sas}"')

        # test sas-token for a blob
        sas = self.oauth_cmd('storage blob generate-sas -c {container} -n {blob} --https-only --permissions acdrw '
                             '--expiry {expiry} --as-user --account-name {account} -otsv').output.strip()
        self.kwargs['blob_sas'] = sas
        self.cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} --overwrite '
                 '--account-name {account} --sas-token "{blob_sas}"')

        self.cmd('storage blob show -c {container} -n {blob} --account-name {account} --sas-token {blob_sas}') \
            .assert_with_checks(JMESPathCheck('name', blob_name))

    @ResourceGroupPreparer()
    @StorageAccountPreparer()
    def test_storage_append_blob_upload_oauth(self, resource_group, storage_account):
        account_info = self.get_account_info(resource_group, storage_account)
        self.kwargs = {
            'account': storage_account,
            'container': self.create_container(account_info),
            'local_file': self.create_temp_file(1, full_random=False),
            'blob': self.create_random_name('blob', 16)
        }

        # create an append blob with pre-condition
        self.oauth_cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} --type append --if-none-match * '
                       '--account-name {account} ')
        result = self.oauth_cmd('storage blob show -n {blob} -c {container} --account-name {account}')\
            .get_output_in_json()
        self.assertEqual(result['properties']['blobType'], 'AppendBlob')
        length = int(result['properties']['contentLength'])

        # append if-none-match should throw exception
        with self.assertRaises(Exception):
            self.oauth_cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} --type append '
                           '--if-none-match * --account-name {} ')

        # append an append blob
        self.oauth_cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} --type append '
                       '--account-name {account} ')
        self.oauth_cmd('storage blob show -n {blob} -c {container} --account-name {account}').assert_with_checks(
            JMESPathCheck('properties.contentLength', length * 2),
            JMESPathCheck('properties.blobType', 'AppendBlob')
        )

        # append an append blob with maxsize_condition
        with self.assertRaises(Exception):
            self.oauth_cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} --type append '
                           '--maxsize-condition 1000 --account-name {account} ')

        # append an append blob with overwrite
        self.oauth_cmd('storage blob upload -c {container} -f "{local_file}" -n {blob} --type append '
                       '--overwrite --account-name {account} ')
        self.oauth_cmd('storage blob show -n {blob} -c {container} --account-name {account}').assert_with_checks(
            JMESPathCheck('properties.contentLength', length),
            JMESPathCheck('properties.blobType', 'AppendBlob')
        )

    @ResourceGroupPreparer()
    @StorageAccountPreparer()
    def test_storage_blob_show_oauth(self, resource_group, storage_account):
        account_info = self.get_account_info(resource_group, storage_account)

        self.kwargs.update({
            'rg': resource_group,
            'account': storage_account,
            'container': self.create_container(account_info=account_info),
            'local_file': self.create_temp_file(128),
            'block': self.create_random_name(prefix='block', length=12),
            'page': self.create_random_name(prefix='page', length=12),
        })

        # test block blob
        self.oauth_cmd('storage blob upload -c {container} -n {block} -f "{local_file}" --account-name {sa}')

        self.oauth_cmd('storage blob show -c {container} -n {block} --account-name {sa}')\
            .assert_with_checks(JMESPathCheck('name', self.kwargs['block']),
                                JMESPathCheck('deleted', False),
                                JMESPathCheck('encryptionScope', None),
                                JMESPathCheck('properties.appendBlobCommittedBlockCount', None),
                                JMESPathCheck('properties.blobTier', None),
                                JMESPathCheck('properties.blobTierChangeTime', None),
                                JMESPathCheck('properties.blobTierInferred', None),
                                JMESPathCheck('properties.blobType', 'BlockBlob'),
                                JMESPathCheck('properties.contentLength', 128 * 1024),
                                JMESPathCheck('properties.contentSettings.contentType', 'application/octet-stream'),
                                JMESPathCheck('properties.contentSettings.cacheControl', None),
                                JMESPathCheck('properties.contentSettings.contentDisposition', None),
                                JMESPathCheck('properties.contentSettings.contentEncooding', None),
                                JMESPathCheck('properties.contentSettings.contentLanguage', None),
                                JMESPathCheckExists('properties.contentSettings.contentMd5'),
                                JMESPathCheck('properties.copy.completionTime', None),
                                JMESPathCheck('properties.copy.id', None),
                                JMESPathCheck('properties.copy.progress', None),
                                JMESPathCheck('properties.copy.source', None),
                                JMESPathCheck('properties.copy.status', None),
                                JMESPathCheck('properties.copy.statusDescription', None),
                                JMESPathCheck('properties.pageRanges', None),
                                JMESPathCheckExists('properties.etag'),
                                JMESPathCheckExists('properties.creationTime'),
                                JMESPathCheck('properties.deletedTime', None),
                                JMESPathCheckExists('properties.etag'),
                                JMESPathCheckExists('properties.lastModified'),
                                JMESPathCheck('properties.lease.duration', None),
                                JMESPathCheck('properties.lease.state', 'available'),
                                JMESPathCheck('properties.lease.status', 'unlocked'),
                                JMESPathCheck('snapshot', None),
                                JMESPathCheck('objectReplicationDestinationPolicy', None),
                                JMESPathCheck('objectReplicationSourceProperties', []),
                                JMESPathCheck('rehydratePriority', None),
                                JMESPathCheck('tags', None),
                                JMESPathCheck('tagCount', None),
                                JMESPathCheck('versionId', None),
                                JMESPathCheck('lastAccessOn', None))

        self.kwargs['etag'] = self.oauth_cmd('storage blob show -c {container} -n {block} --account-name {sa}')\
            .get_output_in_json()['properties']['etag']

        # test page blob
        self.oauth_cmd('storage blob upload -c {container} -n {page} -f "{local_file}" --type page --account-name {sa}')
        self.oauth_cmd('storage blob show -c {container} -n {page} --account-name {sa}') \
            .assert_with_checks(JMESPathCheck('name', self.kwargs['page']),
                                JMESPathCheck('properties.blobType', 'PageBlob'),
                                JMESPathCheck('properties.contentLength', 128 * 1024),
                                JMESPathCheck('properties.contentSettings.contentType', 'application/octet-stream'),
                                JMESPathCheck('properties.pageBlobSequenceNumber', 0),
                                JMESPathCheckExists('properties.pageRanges'))

        # test snapshot
        self.kwargs['snapshot'] = self.oauth_cmd('storage blob snapshot -c {container} -n {block} --account-name {sa}')\
            .get_output_in_json()['snapshot']
        self.oauth_cmd('storage blob show -c {container} -n {block} --account-name {sa}') \
            .assert_with_checks(JMESPathCheck('name', self.kwargs['block']),
                                JMESPathCheck('properties.blobType', 'BlockBlob'),
                                JMESPathCheck('properties.contentLength', 128 * 1024),
                                JMESPathCheck('properties.contentSettings.contentType', 'application/octet-stream'),
                                JMESPathCheck('properties.pageRanges', None))

        # test precondition
        self.oauth_cmd('storage blob show -c {container} -n {block} --account-name {sa} --if-match {etag}') \
            .assert_with_checks(JMESPathCheck('name', self.kwargs['block']),
                                JMESPathCheck('properties.blobType', 'BlockBlob'),
                                JMESPathCheck('properties.contentLength', 128 * 1024),
                                JMESPathCheck('properties.contentSettings.contentType', 'application/octet-stream'),
                                JMESPathCheck('properties.pageRanges', None))

        self.oauth_cmd('storage blob show -c {container} -n {block} --account-name {sa} --if-match *') \
            .assert_with_checks(JMESPathCheck('name', self.kwargs['block']),
                                JMESPathCheck('properties.blobType', 'BlockBlob'),
                                JMESPathCheck('properties.contentLength', 128 * 1024),
                                JMESPathCheck('properties.contentSettings.contentType', 'application/octet-stream'),
                                JMESPathCheck('properties.pageRanges', None))

        from azure.core.exceptions import ResourceModifiedError, HttpResponseError
        with self.assertRaisesRegex(ResourceModifiedError, 'ErrorCode:ConditionNotMet'):
            self.oauth_cmd('storage blob show -c {container} -n {block} --account-name {sa} --if-none-match {etag}')

        with self.assertRaisesRegex(HttpResponseError, 'ErrorCode:UnsatisfiableCondition'):
            self.oauth_cmd('storage blob show -c {container} -n {block} --account-name {sa} --if-none-match *')

        with self.assertRaisesRegex(ResourceModifiedError, 'ErrorCode:ConditionNotMet'):
            self.oauth_cmd('storage blob show -c {container} -n {block} --account-name {sa} --if-unmodified-since "2020-06-29T06:32Z"')

        self.oauth_cmd('storage blob show -c {container} -n {block} --account-name {sa} --if-modified-since "2020-06-29T06:32Z"') \
            .assert_with_checks(JMESPathCheck('name', self.kwargs['block']),
                                JMESPathCheck('properties.blobType', 'BlockBlob'),
                                JMESPathCheck('properties.contentLength', 128 * 1024),
                                JMESPathCheck('properties.contentSettings.contentType', 'application/octet-stream'),
                                JMESPathCheck('properties.pageRanges', None))

    @ResourceGroupPreparer(name_prefix='clitest')
    @StorageAccountPreparer(kind='StorageV2', name_prefix='clitest', location='eastus2euap')
    def test_storage_container_soft_delete_oauth(self, resource_group, storage_account):
        import time
        account_info = self.get_account_info(resource_group, storage_account)
        container = self.create_container(account_info, prefix="con1")
        self.cmd('storage account blob-service-properties update -n {sa} -g {rg} --container-delete-retention-days 7 '
                 '--enable-container-delete-retention',
                 checks={
                     JMESPathCheck('containerDeleteRetentionPolicy.days', 7),
                     JMESPathCheck('containerDeleteRetentionPolicy.enabled', True)
                 })
        self.oauth_cmd('storage container list --account-name {} '.format(storage_account)) \
            .assert_with_checks(JMESPathCheck('length(@)', 1))

        self.oauth_cmd('storage container delete -n {} --account-name {} '.format(container, storage_account))
        self.oauth_cmd('storage container list --account-name {} '.format(storage_account)) \
            .assert_with_checks(JMESPathCheck('length(@)', 0))
        self.oauth_cmd('storage container list --include-deleted --account-name {} '.format(storage_account))\
            .assert_with_checks(JMESPathCheck('length(@)', 1),
                                JMESPathCheck('[0].deleted', True))

        time.sleep(30)
        version = self.oauth_cmd('storage container list --include-deleted --query [0].version -o tsv --account-name {}'
                                 .format(storage_account)).output.strip('\n')
        self.oauth_cmd('storage container restore -n {} --deleted-version {} --account-name {} '.format(
            container, version, storage_account))\
            .assert_with_checks(JMESPathCheck('containerName', container))

        self.oauth_cmd('storage container list --account-name {} '.format(storage_account)) \
            .assert_with_checks(JMESPathCheck('length(@)', 1))
        self.oauth_cmd('storage container list --include-deleted --account-name {} '.format(storage_account)) \
            .assert_with_checks(JMESPathCheck('length(@)', 1))
