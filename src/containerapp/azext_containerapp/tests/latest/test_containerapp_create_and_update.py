# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, live_only)

from azext_containerapp.tests.latest.utils import create_and_verify_containerapp_create_and_update, verify_containerapp_create_exception_with_source_and_repo

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class ContainerAppCreateTest(ScenarioTest):
    @live_only()
    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_create_source_with_Dockerfile_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_dockerfile"))
        ingress = 'external'
        target_port = '80'
        create_and_verify_containerapp_create_and_update(self, resource_group=resource_group, source_path=source_path, ingress=ingress, target_port=target_port)

    @live_only()
    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_create_source_with_buildpack_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_buildpack"))
        ingress = 'external'
        target_port = '8080'
        create_and_verify_containerapp_create_and_update(self, resource_group=resource_group, source_path=source_path, ingress=ingress, target_port=target_port)

    @live_only()
    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_create_source_and_image_e2e(self, resource_group):
       image = "mcr.microsoft.com/dotnet/runtime:7.0"
       source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_dockerfile"))
       create_and_verify_containerapp_create_and_update(self,resource_group=resource_group, image=image, source_path=source_path)

    @live_only()
    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_create_source_with_acr_task_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_acr_task"))
        ingress = 'external'
        target_port = '8080'
        create_and_verify_containerapp_create_and_update(self,resource_group=resource_group, source_path=source_path, ingress=ingress, target_port=target_port)

    @live_only()
    @ResourceGroupPreparer(location="eastus")
    def test_containerapp_create_source_and_repo_e2e(self, resource_group):
        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_built_using_dockerfile"))
        repo = "https://github.com/test/repo"
        verify_containerapp_create_exception_with_source_and_repo(self,resource_group=resource_group, source_path=source_path, repo=repo)