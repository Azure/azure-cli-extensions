# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
import logging
import os
import time

from contextlib import redirect_stdout
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, live_only, record_only)
from knack.log import get_logger
from azext_vme import utils
from azure.core.exceptions import ResourceNotFoundError
from knack.util import CLIError

from azext_vme.tests.latest.testutils import deploy_arm_template_with_tags, delete_arm_template

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))
logger = logging.getLogger('azure.cli.testsdk')
logger.addHandler(logging.StreamHandler())

def _get_test_data_file(filename):
    root = os.path.abspath(os.path.join(__file__, "../../../../../.."))
    temp_dir = os.path.join(root, "temp")
    return os.path.join(temp_dir, filename).replace("\\", "\\\\")

class VmeScenarioTest(ScenarioTest):
    # os.environ["AZURE_CLI_TEST_DEV_RESOURCE_GROUP_NAME"] = "vmetestrg"
    # os.environ["AZURE_LOCAL_DISCONNECTED"] = "true"

    @live_only()
    @ResourceGroupPreparer(
        name_prefix="vmetest", location="eastus2euap", random_name_length=12
    )
    def test_vme_upgrade_live(self, resource_group, resource_group_location):
        managed_cluster_name = self.create_random_name(prefix="vmetest", length=12)
        connected_cluster_name = self.create_random_name(prefix="cc-vme-", length=12)
        kubeconfig = _get_test_data_file(managed_cluster_name + "-config.yaml")
        kubecontext = f"{managed_cluster_name}-admin"

        self.kwargs.update(
            {
                "rg": resource_group,
                "managed_cluster_name": managed_cluster_name,
                "cluster_name": connected_cluster_name,
                "kubeconfig": kubeconfig,
                "location": resource_group_location,
                "kubecontext": kubecontext
            }
        )

        self.cmd("aks create -g {rg} -n {managed_cluster_name} --location {location}  --generate-ssh-keys")
        self.cmd("aks wait -g {rg} -n {managed_cluster_name} --created")
        self.cmd(
            "aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig} --admin"
        )

        try:
            self.cmd(
                "connectedk8s connect -g {rg} -n {cluster_name} -l {location} --kube-config {kubeconfig} \
                    --kube-context {kubecontext}")
        except Exception as e:
            self.cmd(
                "connectedk8s connect -g {rg} -n {cluster_name} -l {location} --kube-config {kubeconfig} \
                    --kube-context {kubecontext}")

        helm_client_location = utils.install_helm_client()
        self.assertIsNotNone(helm_client_location, "Helm client installation failed")
        # Check Release Existence
        release_namespace = utils.get_release_namespace(
            kubeconfig, kubecontext, helm_client_location
        )
        self.assertEqual(release_namespace, "azure-arc-release")
        agent_version = utils.get_agent_version(helm_client_location, release_namespace, kubeconfig, kubecontext)
        self.assertIsNotNone(agent_version, "Agent version retrieval failed")

        with self.assertRaisesRegex(ResourceNotFoundError, "ResourceNotFound"):
            self.cmd("vme upgrade -g {rg} -c notexistcluster")

        # Test succeeded upgrade
        subscription_id = self.get_subscription_id()
        deploy_arm_template_with_tags(self.cli_ctx, subscription_id, resource_group, "Arc-Update-" + connected_cluster_name, TEST_DIR + "\\template_succeeded.json", agent_version)

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            self.cmd("vme upgrade -g {rg} -c {cluster_name} --timeout 60 --kube-config {kubeconfig} --kube-context {kubecontext} --wait")
            self.assertIn("Version managed extensions upgrade completed", captured_output.getvalue())

        # Test failed upgrade
        deploy_arm_template_with_tags(self.cli_ctx, subscription_id, resource_group, "Arc-Update-" + connected_cluster_name, TEST_DIR + "\\template_failed.json", agent_version, connected_cluster_name)

        with self.assertRaisesRegex(CLIError, "Version managed extensions upgrade failed."):
            self.cmd("vme upgrade -g {rg} -c {cluster_name} --timeout 60 --kube-config {kubeconfig} --kube-context {kubecontext} --wait")

        delete_arm_template(self.cli_ctx, subscription_id, resource_group, "Arc-Update-" + connected_cluster_name)

        time.sleep(10)
        # Test timout upgrade
        with self.assertRaisesRegex(CLIError, "Error: version managed extensions upgrade could not start"):
            self.cmd("vme upgrade -g {rg} -c {cluster_name} --timeout 10 --kube-config {kubeconfig} --kube-context {kubecontext} --wait")