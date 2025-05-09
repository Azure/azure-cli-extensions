# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import yaml
import tempfile

from .common import TEST_LOCATION
from .utils import create_containerapp_env
from azext_containerapp.tests.latest.common import (write_test_file, clean_up_test_file)

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)


class ContainerappResiliencyTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_resiliency(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        ca_name = self.create_random_name(prefix='containerapp', length=24)
        resil_name = self.create_random_name(prefix='resil', length=24)
        bad_resil = "bad-resil"
        bad_rg = "bad-rg"
        bad_capp = "bad-capp"
        resil_policy_count = 1
        
        create_containerapp_env(self, env_name, resource_group)

        self.cmd('containerapp create -g {} -n {} --environment {}'.format(resource_group, ca_name, env_name))
        self.cmd(f'containerapp show -g {resource_group} -n {ca_name}', checks=[JMESPathCheck("properties.provisioningState", "Succeeded")])

        #Incorrect resource group (create)
        self.cmd('containerapp resiliency create -g {} -n {} --container-app-name {} --cb-interval 15 --cb-sequential-errors 5 --cb-max-ejection 60'.format(bad_rg, resil_name, ca_name), expect_failure=True)

        #Incorrect capp name (create)
        self.cmd('containerapp resiliency create -g {} -n {} --container-app-name {} --cb-interval 15 --cb-sequential-errors 5 --cb-max-ejection 60'.format(resource_group, resil_name, bad_capp), expect_failure=True)

        #Create app resiliency using flags
        self.cmd('containerapp resiliency create -g {} -n {} --container-app-name {} --cb-interval 15 --cb-sequential-errors 5 --cb-max-ejection 60'.format(resource_group, resil_name, ca_name))

        #Show app resiliency
        self.cmd('containerapp resiliency show -g {} -n {} --container-app-name {}'.format(resource_group, resil_name, ca_name), checks=[
            JMESPathCheck("properties.circuitBreakerPolicy.consecutiveErrors", "5"),
            JMESPathCheck("properties.circuitBreakerPolicy.intervalInSeconds", "15"),
            JMESPathCheck("properties.circuitBreakerPolicy.maxEjectionPercent", "60"),
        ])

        #Update app resiliency using flags
        self.cmd('containerapp resiliency update -g {} -n {} --container-app-name {} --timeout 45 --timeout-connect 5'.format(resource_group, resil_name, ca_name))

        #Incorrect resource group (update)
        self.cmd('containerapp resiliency update -g {} -n {} --container-app-name {} --cb-interval 15 --cb-sequential-errors 5 --cb-max-ejection 60'.format(bad_rg, resil_name, ca_name), expect_failure=True)

        #Incorrect capp name (update)
        self.cmd('containerapp resiliency update -g {} -n {} --container-app-name {} --cb-interval 15 --cb-sequential-errors 5 --cb-max-ejection 60'.format(resource_group, resil_name, bad_capp), expect_failure=True)

        self.cmd('containerapp resiliency show -g {} -n {} --container-app-name {}'.format(resource_group, resil_name, ca_name), checks=[
            JMESPathCheck("properties.circuitBreakerPolicy.consecutiveErrors", "5"),
            JMESPathCheck("properties.circuitBreakerPolicy.intervalInSeconds", "15"),
            JMESPathCheck("properties.circuitBreakerPolicy.maxEjectionPercent", "60"),
            JMESPathCheck("properties.timeoutPolicy.responseTimeoutInSeconds", "45"),
            JMESPathCheck("properties.timeoutPolicy.connectionTimeoutInSeconds", "5")
        ])

        #Incorrect resource group (show)
        self.cmd('containerapp resiliency show -g {} -n {} --container-app-name {}'.format(bad_rg, resil_name, ca_name), expect_failure=True)

        #Incorrect capp name (show)
        self.cmd('containerapp resiliency show -g {} -n {} --container-app-name {}'.format(resource_group, resil_name, bad_capp), expect_failure=True)

        #Incorrect resil name (show)
        self.cmd('containerapp resiliency show -g {} -n {} --container-app-name {}'.format(resource_group, bad_resil, ca_name), expect_failure=True)

        #List app resiliency
        self.cmd('containerapp resiliency list -g {} --container-app-name {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('length(@)', resil_policy_count),
            JMESPathCheck("[0].properties.circuitBreakerPolicy.consecutiveErrors", "5"),
            JMESPathCheck("[0].properties.circuitBreakerPolicy.intervalInSeconds", "15"),
            JMESPathCheck("[0].properties.circuitBreakerPolicy.maxEjectionPercent", "60"),
            JMESPathCheck("[0].properties.timeoutPolicy.responseTimeoutInSeconds", "45"),
            JMESPathCheck("[0].properties.timeoutPolicy.connectionTimeoutInSeconds", "5")
        ])

        #Incorrect resource group (list)
        self.cmd('containerapp resiliency list -g {} --container-app-name {}'.format(bad_rg, ca_name), expect_failure=True)

        #Incorrect capp name (list)
        self.cmd('containerapp resiliency list -g {} --container-app-name {}'.format(resource_group, bad_capp), expect_failure=True)

        #Delete app resiliency
        self.cmd('containerapp resiliency delete -g {} -n {} --container-app-name {} --yes'.format(resource_group, resil_name, ca_name), expect_failure=False)

        #List app resiliency after deletion
        self.cmd('containerapp resiliency list -g {} --container-app-name {}'.format(resource_group, ca_name), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        #Show app resiliency after deletion
        self.cmd('containerapp resiliency show -g {} -n {} --container-app-name {}'.format(resource_group, resil_name, ca_name), expect_failure=True)

        #Create app resiliency using yaml
        resil_yaml_text = f"""
  timeoutPolicy:
    responseTimeoutInSeconds: 25
    connectionTimeoutInSeconds: 15
  httpRetryPolicy:
    maxRetries: 15
    retryBackOff:
      initialDelayInMilliseconds: 5000
      maxIntervalInMilliseconds: 50000
    matches:
      headers:
        - header: X-Content-Type
          match:
            prefixMatch: GOATS
      httpStatusCodes:
        - 502
        - 503
      errors:
        - 5xx
        - connect-failure
        - reset
        - retriable-headers
        - retriable-status-codes
  tcpRetryPolicy:
    maxConnectAttempts: 8
  circuitBreakerPolicy:
    consecutiveErrors: 15
    intervalInSeconds: 15
    maxEjectionPercent: 60
  tcpConnectionPool:
    maxConnections: 700
  httpConnectionPool:
    http1MaxPendingRequests: 2048
    http2MaxRequests: 2048
"""
        resil_file_name = f"{self._testMethodName}_containerapp.yml"

        write_test_file(resil_file_name, resil_yaml_text)
        self.cmd(f'containerapp resiliency create -n {resil_name} --container-app {ca_name} -g {resource_group} --yaml {resil_file_name}', checks=[
            # HTTP Retry Policy
            JMESPathCheck("properties.httpRetryPolicy.matches.errors[0]", "5xx"),
            JMESPathCheck("properties.httpRetryPolicy.matches.errors[1]", "connect-failure"),
            JMESPathCheck("properties.httpRetryPolicy.matches.errors[2]", "reset"),
            JMESPathCheck("properties.httpRetryPolicy.matches.errors[3]", "retriable-headers"),
            JMESPathCheck("properties.httpRetryPolicy.matches.errors[4]", "retriable-status-codes"),
            JMESPathCheck("properties.httpRetryPolicy.matches.headers[0].header", "X-Content-Type"),
            JMESPathCheck("properties.httpRetryPolicy.matches.headers[0].match.prefixMatch", "GOATS"),
            JMESPathCheck("properties.httpRetryPolicy.matches.httpStatusCodes[0]", "502"),
            JMESPathCheck("properties.httpRetryPolicy.matches.httpStatusCodes[1]", "503"),
            JMESPathCheck("properties.httpRetryPolicy.maxRetries", "15"),
            JMESPathCheck("properties.httpRetryPolicy.retryBackOff.initialDelayInMilliseconds", "5000"),
            JMESPathCheck("properties.httpRetryPolicy.retryBackOff.maxIntervalInMilliseconds", "50000"),
            # TCP Retry Policy
            JMESPathCheck("properties.tcpRetryPolicy.maxConnectAttempts", "8"),
            # Circuit Breaker Policy
            JMESPathCheck("properties.circuitBreakerPolicy.consecutiveErrors", "15"),
            JMESPathCheck("properties.circuitBreakerPolicy.intervalInSeconds", "15"),
            JMESPathCheck("properties.circuitBreakerPolicy.maxEjectionPercent", "60"),
            # TCP Connection Pool
            JMESPathCheck("properties.tcpConnectionPool.maxConnections", "700"),
            # HTTP Connection Pool
            JMESPathCheck("properties.httpConnectionPool.httP1MaxPendingRequests", "2048"),
            JMESPathCheck("properties.httpConnectionPool.httP2MaxRequests", "2048"),
            # Timeout Policy
            JMESPathCheck("properties.timeoutPolicy.responseTimeoutInSeconds", "25"),
            JMESPathCheck("properties.timeoutPolicy.connectionTimeoutInSeconds", "15")
        ])
        clean_up_test_file(resil_file_name)

        #Update resiliency using yaml
        resil_yaml_text = f"""
tcpConnectionPool:
  maxConnections: 100
"""
        resil_file_name = f"{self._testMethodName}_containerapp.yml"

        write_test_file(resil_file_name, resil_yaml_text)
        self.cmd(f'containerapp resiliency update -n {resil_name} --container-app {ca_name} -g {resource_group} --yaml {resil_file_name}', checks=[
            JMESPathCheck("properties.tcpConnectionPool.maxConnections", "100"),
        ])
        clean_up_test_file(resil_file_name)


class DaprComponentResiliencyTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="eastus2")
    def test_dapr_component_resiliency(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='containerapp-env', length=24)
        dapr_comp_name = self.create_random_name(prefix='daprcomp', length=24)
        resil_name = self.create_random_name(prefix='resil', length=24)
        bad_rg = "bad-rg"
        bad_comp = "bad-comp"
        bad_env = "bad-env"
        resil_policy_count = 1

        create_containerapp_env(self, env_name, resource_group)

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
        
        self.cmd('containerapp env dapr-component set -n {} -g {} --dapr-component-name {} --yaml {}'.format(env_name, resource_group, dapr_comp_name, dapr_file.replace(os.sep, os.sep + os.sep)), checks=[
            JMESPathCheck('name', dapr_comp_name),
        ])

        os.close(file_ref)

        #Incorrect resource group (create)
        self.cmd('containerapp env dapr-component resiliency create -n {} --dapr-component-name {} --environment {} -g {} --in-timeout 15 --in-http-retries 5'.format(resil_name, dapr_comp_name, env_name, bad_rg), expect_failure=True)

        #Incorrect dapr component name (create)
        self.cmd('containerapp env dapr-component resiliency create -n {} --dapr-component-name {} --environment {} -g {} --in-timeout 15 --in-http-retries 5'.format(resil_name, bad_comp, env_name, resource_group), expect_failure=True)

        #Incorrect environment name (create)
        self.cmd('containerapp env dapr-component resiliency create -n {} --dapr-component-name {} --environment {} -g {} --in-timeout 15 --in-http-retries 5'.format(resil_name, dapr_comp_name, bad_env, resource_group), expect_failure=True)

        #Create dapr component resiliency using flags with missing conditional required flags
        self.cmd('containerapp env dapr-component resiliency create -n {} --dapr-component-name {} --environment {} -g {} --in-timeout 15 --in-http-retries 5 --in-cb-timeout 1'.format(resil_name, dapr_comp_name, env_name, resource_group), expect_failure=True)

        #Create dapr component resiliency using flags with missing conditional required flags
        self.cmd('containerapp env dapr-component resiliency create -n {} --dapr-component-name {} --environment {} -g {} --in-timeout 15 --in-http-retries 5 --out-cb-interval 1'.format(resil_name, dapr_comp_name, env_name, resource_group), expect_failure=True)

        #Create dapr component resiliency using flags
        self.cmd('containerapp env dapr-component resiliency create -n {} --dapr-component-name {} --environment {} -g {} --in-timeout 15 --in-http-retries 5 --in-cb-timeout 5 --in-cb-sequential-err 3'.format(resil_name, dapr_comp_name, env_name, resource_group), checks=[
            JMESPathCheck("properties.inboundPolicy.httpRetryPolicy.maxRetries", "5"),
            JMESPathCheck("properties.inboundPolicy.httpRetryPolicy.retryBackOff.initialDelayInMilliseconds", "1000"),
            JMESPathCheck("properties.inboundPolicy.httpRetryPolicy.retryBackOff.maxIntervalInMilliseconds", "10000"),
            JMESPathCheck("properties.inboundPolicy.timeoutPolicy.responseTimeoutInSeconds", "15"),
            JMESPathCheck("properties.inboundPolicy.circuitBreakerPolicy.consecutiveErrors", "3"),
            JMESPathCheck("properties.inboundPolicy.circuitBreakerPolicy.timeoutInSeconds", "5"),
        ])

        #Show dapr component resiliency
        self.cmd('containerapp env dapr-component resiliency show -n {} --dapr-component-name {} --environment {} -g {}'.format(resil_name, dapr_comp_name, env_name, resource_group), checks=[
            JMESPathCheck("properties.inboundPolicy.httpRetryPolicy.maxRetries", "5"),
            JMESPathCheck("properties.inboundPolicy.httpRetryPolicy.retryBackOff.initialDelayInMilliseconds", "1000"),
            JMESPathCheck("properties.inboundPolicy.httpRetryPolicy.retryBackOff.maxIntervalInMilliseconds", "10000"),
            JMESPathCheck("properties.inboundPolicy.timeoutPolicy.responseTimeoutInSeconds", "15"),
            JMESPathCheck("properties.inboundPolicy.circuitBreakerPolicy.consecutiveErrors", "3"),
            JMESPathCheck("properties.inboundPolicy.circuitBreakerPolicy.timeoutInSeconds", "5"),
        ])

        #Update dapr component resiliency using flags
        self.cmd('containerapp env dapr-component resiliency update -n {} --dapr-component-name {} --environment {} -g {} --out-timeout 45'.format(resil_name, dapr_comp_name, env_name, resource_group))

        self.cmd('containerapp env dapr-component resiliency show -n {} --dapr-component-name {} --environment {} -g {}'.format(resil_name, dapr_comp_name, env_name, resource_group), checks=[
            JMESPathCheck("properties.inboundPolicy.httpRetryPolicy.maxRetries", "5"),
            JMESPathCheck("properties.inboundPolicy.httpRetryPolicy.retryBackOff.initialDelayInMilliseconds", "1000"),
            JMESPathCheck("properties.inboundPolicy.httpRetryPolicy.retryBackOff.maxIntervalInMilliseconds", "10000"),
            JMESPathCheck("properties.inboundPolicy.timeoutPolicy.responseTimeoutInSeconds", "15"),
            JMESPathCheck("properties.outboundPolicy.timeoutPolicy.responseTimeoutInSeconds", "45"),
            JMESPathCheck("properties.inboundPolicy.circuitBreakerPolicy.consecutiveErrors", "3"),
            JMESPathCheck("properties.inboundPolicy.circuitBreakerPolicy.timeoutInSeconds", "5"),
        ])

        #Incorrect resource group (update)
        self.cmd('containerapp env dapr-component resiliency update -n {} --dapr-component-name {} --environment {} -g {} --out-timeout 45'.format(resil_name, dapr_comp_name, env_name, bad_rg), expect_failure=True)

        #Incorrect dapr component name (update)
        self.cmd('containerapp env dapr-component resiliency update -n {} --dapr-component-name {} --environment {} -g {} --out-timeout 45'.format(resil_name, bad_comp, env_name, resource_group), expect_failure=True)

        #Incorrect environment name (update)
        self.cmd('containerapp env dapr-component resiliency update -n {} --dapr-component-name {} --environment {} -g {} --out-timeout 45'.format(resil_name, dapr_comp_name, bad_env, resource_group), expect_failure=True)

        #List dapr component resiliency
        self.cmd('containerapp env dapr-component resiliency list --dapr-component-name {} --environment {} -g {}'.format(dapr_comp_name, env_name, resource_group), checks=[
            JMESPathCheck('length(@)', resil_policy_count),
            JMESPathCheck("[0].properties.inboundPolicy.httpRetryPolicy.maxRetries", "5"),
            JMESPathCheck("[0].properties.inboundPolicy.httpRetryPolicy.retryBackOff.initialDelayInMilliseconds", "1000"),
            JMESPathCheck("[0].properties.inboundPolicy.httpRetryPolicy.retryBackOff.maxIntervalInMilliseconds", "10000"),
            JMESPathCheck("[0].properties.inboundPolicy.timeoutPolicy.responseTimeoutInSeconds", "15"),
            JMESPathCheck("[0].properties.outboundPolicy.timeoutPolicy.responseTimeoutInSeconds", "45"),
            JMESPathCheck("[0].properties.inboundPolicy.circuitBreakerPolicy.consecutiveErrors", "3"),
            JMESPathCheck("[0].properties.inboundPolicy.circuitBreakerPolicy.timeoutInSeconds", "5"),
        ])

        #Incorrect resource group (list)
        self.cmd('containerapp env dapr-component resiliency list --dapr-component-name {} --environment {} -g {}'.format(dapr_comp_name, env_name, bad_rg), expect_failure=True)

        #Incorrect dapr component name (list)
        self.cmd('containerapp env dapr-component resiliency list --dapr-component-name {} --environment {} -g {}'.format(bad_comp, env_name, resource_group), expect_failure=True)

        #Incorrect environment name (list)
        self.cmd('containerapp env dapr-component resiliency list --dapr-component-name {} --environment {} -g {}'.format(dapr_comp_name, bad_env, resource_group), expect_failure=True)

        #Delete dapr component resiliency
        self.cmd('containerapp env dapr-component resiliency delete -n {} --dapr-component-name {} --environment {} -g {} --yes'.format(resil_name, dapr_comp_name, env_name, resource_group), expect_failure=False)

        #List dapr component resiliency after deletion
        self.cmd('containerapp env dapr-component resiliency list --dapr-component-name {} --environment {} -g {}'.format(dapr_comp_name, env_name, resource_group), checks=[
            JMESPathCheck('length(@)', 0),
        ])

        #Show dapr component resiliency after deletion
        self.cmd('containerapp env dapr-component resiliency show -n {} --dapr-component-name {} --environment {} -g {}'.format(resil_name, dapr_comp_name, env_name, resource_group), expect_failure=True)

        #Create dapr component resiliency using yaml
        resil_yaml_text = f"""
outboundPolicy:
  httpRetryPolicy:
    maxRetries: 16
    retryBackOff:
      initialDelayInMilliseconds: 10
      maxIntervalInMilliseconds: 100
  timeoutPolicy:
    responseTimeoutInSeconds: 17
  circuitBreakerPolicy:
    consecutiveErrors: 5
    timeoutInSeconds: 15
    intervalInSeconds: 60
inboundPolicy:
  httpRetryPolicy:
    maxRetries: 15
    retryBackOff:
      initialDelayInMilliseconds: 9
      maxIntervalInMilliseconds: 99
  circuitBreakerPolicy:
    consecutiveErrors: 3
    timeoutInSeconds: 10
"""
        resil_file_name = f"{self._testMethodName}_daprcomp.yml"

        write_test_file(resil_file_name, resil_yaml_text)
        self.cmd(f'containerapp env dapr-component resiliency create -n {resil_name} --dapr-component-name {dapr_comp_name} -g {resource_group} --environment {env_name} --yaml {resil_file_name}', checks=[
            JMESPathCheck("properties.outboundPolicy.httpRetryPolicy.maxRetries", "16"),
            JMESPathCheck("properties.outboundPolicy.httpRetryPolicy.retryBackOff.initialDelayInMilliseconds", "10"),
            JMESPathCheck("properties.outboundPolicy.httpRetryPolicy.retryBackOff.maxIntervalInMilliseconds", "100"),
            JMESPathCheck("properties.outboundPolicy.timeoutPolicy.responseTimeoutInSeconds", "17"),
            JMESPathCheck("properties.outboundPolicy.circuitBreakerPolicy.consecutiveErrors", "5"),
            JMESPathCheck("properties.outboundPolicy.circuitBreakerPolicy.timeoutInSeconds", "15"),
            JMESPathCheck("properties.outboundPolicy.circuitBreakerPolicy.intervalInSeconds", "60"),
            JMESPathCheck("properties.inboundPolicy.httpRetryPolicy.maxRetries", "15"),
            JMESPathCheck("properties.inboundPolicy.httpRetryPolicy.retryBackOff.initialDelayInMilliseconds", "9"),
            JMESPathCheck("properties.inboundPolicy.httpRetryPolicy.retryBackOff.maxIntervalInMilliseconds", "99"),
            JMESPathCheck("properties.inboundPolicy.circuitBreakerPolicy.consecutiveErrors", "3"),
            JMESPathCheck("properties.inboundPolicy.circuitBreakerPolicy.timeoutInSeconds", "10"),
        ])
        clean_up_test_file(resil_file_name)

        #Update dapr component resiliency using yaml
        resil_yaml_text = f"""
outboundPolicy:
  httpRetryPolicy:
    maxRetries: 25
    retryBackOff:
      initialDelayInMilliseconds: 25
      maxIntervalInMilliseconds: 250
"""
        resil_file_name = f"{self._testMethodName}_daprcomp.yml"

        write_test_file(resil_file_name, resil_yaml_text)

        self.cmd(f'containerapp env dapr-component resiliency update -n {resil_name} --dapr-component-name {dapr_comp_name} -g {resource_group} --environment {env_name} --yaml {resil_file_name}', checks=[
            JMESPathCheck("properties.outboundPolicy.httpRetryPolicy.maxRetries", "25"),
            JMESPathCheck("properties.outboundPolicy.httpRetryPolicy.retryBackOff.initialDelayInMilliseconds", "25"),
            JMESPathCheck("properties.outboundPolicy.httpRetryPolicy.retryBackOff.maxIntervalInMilliseconds", "250"),
        ])
        clean_up_test_file(resil_file_name)
