# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os.path

from knack.help_files import helps

ACS_SERVICE_PRINCIPAL_CACHE = os.path.join('$HOME', '.azure', 'acsServicePrincipal.json')
AKS_SERVICE_PRINCIPAL_CACHE = os.path.join('$HOME', '.azure', 'aksServicePrincipal.json')


# AKS command help
helps['aks create'] = """
    type: command
    short-summary: Create a new managed Kubernetes cluster.
    parameters:
        - name: --generate-ssh-keys
          type: string
          short-summary: Generate SSH public and private key files if missing.
        - name: --service-principal
          type: string
          short-summary: Service principal used for authentication to Azure APIs.
          long-summary:  If not specified, a new service principal is created and cached at
                         {sp_cache} to be used by subsequent `az aks` commands.
        - name: --skip-subnet-role-assignment
          type: bool
          short-summary: Skip role assignment for subnet (advanced networking).
          long-summary:  If specified, please make sure your service principal has the access to your subnet.
        - name: --client-secret
          type: string
          short-summary: Secret associated with the service principal. This argument is required if
                         `--service-principal` is specified.
        - name: --node-vm-size -s
          type: string
          short-summary: Size of Virtual Machines to create as Kubernetes nodes.
        - name: --dns-name-prefix -p
          type: string
          short-summary: Prefix for hostnames that are created. If not specified, generate a hostname using the
                         managed cluster and resource group names.
        - name: --node-count -c
          type: int
          short-summary: Number of nodes in the Kubernetes node pool. It is required when --enable-cluster-autoscaler specified. After creating a cluster, you can change the
                         size of its node pool with `az aks scale`.
        - name: --node-osdisk-size
          type: int
          short-summary: Size in GB of the OS disk for each node in the node pool. Minimum 30 GB.
        - name: --kubernetes-version -k
          type: string
          short-summary: Version of Kubernetes to use for creating the cluster, such as "1.7.12" or "1.8.7".
          populator-commands:
          - "`az aks get-versions`"
        - name: --ssh-key-value
          type: string
          short-summary: Public key path or key contents to install on node VMs for SSH access. For example,
                         'ssh-rsa AAAAB...snip...UcyupgH azureuser@linuxvm'.
        - name: --admin-username -u
          type: string
          short-summary: User account to create on node VMs for SSH access.
        - name: --windows-admin-username
          type: string
          short-summary: User account to create on windows node VMs.
        - name: --windows-admin-password
          type: string
          short-summary: User account password to use on windows node VMs.
        - name: --aad-client-app-id
          type: string
          short-summary: (PREVIEW) The ID of an Azure Active Directory client application of type "Native". This
                         application is for user login via kubectl.
        - name: --aad-server-app-id
          type: string
          short-summary: (PREVIEW) The ID of an Azure Active Directory server application of type "Web app/API". This
                         application represents the managed cluster's apiserver (Server application).
        - name: --aad-server-app-secret
          type: string
          short-summary: (PREVIEW) The secret of an Azure Active Directory server application.
        - name: --aad-tenant-id
          type: string
          short-summary: (PREVIEW) The ID of an Azure Active Directory tenant.
        - name: --dns-service-ip
          type: string
          short-summary: An IP address assigned to the Kubernetes DNS service.
          long-summary: This address must be within the Kubernetes service address range specified by "--service-cidr".
                        For example, 10.0.0.10.
        - name: --docker-bridge-address
          type: string
          short-summary: A specific IP address and netmask for the Docker bridge, using standard CIDR notation.
          long-summary: This address must not be in any Subnet IP ranges, or the Kubernetes service address range.
                        For example, 172.17.0.1/16.
        - name: --load-balancer-sku
          type: string
          short-summary: Azure Load Balancer SKU selection for your cluster. Basic or Standard.
          long-summary: Select between Basic or Standard Azure Load Balancer SKU for your AKS cluster.
        - name: --enable-addons -a
          type: string
          short-summary: Enable the Kubernetes addons in a comma-separated list.
          long-summary: |-
            These addons are available:
                http_application_routing - configure ingress with automatic public DNS name creation.
                monitoring - turn on Log Analytics monitoring. Uses the Log Analytics Default Workspace if it exists, else creates one. Specify "--workspace-resource-id" to use an existing workspace.
                virtual-node - enable AKS Virtual Node (PREVIEW). Requires --subnet-name to provide the name of an existing subnet for the Virtual Node to use.
                azure-policy - enable Azure policy (PREVIEW).
        - name: --disable-rbac
          type: bool
          short-summary: Disable Kubernetes Role-Based Access Control.
        - name: --enable-rbac -r
          type: bool
          short-summary: "Enable Kubernetes Role-Based Access Control. Default: enabled."
        - name: --max-pods -m
          type: int
          short-summary: The maximum number of pods deployable to a node.
          long-summary: If not specified, defaults to 110, or 30 for advanced networking configurations.
        - name: --network-plugin
          type: string
          short-summary: The Kubernetes network plugin to use.
          long-summary: Specify "azure" for advanced networking configurations. Defaults to "kubenet".
        - name: --network-policy
          type: string
          short-summary: (PREVIEW) The Kubernetes network policy to use.
          long-summary: |
              Using together with "azure" network plugin.
              Specify "azure" for Azure network policy manager and "calico" for calico network policy controller.
              Defaults to "" (network policy disabled).
        - name: --no-ssh-key -x
          type: string
          short-summary: Do not use or create a local SSH key.
          long-summary: To access nodes after creating a cluster with this option, use the Azure Portal.
        - name: --pod-cidr
          type: string
          short-summary: A CIDR notation IP range from which to assign pod IPs when kubenet is used.
          long-summary: This range must not overlap with any Subnet IP ranges. For example, 172.244.0.0/16.
        - name: --service-cidr
          type: string
          short-summary: A CIDR notation IP range from which to assign service cluster IPs.
          long-summary: This range must not overlap with any Subnet IP ranges. For example, 10.0.0.0/16.
        - name: --vnet-subnet-id
          type: string
          short-summary: The ID of a subnet in an existing VNet into which to deploy the cluster.
        - name: --workspace-resource-id
          type: string
          short-summary: The resource ID of an existing Log Analytics Workspace to use for storing monitoring data. If not specified, uses the default Log Analytics Workspace if it exists, otherwise creates one.
        - name: --enable-cluster-autoscaler
          type: bool
          short-summary: Enable cluster autoscaler, default value is false.
          long-summary: If specified, please make sure the kubernetes version is larger than 1.10.6.
        - name: --min-count
          type: int
          short-summary: Minimun nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specifying the value in the range of [1, 100].
        - name: --max-count
          type: int
          short-summary: Maximum nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specifying the value in the range of [1, 100].
        - name: --enable-vmss
          type: bool
          short-summary: (PREVIEW) Enable VMSS agent type.
        - name: --enable-pod-security-policy
          type: bool
          short-summary: (PREVIEW) Enable pod security policy.
        - name: --node-resource-group
          type: string
          short-summary: The node resource group is the resource group where all customer's resources will be created in, such as virtual machines.
        - name: --enable-acr
          type: bool
          short-summary: (PREVIEW) Grant the 'acrpull' role assignment for the ACR set by --acr.
        - name: --acr
          type: string
          short-summary: (PREVIEW) ACR name in AKS resource group or ACR resource ID. If it's empty and --enable-acr is true, then a new ACR with name 'aks<resource-group>acr' would be created.
    examples:
        - name: Create a Kubernetes cluster with an existing SSH public key.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --ssh-key-value /path/to/publickey
        - name: Create a Kubernetes cluster with a specific version.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --kubernetes-version 1.11.2
        - name: Create a Kubernetes cluster with a larger node pool.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --node-count 7
        - name: Create a kubernetes cluster with preview api version and cluster autosclaler enabled.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --kubernetes-version 1.11.2 --node-count 3 --enable-cluster-autoscaler --min-count 1 --max-count 5 --enable-vmss

""".format(sp_cache=AKS_SERVICE_PRINCIPAL_CACHE)

helps['aks scale'] = """
    type: command
    short-summary: Scale the node pool in a managed Kubernetes cluster.
    parameters:
        - name: --node-count -c
          type: int
          short-summary: Number of nodes in the Kubernetes node pool.
"""

helps['aks upgrade'] = """
    type: command
    short-summary: Upgrade a managed Kubernetes cluster to a newer version.
    long-summary: "Kubernetes will be unavailable during cluster upgrades."
    parameters:
        - name: --kubernetes-version -k
          type: string
          short-summary: Version of Kubernetes to upgrade the cluster to, such as "1.11.12".
          populator-commands:
          - "`az aks get-upgrades`"
"""

helps['aks update'] = """
    type: command
    short-summary: Update a managed Kubernetes cluster to enable/disable cluster-autoscaler or change min-count or max-count
    parameters:
        - name: --enable-cluster-autoscaler -e
          type: bool
          short-summary: Enable cluster autoscaler.
        - name: --disable-cluster-autoscaler -d
          type: bool
          short-summary: Disable cluster autoscaler.
        - name: --update-cluster-autoscaler -u
          type: bool
          short-summary: Update min-count or max-count for cluster autoscaler.
        - name: --min-count
          type: int
          short-summary: Minimun nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specifying the value in the range of [1, 100]
        - name: --max-count
          type: int
          short-summary: Maximum nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specifying the value in the range of [1, 100]
        - name: --api-server-authorized-ip-ranges
          type: str
          short-summary: List of authorized IP ranges (separated by comma) for apiserver. Set to "" for disabling it.
        - name: --enable-pod-security-policy
          type: bool
          short-summary: (PREVIEW) Enable pod security policy.
        - name: --disable-pod-security-policy
          type: bool
          short-summary: (PREVIEW) Disable pod security policy.
        - name: --enable-acr
          type: bool
          short-summary: (PREVIEW) Grant the 'acrpull' role assignment for the ACR set by --acr.
        - name: --disable-acr
          type: bool
          short-summary: (PREVIEW) Disable the 'acrpull' role assignment for the ACR set by --acr.
        - name: --acr
          type: string
          short-summary: (PREVIEW) ACR name in AKS resource group or ACR resource ID.
    examples:
      - name: Enable cluster-autoscaler within node count range [1,5]
        text: az aks update --enable-cluster-autoscaler --min-count 1 --max-count 5 -g MyResourceGroup -n MyManagedCluster
      - name: Disable cluster-autoscaler for an existing cluster
        text: az aks update --disable-cluster-autoscaler -g MyResourceGroup -n MyManagedCluster
      - name: Update min-count or max-count for cluster autoscaler.
        text: az aks update --update-cluster-autoscaler --min-count 1 --max-count 10 -g MyResourceGroup -n MyManagedCluster
      - name: Enable authorized IP ranges for apiserver.
        text: az aks update --api-server-authorized-ip-ranges 172.0.0.10/16,168.10.0.10/18 -g MyResourceGroup -n MyManagedCluster
      - name: Enable pod security policy.
        text: az aks update --enable-pod-security-policy -g MyResourceGroup -n MyManagedCluster
      - name: Disable pod security policy.
        text: az aks update --disable-pod-security-policy -g MyResourceGroup -n MyManagedCluster
"""

helps['aks nodepool'] = """
    type: group
    short-summary: Commands to manage node pools in Kubernetes kubernetes cluster.
"""
helps['aks nodepool show'] = """
    type: command
    short-summary: Show the details for a node pool in the managed Kubernetes cluster.
"""

helps['aks nodepool list'] = """
    type: command
    short-summary: List node pools in the managed Kubernetes cluster.
"""

helps['aks nodepool add'] = """
    type: command
    short-summary: Add a node pool to the managed Kubernetes cluster.
    parameters:
        - name: --node-vm-size -s
          type: string
          short-summary: Size of Virtual Machines to create as Kubernetes nodes.
        - name: --node-count -c
          type: int
          short-summary: Number of nodes in the Kubernetes agent pool. After creating a cluster, you can change the
                         size of its node pool with `az aks scale`.
        - name: --kubernetes-version -k
          type: string
          short-summary: Version of Kubernetes to use for creating the cluster, such as "1.7.12" or "1.8.7".
          populator-commands:
          - "`az aks get-versions`"
        - name: --node-osdisk-size
          type: int
          short-summary: Size in GB of the OS disk for each node in the agent pool. Minimum 30 GB.
        - name: --max-pods -m
          type: int
          short-summary: The maximum number of pods deployable to a node.
          long-summary: If not specified, defaults to 110, or 30 for advanced networking configurations.
        - name: --node-zones
          type: string array
          short-summary: (PREVIEW) Availability zones where agent nodes will be placed.
        - name: --vnet-subnet-id
          type: string
          short-summary: The ID of a subnet in an existing VNet into which to deploy the cluster.
        - name: --os-type
          type: string
          short-summary: The OS Type. Linux or Windows.
        - name: --enable-cluster-autoscaler -e
          type: bool
          short-summary: Enable cluster autoscaler.
        - name: --min-count
          type: int
          short-summary: Minimun nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specifying the value in the range of [1, 100]
        - name: --max-count
          type: int
          short-summary: Maximum nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specifying the value in the range of [1, 100]
"""

helps['aks nodepool scale'] = """
    type: command
    short-summary: Scale the node pool in a managed Kubernetes cluster.
    parameters:
        - name: --node-count -c
          type: int
          short-summary: Number of nodes in the Kubernetes node pool.
"""

helps['aks nodepool upgrade'] = """
    type: command
    short-summary: Upgrade the node pool in a managed Kubernetes cluster.
    parameters:
        - name: --kubernetes-version -k
          type: string
          short-summary: Version of Kubernetes to upgrade the node pool to, such as "1.11.12".
"""

helps['aks nodepool update'] = """
    type: command
    short-summary: Update a node pool to enable/disable cluster-autoscaler or change min-count or max-count
    parameters:
        - name: --enable-cluster-autoscaler -e
          type: bool
          short-summary: Enable cluster autoscaler.
        - name: --disable-cluster-autoscaler -d
          type: bool
          short-summary: Disable cluster autoscaler.
        - name: --update-cluster-autoscaler -u
          type: bool
          short-summary: Update min-count or max-count for cluster autoscaler.
        - name: --min-count
          type: int
          short-summary: Minimun nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specifying the value in the range of [1, 100]
        - name: --max-count
          type: int
          short-summary: Maximum nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specifying the value in the range of [1, 100]
    examples:
      - name: Enable cluster-autoscaler within node count range [1,5]
        text: az aks nodepool update --enable-cluster-autoscaler --min-count 1 --max-count 5 -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster
      - name: Disable cluster-autoscaler for an existing cluster
        text: az aks nodepool update --disable-cluster-autoscaler -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster
      - name: Update min-count or max-count for cluster autoscaler.
        text: az aks nodepool update --update-cluster-autoscaler --min-count 1 --max-count 10 -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster
"""

helps['aks nodepool delete'] = """
    type: command
    short-summary: Delete the agent pool in the managed Kubernetes cluster.
"""

helps['aks enable-addons'] = """
type: command
short-summary: Enable Kubernetes addons.
long-summary: |-
    These addons are available:
        http_application_routing - configure ingress with automatic public DNS name creation.
        monitoring - turn on Log Analytics monitoring. Requires "--workspace-resource-id".
        virtual-node - enable AKS Virtual Node (PREVIEW). Requires "--subnet-name".
        azure-policy - enable Azure policy (PREVIEW).
parameters:
  - name: --addons -a
    type: string
    short-summary: Enable the Kubernetes addons in a comma-separated list.
  - name: --workspace-resource-id
    type: string
    short-summary: The resource ID of an existing Log Analytics Workspace to use for storing monitoring data.
  - name: --subnet-name -s
    type: string
    short-summary: The subnet name for the virtual node to use.
examples:
  - name: Enable Kubernetes addons. (autogenerated)
    text: az aks enable-addons --addons virtual-node --name MyManagedCluster --resource-group MyResourceGroup --subnet-name VirtualNodeSubnet
    crafted: true
"""

helps['aks get-versions'] = """
type: command
short-summary: Get the versions available for creating a managed Kubernetes cluster.
examples:
  - name: Get the versions available for creating a managed Kubernetes cluster
    text: az aks get-versions --location westus2
    crafted: true
"""

helps['aks get-credentials'] = """
type: command
short-summary: Get access credentials for a managed Kubernetes cluster.
parameters:
  - name: --admin -a
    type: bool
    short-summary: "Get cluster administrator credentials.  Default: cluster user credentials."
  - name: --file -f
    type: string
    short-summary: Kubernetes configuration file to update. Use "-" to print YAML to stdout instead.
  - name: --overwrite-existing
    type: bool
    short-summary: Overwrite any existing cluster entry with the same name.
  - name: --output -o
    type: string
    long-summary: Credentials are always in YAML format, so this argument is effectively ignored.
examples:
  - name: Get access credentials for a managed Kubernetes cluster. (autogenerated)
    text: az aks get-credentials --name MyManagedCluster --resource-group MyResourceGroup
    crafted: true
"""
