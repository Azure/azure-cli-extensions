# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from unittest import mock
import time
import requests

from azure.cli.testsdk.reverse_dependency import get_dummy_cli
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, live_only)
from knack.util import CLIError

from azext_containerapp.tests.latest.common import TEST_LOCATION

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


@live_only()
class ContainerAppUpImageTest(ScenarioTest):
    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_up_image_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        env_name = self.create_random_name(prefix='env', length=24)
        self.cmd(f'containerapp env create -g {resource_group} -n {env_name}')
        image = "mcr.microsoft.com/k8se/quickstart:latest"
        app_name = self.create_random_name(prefix='containerapp', length=24)
        self.cmd(f"containerapp up --image {image} --environment {env_name} -g {resource_group} -n {app_name}")

        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        url = app["properties"]["configuration"]["ingress"]["fqdn"]
        url = url if url.startswith("http") else f"http://{url}"
        resp = requests.get(url)
        self.assertTrue(resp.ok)

        self.cmd(f"containerapp up --image {image} --environment {env_name} -g {resource_group} -n {app_name} -l {TEST_LOCATION.upper()}")


    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_up_source_with_dockerfile_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_using_dockerfile"))
        env_name = self.create_random_name(prefix='env', length=24)
        self.cmd(f'containerapp env create -g {resource_group} -n {env_name}')
        app_name = self.create_random_name(prefix='containerapp', length=24)
        self.cmd('containerapp up --source "{}" --environment {} -g {} -n {}'.format(source_path, env_name, resource_group, app_name))

        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        url = app["properties"]["configuration"]["ingress"]["fqdn"]
        url = url if url.startswith("http") else f"http://{url}"
        resp = requests.get(url)
        self.assertTrue(resp.ok)

        self.cmd('containerapp up --source "{}" --environment {} -g {} -n {} -l {}'.format(source_path, env_name, resource_group, app_name, TEST_LOCATION.upper()))


    @ResourceGroupPreparer(location="eastus2")
    def test_containerapp_up_source_with_acr_task_e2e(self, resource_group):
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        source_path = os.path.join(TEST_DIR, os.path.join("data", "source_using_acr_task"))
        env_name = self.create_random_name(prefix='env', length=24)
        self.cmd(f'containerapp env create -g {resource_group} -n {env_name}')
        app_name = self.create_random_name(prefix='containerapp', length=24)
        self.cmd('containerapp up --source "{}" --environment {} -g {} -n {}'.format(source_path, env_name, resource_group, app_name))

        app = self.cmd(f"containerapp show -g {resource_group} -n {app_name}").get_output_in_json()
        url = app["properties"]["configuration"]["ingress"]["fqdn"]
        url = url if url.startswith("http") else f"http://{url}"
        resp = requests.get(url)
        self.assertTrue(resp.ok)

        self.cmd('containerapp up --source "{}" --environment {} -g {} -n {} -l {}'.format(source_path, env_name, resource_group, app_name, TEST_LOCATION.upper()))
