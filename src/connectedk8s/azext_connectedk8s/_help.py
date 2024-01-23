# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['connectedk8s'] = """
    type: group
    short-summary: Commands to manage connected kubernetes clusters.
"""

helps['connectedk8s connect'] = """
    type: command
    short-summary: Onboard a connected kubernetes cluster to azure.
    examples:
    - name: Onboard a connected kubernetes cluster with default kube config and kube context.
      text: az connectedk8s connect -g resourceGroupName -n connectedClusterName
    - name: Onboard a connected kubernetes cluster with default kube config and kube context and disabling auto upgrade of arc agents.
      text: az connectedk8s connect -g resourceGroupName -n connectedClusterName --disable-auto-upgrade
    - name: Onboard a connected kubernetes cluster by specifying the kubeconfig and kubecontext.
      text: az connectedk8s connect -g resourceGroupName -n connectedClusterName --kube-config /path/to/kubeconfig --kube-context kubeContextName
    - name: Onboard a connected kubernetes cluster by specifying the https proxy, http proxy, no proxy settings.
      text: az connectedk8s connect -g resourceGroupName -n connectedClusterName --proxy-https https://proxy-url --proxy-http http://proxy-url --proxy-skip-range excludedIP,excludedCIDR,exampleCIDRfollowed,10.0.0.0/24
    - name: Onboard a connected kubernetes cluster by specifying the https proxy, http proxy, no proxy  with cert settings.
      text: az connectedk8s connect -g resourceGroupName -n connectedClusterName --proxy-cert /path/to/crt --proxy-https https://proxy-url --proxy-http http://proxy-url --proxy-skip-range excludedIP,excludedCIDR,exampleCIDRfollowed,10.0.0.0/24
    - name: Onboard a connected kubernetes cluster with private link feature enabled by specifying private link parameters.
      text: az connectedk8s connect -g resourceGroupName -n connectedClusterName --enable-private-link true --private-link-scope-resource-id pls/resource/arm/id
    - name: Onboard a connected kubernetes cluster with custom onboarding timeout.
      text: az connectedk8s connect -g resourceGroupName -n connectedClusterName --onboarding-timeout 600

"""

helps['connectedk8s update'] = """
    type: command
    short-summary: Update properties of the arc onboarded kubernetes cluster.
    examples:
    - name: Update proxy values for the agents
      text: az connectedk8s update -g resourceGroupName -n connectedClusterName  --proxy-cert /path/to/crt --proxy-https https://proxy-url --proxy-http http://proxy-url --proxy-skip-range excludedIP,excludedCIDR,exampleCIDRfollowed,10.0.0.0/24
    - name: Disable proxy settings for agents
      text: az connectedk8s update -g resourceGroupName -n connectedClusterName --disable-proxy
    - name: Disable auto-upgrade of agents
      text: az connectedk8s update -g resourceGroupName -n connectedClusterName --auto-upgrade false
"""

helps['connectedk8s upgrade'] = """
    type: command
    short-summary: Atomically upgrade onboarded agents to the specific version or default to the latest version.
    examples:
    - name: Upgrade the agents to the latest version
      text: az connectedk8s upgrade -g resourceGroupName -n connectedClusterName
    - name: Upgrade the agents to a specific version
      text: az connectedk8s upgrade -g resourceGroupName -n connectedClusterName --agent-version 0.2.62
    - name: Upgrade the agents with custom upgrade timeout.
      text: az connectedk8s upgrade -g resourceGroupName -n connectedClusterName --upgrade-timeout 600
"""

helps['connectedk8s list'] = """
    type: command
    short-summary: List connected kubernetes clusters.
    examples:
    - name: List all connected kubernetes clusters in a resource group.
      text: az connectedk8s list -g resourceGroupName --subscription subscriptionName
    - name: List all connected kubernetes clusters in a subscription.
      text: az connectedk8s list --subscription subscriptionName

"""

helps['connectedk8s delete'] = """
    type: command
    short-summary: Delete a connected kubernetes cluster along with connected cluster agents.
    examples:
    - name: Delete a connected kubernetes cluster and connected cluster agents with default kubeconfig and kubecontext.
      text: az connectedk8s delete -g resourceGroupName -n connectedClusterName
    - name: Delete a connected kubernetes cluster by specifying the kubeconfig and kubecontext for connected cluster agents deletion.
      text: az connectedk8s delete -g resourceGroupName -n connectedClusterName --kube-config /path/to/kubeconfig --kube-context kubeContextName
"""

helps['connectedk8s show'] = """
    type: command
    short-summary: Show details of a connected kubernetes cluster.
    examples:
    - name: Show the details for a connected kubernetes cluster
      text: az connectedk8s show -g resourceGroupName -n connectedClusterName
"""

helps['connectedk8s proxy'] = """
  type: command
  short-summary: Get access to a connected kubernetes cluster.
  examples:
  - name: Get access to a connected kubernetes cluster.
    text: az connectedk8s proxy -n clusterName -g resourceGroupName
  - name: Get access to a connected kubernetes cluster with custom port
    text: az connectedk8s proxy -n clusterName -g resourceGroupName --port portValue
  - name: Get access to a connected kubernetes cluster with service account token
    text: az connectedk8s proxy -n clusterName -g resourceGroupName --token tokenValue
  - name: Get access to a connected kubernetes cluster by specifying custom kubeconfig location
    text: az connectedk8s proxy -n clusterName -g resourceGroupName -f path/to/kubeconfig
  - name: Get access to a connected kubernetes cluster by specifying custom context
    text: az connectedk8s proxy -n clusterName -g resourceGroupName --kube-context contextName
"""

helps['connectedk8s enable-features'] = """
  type: command
  short-summary: Enables the selective features on the connected cluster.
  examples:
  - name: Enables the Cluster-Connect feature.
    text: az connectedk8s enable-features -n clusterName -g resourceGroupName --features cluster-connect
  - name: Enable Azure RBAC feature.
    text: az connectedk8s enable-features -n clusterName -g resourceGroupName --features azure-rbac --skip-azure-rbac-list "user1@domain.com,spn_oid"
  - name: Enable multiple features.
    text: az connectedk8s enable-features -n clusterName -g resourceGroupName --features cluster-connect custom-locations
"""

helps['connectedk8s disable-features'] = """
  type: command
  short-summary: Disables the selective features on the connected cluster.
  examples:
  - name: Disables the azure-rbac feature.
    text: az connectedk8s disable-features -n clusterName -g resourceGroupName --features azure-rbac
  - name: Disable multiple features.
    text: az connectedk8s disable-features -n clusterName -g resourceGroupName --features custom-locations azure-rbac
"""

helps['connectedk8s troubleshoot'] = """
  type: command
  short-summary: Perform diagnostic checks on an Arc enabled Kubernetes cluster.
  examples:
  - name: Perform diagnostic checks on an Arc enabled Kubernetes cluster.
    text: az connectedk8s troubleshoot -n clusterName -g resourceGroupName
"""
