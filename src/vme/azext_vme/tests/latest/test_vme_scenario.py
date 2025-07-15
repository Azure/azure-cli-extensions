# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
import logging
import os
import time

from contextlib import redirect_stdout
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, live_only)
from azure.core.exceptions import ResourceNotFoundError
from knack.util import CLIError


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
    def test_vme_live(self, resource_group, resource_group_location):
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

        self.cmd("aks create -g {rg} -n {managed_cluster_name} --location {location}")
        self.cmd("aks get-credentials -g {rg} -n {managed_cluster_name} -f {kubeconfig} --admin")
        self.cmd("connectedk8s connect -g {rg} -n {cluster_name} -l {location} --kube-config {kubeconfig} --kube-context {kubecontext}")

        self.cmd("connectedk8s update -g {rg} -n {cluster_name} --auto-upgrade false --config \
                 extensionSets.versionManagedExtensions=Disabled --kube-config {kubeconfig} --kube-context {kubecontext}")

        self.cmd("k8s-extension create --cluster-name {cluster_name} --cluster-type connectedClusters --extension-type \
                 microsoft.iotoperations.platform --resource-group {rg} --name azure-iot-operations-platform \
                 --release-train preview --auto-upgrade-minor-version False --config installTrustManager=true  \
                 --config installCertManager=true  --version 0.7.6  --release-namespace cert-manager  --scope cluster")

        with self.assertRaisesRegex(ResourceNotFoundError, "ResourceNotFound"):
            self.cmd("vme install -g {rg} -c notexistcluster --include all --kube-config {kubeconfig} --kube-context {kubecontext}")

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            self.cmd("vme install -g {rg} -c {cluster_name} --include all --kube-config {kubeconfig} --kube-context {kubecontext}")
            self.assertIn("All extensions installed successfully.", captured_output.getvalue())

        self.cmd("vme list -g {rg} -c {cluster_name}")

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            self.cmd("vme uninstall -g {rg} -c {cluster_name} --include all --force")
            self.assertIn("All extensions uninstalled successfully.", captured_output.getvalue())