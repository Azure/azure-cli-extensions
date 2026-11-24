# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
import time
import unittest

from azure.cli.command_modules.containerapp._utils import format_location

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)
from .custom_preparers import SubnetPreparer

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))
from .common import (TEST_LOCATION, STAGE_LOCATION, write_test_file,
                     clean_up_test_file,
                     )
from .utils import create_containerapp_env


class ContainerAppMountNfsAzureFileTest(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus")
    @SubnetPreparer(location="centralus", vnet_name='test-vnet', vnet_address_prefixes='14.0.0.0/22',
                    subnet_address_prefixes='14.0.0.0/23',
                    delegations='Microsoft.App/environments', service_endpoints="Microsoft.Storage.Global")
    def test_container_app_mount_nfsazurefile_e2e(self, resource_group, subnet_id, vnet_name, subnet_name):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env = self.create_random_name(prefix='env', length=24)
        app = self.create_random_name(prefix='app1', length=24)
        storage = self.create_random_name(prefix='storage', length=24)
        share = self.create_random_name(prefix='share', length=10)

        storage_account_location = TEST_LOCATION
        if format_location(storage_account_location) == format_location(STAGE_LOCATION):
            storage_account_location = "eastus"

        storage_id = self.cmd(
            f'az storage account create --resource-group {resource_group} --name {storage} '
            f'--location {storage_account_location} --kind FileStorage --sku Premium_LRS '
            '--enable-large-file-share --https-only false --public-network-access Disabled '
            '--allow-blob-public-access false '
            '--tags "Az.Sec.DisableLocalAuth.Storage::Skip=true"').get_output_in_json()['id']
        self.cmd(f'az network vnet subnet create -g {resource_group} --vnet-name {vnet_name} '
                 '-n private-endpoints --address-prefixes 14.0.2.0/24')
        self.cmd(f'az network private-dns zone create -g {resource_group} -n privatelink.file.core.windows.net')
        self.cmd(f'az network private-dns link vnet create -g {resource_group} '
                 f'-z privatelink.file.core.windows.net -n storage-link --virtual-network {vnet_name} '
                 '--registration-enabled false')
        self.cmd(f'az network private-endpoint create -g {resource_group} -n storage-endpoint '
                 f'--location centralus --vnet-name {vnet_name} --subnet private-endpoints '
                 f'--private-connection-resource-id {storage_id} --group-ids file --connection-name storage-connection')
        self.cmd(f'az network private-endpoint dns-zone-group create -g {resource_group} '
                 '--endpoint-name storage-endpoint -n default '
                 '--private-dns-zone privatelink.file.core.windows.net --zone-name file')
        self.cmd(
            f'az storage share-rm create --resource-group {resource_group}  --storage-account {storage} --name {share} --quota 1024 --enabled-protocols NFS --root-squash NoRootSquash --output none')

        print(subnet_id, file=sys.stdout)
        create_containerapp_env(self, env, resource_group, TEST_LOCATION, subnet_id)
        containerapp_env = self.cmd('containerapp env show -n {} -g {}'.format(env, resource_group), checks=[
            JMESPathCheck('name', env)
        ]).get_output_in_json()

        self.cmd(f'az containerapp env storage set -g {resource_group} -n {env} --storage-type NfsAzureFile --storage-name {share} -s {storage}.file.core.windows.net -f /{storage}/{share} --access-mode ReadWrite', checks=[
            JMESPathCheck('name', share),
            JMESPathCheck('properties.nfsAzureFile.server', f'{storage}.file.core.windows.net'),
            JMESPathCheck('properties.nfsAzureFile.shareName', f'/{storage}/{share}'),
            JMESPathCheck('properties.nfsAzureFile.accessMode', 'ReadWrite'),
        ])

        self.cmd('containerapp env storage show -n {} -g {} --storage-name {}'.format(env, resource_group, share), checks=[
            JMESPathCheck('name', share),
            JMESPathCheck('properties.nfsAzureFile.server', f'{storage}.file.core.windows.net'),
            JMESPathCheck('properties.nfsAzureFile.shareName', f'/{storage}/{share}'),
            JMESPathCheck('properties.nfsAzureFile.accessMode', 'ReadWrite'),
        ])

        self.cmd('containerapp env storage list -n {} -g {}'.format(env, resource_group), checks=[
            JMESPathCheck('[0].name', share),
            JMESPathCheck('[0].properties.nfsAzureFile.server', f'{storage}.file.core.windows.net'),
            JMESPathCheck('[0].properties.nfsAzureFile.shareName', f'/{storage}/{share}'),
            JMESPathCheck('[0].properties.nfsAzureFile.accessMode', 'ReadWrite'),
        ])

        containerapp_yaml_text = f"""
                    location: {TEST_LOCATION}
                    type: Microsoft.App/containerApps
                    name: {app}
                    resourceGroup: {resource_group}
                    properties:
                        managedEnvironmentId: {containerapp_env["id"]}
                        configuration:
                            activeRevisionsMode: Single
                            ingress:
                                external: true
                                allowInsecure: true
                                targetPort: 80
                                traffic:
                                    - latestRevision: true
                                      weight: 100
                                transport: Auto
                        template:
                            containers:
                                - image: mcr.microsoft.com/k8se/quickstart:latest
                                  name: acamounttest
                                  resources:
                                      cpu: 0.5
                                      ephemeralStorage: 1Gi
                                      memory: 1Gi
                                  volumeMounts:
                                      - mountPath: /mnt/data
                                        volumeName: nfs-azure-files-volume
                                        subPath: sub
                            volumes:
                                - name: nfs-azure-files-volume
                                  storageType: NfsAzureFile
                                  storageName: {share}
                                  mountOptions: hard
                    """
        containerapp_file_name = f"{self._testMethodName}_containerapp.yml"

        write_test_file(containerapp_file_name, containerapp_yaml_text)
        self.cmd(
            f'az containerapp create -g {resource_group} --environment {env} -n {app} --yaml {containerapp_file_name}')

        self.cmd('containerapp show -g {} -n {}'.format(resource_group, app), checks=[
            JMESPathCheck('properties.template.volumes[0].storageType', 'NfsAzureFile'),
            JMESPathCheck('properties.template.volumes[0].storageName', share),
            JMESPathCheck('properties.template.volumes[0].name', 'nfs-azure-files-volume'),
            JMESPathCheck('properties.template.volumes[0].mountOptions', 'hard'),
            JMESPathCheck('properties.template.containers[0].volumeMounts[0].subPath', 'sub'),
            JMESPathCheck('properties.template.containers[0].volumeMounts[0].mountPath', '/mnt/data'),
            JMESPathCheck('properties.template.containers[0].volumeMounts[0].volumeName', 'nfs-azure-files-volume'),
        ])

        self.cmd('az containerapp revision list -g {} -n {}'.format(resource_group, app), checks=[
            JMESPathCheck('[0].properties.template.volumes[0].storageType', 'NfsAzureFile'),
            JMESPathCheck('[0].properties.template.volumes[0].storageName', share),
            JMESPathCheck('[0].properties.template.volumes[0].name', 'nfs-azure-files-volume'),
            JMESPathCheck('[0].properties.template.volumes[0].mountOptions', 'hard'),
            JMESPathCheck('[0].properties.template.containers[0].volumeMounts[0].subPath', 'sub'),
            JMESPathCheck('[0].properties.template.containers[0].volumeMounts[0].mountPath', '/mnt/data'),
            JMESPathCheck('[0].properties.template.containers[0].volumeMounts[0].volumeName', 'nfs-azure-files-volume'),
        ])
        clean_up_test_file(containerapp_file_name)

        containerapp_yaml_text = f"""
                           location: {TEST_LOCATION}
                           type: Microsoft.App/containerApps
                           name: {app}
                           resourceGroup: {resource_group}
                           properties:
                               managedEnvironmentId: {containerapp_env["id"]}
                               configuration:
                                   activeRevisionsMode: Single
                                   ingress:
                                       external: true
                                       allowInsecure: true
                                       targetPort: 80
                                       traffic:
                                           - latestRevision: true
                                             weight: 100
                                       transport: Auto
                               template:
                                   containers:
                                       - image: mcr.microsoft.com/k8se/quickstart:latest
                                         name: acamounttest
                                         resources:
                                             cpu: 0.5
                                             ephemeralStorage: 1Gi
                                             memory: 1Gi
                                         volumeMounts:
                                             - mountPath: /mnt/data
                                               volumeName: nfs-azure-files-volume
                                               subPath: sub2
                                   volumes:
                                       - name: nfs-azure-files-volume
                                         storageType: NfsAzureFile
                                         storageName: {share}
                                         mountOptions: hard
                           """
        containerapp_file_name = f"{self._testMethodName}_containerapp_1.yml"

        write_test_file(containerapp_file_name, containerapp_yaml_text)
        self.cmd(
            f'az containerapp update -g {resource_group} -n {app} --yaml {containerapp_file_name}')

        self.cmd('containerapp show -g {} -n {}'.format(resource_group, app), checks=[
            JMESPathCheck('properties.template.volumes[0].storageType', 'NfsAzureFile'),
            JMESPathCheck('properties.template.volumes[0].storageName', share),
            JMESPathCheck('properties.template.volumes[0].name', 'nfs-azure-files-volume'),
            JMESPathCheck('properties.template.volumes[0].mountOptions', 'hard'),
            JMESPathCheck('properties.template.containers[0].volumeMounts[0].subPath', 'sub2'),
            JMESPathCheck('properties.template.containers[0].volumeMounts[0].mountPath', '/mnt/data'),
            JMESPathCheck('properties.template.containers[0].volumeMounts[0].volumeName', 'nfs-azure-files-volume'),
        ])

        self.cmd('az containerapp revision list -g {} -n {}'.format(resource_group, app), checks=[
            JMESPathCheck('[1].properties.template.volumes[0].storageType', 'NfsAzureFile'),
            JMESPathCheck('[1].properties.template.volumes[0].storageName', share),
            JMESPathCheck('[1].properties.template.volumes[0].name', 'nfs-azure-files-volume'),
            JMESPathCheck('[1].properties.template.volumes[0].mountOptions', 'hard'),
            JMESPathCheck('[1].properties.template.containers[0].volumeMounts[0].subPath', 'sub2'),
            JMESPathCheck('[1].properties.template.containers[0].volumeMounts[0].mountPath', '/mnt/data'),
            JMESPathCheck('[1].properties.template.containers[0].volumeMounts[0].volumeName', 'nfs-azure-files-volume'),
        ])

        clean_up_test_file(containerapp_file_name)
