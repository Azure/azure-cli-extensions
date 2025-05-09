# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import json
from azure.cli.testsdk import (ScenarioTest, record_only)
from knack.log import get_logger

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

@record_only()
class BuildpackBindingTest(ScenarioTest):

    def test_buildpack_binding(self):
        py_path = os.path.abspath(os.path.dirname(__file__))
        
        self.kwargs.update({
            'serviceName': 'test-buildpack-binding',
            'rg': 'enterprise-test',
            'bindingName': "test-binding-name",
            'bindingType': "ApplicationInsights",
            'properties': "a=b b=c",
            'secrets': "x=y y=z",
            'builderName': "test-builder-name",
        })

        self.cmd('spring-cloud build-service builder buildpack-binding create --name {bindingName} --type {bindingType} \
            --properties {properties} --secrets {secrets} -g {rg} -s {serviceName}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.bindingType', 'ApplicationInsights'),
                self.check('properties.launchProperties.properties', {'a': 'b', 'b': 'c'}),
                self.check('properties.launchProperties.secrets', {'x': '*', 'y': '*'}),
            ])

        self.cmd('spring-cloud build-service builder buildpack-binding show --name {bindingName} -g {rg} -s {serviceName}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.bindingType', 'ApplicationInsights'),
            ])

        self.cmd('spring-cloud build-service builder buildpack-binding set --name {bindingName} --type NewRelic \
            --properties a=b --secrets c=d -g {rg} -s {serviceName}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.bindingType', 'NewRelic'),
                self.check('properties.launchProperties.properties', {'a': 'b'}),
                self.check('properties.launchProperties.secrets', {'c': '*'}),
            ])

        self.cmd('spring-cloud build-service builder buildpack-binding delete --name {bindingName} -g {rg} -s {serviceName} --yes')

        self.cmd('spring-cloud build-service builder buildpack-binding create --name {bindingName}-0 --type ApplicationInsights \
            --properties {properties} --secrets {secrets} -g {rg} -s {serviceName}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.bindingType', 'ApplicationInsights'),
                self.check('properties.launchProperties.properties', {'a': 'b', 'b': 'c'}),
                self.check('properties.launchProperties.secrets', {'x': '*', 'y': '*'}),
            ])

        self.cmd('spring-cloud build-service builder buildpack-binding create --name {bindingName}-1 --type NewRelic \
            --properties {properties} --secrets {secrets} -g {rg} -s {serviceName}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.bindingType', 'NewRelic'),
                self.check('properties.launchProperties.properties', {'a': 'b', 'b': 'c'}),
                self.check('properties.launchProperties.secrets', {'x': '*', 'y': '*'}),
            ])

        results = self.cmd('spring-cloud build-service builder buildpack-binding list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertEqual(2, len(results))
