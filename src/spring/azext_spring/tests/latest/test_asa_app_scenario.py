# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile

from knack.util import CLIError
from azure.cli.testsdk import (ScenarioTest, record_only)
from .custom_preparers import (SpringPreparer, SpringResourceGroupPreparer, SpringAppNamePreparer)
from .custom_recording_processor import (SpringTestEndpointReplacer)
from .custom_dev_setting_constant import SpringTestEnvironmentEnum

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AppDeploy(ScenarioTest):
    def __init__(self, method_name):
        super(AppDeploy, self).__init__(
            method_name,
            recording_processors=[SpringTestEndpointReplacer()]
        )

    def test_replacer(self):
        original_string = '"primaryKey":"xxxxxxxxx"abcdefg'
        expected_string = '"primaryKey":"fake"abcdefg'
        actual_string = SpringTestEndpointReplacer()._replace(original_string)
        self.assertEqual(expected_string, actual_string)

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.STANDARD['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.STANDARD['spring'])
    @SpringAppNamePreparer()
    def test_deploy_app(self, resource_group, spring, app):
        py_path = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(py_path, 'files/test.jar').replace("\\", "/")
        self.kwargs.update({
            'app': app,
            'serviceName': spring,
            'rg': resource_group,
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
        with self.assertRaisesRegex(CLIError, "112404: Exit code 1: application error"):
            self.cmd('spring app deploy -n {app} -g {rg} -s {serviceName} --artifact-path {file} --version v1')

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.STANDARD['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.STANDARD['spring'])
    @SpringAppNamePreparer()
    def test_deploy_app_1(self, resource_group, spring, app):
        py_path = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(py_path, 'files/test.jar').replace("\\", "/")
        self.kwargs.update({
            'app': app,
            'serviceName': spring,
            'rg': resource_group,
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

        # deploy change to .Net
        with self.assertRaisesRegex(CLIError, "112404: Exit code 0: purposely stopped"):
            self.cmd('spring app deploy -n {app} -g {rg} -s {serviceName} --artifact-path {file} --version v2 --runtime-version NetCore_31 --main-entry test')

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.STANDARD['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.STANDARD['spring'])
    @SpringAppNamePreparer()
    def test_deploy_app_2(self, resource_group, spring, app):
        py_path = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(py_path, 'files/test1.jar').replace("\\", "/")
        self.kwargs.update({
            'app': app,
            'serviceName': spring,
            'rg': resource_group,
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

        # deploy unexist file, the fail is expected
        with self.assertRaisesRegex(CLIError, "artifact path {} does not exist.".format(file_path)):
            self.cmd('spring app deploy -n {app} -g {rg} -s {serviceName} --artifact-path {file} --version v3')

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.STANDARD['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.STANDARD['spring'])
    @SpringAppNamePreparer()
    def test_deploy_app_3(self, resource_group, spring, app):
        py_path = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(py_path, 'files/test1.jar').replace("\\", "/")
        self.kwargs.update({
            'app': app,
            'serviceName': spring,
            'rg': resource_group,
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

        # deploy unexist file, the fail is expected
        with self.assertRaisesRegex(CLIError, "artifact path {} does not exist.".format(file_path)):
            self.cmd('spring app deployment create -n green --app {app} -g {rg} -s {serviceName} --instance-count 2 --artifact-path {file}')


class AppCRUD(ScenarioTest):
    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.STANDARD['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.STANDARD['spring'])
    @SpringAppNamePreparer()
    def test_app_crud(self, resource_group, spring, app):
        self.kwargs.update({
            'app': app,
            'serviceName': spring,
            'rg': resource_group
        })

        self.cmd('spring app create -n {app} -g {rg} -s {serviceName} --cpu 2  --env "foo=bar"', checks=[
            self.check('name', '{app}'),
            self.check('properties.testEndpointAuthState', "Enabled"),
            self.check('properties.activeDeployment.name', 'default'),
            self.check('properties.activeDeployment.properties.deploymentSettings.resourceRequests.cpu', '2'),
            self.check('properties.activeDeployment.sku.capacity', 1),
            self.check('properties.activeDeployment.properties.source.type', 'Jar'),
            self.check('properties.activeDeployment.properties.source.runtimeVersion', 'Java_11'),
            self.check('properties.activeDeployment.properties.deploymentSettings.environmentVariables', {'foo': 'bar'}),
        ])

        self.cmd('spring app update -n {app} -g {rg} -s {serviceName} --session-max-age 1800',
                 checks=[
                     self.check('properties.testEndpointAuthState', "Enabled"),
                ])

        # ingress only set session affinity
        self.cmd('spring app update -n {app} -g {rg} -s {serviceName} --session-affinity Cookie --session-max-age 1800 '
                 '--disable-test-endpoint-auth',
                 checks=[
                     self.check('name', '{app}'),
                     self.check('properties.testEndpointAuthState', "Disabled"),
                     self.check('properties.ingressSettings.readTimeoutInSeconds', '300'),
                     self.check('properties.ingressSettings.sendTimeoutInSeconds', '60'),
                     self.check('properties.ingressSettings.backendProtocol', 'Default'),
                     self.check('properties.ingressSettings.sessionAffinity', 'Cookie'),
                     self.check('properties.ingressSettings.sessionCookieMaxAge', '1800'),
                ])

        # green deployment copy settings from active, but still accept input as highest priority
        self.cmd('spring app deployment create -n green --app {app} -g {rg} -s {serviceName} --instance-count 2', checks=[
            self.check('name', 'green'),
            self.check('properties.testEndpointAuthState', None),
            self.check('properties.deploymentSettings.resourceRequests.cpu', '2'),
            self.check('properties.deploymentSettings.resourceRequests.memory', '1Gi'),
            self.check('properties.source.type', 'Jar'),
            self.check('properties.source.runtimeVersion', 'Java_11'),
            self.check('sku.capacity', 2),
            self.check('properties.deploymentSettings.environmentVariables', {'foo': 'bar'}),
        ])

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.STANDARD['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.STANDARD['spring'])
    @SpringAppNamePreparer()
    def test_app_crud_1(self, resource_group, spring, app):
        self.kwargs.update({
            'app': app,
            'serviceName': spring,
            'rg': resource_group
        })

        # public endpoint is assigned
        self.cmd('spring app create -n {app} -g {rg} -s {serviceName} --assign-endpoint --memory 2Gi', checks=[
            self.check('name', '{app}'),
            self.check('properties.activeDeployment.name', 'default'),
            self.check('properties.activeDeployment.properties.deploymentSettings.resourceRequests.cpu', '1'),
            self.check('properties.activeDeployment.properties.deploymentSettings.resourceRequests.memory', '2Gi'),
        ])

        # green deployment not copy settings from active
        self.cmd('spring app deployment create -n green --app {app} -g {rg} -s {serviceName} --skip-clone-settings', checks=[
            self.check('name', 'green'),
            self.check('properties.deploymentSettings.resourceRequests.cpu', '1'),
            self.check('properties.deploymentSettings.resourceRequests.memory', '1Gi'),
            self.check('sku.capacity', 1)
        ])

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['resource_group_name'])
    @SpringPreparer(dev_setting_name="AZURE_CLI_TEST_DEV_SPRING_NAME_TANZU",
                    additional_params="--sku Enterprise --disable-app-insights --enable-application-configuration-service \
                              --enable-service-registry --enable-gateway --enable-api-portal \
                              --enable-application-live-view  --enable-application-accelerator --enable-config-server")
    @SpringAppNamePreparer()
    def test_app_create_binding_tanzu_components(self, resource_group, spring, app):
        self.kwargs.update({
            'app': app,
            'serviceName': spring,
            'rg': resource_group
        })

        self.cmd('spring app create -n {app} -g {rg} -s {serviceName} --bind-service-registry --bind-application-configuration-service --bind-config-server', checks=[
            self.check('name', '{app}'),
            self.check('properties.addonConfigs.applicationConfigurationService.resourceId', "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}/configurationServices/default".format(self.get_subscription_id(), resource_group, spring)),
            self.check('properties.addonConfigs.serviceRegistry.resourceId', "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}/serviceRegistries/default".format(self.get_subscription_id(), resource_group, spring)),
            self.check('properties.addonConfigs.configServer.resourceId', "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}/configServers/default".format(self.get_subscription_id(), resource_group, spring))
        ])

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.ENTERPRISE['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.ENTERPRISE['spring'], location = 'eastasia')
    @SpringAppNamePreparer()
    def test_enterprise_app_crud(self, resource_group, spring, app):
        self.kwargs.update({
            'app': app,
            'serviceName': spring,
            'rg': resource_group
        })

        self.cmd('spring app create -n {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{app}'),
            self.check('properties.testEndpointAuthState', "Enabled"),
        ])

        # The property 'testEndpointAuthState' is enabled, update app without parameter 'disable-test-endpoint-auth'
        self.cmd('spring app update -n {app} -g {rg} -s {serviceName} --custom-actuator-port 8080 --custom-actuator-path actuator',
                 checks=[
                     self.check('properties.activeDeployment.properties.deploymentSettings.addonConfigs', {'appLiveView': {'actuatorPath': 'actuator', 'actuatorPort': 8080}}),
                     self.check('properties.testEndpointAuthState', "Enabled"),
                 ])

        # Update actuator configs, and test endpoint auth
        self.cmd('spring app update -n {app} -g {rg} -s {serviceName} --custom-actuator-port 8081 --custom-actuator-path actuator '
                 '--disable-test-endpoint-auth',
                 checks=[
                     self.check('properties.activeDeployment.properties.deploymentSettings.addonConfigs', {'appLiveView': {'actuatorPath': 'actuator', 'actuatorPort': 8081}}),
                     self.check('properties.testEndpointAuthState', "Disabled"),
                 ])
        # The property 'testEndpointAuthState' is disabled, update app without parameter 'disable-test-endpoint-auth'
        self.cmd('spring app update -n {app} -g {rg} -s {serviceName} --custom-actuator-port 8082',
                 checks=[
                     self.check('properties.activeDeployment.properties.deploymentSettings.addonConfigs', {'appLiveView': {'actuatorPath': 'actuator', 'actuatorPort': 8082}}),
                     self.check('properties.testEndpointAuthState', "Disabled"),
                 ])


class BlueGreenTest(ScenarioTest):

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.STANDARD['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.STANDARD['spring'])
    @SpringAppNamePreparer()
    def test_blue_green_deployment(self, resource_group, spring, app):
        self.kwargs.update({
            'app': app,
            'serviceName': spring,
            'rg': resource_group
        })

        self.cmd('spring app create -n {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{app}'),
            self.check('properties.activeDeployment.name', 'default')
        ])

        self.cmd('spring app deployment show -n default --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('properties.active', True)
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


@record_only()
class CustomImageTest(ScenarioTest):

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.STANDARD['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.STANDARD['spring'])
    @SpringAppNamePreparer()
    def test_app_deploy_container(self, resource_group, spring, app):
        self.kwargs.update({
            'app': app,
            'serviceName': spring,
            'containerImage': 'springio/gs-spring-boot-docker',
            'resourceGroup': resource_group,
        })

        self.cmd('spring app create -s {serviceName} -g {resourceGroup} -n {app}')

        self.cmd('spring app deploy -g {resourceGroup} -s {serviceName} -n {app} --container-image {containerImage}', checks=[
            self.check('properties.source.type', 'Container'),
            self.check('properties.source.customContainer.containerImage', '{containerImage}'),
            self.check('properties.source.customContainer.languageFramework', None),
        ])

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.STANDARD['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.STANDARD['spring'])
    @SpringAppNamePreparer()
    def test_app_deploy_container_command(self, resource_group, spring, app):
        self.kwargs.update({
            'app': app,
            'serviceName': spring,
            'containerImage': 'springio/gs-spring-boot-docker',
            'resourceGroup': resource_group,
        })

        self.cmd('spring app create -s {serviceName} -g {resourceGroup} -n {app}')

        self.cmd('spring app deploy -g {resourceGroup} -s {serviceName} -n {app} --container-image {containerImage} --container-command "java" --container-args "-cp /app/resources:/app/classes:/app/libs/* hello.Application"', checks=[
            self.check('properties.source.type', 'Container'),
            self.check('properties.source.customContainer.containerImage', '{containerImage}'),
            self.check('properties.source.customContainer.command', ['java']),
            self.check('properties.source.customContainer.args', ['-cp', '/app/resources:/app/classes:/app/libs/*', 'hello.Application']),
        ])
