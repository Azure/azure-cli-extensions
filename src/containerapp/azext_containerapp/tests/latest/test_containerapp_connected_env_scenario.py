# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import time

import yaml

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, live_only)
from azure.cli.testsdk.decorators import serial_test

from .common import TEST_LOCATION
from .custom_preparers import ConnectedClusterPreparer
from .utils import create_extension_and_custom_location

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappPreviewScenarioTest(ScenarioTest):
    @serial_test()
    @ResourceGroupPreparer(location="southcentralus", random_name_length=15)
    @ConnectedClusterPreparer(location=TEST_LOCATION)
    def test_containerapp_preview_connected_env_e2e(self, resource_group, connected_cluster_name):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        custom_location_name = "my-custom-location"
        create_extension_and_custom_location(self, resource_group, connected_cluster_name, custom_location_name)

        # create connected environment with client or create a command for connected?
        sub_id = self.cmd('az account show').get_output_in_json()['id']
        static_ip = '1.1.1.1'
        env_name = 'my-connected-env'
        custom_location_id = f"/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/Microsoft.ExtendedLocation/customLocations/{custom_location_name}"
        self.cmd(f'containerapp connected-env create -g {resource_group} --name {env_name} --custom-location {custom_location_name} --static-ip {static_ip} -d "InstrumentationKey=TestInstrumentationKey;IngestionEndpoint=https://ingestion.com/;LiveEndpoint=https://abc.com/"', checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('extendedLocation.name', custom_location_id),
            JMESPathCheck('properties.staticIp', static_ip)
        ])

        connected_env_resource_id = self.cmd(f'containerapp connected-env show -g {resource_group} --name {env_name}', checks=[
            JMESPathCheck('name', env_name),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('extendedLocation.name', custom_location_id),
            JMESPathCheck('properties.staticIp', static_ip)
        ]).get_output_in_json()['id']

        self.cmd(f'containerapp connected-env list -g {resource_group} --custom-location {custom_location_name}', expect_failure=False, checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', env_name),
            JMESPathCheck('[0].properties.provisioningState', "Succeeded"),
            JMESPathCheck('[0].extendedLocation.name', custom_location_id),
            JMESPathCheck('[0].properties.staticIp', static_ip)
        ])
        ca_name1 = self.create_random_name(prefix='containerapp1', length=24)
        self.cmd(
            f'az containerapp create --name {ca_name1} --resource-group {resource_group} --environment {env_name} --image "mcr.microsoft.com/k8se/quickstart:latest" --ingress external --target-port 80 --environment-type connected',
            checks=[
                JMESPathCheck('name', ca_name1),
                JMESPathCheck('properties.environmentId', connected_env_resource_id),
                JMESPathCheck('properties.provisioningState', "Succeeded")
            ])

        self.cmd(f'containerapp connected-env delete -g {resource_group} --name {env_name} --yes', expect_failure=True)

        self.cmd('containerapp delete -n {} -g {} --yes'.format(ca_name1, resource_group))

        self.cmd(f'containerapp connected-env delete -g {resource_group} --name {env_name} --yes', expect_failure=False)

        self.cmd(f'containerapp connected-env list -g {resource_group} --custom-location {custom_location_name}', expect_failure=False, checks=[
                JMESPathCheck('length(@)', 0),
        ])

    @serial_test()
    @ResourceGroupPreparer(location="southcentralus", random_name_length=15)
    @ConnectedClusterPreparer(location=TEST_LOCATION)
    def test_containerapp_preview_connected_env_storage(self, resource_group, connected_cluster_name):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        custom_location_name = "my-custom-location"
        create_extension_and_custom_location(self, resource_group, connected_cluster_name, custom_location_name)

        # create connected environment with client or create a command for connected?
        sub_id = self.cmd('az account show').get_output_in_json()['id']
        env_name = 'my-connected-env'
        custom_location_id = f"/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/Microsoft.ExtendedLocation/customLocations/{custom_location_name}"
        self.cmd(
            f'containerapp connected-env create -g {resource_group} --name {env_name} --custom-location {custom_location_name}',
            checks=[
                JMESPathCheck('name', env_name),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('extendedLocation.name', custom_location_id)
            ])
        storage_name = self.create_random_name(prefix='storage', length=24)
        shares_name = self.create_random_name(prefix='share', length=24)

        self.cmd('storage account create -g {} -n {} --kind StorageV2 --sku Standard_LRS --enable-large-file-share'.format(resource_group, storage_name))
        self.cmd('storage share-rm create -g {} -n {} --storage-account {} --access-tier "TransactionOptimized" --quota 1024'.format(resource_group, shares_name, storage_name))

        storage_keys = self.cmd('az storage account keys list -g {} -n {}'.format(resource_group, storage_name)).get_output_in_json()[0]

        self.cmd('containerapp connected-env storage set -g {} -n {} --storage-name {} --azure-file-account-name {} --azure-file-account-key {} --access-mode ReadOnly --azure-file-share-name {}'
                 .format(resource_group, env_name, storage_name, storage_name, storage_keys["value"], shares_name), checks=[
            JMESPathCheck('name', storage_name),
            JMESPathCheck('properties.azureFile.accountName', storage_name),
            JMESPathCheck('properties.azureFile.shareName', shares_name),
            JMESPathCheck('properties.azureFile.accessMode', 'ReadOnly'),
        ])

        self.cmd('containerapp connected-env storage show -g {} -n {} --storage-name {}'.format(resource_group, env_name, storage_name), checks=[
            JMESPathCheck('name', storage_name),
            JMESPathCheck('properties.azureFile.accountName', storage_name),
            JMESPathCheck('properties.azureFile.shareName', shares_name),
            JMESPathCheck('properties.azureFile.accessMode', 'ReadOnly'),
        ])

        self.cmd('containerapp connected-env storage list -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('[0].name', storage_name),
        ])

        self.cmd('containerapp connected-env storage remove -g {} -n {} --storage-name {} --yes'.format(resource_group, env_name, storage_name))

        self.cmd('containerapp connected-env storage list -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

    @serial_test()
    @ResourceGroupPreparer(location="southcentralus", random_name_length=15)
    @ConnectedClusterPreparer(location=TEST_LOCATION)
    def test_containerapp_preview_connected_env_dapr_components(self, resource_group, connected_cluster_name):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        custom_location_name = "my-custom-location"
        create_extension_and_custom_location(self, resource_group, connected_cluster_name, custom_location_name)

        # create connected environment with client or create a command for connected?
        sub_id = self.cmd('az account show').get_output_in_json()['id']
        env_name = 'my-connected-env'
        custom_location_id = f"/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/Microsoft.ExtendedLocation/customLocations/{custom_location_name}"
        dapr_comp_name = self.create_random_name(prefix='dapr-component', length=24)

        self.cmd(
            f'containerapp connected-env create -g {resource_group} --name {env_name} --custom-location {custom_location_name}',
            checks=[
                JMESPathCheck('name', env_name),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('extendedLocation.name', custom_location_id)
            ])
        
        file_ref, dapr_file = tempfile.mkstemp(suffix=".yml")

        dapr_yaml = """
                name: statestore
                componentType: state.azure.blobstorage
                version: v1
                metadata:
                - name: accountName
                  secretRef: storage-account-name
                secrets:
                - name: storage-account-name
                  value: storage-account-name
                """

        daprloaded = yaml.safe_load(dapr_yaml)

        with open(dapr_file, 'w') as outfile:
            yaml.dump(daprloaded, outfile, default_flow_style=False)

        containerapp_env = self.cmd('containerapp connected-env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        while containerapp_env["properties"]["provisioningState"].lower() == "waiting":
            time.sleep(5)
            containerapp_env = self.cmd('containerapp connected-env show -g {} -n {}'.format(resource_group, env_name)).get_output_in_json()

        self.cmd('containerapp connected-env dapr-component set -n {} -g {} --dapr-component-name {} --yaml {}'
                 .format(env_name, resource_group, dapr_comp_name, dapr_file.replace( os.sep, os.sep + os.sep)),
                 checks=[
                     JMESPathCheck('name', dapr_comp_name),
                 ])

        os.close(file_ref)

        self.cmd('containerapp connected-env dapr-component list -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', dapr_comp_name),
        ])

        self.cmd('containerapp connected-env dapr-component show -n {} -g {} --dapr-component-name {}'.format(env_name, resource_group, dapr_comp_name), checks=[
            JMESPathCheck('name', dapr_comp_name),
            JMESPathCheck('properties.version', 'v1'),
            JMESPathCheck('properties.secrets[0].name', 'storage-account-name'),
            JMESPathCheck('properties.metadata[0].name', 'accountName'),
            JMESPathCheck('properties.metadata[0].secretRef', 'storage-account-name'),
        ])

        self.cmd('containerapp connected-env dapr-component remove -n {} -g {} --dapr-component-name {}'.format(env_name, resource_group, dapr_comp_name))

        self.cmd('containerapp connected-env dapr-component list -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('length(@)', 0),
        ])

    @serial_test()
    @live_only()  # generate_randomized_cert_name cause No match for the request (<Request (PUT) /my-connected-env/certificates/my-connected-e-clitest.rg0000-8d2d-6528?
    @ResourceGroupPreparer(location="southcentralus", random_name_length=15)
    @ConnectedClusterPreparer(location=TEST_LOCATION)
    def test_containerapp_preview_connected_env_certificate(self, resource_group, connected_cluster_name):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        custom_location_name = "my-custom-location"
        create_extension_and_custom_location(self, resource_group, connected_cluster_name, custom_location_name)

        # create connected environment with client or create a command for connected?
        sub_id = self.cmd('az account show').get_output_in_json()['id']
        env_name = 'my-connected-env'
        custom_location_id = f"/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/Microsoft.ExtendedLocation/customLocations/{custom_location_name}"
        self.cmd(
            f'containerapp connected-env create -g {resource_group} --name {env_name} --custom-location {custom_location_name}',
            checks=[
                JMESPathCheck('name', env_name),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('extendedLocation.name', custom_location_id)
            ])
        self.cmd('containerapp connected-env certificate list -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        # test that non pfx or pem files are not supported
        txt_file = os.path.join(TEST_DIR, 'cert.txt')
        self.cmd('containerapp connected-env certificate upload -g {} -n {} --certificate-file "{}"'.format(resource_group, env_name, txt_file), expect_failure=True)

        # test pfx file with password
        pfx_file = os.path.join(TEST_DIR, 'cert.pfx')
        pfx_password = 'test12'
        cert = self.cmd('containerapp connected-env certificate upload -g {} -n {} --certificate-file "{}" --password {}'.format(
            resource_group, env_name, pfx_file, pfx_password), checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('type', "Microsoft.App/connectedEnvironments/certificates"),
        ]).get_output_in_json()

        cert_name = cert["name"]
        cert_id = cert["id"]
        cert_thumbprint = cert["properties"]["thumbprint"]

        self.cmd('containerapp connected-env certificate list -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].properties.thumbprint', cert_thumbprint),
            JMESPathCheck('[0].name', cert_name),
            JMESPathCheck('[0].id', cert_id),
        ])

        # list certs with a wrong location
        self.cmd('containerapp connected-env certificate upload -g {} -n {} --certificate-file "{}"'.format(resource_group, env_name, pfx_file), expect_failure=True)

        self.cmd('containerapp connected-env certificate list -n {} -g {} --certificate {}'.format(env_name, resource_group, cert_name), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', cert_name),
            JMESPathCheck('[0].id', cert_id),
            JMESPathCheck('[0].properties.thumbprint', cert_thumbprint),
        ])

        self.cmd('containerapp connected-env certificate list -n {} -g {} --certificate {}'.format(env_name, resource_group, cert_id), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', cert_name),
            JMESPathCheck('[0].id', cert_id),
            JMESPathCheck('[0].properties.thumbprint', cert_thumbprint),
        ])

        self.cmd('containerapp connected-env certificate list -n {} -g {} --thumbprint {}'.format(env_name, resource_group, cert_thumbprint), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', cert_name),
            JMESPathCheck('[0].id', cert_id),
            JMESPathCheck('[0].properties.thumbprint', cert_thumbprint),
        ])

        self.cmd('containerapp connected-env certificate delete -n {} -g {} --thumbprint {} --certificate {} --yes'.format(env_name, resource_group, cert_thumbprint, cert_name), expect_failure=False)
        self.cmd('containerapp connected-env certificate list -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])
        self.cmd('containerapp connected-env delete -g {} -n {} --yes'.format(resource_group, env_name), expect_failure=False)

    @serial_test()
    @ResourceGroupPreparer(location="southcentralus", random_name_length=15)
    @ConnectedClusterPreparer(location=TEST_LOCATION)
    def test_containerapp_preview_connected_env_certificate_upload_with_certificate_name(self, resource_group, connected_cluster_name):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        custom_location_name = "my-custom-location"
        create_extension_and_custom_location(self, resource_group, connected_cluster_name, custom_location_name)

        # create connected environment with client or create a command for connected?
        sub_id = self.cmd('az account show').get_output_in_json()['id']
        env_name = 'my-connected-env'
        custom_location_id = f"/subscriptions/{sub_id}/resourceGroups/{resource_group}/providers/Microsoft.ExtendedLocation/customLocations/{custom_location_name}"
        self.cmd(
            f'containerapp connected-env create -g {resource_group} --name {env_name} --custom-location {custom_location_name}',
            checks=[
                JMESPathCheck('name', env_name),
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('extendedLocation.name', custom_location_id)
            ])
        self.cmd('containerapp connected-env certificate list -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        # test that non pfx or pem files are not supported
        txt_file = os.path.join(TEST_DIR, 'cert.txt')
        self.cmd('containerapp connected-env certificate upload -g {} -n {} --certificate-file "{}"'.format(resource_group, env_name, txt_file), expect_failure=True)

        # test pfx file with password
        pfx_file = os.path.join(TEST_DIR, 'cert.pfx')
        pfx_password = 'test12'
        cert_pfx_name = self.create_random_name(prefix='cert-pfx', length=24)
        cert = self.cmd(
            'containerapp connected-env certificate upload -g {} -n {} -c {} --certificate-file "{}" --password {}'.format(
                resource_group, env_name, cert_pfx_name, pfx_file, pfx_password), checks=[
                JMESPathCheck('properties.provisioningState', "Succeeded"),
                JMESPathCheck('name', cert_pfx_name),
                JMESPathCheck('type', "Microsoft.App/connectedEnvironments/certificates"),
            ]).get_output_in_json()

        cert_name = cert["name"]
        cert_id = cert["id"]
        cert_thumbprint = cert["properties"]["thumbprint"]

        self.cmd('containerapp connected-env certificate list -n {} -g {}'.format(env_name, resource_group), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].properties.thumbprint', cert_thumbprint),
            JMESPathCheck('[0].name', cert_name),
            JMESPathCheck('[0].id', cert_id),
        ])

        # list certs with a wrong location
        self.cmd('containerapp connected-env certificate upload -g {} -n {} --certificate-file "{}"'.format(resource_group, env_name, pfx_file), expect_failure=True)

        self.cmd(
            'containerapp connected-env certificate list -n {} -g {} --certificate {}'.format(env_name, resource_group,
                                                                                              cert_name), checks=[
                JMESPathCheck('length(@)', 1),
                JMESPathCheck('[0].name', cert_name),
                JMESPathCheck('[0].id', cert_id),
                JMESPathCheck('[0].properties.thumbprint', cert_thumbprint),
            ])

        self.cmd(
            'containerapp connected-env certificate list -n {} -g {} --certificate {}'.format(env_name, resource_group,
                                                                                              cert_id), checks=[
                JMESPathCheck('length(@)', 1),
                JMESPathCheck('[0].name', cert_name),
                JMESPathCheck('[0].id', cert_id),
                JMESPathCheck('[0].properties.thumbprint', cert_thumbprint),
            ])

        self.cmd(
            'containerapp connected-env certificate list -n {} -g {} --thumbprint {}'.format(env_name, resource_group,
                                                                                             cert_thumbprint), checks=[
                JMESPathCheck('length(@)', 1),
                JMESPathCheck('[0].name', cert_name),
                JMESPathCheck('[0].id', cert_id),
                JMESPathCheck('[0].properties.thumbprint', cert_thumbprint),
            ])

        self.cmd(
            'containerapp connected-env certificate delete -n {} -g {} --thumbprint {} --certificate {} --yes'.format(
                env_name, resource_group, cert_thumbprint, cert_name), expect_failure=False)
        self.cmd('containerapp connected-env certificate list -g {} -n {}'.format(resource_group, env_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])
        self.cmd('containerapp connected-env delete -g {} -n {} --yes'.format(resource_group, env_name), expect_failure=False)
