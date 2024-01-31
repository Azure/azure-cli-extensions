# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, live_only)

from azext_containerapp.tests.latest.utils import create_and_verify_containerapp_create_and_update, \
    create_and_verify_containerapp_up, verify_containerapp_create_exception

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerAppCreateTest(ScenarioTest):

    # We have to use @live_only() here as cloud builder and build resource name is generated randomly
    # and no matched request could be found for all builder/build ARM requests.
    @live_only()
    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_up_artifact_with_buildpack_java(self, resource_group):
        artifact_path = os.path.join(TEST_DIR, os.path.join("data", "artifact_built_using_buildpack", "sample.jar"))
        ingress = 'external'
        target_port = '8080'
        build_env_vars = 'BP_JVM_VERSION=21'
        create_and_verify_containerapp_up(self, resource_group=resource_group, artifact_path=artifact_path,
                                          build_env_vars=build_env_vars, ingress=ingress, target_port=target_port,
                                          no_log_destination=True)

    @live_only()
    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_up_source_with_buildpack_java(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_buildpack_java"))
        ingress = 'external'
        target_port = '8080'
        build_env_vars = 'BP_JVM_VERSION=21 BP_MAVEN_VERSION=4 "BP_MAVEN_BUILD_ARGUMENTS=-Dmaven.test.skip=true --no-transfer-progress package"'
        create_and_verify_containerapp_up(self, resource_group=resource_group, source_path=source_path,
                                          build_env_vars=build_env_vars, ingress=ingress, target_port=target_port,
                                          no_log_destination=True)

    @live_only()
    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_create_artifact_with_buildpack_java(self, resource_group):
        artifact_path = os.path.join(TEST_DIR, os.path.join("data", "artifact_built_using_buildpack", "sample.jar"))
        ingress = 'external'
        target_port = '8080'
        build_env_vars = 'BP_JVM_VERSION=21'
        create_and_verify_containerapp_create_and_update(self, resource_group=resource_group,
                                                         artifact_path=artifact_path, build_env_vars=build_env_vars,
                                                         ingress=ingress, target_port=target_port)

    @live_only()
    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_create_source_with_buildpack_java(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_buildpack_java"))
        ingress = 'external'
        target_port = '8080'
        build_env_vars = 'BP_JVM_VERSION=21 BP_MAVEN_VERSION=4 "BP_MAVEN_BUILD_ARGUMENTS=-Dmaven.test.skip=true --no-transfer-progress package"'
        create_and_verify_containerapp_create_and_update(self, resource_group=resource_group, source_path=source_path,
                                                         build_env_vars=build_env_vars, ingress=ingress,
                                                         target_port=target_port)
