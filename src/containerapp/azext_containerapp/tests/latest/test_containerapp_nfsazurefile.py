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
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, live_only, StorageAccountPreparer)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))
from .common import (TEST_LOCATION, STAGE_LOCATION, write_test_file,
                     clean_up_test_file,
                     )
from .utils import create_containerapp_env


class ContainerAppMountNfsAzureFileTest(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus")
    def test_container_app_mount_nfsazurefile_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env = self.create_random_name(prefix='env', length=24)
        app = self.create_random_name(prefix='app1', length=24)
        storage = self.create_random_name(prefix='storage', length=24)
        share = self.create_random_name(prefix='share', length=10)
        vnet = self.create_random_name(prefix='vnet', length=10)
        subnet = 'nfstest'
        storage_account_location = TEST_LOCATION
        vnet_location = TEST_LOCATION
        if format_location(storage_account_location) == format_location(STAGE_LOCATION):
            storage_account_location = "eastus"
            vnet_location = "centralus"
        self.cmd(
            f'az network vnet create --resource-group {resource_group}  --name {vnet} --address-prefix 10.0.0.0/16 --subnet-name {subnet} --subnet-prefixes 10.0.0.0/23 --location {vnet_location}')
        self.cmd(
            f'az network vnet subnet update --resource-group {resource_group} --vnet-name {vnet} --name {subnet} --service-endpoints Microsoft.Storage.Global --delegations Microsoft.App/environments')

        subnet_resource = self.cmd(
            f'az network vnet subnet show --resource-group {resource_group} --vnet-name {vnet} --name {subnet}')

        self.cmd(
            f'az storage account create --resource-group {resource_group}  --name {storage} --location {storage_account_location} --kind FileStorage --sku Premium_LRS --enable-large-file-share --https-only false --output none')
        self.cmd(
            f'az storage share-rm create --resource-group {resource_group}  --storage-account {storage} --name {share} --quota 1024 --enabled-protocols NFS --root-squash NoRootSquash --output none')
        self.cmd(
            f'az storage account network-rule add --resource-group {resource_group} --account-name {storage} --vnet-name {vnet} --subnet {subnet}'
        )

        subnet_id = subnet_resource.get_output_in_json()['id']

        print(*subnet_id, file=sys.stdout)
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
