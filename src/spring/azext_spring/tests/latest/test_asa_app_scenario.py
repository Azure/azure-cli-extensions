# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile

from knack.util import CLIError
from azure.cli.testsdk import (ScenarioTest, record_only)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

@record_only()
class AppDeploy(ScenarioTest):
    def test_deploy_app(self):
        py_path = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(py_path, 'files/test.jar').replace("\\","/")
        self.kwargs.update({
            'app': 'deploy',
            'serviceName': 'cli-unittest',
            'rg': 'cli',
            'file': file_path
        })

        self.cmd('spring app create -n {app} -g {rg} -s {serviceName} --cpu 2  --env "foo=bar" --runtime-version Java_11', checks=[
            self.check('name', '{app}'),
            self.check('properties.activeDeployment.name', 'default'),
            self.check('properties.activeDeployment.properties.deploymentSettings.resourceRequests.cpu', '2'),
            self.check('properties.activeDeployment.sku.capacity', 1),
            self.check('properties.activeDeployment.properties.source.type', 'Jar'),
            self.check('properties.activeDeployment.properties.source.runtimeVersion', 'Java_11'),
            self.check('properties.activeDeployment.properties.deploymentSettings.environmentVariables', {'foo': 'bar'}),
        ])

        # deploy fake file, the fail is expected
        with self.assertRaisesRegexp(CLIError, "112404: Exit code 1: application error."):
            self.cmd('spring app deploy -n {app} -g {rg} -s {serviceName} --artifact-path {file} --version v1')
        deployment = self.cmd('spring app deployment show -n default --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', 'default'),
            self.check('properties.deploymentSettings.resourceRequests.cpu', '2'),
            self.check('sku.capacity', 1),
            self.check('properties.source.type', 'Jar'),
            self.check('starts_with(properties.source.relativePath, `resources/`)', True),
            self.check('properties.source.runtimeVersion', 'Java_11'),
            self.check('properties.deploymentSettings.environmentVariables', {'foo': 'bar'}),
        ]).get_output_in_json()
        relative_path = deployment['properties']['source']['relativePath']

        self.cmd('spring app update -n {app} -g {rg} -s {serviceName} --runtime-version Java_8 --env "bas=baz"')
        self.cmd('spring app deployment show -n default --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', 'default'),
            self.check('properties.deploymentSettings.resourceRequests.cpu', '2'),
            self.check('properties.deploymentSettings.resourceRequests.memory', '1Gi'),
            self.check('sku.capacity', 1),
            self.check('properties.source.type', 'Jar'),
            self.check('properties.source.relativePath', relative_path),
            self.check('properties.source.version', 'v1'),
            self.check('properties.source.runtimeVersion', 'Java_8'),
            self.check('properties.deploymentSettings.environmentVariables', {'bas': 'baz'}),
        ])

        # deploy change to .Net
        with self.assertRaisesRegexp(CLIError, "112404: Exit code 0: purposely stopped."):
            self.cmd('spring app deploy -n {app} -g {rg} -s {serviceName} --artifact-path {file} --version v2 --runtime-version NetCore_31 --main-entry test')
        deployment = self.cmd('spring app deployment show -n default --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', 'default'),
            self.check('properties.deploymentSettings.resourceRequests.cpu', '2'),
            self.check('sku.capacity', 1),
            self.check('properties.source.type', 'NetCoreZip'),
            self.check('starts_with(properties.source.relativePath, `resources/`)', True),
            self.check('properties.source.runtimeVersion', 'NetCore_31'),
            self.check('properties.deploymentSettings.environmentVariables', {'bas': 'baz'}),
        ]).get_output_in_json()
        relative_path = deployment['properties']['source']['relativePath']

        self.cmd('spring app update -n {app} -g {rg} -s {serviceName} --main-entry test1')
        self.cmd('spring app deployment show -n default --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', 'default'),
            self.check('properties.deploymentSettings.resourceRequests.cpu', '2'),
            self.check('properties.deploymentSettings.resourceRequests.memory', '1Gi'),
            self.check('sku.capacity', 1),
            self.check('properties.source.type', 'NetCoreZip'),
            self.check('properties.source.relativePath', relative_path),
            self.check('properties.source.version', 'v2'),
            self.check('properties.source.runtimeVersion', 'NetCore_31'),
            self.check('properties.source.netCoreMainEntryPath', 'test1'),
            self.check('properties.deploymentSettings.environmentVariables', {'bas': 'baz'}),
        ])

        # keep deploy .net
        with self.assertRaisesRegexp(CLIError, "112404: Exit code 0: purposely stopped."):
            self.cmd('spring app deploy -n {app} -g {rg} -s {serviceName} --artifact-path {file} --version v3 --main-entry test3')
        self.cmd('spring app deployment show -n default --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', 'default'),
            self.check('properties.deploymentSettings.resourceRequests.cpu', '2'),
            self.check('sku.capacity', 1),
            self.check('properties.source.type', 'NetCoreZip'),
            self.check('starts_with(properties.source.relativePath, `resources/`)', True),
            self.check('properties.source.runtimeVersion', 'NetCore_31'),
            self.check('properties.source.netCoreMainEntryPath', 'test3'),
            self.check('properties.deploymentSettings.environmentVariables', {'bas': 'baz'}),
        ])


@record_only()
class AppCRUD(ScenarioTest):
    def test_app_crud(self):
        self.kwargs.update({
            'app': 'test-crud-app',
            'serviceName': 'cli-unittest',
            'rg': 'cli'
        })

        self.cmd('spring app create -n {app} -g {rg} -s {serviceName} --cpu 2  --env "foo=bar"', checks=[
            self.check('name', '{app}'),
            self.check('properties.activeDeployment.name', 'default'),
            self.check('properties.activeDeployment.properties.deploymentSettings.resourceRequests.cpu', '2'),
            self.check('properties.activeDeployment.sku.capacity', 1),
            self.check('properties.activeDeployment.properties.source.type', 'Jar'),
            self.check('properties.activeDeployment.properties.source.runtimeVersion', 'Java_11'),
            self.check('properties.activeDeployment.properties.deploymentSettings.environmentVariables', {'foo': 'bar'}),
        ])

        # green deployment copy settings from active, but still accept input as highest priority
        self.cmd('spring app deployment create -n green --app {app} -g {rg} -s {serviceName} --instance-count 2', checks=[
            self.check('name', 'green'),
            self.check('properties.deploymentSettings.resourceRequests.cpu', '2'),
            self.check('properties.deploymentSettings.resourceRequests.memory', '1Gi'),
            self.check('properties.source.type', 'Jar'),
            self.check('properties.source.runtimeVersion', 'Java_11'),
            self.check('sku.capacity', 2),
            self.check('properties.deploymentSettings.environmentVariables', {'foo': 'bar'}),
        ])

        self.cmd('spring app update -n {app} -g {rg} -s {serviceName} --runtime-version Java_11', checks=[
            self.check('properties.activeDeployment.name', 'default'),
            self.check('properties.activeDeployment.properties.deploymentSettings.resourceRequests.cpu', '2'),
            self.check('properties.activeDeployment.properties.deploymentSettings.resourceRequests.memory', '1Gi'),
            self.check('properties.activeDeployment.sku.capacity', 1),
            self.check('properties.activeDeployment.properties.source.type', 'Jar'),
            self.check('properties.activeDeployment.properties.source.runtimeVersion', 'Java_11'),
            self.check('properties.activeDeployment.properties.deploymentSettings.environmentVariables', {'foo': 'bar'}),
        ])
        self.cmd('spring app delete -n {app} -g {rg} -s {serviceName}')


    def test_app_crud_1(self):
        self.kwargs.update({
            'app': 'test-crud-app-1',
            'serviceName': 'cli-unittest',
            'rg': 'cli'
        })

        # public endpoint is assigned
        self.cmd('spring app create -n {app} -g {rg} -s {serviceName} --assign-endpoint --memory 2Gi', checks=[
            self.check('name', '{app}'),
            self.check('properties.activeDeployment.name', 'default'),
            self.check('properties.activeDeployment.properties.deploymentSettings.resourceRequests.cpu', '1'),
            self.check('properties.activeDeployment.properties.deploymentSettings.resourceRequests.memory', '2Gi'),
            self.check('properties.url', 'https://{serviceName}-{app}.azuremicroservices.io')
        ])

        # green deployment not copy settings from active
        self.cmd('spring app deployment create -n green --app {app} -g {rg} -s {serviceName} --skip-clone-settings', checks=[
            self.check('name', 'green'),
            self.check('properties.deploymentSettings.resourceRequests.cpu', '1'),
            self.check('properties.deploymentSettings.resourceRequests.memory', '1Gi'),
            self.check('sku.capacity', 1)
        ])


@record_only()
class BlueGreenTest(ScenarioTest):

    def test_blue_green_deployment(self):
        self.kwargs.update({
            'app': 'test-app-blue-green',
            'serviceName': 'cli-unittest',
            'rg': 'cli'
        })

        self.cmd('spring app create -n {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{app}'),
            self.check('properties.activeDeployment.name', 'default')
        ])

        self.cmd('spring app deployment create --app {app} -n green -g {rg} -s {serviceName}', checks=[
            self.check('name', 'green'),
            self.check('properties.active', False)
        ])

        result = self.cmd('spring app deployment list --app {app} -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) == 2)

        self.cmd('spring app set-deployment -d green -n {app} -g {rg} -s {serviceName}')

        self.cmd('spring app show -n {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{app}'),
            self.check('properties.activeDeployment.name', 'green')
        ])

        self.cmd('spring app deployment show -n default --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('properties.active', False)
        ])

        self.cmd('spring app deployment show -n green --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('properties.active', True)
        ])

        self.cmd('spring app unset-deployment -n {app} -g {rg} -s {serviceName}')

        self.cmd('spring app deployment show -n default --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('properties.active', False)
        ])

        self.cmd('spring app deployment show -n green --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('properties.active', False)
        ])

        self.cmd('spring app delete -n {app} -g {rg} -s {serviceName}')


@record_only()
class I2aTLSTest(ScenarioTest):
    def test_app_i2a_tls(self):
        self.kwargs.update({
            'app': 'test-i2atls-app',
            'serviceName': 'cli-unittest',
            'rg': 'cli'
        })

        self.cmd('spring app create -n {app} -g {rg} -s {serviceName}')

        self.cmd('spring app update -n {app} -g {rg} -s {serviceName} --enable-ingress-to-app-tls true', checks=[
            self.check('properties.enableEndToEndTls', True)
        ])

        self.cmd('spring app update -n {app} -g {rg} -s {serviceName} --enable-ingress-to-app-tls false', checks=[
            self.check('properties.enableEndToEndTls', False)
        ])

        self.cmd('spring app update -n {app} -g {rg} -s {serviceName} --enable-end-to-end-tls true', checks=[
            self.check('properties.enableEndToEndTls', True)
        ])

        self.cmd('spring app update -n {app} -g {rg} -s {serviceName} --enable-end-to-end-tls false', checks=[
            self.check('properties.enableEndToEndTls', False)
        ])


@record_only()
class GenerateDumpTest(ScenarioTest):
    def test_generate_deployment_dump(self):
        file_path = os.path.join(tempfile.gettempdir(), 'dumpfile.txt')
        self.kwargs.update({
            'app': 'test-app-dump',
            'deployment': 'default',
            'serviceName': 'cli-unittest',
            'resourceGroup': 'cli',
            'path': file_path
        })
        result = self.cmd('spring app deployment show -g {resourceGroup} -s {serviceName} --app {app} -n {deployment}').get_output_in_json()
        self.kwargs['instance'] = result['properties'].get('instances', [{}])[0].get('name')
        self.assertTrue(self.kwargs['instance'])
        self.cmd('spring app deployment generate-heap-dump -g {resourceGroup} -s {serviceName} --app {app} --deployment {deployment} --app-instance {instance} --file-path {path}')


@record_only()
class VnetPublicEndpointTest(ScenarioTest):
    def test_vnet_public_endpoint(self):
        self.kwargs.update({
            'app': 'test-app',
            'serviceName': 'cli-unittest',
            'rg': 'cli'
        })

        self.cmd('spring app create -n {app} -g {rg} -s {serviceName} --assign-public-endpoint true', checks=[
            self.check('properties.vnetAddons.publicEndpoint', True)
        ])

        self.cmd('spring app update -n {app} -g {rg} -s {serviceName} --assign-public-endpoint false', checks=[
            self.check('properties.vnetAddons.publicEndpoint', False)
        ])

        self.cmd('spring app update -n {app} -g {rg} -s {serviceName} --assign-public-endpoint true', checks=[
            self.check('properties.vnetAddons.publicEndpoint', True)
        ])


@record_only()
class ClientAuthTest(ScenarioTest):
    def test_client_auth(self):
        self.kwargs.update({
            'cert': 'test-cert',
            'keyVaultUri': 'https://integration-test-prod.vault.azure.net/',
            'kvCertName': 'cli-unittest',
            'app': 'test-client-auth',
            'serviceName': 'cli-unittest',
            'rg': 'cli',
            'location': 'eastus'
        })

        cert_id = self.cmd(
            'spring certificate add --name {cert} --vault-uri {keyVaultUri} --only-public-cert '
            '--vault-certificate-name {kvCertName} -g {rg} -s {serviceName} --query "id" -o tsv').output.strip()
        app_create_cmd_template = 'spring app update -n {{app}} -s {{serviceName}} -g {{rg}} --client-auth-certs {}'
        self.cmd(app_create_cmd_template.format(cert_id), checks=[
            self.check('properties.ingressSettings.clientAuth.certificates[0]', cert_id)
        ])
