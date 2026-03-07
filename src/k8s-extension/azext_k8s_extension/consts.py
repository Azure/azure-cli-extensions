# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

EXTENSION_NAME = "k8s-extension"
EXTENSION_PACKAGE_NAME = "azext_k8s_extension"
PROVIDER_NAMESPACE = "Microsoft.KubernetesConfiguration"
REGISTERED = "Registered"
DF_RM_HOSTNAME = "api-dogfood.resources.windows-int.net"

CONNECTED_CLUSTER_RP = "Microsoft.Kubernetes"
MANAGED_CLUSTER_RP = "Microsoft.ContainerService"
APPLIANCE_RP = "Microsoft.ResourceConnector"
HYBRIDCONTAINERSERVICE_RP = "microsoft.hybridcontainerservice"

CONNECTED_CLUSTER_TYPE = "connectedclusters"
MANAGED_CLUSTER_TYPE = "managedclusters"
APPLIANCE_TYPE = "appliances"
PROVISIONED_CLUSTER_TYPE = "provisionedclusters"

CONNECTED_CLUSTER_API_VERSION = "2021-10-01"
MANAGED_CLUSTER_API_VERSION = "2022-11-01"
APPLIANCE_API_VERSION = "2021-10-31-preview"
HYBRIDCONTAINERSERVICE_API_VERSION = "2022-05-01-preview"

EXTENSION_TYPE_API_VERSION = "2023-05-01-preview"

# Fault type constants for error categorization.
# Used to classify different types of faults encountered during diagnostics.
LOAD_KUBECONFIG_FAULT_TYPE = "kubeconfig-load-error"    # Error loading kubeconfig file.

# Warning messages for diagnostic failures.
KUBECONFIG_LOAD_FAILED_WARNING = """Unable to load the kubeconfig file.
Please check
https://learn.microsoft.com/en-us/azure/azure-arc/kubernetes/diagnose-connection-issues#is-kubeconfig-pointing-to-the-right-cluster"""

EXTRACT_HELMEXE_FAULT_TYPE = "helm-client-extract-error"    # Error extracting Helm client executable.

HELM_VERSION = "v3.12.2"

DOWNLOAD_AND_INSTALL_KUBECTL_FAULT_TYPE = "Failed to download and install kubectl"  # Error downloading/installing kubectl.

KUBEAPI_CONNECTIVITY_FAILED_WARNING = """Unable to verify connectivity to the Kubernetes cluster.
Please check https://learn.microsoft.com/en-us/azure/azure-arc/kubernetes/diagnose-connection-issues"""

KUBERNETES_CONNECTIVITY_FAULT_TYPE = "kubernetes-cluster-connection-error"  # Error connecting to Kubernetes cluster.

# Diagnostic log file path constant.
# Used to specify the name of the file where extension diagnostic logs are stored.
ARC_EXT_DIAGNOSTIC_LOGS = "arc_ext_diagnostic_logs"
