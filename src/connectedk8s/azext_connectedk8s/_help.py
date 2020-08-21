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
    - name: Onboard a connected kubernetes cluster by specifying the kubeconfig and kubecontext.
      text: az connectedk8s connect -g resourceGroupName -n connectedClusterName --kube-config /path/to/kubeconfig --kube-context kubeContextName
    - name: Onboard a connected kubernetes cluster by specifying the https proxy, http proxy, no proxy settings.
      text: az connectedk8s connect -g resourceGroupName -n connectedClusterName --proxy-https https://proxy-url --proxy-http http://proxy-url --proxy-skip-range excludedIP,excludedCIDR,exampleCIDRfollowed,10.0.0.0/24

"""

helps['connectedk8s update'] = """
    type: command
    short-summary: Update properties of the onboarded agents.
    examples:
    - name: Update proxy values for the agents
      text: az connectedk8s update -g resourceGroupName -n connectedClusterName --proxy-https https://proxy-url --proxy-http http://proxy-url --proxy-skip-range excludedIP,excludedCIDR,exampleCIDRfollowed,10.0.0.0/24
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
