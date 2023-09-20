# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import time
import unittest

from azure.cli.testsdk.scenario_tests import AllowLargeResponse, live_only
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)
from msrestazure.tools import parse_resource_id

from .common import (write_test_file, clean_up_test_file)
from .common import TEST_LOCATION
from .utils import create_containerapp_env

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappYamlTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="westeurope")
    def test_containerapp_preview_create_with_environment_id(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env1 = self.create_random_name(prefix='env1', length=24)
        env2 = self.create_random_name(prefix='env2', length=24)

        app = self.create_random_name(prefix='yaml1', length=24)

        create_containerapp_env(self, env1, resource_group)
        containerapp_env1 = self.cmd(
            'containerapp env show -g {} -n {}'.format(resource_group, env1)).get_output_in_json()

        create_containerapp_env(self, env2, resource_group)
        containerapp_env2 = self.cmd(
            'containerapp env show -g {} -n {}'.format(resource_group, env2)).get_output_in_json()

        user_identity_name = self.create_random_name(prefix='containerapp-user', length=24)
        user_identity = self.cmd(
            'identity create -g {} -n {}'.format(resource_group, user_identity_name)).get_output_in_json()
        user_identity_id = user_identity['id']

        # the value in --yaml is used, warning for different value in --environmentId
        containerapp_yaml_text = f"""
                                location: {TEST_LOCATION}
                                type: Microsoft.App/containerApps
                                tags:
                                    tagname: value
                                properties:
                                  environmentId: {containerapp_env1["id"]}
                                  configuration:
                                    activeRevisionsMode: Multiple
                                    ingress:
                                      external: false
                                      additionalPortMappings:
                                      - external: false
                                        targetPort: 12345
                                      - external: false
                                        targetPort: 9090
                                        exposedPort: 23456
                                      allowInsecure: false
                                      targetPort: 80
                                      traffic:
                                        - latestRevision: true
                                          weight: 100
                                      transport: Auto
                                      ipSecurityRestrictions:
                                        - name: name
                                          ipAddressRange: "1.1.1.1/10"
                                          action: "Allow"
                                  template:
                                    revisionSuffix: myrevision
                                    terminationGracePeriodSeconds: 90
                                    containers:
                                      - image: nginx
                                        name: nginx
                                        env:
                                          - name: HTTP_PORT
                                            value: 80
                                        command:
                                          - npm
                                          - start
                                        resources:
                                          cpu: 0.5
                                          memory: 1Gi
                                    scale:
                                      minReplicas: 1
                                      maxReplicas: 3
                                      rules:
                                      - http:
                                          auth:
                                          - secretRef: secretref
                                            triggerParameter: trigger
                                          metadata:
                                            concurrentRequests: '50'
                                            key: value
                                        name: http-scale-rule
                                identity:
                                  type: UserAssigned
                                  userAssignedIdentities:
                                    {user_identity_id}: {{}}
                                """
        containerapp_file_name = f"{self._testMethodName}_containerapp.yml"

        write_test_file(containerapp_file_name, containerapp_yaml_text)
        self.cmd(f'containerapp create -n {app} -g {resource_group} --environment {env2} --yaml {containerapp_file_name}')

        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.environmentId", containerapp_env1["id"]),
            JMESPathCheck("properties.configuration.ingress.external", False),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[0].external", False),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[0].targetPort", 12345),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[1].external", False),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[1].targetPort", 9090),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[1].exposedPort", 23456),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].name", "name"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].ipAddressRange",
                          "1.1.1.1/10"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].action", "Allow"),
            JMESPathCheck("properties.environmentId", containerapp_env1["id"]),
            JMESPathCheck("properties.template.revisionSuffix", "myrevision"),
            JMESPathCheck("properties.template.terminationGracePeriodSeconds", 90),
            JMESPathCheck("properties.template.containers[0].name", "nginx"),
            JMESPathCheck("properties.template.scale.minReplicas", 1),
            JMESPathCheck("properties.template.scale.maxReplicas", 3),
            JMESPathCheck("properties.template.scale.rules[0].name", "http-scale-rule"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.concurrentRequests", "50"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.key", "value"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].triggerParameter", "trigger"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].secretRef", "secretref"),
        ])

        containerapp_yaml_text = f"""
                                        location: {TEST_LOCATION}
                                        type: Microsoft.App/containerApps
                                        tags:
                                            tagname: value
                                        properties:
                                          configuration:
                                            activeRevisionsMode: Multiple
                                            ingress:
                                              external: false
                                              additionalPortMappings:
                                              - external: false
                                                targetPort: 12345
                                              - external: false
                                                targetPort: 9090
                                                exposedPort: 23456
                                              allowInsecure: false
                                              targetPort: 80
                                              traffic:
                                                - latestRevision: true
                                                  weight: 100
                                              transport: Auto
                                              ipSecurityRestrictions:
                                                - name: name
                                                  ipAddressRange: "1.1.1.1/10"
                                                  action: "Allow"
                                          template:
                                            revisionSuffix: myrevision
                                            terminationGracePeriodSeconds: 90
                                            containers:
                                              - image: nginx
                                                name: nginx
                                                env:
                                                  - name: HTTP_PORT
                                                    value: 80
                                                command:
                                                  - npm
                                                  - start
                                                resources:
                                                  cpu: 0.5
                                                  memory: 1Gi
                                            scale:
                                              minReplicas: 1
                                              maxReplicas: 3
                                              rules:
                                              - http:
                                                  auth:
                                                  - secretRef: secretref
                                                    triggerParameter: trigger
                                                  metadata:
                                                    concurrentRequests: '50'
                                                    key: value
                                                name: http-scale-rule
                                        identity:
                                          type: UserAssigned
                                          userAssignedIdentities:
                                            {user_identity_id}: {{}}
                                        """

        write_test_file(containerapp_file_name, containerapp_yaml_text)
        app2 = self.create_random_name(prefix='yaml2', length=24)
        self.cmd(f'containerapp create -n {app2} -g {resource_group} --environment {env2} --yaml {containerapp_file_name}')
        self.cmd(f'containerapp show -g {resource_group} -n {app2}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("properties.environmentId", containerapp_env2["id"]),
            JMESPathCheck("properties.configuration.ingress.external", False),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[0].external", False),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[0].targetPort", 12345),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[1].external", False),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[1].targetPort", 9090),
            JMESPathCheck("properties.configuration.ingress.additionalPortMappings[1].exposedPort", 23456),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].name", "name"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].ipAddressRange",
                          "1.1.1.1/10"),
            JMESPathCheck("properties.configuration.ingress.ipSecurityRestrictions[0].action", "Allow"),
            JMESPathCheck("properties.environmentId", containerapp_env2["id"]),
            JMESPathCheck("properties.template.revisionSuffix", "myrevision"),
            JMESPathCheck("properties.template.terminationGracePeriodSeconds", 90),
            JMESPathCheck("properties.template.containers[0].name", "nginx"),
            JMESPathCheck("properties.template.scale.minReplicas", 1),
            JMESPathCheck("properties.template.scale.maxReplicas", 3),
            JMESPathCheck("properties.template.scale.rules[0].name", "http-scale-rule"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.concurrentRequests", "50"),
            JMESPathCheck("properties.template.scale.rules[0].http.metadata.key", "value"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].triggerParameter", "trigger"),
            JMESPathCheck("properties.template.scale.rules[0].http.auth[0].secretRef", "secretref"),
        ])
        clean_up_test_file(containerapp_file_name)
