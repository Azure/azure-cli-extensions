# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, JMESPathCheckNotExists)

from .common import TEST_LOCATION
from .utils import prepare_containerapp_env_for_app_e2e_tests


class ContainerappJavaLoggerTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer()
    def test_containerapp_java_loggers(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))
        app = self.create_random_name(prefix='aca', length=24)
        image = "mcr.microsoft.com/azurespringapps/samples/hello-world:0.0.1"
        env = prepare_containerapp_env_for_app_e2e_tests(self)

        # Create container app
        self.cmd(f'containerapp create -g {resource_group} -n {app} --image {image} --environment {env}')
        self.cmd(f'containerapp show -g {resource_group} -n {app}', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime", None)
        ])

        self.cmd(f'containerapp java logger set --logger-name root --logger-level debug -g {resource_group} -n {app}',
                 expect_failure=True)

        self.cmd(f'containerapp java logger delete --logger-name testpkg -g {resource_group} -n {app}',
                 expect_failure=True)

        self.cmd(f'containerapp java logger show --logger-name "org.springframework.boot" -g {resource_group} -n {app}',
                 expect_failure=True)

        # Enable java agent
        self.cmd(f'containerapp update -g {resource_group} -n {app} --enable-java-agent', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", True),
            JMESPathCheckNotExists("properties.configuration.runtime.java.javaAgent.logging")
        ])

        # Add logger
        self.cmd(f'containerapp java logger set --logger-name root --logger-level debug -g {resource_group} -n {app}', checks=[
            JMESPathCheck("length([*])", 1),
            JMESPathCheck("[0].level", "debug"),
            JMESPathCheck("[0].logger", "root")
        ])

        # Add logger
        self.cmd(f'containerapp java logger set --logger-name testpkg --logger-level info -g {resource_group} -n {app}', checks=[
            JMESPathCheck("length([*])", 2),
            JMESPathCheck("[0].level", "debug"),
            JMESPathCheck("[0].logger", "root"),
            JMESPathCheck("[1].level", "info"),
            JMESPathCheck("[1].logger", "testpkg")
        ])

        # Update logger
        self.cmd(f'containerapp java logger set --logger-name testpkg --logger-level debug -g {resource_group} -n {app}', checks=[
            JMESPathCheck("length([*])", 2),
            JMESPathCheck("[0].level", "debug"),
            JMESPathCheck("[0].logger", "root"),
            JMESPathCheck("[1].level", "debug"),
            JMESPathCheck("[1].logger", "testpkg")
        ])

        # Delete not exist logger
        self.cmd(f'containerapp java logger delete --logger-name notexistlogger -g {resource_group} -n {app}', expect_failure=True)

        # Delete logger
        self.cmd(f'containerapp java logger delete --logger-name testpkg -g {resource_group} -n {app}', checks=[
            JMESPathCheck("length([*])", 1),
            JMESPathCheck("[0].level", "debug"),
            JMESPathCheck("[0].logger", "root"),
        ])

        # Add logger
        self.cmd(f'containerapp java logger set --logger-name "org.springframework.boot" --logger-level debug -g {resource_group} -n {app}', checks=[
            JMESPathCheck("length([*])", 2),
            JMESPathCheck("[0].level", "debug"),
            JMESPathCheck("[0].logger", "root"),
            JMESPathCheck("[1].level", "debug"),
            JMESPathCheck("[1].logger", "org.springframework.boot")
        ])

        # Display logger
        self.cmd(f'containerapp java logger show --logger-name "org.springframework.boot" -g {resource_group} -n {app}', checks=[
            JMESPathCheck('logger', "org.springframework.boot"),
            JMESPathCheck('level', "debug")
        ])

        # Display not exist logger
        self.cmd(f'containerapp java logger show --logger-name "notexistlogger" -g {resource_group} -n {app}', expect_failure=True)

        # Display all loggers
        self.cmd(f'containerapp java logger show --all -g {resource_group} -n {app}', checks=[
            JMESPathCheck("length([*])", 2),
            JMESPathCheck('[0].logger', "root"),
            JMESPathCheck('[0].level', "debug"),
            JMESPathCheck('[1].logger', "org.springframework.boot"),
            JMESPathCheck('[1].level', "debug")
        ])

        # Update container app with runtime=java and enable-java-metrics is set
        self.cmd(f'containerapp update -g {resource_group} -n {app} --runtime=java --enable-java-metrics', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", True),
            JMESPathCheck("length(properties.configuration.runtime.java.javaAgent.logging.loggerSettings[*])", 2),
            JMESPathCheck('properties.configuration.runtime.java.javaAgent.logging.loggerSettings[0].logger', "root"),
            JMESPathCheck('properties.configuration.runtime.java.javaAgent.logging.loggerSettings[0].level', "debug"),
            JMESPathCheck('properties.configuration.runtime.java.javaAgent.logging.loggerSettings[1].logger', "org.springframework.boot"),
            JMESPathCheck('properties.configuration.runtime.java.javaAgent.logging.loggerSettings[1].level', "debug")
        ])

        # Update container app with enable-java-agent is set
        self.cmd(f'containerapp update -g {resource_group} -n {app} --enable-java-agent', checks=[
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck("properties.configuration.runtime.java.enableMetrics", True),
            JMESPathCheck("properties.configuration.runtime.java.javaAgent.enabled", True),
            JMESPathCheck("length(properties.configuration.runtime.java.javaAgent.logging.loggerSettings[*])", 2),
            JMESPathCheck('properties.configuration.runtime.java.javaAgent.logging.loggerSettings[0].logger', "root"),
            JMESPathCheck('properties.configuration.runtime.java.javaAgent.logging.loggerSettings[0].level', "debug"),
            JMESPathCheck('properties.configuration.runtime.java.javaAgent.logging.loggerSettings[1].logger',
                          "org.springframework.boot"),
            JMESPathCheck('properties.configuration.runtime.java.javaAgent.logging.loggerSettings[1].level', "debug")
        ])

        # Delete all loggers
        self.cmd(f'containerapp java logger delete --all -g {resource_group} -n {app}', checks=[
            JMESPathCheck("length([*])", 0)
        ])

        # Delete container app
        self.cmd(f'containerapp delete  -g {resource_group} -n {app} --yes')