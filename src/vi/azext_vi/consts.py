# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

EXTENSION_NAME = "vi"
EXTENSION_PACKAGE_NAME = "azext_vi"
PROVIDER_NAMESPACE = "Microsoft.KubernetesConfiguration"

KUBECONFIG_LOAD_FAILED_WARNING = """Unable to load the kubeconfig file.
Please check
https://learn.microsoft.com/en-us/azure/azure-arc/kubernetes/diagnose-connection-issues#is-kubeconfig-pointing-to-the-right-cluster"""

HELM_VERSION = "v3.12.2"
HELM_MCR_URL = "azure-cli/helm"
PROVISIONED_CLUSTER_TYPE = "provisionedclusters"
KUBEAPI_CONNECTIVITY_FAILED_WARNING = """Unable to verify connectivity to the Kubernetes cluster.
Please check https://learn.microsoft.com/en-us/azure/azure-arc/kubernetes/diagnose-connection-issues"""

KUBERNETES_CONNECTIVITY_FAULT_TYPE = "kubernetes-cluster-connection-error"
ARC_EXT_DIAGNOSTIC_LOGS = "arc_ext_diagnostic_logs"
