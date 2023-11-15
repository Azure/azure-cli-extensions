# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import
from . import consts


helps[f'{consts.EXTENSION_NAME}'] = """
    type: group
    short-summary: Commands to manage Kubernetes Extensions.
"""

helps[f'{consts.EXTENSION_NAME} create'] = f"""
    type: command
    short-summary: Create a Kubernetes Cluster Extension, including purchasing an extension Offer from Azure Marketplace (AKS only). \
      Please refer to the example at the end to see how to create an extension or purchase an extension offer.
    long-summary: Create a Kubernetes Extension. \
The output includes secrets that you must protect. Be sure that you do not include these secrets in your \
  source control. Also verify that no secrets are present in the logs of your command or script. \
  For additional information, see http://aka.ms/clisecrets.
    examples:
      - name: Create a Kubernetes Extension
        text: |-
          az {consts.EXTENSION_NAME} create --resource-group my-resource-group \
--cluster-name mycluster --cluster-type connectedClusters --name myextension \
--extension-type microsoft.openservicemesh --scope cluster --release-train stable
      - name: Create a Kubernetes Marketplace Extension
        text: |-
          az {consts.EXTENSION_NAME} create --resource-group my-resource-group \
--cluster-name mycluster --cluster-type managedClusters --name myextension \
--extension-type Contoso.AzureVoteKubernetesAppTest --scope cluster --release-train stable \
--plan-name testplan --plan-product kubernetest_apps_demo_offer --plan-publisher test_test_mix3pptest0011614206850774
"""

helps[f'{consts.EXTENSION_NAME} list'] = f"""
    type: command
    short-summary: List Kubernetes Extensions.
    long-summary: List all Kubernetes Extensions in a cluster, including their properties. \
The output includes secrets that you must protect. Be sure that you do not include these secrets in your \
  source control. Also verify that no secrets are present in the logs of your command or script. \
  For additional information, see http://aka.ms/clisecrets.
    examples:
      - name: List all Kubernetes Extensions on a cluster
        text: |-
          az {consts.EXTENSION_NAME} list --resource-group my-resource-group \
--cluster-name mycluster --cluster-type connectedClusters
"""

helps[f'{consts.EXTENSION_NAME} delete'] = f"""
    type: command
    short-summary: Delete a Kubernetes Extension.
    examples:
      - name: Delete an existing Kubernetes Extension
        text: |-
          az {consts.EXTENSION_NAME} delete --resource-group my-resource-group \
--cluster-name mycluster --cluster-type connectedClusters --name myextension
"""

helps[f'{consts.EXTENSION_NAME} show'] = f"""
    type: command
    short-summary: Show a Kubernetes Extension.
    long-summary: Show a Kubernetes Extension including its properties. \
The output includes secrets that you must protect. Be sure that you do not include these secrets in your \
  source control. Also verify that no secrets are present in the logs of your command or script. \
  For additional information, see http://aka.ms/clisecrets.
    examples:
      - name: Show details of a Kubernetes Extension
        text: |-
          az {consts.EXTENSION_NAME} show --resource-group my-resource-group \
--cluster-name mycluster --cluster-type connectedClusters --name myextension
"""

helps[f'{consts.EXTENSION_NAME} update'] = f"""
    type: command
    short-summary: Update mutable properties of a Kubernetes Extension.
    long-summary: For update to ConfigSettings and ConfigProtectedSettings, please \
refer to documentation of the cluster extension service to check update to these \
properties is supported before updating these properties. \
The output includes secrets that you must protect. Be sure that you do not include these secrets in your \
 source control. Also verify that no secrets are present in the logs of your command or script. \
 For additional information, see http://aka.ms/clisecrets.
    examples:
      - name: Update a Kubernetes Extension
        text: |-
          az {consts.EXTENSION_NAME} update --resource-group my-resource-group \
--cluster-name mycluster --cluster-type connectedClusters \
--name myextension --auto-upgrade true/false --version extension-version \
--release-train stable --configuration-settings settings-key=settings-value \
--config-protected-settings protected-settings-key=protected-value \
--config-settings-file=config-settings-file \
--config-protected-file=protected-settings-file
"""

helps[f'{consts.EXTENSION_NAME} extension-types'] = """
    type: group
    short-summary: Commands to discover Kubernetes Extension Types.
"""

helps[f'{consts.EXTENSION_NAME} extension-types show-by-cluster'] = f"""
    type: command
    short-summary: Show properties for a Cluster Extension Type for an existing cluster. The properties used for filtering include type of cluster (managed, connected, etc), kubernetes version, location of the cluster.
    examples:
      - name: Show properties for a Cluster Extension Type for an existing cluster
        text: |-
          az {consts.EXTENSION_NAME} extension-types show-by-cluster --resource-group my-resource-group \
--cluster-name mycluster --cluster-type connectedClusters --extension-type microsoft.openservicemesh
"""

helps[f'{consts.EXTENSION_NAME} extension-types show-by-location'] = f"""
    type: command
    short-summary: Show properties for a Cluster Extension Type in a region.
    examples:
      - name: Show properties for a Cluster Extension Type in a region
        text: |-
          az {consts.EXTENSION_NAME} extension-types show-by-location --location eastus --extension-type microsoft.openservicemesh
"""

helps[f'{consts.EXTENSION_NAME} extension-types show-version-by-cluster'] = f"""
    type: command
    short-summary: Show properties associated with a Cluster Extension Type version for an existing cluster. The properties used for filtering include type of cluster (managed, connected, etc), kubernetes version, location of the cluster.
    examples:
      - name: Show properties associated with a Cluster Extension Type version for an existing cluster
        text: |-
          az {consts.EXTENSION_NAME} extension-types show-version-by-cluster --resource-group my-resource-group \
--cluster-name mycluster --cluster-type connectedClusters --extension-type microsoft.openservicemesh --version 1.0.0
"""

helps[f'{consts.EXTENSION_NAME} extension-types show-version-by-location'] = f"""
    type: command
    short-summary: Show properties associated with a Cluster Extension Type version in a region.
    examples:
      - name: Show properties associated with a Cluster Extension Type version in a region.
        text: |-
          az {consts.EXTENSION_NAME} extension-types show-version-by-location --location eastus --extension-type microsoft.openservicemesh \
--version 1.0.0
"""

helps[f'{consts.EXTENSION_NAME} extension-types list-by-cluster'] = f"""
    type: command
    short-summary: List available Cluster Extension Types for an existing cluster. The properties used for filtering include type of cluster (managed, connected, etc), kubernetes version, location of the cluster.
    examples:
      - name: List available Cluster Extension Types for an existing cluster
        text: |-
          az {consts.EXTENSION_NAME} extension-types list-by-cluster --resource-group my-resource-group \
--cluster-name mycluster --cluster-type connectedClusters
"""

helps[f'{consts.EXTENSION_NAME} extension-types list-by-location'] = f"""
    type: command
    short-summary: List available Cluster Extension Types in a region.
    examples:
      - name: List available Cluster Extension Types in a region
        text: |-
          az {consts.EXTENSION_NAME} extension-types list-by-location --location eastus
"""

helps[f'{consts.EXTENSION_NAME} extension-types list-versions-by-cluster'] = f"""
    type: command
    short-summary: List available versions for a Cluster Extension Type for a given cluster. The properties used for filtering include type of cluster (managed, connected, etc), kubernetes version, location of the cluster.
    examples:
      - name: List available versions for a Cluster Extension Type for a given cluster
        text: |-
          az {consts.EXTENSION_NAME} extension-types list-versions-by-cluster --resource-group my-resource-group \
--cluster-name mycluster --cluster-type connectedClusters --extension-type microsoft.flux
"""

helps[f'{consts.EXTENSION_NAME} extension-types list-versions-by-location'] = f"""
    type: command
    short-summary: List available versions for a Cluster Extension Type versions in a region.
    examples:
      - name: List available versions for a Cluster Extension Type versions in a region
        text: |-
          az {consts.EXTENSION_NAME} extension-types list-versions-by-location --location eastus --extension-type microsoft.flux
"""
