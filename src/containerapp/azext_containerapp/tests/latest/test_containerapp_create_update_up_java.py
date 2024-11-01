# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import requests
import shutil
import tarfile
import tempfile

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, live_only)

from azext_containerapp.tests.latest.utils import create_and_verify_containerapp_create_and_update, \
    create_and_verify_containerapp_up, verify_containerapp_create_exception

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


def download_java_source(source_path):
    response = requests.get("https://api.github.com/repos/Azure/java-buildpack-e2e-test/releases/tags/v1.0.6")
    response.raise_for_status()
    data = response.json()
    if data['assets']:
        for asset in data['assets']:
            if asset['name'] == 'java-source-spring.tar.gz':
                source_url = asset['browser_download_url']
                response = requests.get(source_url, stream=True)
                response.raise_for_status()

                with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as temp_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            temp_file.write(chunk)

                if os.path.exists(source_path):
                    shutil.rmtree(source_path)

                with tarfile.open(temp_file.name, 'r:gz') as tar:
                    tar.extractall(path=source_path)

                os.remove(temp_file.name)


def cleanup(source_path):
    shutil.rmtree(source_path)


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
        source_path = os.path.join(TEST_DIR, os.path.join("data", "up_source_with_buildpack_java"))
        download_java_source(source_path)
        ingress = 'external'
        target_port = '8080'
        build_env_vars = 'BP_JVM_VERSION=21 BP_MAVEN_VERSION=4 "BP_MAVEN_BUILD_ARGUMENTS=-Dmaven.test.skip=true --no-transfer-progress package"'
        try:
            create_and_verify_containerapp_up(self, resource_group=resource_group, source_path=source_path,
                                              build_env_vars=build_env_vars, ingress=ingress, target_port=target_port,
                                              no_log_destination=True)
        finally:
            cleanup(source_path)

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
        source_path = os.path.join(TEST_DIR, os.path.join("data", "create_source_with_buildpack_java"))
        download_java_source(source_path)
        ingress = 'external'
        target_port = '8080'
        build_env_vars = 'BP_JVM_VERSION=21 BP_MAVEN_VERSION=4 "BP_MAVEN_BUILD_ARGUMENTS=-Dmaven.test.skip=true --no-transfer-progress package"'
        try:
            create_and_verify_containerapp_create_and_update(self, resource_group=resource_group,
                                                             source_path=source_path,
                                                             build_env_vars=build_env_vars, ingress=ingress,
                                                             target_port=target_port)
        finally:
            cleanup(source_path)
