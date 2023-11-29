# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, live_only)

from azext_containerapp.tests.latest.utils import create_and_verify_containerapp_up, create_and_verify_containerapp_up_with_multiple_environments

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerAppUpImageTest(ScenarioTest):
    @live_only()
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_up_image_e2e(self, resource_group):
        image = "mcr.microsoft.com/k8se/quickstart:latest"
        create_and_verify_containerapp_up(self, resource_group=resource_group, image=image)


    @live_only()
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_up_source_with_bullseye_buildpack_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_bullseye_buildpack_net7"))
        ingress = 'external'
        target_port = '8080'
        create_and_verify_containerapp_up(self, resource_group=resource_group, source_path=source_path, ingress=ingress, target_port=target_port)


    @live_only()
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_up_artifact_with_bullseye_buildpack_e2e(self, resource_group):
        artifact_path = os.path.join(TEST_DIR, os.path.join("data", "artifact_built_using_buildpack", "sample.jar"))
        ingress = 'external'
        target_port = '8080'
        create_and_verify_containerapp_up(self, resource_group=resource_group, artifact_path=artifact_path, ingress=ingress, target_port=target_port, requires_acr_prerequisite=True)


    @live_only()
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_up_source_with_bookworm_buildpack_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_bookworm_buildpack_net8"))
        ingress = 'external'
        target_port = '8080'
        create_and_verify_containerapp_up(self, resource_group=resource_group, source_path=source_path, ingress=ingress, target_port=target_port)


    @live_only()
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_up_source_with_dockerfile_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_dockerfile"))
        ingress = 'external'
        target_port = '80'
        create_and_verify_containerapp_up(self, resource_group=resource_group, source_path=source_path, ingress=ingress, target_port=target_port)


    @live_only()
    @ResourceGroupPreparer(location="eastus2")
    @unittest.skip("acr_task_run function from acr module uses outdated Storage SDK which does not work with testing.")
    def test_containerapp_up_source_with_acr_task_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_acr_task"))
        ingress = 'external'
        target_port = '8080'
        create_and_verify_containerapp_up(self, resource_group=resource_group, source_path=source_path, ingress=ingress, target_port=target_port)


    @live_only()
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_up_source_with_multiple_environments_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_bullseye_buildpack_net7"))
        ingress = 'external'
        target_port = '8080'
        create_and_verify_containerapp_up_with_multiple_environments(self, resource_group=resource_group, source_path=source_path, ingress=ingress, target_port=target_port, location="eastus2")
