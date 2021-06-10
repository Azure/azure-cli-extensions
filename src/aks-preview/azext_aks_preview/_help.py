# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os.path

from knack.help_files import helps

ACS_SERVICE_PRINCIPAL_CACHE = os.path.join(
    '$HOME', '.azure', 'acsServicePrincipal.json')
AKS_SERVICE_PRINCIPAL_CACHE = os.path.join(
    '$HOME', '.azure', 'aksServicePrincipal.json')

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
        - name: --node-osdisk-type
          type: string
          short-summary: OS disk type to be used for machines in a given agent pool. Defaults to 'Managed'. May not be changed for this pool after creation.
        - name: --node-osdisk-diskencryptionset-id
          type: string
          short-summary: ResourceId of the disk encryption set to use for enabling encryption at rest.
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
          long-summary: |-
            Rules for windows-admin-username:
                - restriction: Cannot end in "."
                - Disallowed values: "administrator", "admin", "user", "user1", "test", "user2", "test1", "user3", "admin1", "1", "123", "a", "actuser", "adm", "admin2", "aspnet", "backup", "console", "david", "guest", "john", "owner", "root", "server", "sql", "support", "support_388945a0", "sys", "test2", "test3", "user4", "user5".
                - Minimum-length: 1 character
                - Max-length: 20 characters
            Reference: https://docs.microsoft.com/en-us/dotnet/api/microsoft.azure.management.compute.models.virtualmachinescalesetosprofile.adminusername?view=azure-dotnet
        - name: --windows-admin-password
          type: string
          short-summary: User account password to use on windows node VMs.
          long-summary: |-
            Rules for windows-admin-password:
                - Minimum-length: 14 characters
                - Max-length: 123 characters
                - Complexity requirements: 3 out of 4 conditions below need to be fulfilled
                  * Has lower characters
                  * Has upper characters
                  * Has a digit
                  * Has a special character (Regex match [\\W_])
                - Disallowed values:  "abc@123", "P@$$w0rd", "P@ssw0rd", "P@ssword123", "Pa$$word", "pass@word1", "Password!", "Password1", "Password22", "iloveyou!"
            Reference: https://docs.microsoft.com/en-us/dotnet/api/microsoft.azure.management.compute.models.virtualmachinescalesetosprofile.adminpassword?view=azure-dotnet
        - name: --enable-ahub
          type: bool
          short-summary: Enable Azure Hybrid User Benefits (AHUB) for Windows VMs.
        - name: --enable-aad
          type: bool
          short-summary: Enable managed AAD feature for cluster.
        - name: --enable-azure-rbac
          type: bool
          short-summary: Enable Azure RBAC to control authorization checks on cluster.
        - name: --aad-admin-group-object-ids
          type: string
          short-summary: Comma seperated list of aad group object IDs that will be set as cluster admin.
        - name: --aad-client-app-id
          type: string
          short-summary: The ID of an Azure Active Directory client application of type "Native". This
                         application is for user login via kubectl.
        - name: --aad-server-app-id
          type: string
          short-summary: The ID of an Azure Active Directory server application of type "Web app/API". This
                         application represents the managed cluster's apiserver (Server application).
        - name: --aad-server-app-secret
          type: string
          short-summary: The secret of an Azure Active Directory server application.
        - name: --aad-tenant-id
          type: string
          short-summary: The ID of an Azure Active Directory tenant.
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
          short-summary: Azure Load Balancer SKU selection for your cluster. basic or standard.
          long-summary: Select between Basic or Standard Azure Load Balancer SKU for your AKS cluster.
        - name: --load-balancer-managed-outbound-ip-count
          type: int
          short-summary: Load balancer managed outbound IP count.
          long-summary: Desired number of managed outbound IPs for load balancer outbound connection. Valid for Standard SKU load balancer cluster only.
        - name: --load-balancer-outbound-ips
          type: string
          short-summary: Load balancer outbound IP resource IDs.
          long-summary: Comma-separated public IP resource IDs for load balancer outbound connection. Valid for Standard SKU load balancer cluster only.
        - name: --load-balancer-outbound-ip-prefixes
          type: string
          short-summary: Load balancer outbound IP prefix resource IDs.
          long-summary: Comma-separated public IP prefix resource IDs for load balancer outbound connection. Valid for Standard SKU load balancer cluster only.
        - name: --load-balancer-outbound-ports
          type: int
          short-summary: Load balancer outbound allocated ports.
          long-summary: Desired static number of outbound ports per VM in the load balancer backend pool. By default, set to 0 which uses the default allocation based on the number of VMs. Please specify a value in the range of [0, 64000] that is a multiple of 8.
        - name: --load-balancer-idle-timeout
          type: int
          short-summary: Load balancer idle timeout in minutes.
          long-summary: Desired idle timeout for load balancer outbound flows, default is 30 minutes. Please specify a value in the range of [4, 100].
        - name: --outbound-type
          type: string
          short-summary: How outbound traffic will be configured for a cluster.
          long-summary: Select between loadBalancer and userDefinedRouting. If not set, defaults to type loadBalancer. Requires --vnet-subnet-id to be provided with a preconfigured route table and --load-balancer-sku to be Standard.
        - name: --enable-addons -a
          type: string
          short-summary: Enable the Kubernetes addons in a comma-separated list.
          long-summary: |-
            These addons are available:
                http_application_routing        - configure ingress with automatic public DNS name creation.
                monitoring                      - turn on Log Analytics monitoring. Uses the Log Analytics Default Workspace if it exists, else creates one. Specify "--workspace-resource-id" to use an existing workspace.
                                                  If monitoring addon is enabled --no-wait argument will have no effect
                virtual-node                    - enable AKS Virtual Node. Requires --aci-subnet-name to provide the name of an existing subnet for the Virtual Node to use.
                                                  aci-subnet-name must be in the same vnet which is specified by --vnet-subnet-id (required as well).
                azure-policy                    - enable Azure policy. The Azure Policy add-on for AKS enables at-scale enforcements and safeguards on your clusters in a centralized, consistent manner.
                                                  Learn more at aka.ms/aks/policy.
                ingress-appgw                   - enable Application Gateway Ingress Controller addon (PREVIEW).
                confcom                         - enable confcom addon, this will enable SGX device plugin by default(PREVIEW).
                open-service-mesh               - enable Open Service Mesh addon (PREVIEW).
                gitops                          - enable GitOps (PREVIEW).
                azure-keyvault-secrets-provider - enable Azure Keyvault Secrets Provider addon (PREVIEW).
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
        - name: --pod-subnet-id
          type: string
          short-summary: The ID of a subnet in an existing VNet into which to assign pods in the cluster (requires azure network-plugin)
        - name: --ppg
          type: string
          short-summary: The ID of a PPG.
        - name: --os-sku
          type: string
          short-summary: The os-sku of the agent node pool. Ubuntu or CBLMariner.
        - name: --enable-fips-image
          type: bool
          short-summary: Use FIPS-enabled OS on agent nodes.
        - name: --workspace-resource-id
          type: string
          short-summary: The resource ID of an existing Log Analytics Workspace to use for storing monitoring data. If not specified, uses the default Log Analytics Workspace if it exists, otherwise creates one.
        - name: --enable-cluster-autoscaler
          type: bool
          short-summary: Enable cluster autoscaler, default value is false.
          long-summary: If specified, please make sure the kubernetes version is larger than 1.10.6.
        - name: --min-count
          type: int
          short-summary: Minimun nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specify the value in the range of [1, 100].
        - name: --max-count
          type: int
          short-summary: Maximum nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specify the value in the range of [1, 100].
        - name: --cluster-autoscaler-profile
          type: list
          short-summary: Space-separated list of key=value pairs for configuring cluster autoscaler. Pass an empty string to clear the profile.
        - name: --vm-set-type
          type: string
          short-summary: Agent pool vm set type. VirtualMachineScaleSets or AvailabilitySet.
        - name: --enable-pod-security-policy
          type: bool
          short-summary: (PREVIEW) Enable pod security policy.
        - name: --node-resource-group
          type: string
          short-summary: The node resource group is the resource group where all customer's resources will be created in, such as virtual machines.
        - name: --uptime-sla
          type: bool
          short-summary: Enable a paid managed cluster service with a financially backed SLA.
        - name: --attach-acr
          type: string
          short-summary: Grant the 'acrpull' role assignment to the ACR specified by name or resource ID.
        - name: --enable-private-cluster
          type: string
          short-summary: Enable private cluster.
        - name: --private-dns-zone
          type: string
          short-summary: Private dns zone mode for private cluster. "none" mode is in preview.
          long-summary: Allowed values are "system", "none" (Preview) or your custom private dns zone resource id. If not set, defaults to type system. Requires --enable-private-cluster to be used.
        - name: --fqdn-subdomain
          type: string
          short-summary: Prefix for FQDN that is created for private cluster with custom private dns zone scenario.
        - name: --enable-public-fqdn
          type: bool
          short-summary: (Preview) Enable public fqdn feature for private cluster.
        - name: --enable-node-public-ip
          type: bool
          short-summary: Enable VMSS node public IP.
        - name: --node-public-ip-prefix-id
          type: string
          short-summary: Public IP prefix ID used to assign public IPs to VMSS nodes.
        - name: --enable-managed-identity
          type: bool
          short-summary: Using managed identity to manage cluster resource group. Default value is true, you can explicitly specify "--client-id" and "--secret" to disable managed identity.
        - name: --assign-identity
          type: string
          short-summary: Specify an existing user assigned identity to manage cluster resource group.
        - name: --assign-kubelet-identity
          type: string
          short-summary: Specify an existing user assigned identity for kubelet's usage, which is typically used to pull image from ACR.
        - name: --api-server-authorized-ip-ranges
          type: string
          short-summary: Comma seperated list of authorized apiserver IP ranges. Set to 0.0.0.0/32 to restrict apiserver traffic to node pools.
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
        - name: --appgw-name
          type: string
          short-summary: Name of the application gateway to create/use in the node resource group. Use with ingress-azure addon.
        - name: --appgw-subnet-prefix
          type: string
          short-summary: Subnet Prefix to use for a new subnet created to deploy the Application Gateway. Use with ingress-azure addon.
        - name: --appgw-subnet-cidr
          type: string
          short-summary: Subnet CIDR to use for a new subnet created to deploy the Application Gateway. Use with ingress-azure addon.
        - name: --appgw-id
          type: string
          short-summary: Resource Id of an existing Application Gateway to use with AGIC. Use with ingress-azure addon.
        - name: --appgw-subnet-id
          type: string
          short-summary: Resource Id of an existing Subnet used to deploy the Application Gateway. Use with ingress-azure addon.
        - name: --appgw-watch-namespace
          type: string
          short-summary: Specify the namespace, which AGIC should watch. This could be a single string value, or a comma-separated list of namespaces.
        - name: --enable-sgxquotehelper
          type: bool
          short-summary: Enable SGX quote helper for confcom addon.
        - name: --auto-upgrade-channel
          type: string
          short-summary: Specify the upgrade channel for autoupgrade. It could be rapid, stable, patch, node-image or none, none means disable autoupgrade.
        - name: --kubelet-config
          type: string
          short-summary: Kubelet configurations for agent nodes.
        - name: --linux-os-config
          type: string
          short-summary: OS configurations for Linux agent nodes.
        - name: --enable-pod-identity
          type: bool
          short-summary: (PREVIEW) Enable pod identity addon.
        - name: --enable-pod-identity-with-kubenet
          type: bool
          short-summary: (PREVIEW) Enable pod identity addon for cluster using Kubnet network plugin.
        - name: --aci-subnet-name
          type: string
          short-summary: The name of a subnet in an existing VNet into which to deploy the virtual nodes.
        - name: --tags
          type: string
          short-summary: The tags of the managed cluster. The managed cluster instance and all resources managed by the cloud provider will be tagged.
        - name: --enable-encryption-at-host
          type: bool
          short-summary: Enable EncryptionAtHost on agent node pool.
        - name: --enable-ultra-ssd
          type: bool
          short-summary: Enable UltraSSD on agent node pool.
        - name: --enable-secret-rotation
          type: bool
          short-summary: Enable secret rotation. Use with azure-keyvault-secrets-provider addon.
        - name: --disable-local-accounts
          type: bool
          short-summary: (Preview) If set to true, getting static credential will be disabled for this cluster.
    examples:
        - name: Create a Kubernetes cluster with an existing SSH public key.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --ssh-key-value /path/to/publickey
        - name: Create a Kubernetes cluster with a specific version.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --kubernetes-version 1.13.9
        - name: Create a Kubernetes cluster with a larger node pool.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --node-count 7
        - name: Create a kubernetes cluster with cluster autosclaler enabled.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --kubernetes-version 1.13.9 --node-count 3 --enable-cluster-autoscaler --min-count 1 --max-count 5
        - name: Create a kubernetes cluster with k8s 1.13.9 but use vmas.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --kubernetes-version 1.13.9 --vm-set-type AvailabilitySet
        - name: Create a kubernetes cluster with default kubernetes vesrion, default SKU load balancer(standard) and default vm set type(VirtualMachineScaleSets).
          text: az aks create -g MyResourceGroup -n MyManagedCluster
        - name: Create a kubernetes cluster with standard SKU load balancer and two AKS created IPs for the load balancer outbound connection usage.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --load-balancer-managed-outbound-ip-count 2
        - name: Create a kubernetes cluster with standard SKU load balancer and use the provided public IPs for the load balancer outbound connection usage.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --load-balancer-outbound-ips <ip-resource-id-1,ip-resource-id-2>
        - name: Create a kubernetes cluster with standard SKU load balancer and use the provided public IP prefixes for the load balancer outbound connection usage.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --load-balancer-outbound-ip-prefixes <ip-prefix-resource-id-1,ip-prefix-resource-id-2>
        - name: Create a kubernetes cluster with a standard SKU load balancer, with two outbound AKS managed IPs an idle flow timeout of 5 minutes and 8000 allocated ports per machine
          text: az aks create -g MyResourceGroup -n MyManagedCluster --load-balancer-managed-outbound-ip-count 2 --load-balancer-idle-timeout 5 --load-balancer-outbound-ports 8000
        - name: Create a kubernetes cluster with basic SKU load balancer and AvailabilitySet vm set type.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --load-balancer-sku basic --vm-set-type AvailabilitySet
        - name: Create a kubernetes cluster with authorized apiserver IP ranges.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --api-server-authorized-ip-ranges 193.168.1.0/24,194.168.1.0/24,195.168.1.0
        - name: Create a kubernetes cluster with server side encryption using your owned key.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --node-osdisk-diskencryptionset-id <disk-encryption-set-resource-id>
        - name: Create a kubernetes cluster with userDefinedRouting, standard load balancer SKU and a custom subnet preconfigured with a route table
          text: az aks create -g MyResourceGroup -n MyManagedCluster --outbound-type userDefinedRouting --load-balancer-sku standard --vnet-subnet-id customUserSubnetVnetID
        - name: Create a kubernetes cluster with supporting Windows agent pools with AHUB enabled.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --load-balancer-sku Standard --network-plugin azure --windows-admin-username azure --windows-admin-password 'replacePassword1234$' --enable-ahub
        - name: Create a kubernetes cluster with managed AAD enabled.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --enable-aad --aad-admin-group-object-ids <id-1,id-2> --aad-tenant-id <id>
        - name: Create a kubernetes cluster with ephemeral os enabled.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --node-osdisk-type Ephemeral --node-osdisk-size 48
        - name: Create a kubernetes cluster with custom tags
          text: az aks create -g MyResourceGroup -n MyManagedCluster --tags "foo=bar" "baz=qux"
        - name: Create a kubernetes cluster with EncryptionAtHost enabled.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --enable-encryption-at-host
        - name: Create a kubernetes cluster with UltraSSD enabled.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --enable-ultra-ssd
        - name: Create a kubernetes cluster with custom control plane identity and kubelet identity.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --assign-identity <control-plane-identity-resource-id> --assign-kubelet-identity <kubelet-identity-resource-id>
        - name: Create a kubernetes cluster with Azure RBAC enabled.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --enable-aad --enable-azure-rbac
        - name: Create a kubernetes cluster with a specific os-sku
          text: az aks create -g MyResourceGroup -n MyManagedCluster --os-sku Ubuntu
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
        - name: --control-plane-only
          type: bool
          short-summary: Upgrade the cluster control plane only. If not specified, control plane AND all node pools will be upgraded.
        - name: --node-image-only
          type: bool
          short-summary: Only upgrade node image for agent pools.
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
"""

helps['aks update'] = """
    type: command
    short-summary: Update a managed Kubernetes cluster properties, such as enable/disable cluster-autoscaler
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
          short-summary: Minimun nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specify the value in the range of [1, 100]
        - name: --max-count
          type: int
          short-summary: Maximum nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specify the value in the range of [1, 100]
        - name: --uptime-sla
          type: bool
          short-summary: Enable a paid managed cluster service with a financially backed SLA.
        - name: --no-uptime-sla
          type: bool
          short-summary: Change a paid managed cluster to a free one.
        - name: --cluster-autoscaler-profile
          type: list
          short-summary: Space-separated list of key=value pairs for configuring cluster autoscaler. Pass an empty string to clear the profile.
        - name: --load-balancer-managed-outbound-ip-count
          type: int
          short-summary: Load balancer managed outbound IP count.
          long-summary: Desired number of managed outbound IPs for load balancer outbound connection. Valid for Standard SKU load balancer cluster only. If updated, it will wipe off the existing setting on Load balancer managed outbound IP count; Load balancer outbound IP resource IDs and Load balancer outbound IP prefix resource IDs.
        - name: --load-balancer-outbound-ips
          type: string
          short-summary: Load balancer outbound IP resource IDs.
          long-summary: Comma-separated public IP resource IDs for load balancer outbound connection. Valid for Standard SKU load balancer cluster only. If updated, it will wipe off the existing setting on Load balancer managed outbound IP count; Load balancer outbound IP resource IDs and Load balancer outbound IP prefix resource IDs.
        - name: --load-balancer-outbound-ip-prefixes
          type: string
          short-summary: Load balancer outbound IP prefix resource IDs.
          long-summary: Comma-separated public IP prefix resource IDs for load balancer outbound connection. Valid for Standard SKU load balancer cluster only. If updated, it will wipe off the existing setting on Load balancer managed outbound IP count; Load balancer outbound IP resource IDs and Load balancer outbound IP prefix resource IDs.
        - name: --load-balancer-outbound-ports
          type: int
          short-summary: Load balancer outbound allocated ports.
          long-summary: Desired static number of outbound ports per VM in the load balancer backend pool. By default, set to 0 which uses the default allocation based on the number of VMs. Please specify a value in the range of [0, 64000] that is a multiple of 8.
        - name: --load-balancer-idle-timeout
          type: int
          short-summary: Load balancer idle timeout in minutes.
          long-summary: Desired idle timeout for load balancer outbound flows, default is 30 minutes. Please specify a value in the range of [4, 100].
        - name: --enable-pod-security-policy
          type: bool
          short-summary: (PREVIEW) Enable pod security policy.
        - name: --disable-pod-security-policy
          type: bool
          short-summary: (PREVIEW) Disable pod security policy.
        - name: --attach-acr
          type: string
          short-summary: Grant the 'acrpull' role assignment to the ACR specified by name or resource ID.
        - name: --detach-acr
          type: string
          short-summary: Disable the 'acrpull' role assignment to the ACR specified by name or resource ID.
        - name: --api-server-authorized-ip-ranges
          type: string
          short-summary: Comma seperated list of authorized apiserver IP ranges. Set to "" to allow all traffic on a previously restricted cluster. Set to 0.0.0.0/32 to restrict apiserver traffic to node pools.
        - name: --enable-aad
          type: bool
          short-summary: Enable managed AAD feature for cluster.
        - name: --aad-admin-group-object-ids
          type: string
          short-summary: Comma seperated list of aad group object IDs that will be set as cluster admin.
        - name: --aad-tenant-id
          type: string
          short-summary: The ID of an Azure Active Directory tenant.
        - name: --enable-ahub
          type: bool
          short-summary: Enable Azure Hybrid User Benefits (AHUB) feature for cluster.
        - name: --disable-ahub
          type: bool
          short-summary: Disable Azure Hybrid User Benefits (AHUB) feature for cluster.
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
        - name: --auto-upgrade-channel
          type: string
          short-summary: Specify the upgrade channel for autoupgrade. It could be rapid, stable, patch, node-image or none, none means disable autoupgrade.
        - name: --enable-managed-identity
          type: bool
          short-summary: (PREVIEW) Update current cluster to managed identity to manage cluster resource group.
        - name: --assign-identity
          type: string
          short-summary: (PREVIEW) Specify an existing user assigned identity to manage cluster resource group.
        - name: --enable-pod-identity
          type: bool
          short-summary: (PREVIEW) Enable Pod Identity addon for cluster.
        - name: --enable-pod-identity-with-kubenet
          type: bool
          short-summary: (PREVIEW) Enable pod identity addon for cluster using Kubnet network plugin.
        - name: --disable-pod-identity
          type: bool
          short-summary: (PREVIEW) Disable Pod Identity addon for cluster.
        - name: --enable-secret-rotation
          type: bool
          short-summary: Enable secret rotation. Use with azure-keyvault-secrets-provider addon.
        - name: --disable-secret-rotation
          type: bool
          short-summary: Disable secret rotation. Use with azure-keyvault-secrets-provider addon.
        - name: --tags
          type: string
          short-summary: The tags of the managed cluster. The managed cluster instance and all resources managed by the cloud provider will be tagged.
        - name: --windows-admin-password
          type: string
          short-summary: User account password to use on windows node VMs.
          long-summary: |-
            Rules for windows-admin-password:
                - Minimum-length: 14 characters
                - Max-length: 123 characters
                - Complexity requirements: 3 out of 4 conditions below need to be fulfilled
                  * Has lower characters
                  * Has upper characters
                  * Has a digit
                  * Has a special character (Regex match [\\W_])
                - Disallowed values:  "abc@123", "P@$$w0rd", "P@ssw0rd", "P@ssword123", "Pa$$word", "pass@word1", "Password!", "Password1", "Password22", "iloveyou!"
            Reference: https://docs.microsoft.com/en-us/dotnet/api/microsoft.azure.management.compute.models.virtualmachinescalesetosprofile.adminpassword?view=azure-dotnet
        - name: --enable-azure-rbac
          type: bool
          short-summary: Enable Azure RBAC to control authorization checks on cluster.
        - name: --disable-azure-rbac
          type: bool
          short-summary: Disable Azure RBAC to control authorization checks on cluster.
        - name: --disable-local-accounts
          type: bool
          short-summary: (Preview) If set to true, getting static credential will be disabled for this cluster.
        - name: --enable-local-accounts
          type: bool
          short-summary: (Preview) If set to true, will enable getting static credential for this cluster.
        - name: --enable-public-fqdn
          type: bool
          short-summary: (Preview) Enable public fqdn feature for private cluster.
        - name: --disable-public-fqdn
          type: bool
          short-summary: (Preview) Disable public fqdn feature for private cluster.
    examples:
      - name: Enable cluster-autoscaler within node count range [1,5]
        text: az aks update --enable-cluster-autoscaler --min-count 1 --max-count 5 -g MyResourceGroup -n MyManagedCluster
      - name: Disable cluster-autoscaler for an existing cluster
        text: az aks update --disable-cluster-autoscaler -g MyResourceGroup -n MyManagedCluster
      - name: Update min-count or max-count for cluster autoscaler.
        text: az aks update --update-cluster-autoscaler --min-count 1 --max-count 10 -g MyResourceGroup -n MyManagedCluster
      - name: Enable pod security policy.
        text: az aks update --enable-pod-security-policy -g MyResourceGroup -n MyManagedCluster
      - name: Disable pod security policy.
        text: az aks update --disable-pod-security-policy -g MyResourceGroup -n MyManagedCluster
      - name: Update a kubernetes cluster with standard SKU load balancer to use two AKS created IPs for the load balancer outbound connection usage.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --load-balancer-managed-outbound-ip-count 2
      - name: Update a kubernetes cluster with standard SKU load balancer to use the provided public IPs for the load balancer outbound connection usage.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --load-balancer-outbound-ips <ip-resource-id-1,ip-resource-id-2>
      - name: Update a kubernetes cluster with standard SKU load balancer to use the provided public IP prefixes for the load balancer outbound connection usage.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --load-balancer-outbound-ip-prefixes <ip-prefix-resource-id-1,ip-prefix-resource-id-2>
      - name: Update a kubernetes cluster with two outbound AKS managed IPs an idle flow timeout of 5 minutes and 8000 allocated ports per machine
        text: az aks update -g MyResourceGroup -n MyManagedCluster --load-balancer-managed-outbound-ip-count 2 --load-balancer-idle-timeout 5 --load-balancer-outbound-ports 8000
      - name: Update a kubernetes cluster with authorized apiserver ip ranges.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --api-server-authorized-ip-ranges 193.168.1.0/24,194.168.1.0/24
      - name: Disable authorized apiserver ip ranges feature for a kubernetes cluster.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --api-server-authorized-ip-ranges ""
      - name: Restrict apiserver traffic in a kubernetes cluster to agentpool nodes.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --api-server-authorized-ip-ranges 0.0.0.0/32
      - name: Update a AKS-managed AAD cluster with tenant ID or admin group object IDs.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --aad-admin-group-object-ids <id-1,id-2> --aad-tenant-id <id>
      - name: Migrate a AKS AAD-Integrated cluster or a non-AAAAD cluster to a AKS-managed AAD cluster.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --enable-aad --aad-admin-group-object-ids <id-1,id-2> --aad-tenant-id <id>
      - name: Enable Azure Hybrid User Benefits featture for a kubernetes cluster.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --enable-ahub
      - name: Disable Azure Hybrid User Benefits featture for a kubernetes cluster.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --disable-ahub
      - name: Update the cluster to use system assigned managed identity in control plane.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --enable-managed-identity
      - name: Update the cluster to use user assigned managed identity in control plane.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --enable-managed-identity --assign-identity <user_assigned_identity_resource_id>
      - name: Enable pod identity addon.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --enable-pod-identity
      - name: Disable pod identity addon.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --disable-pod-identity
      - name: Update the tags of a kubernetes cluster
        text: az aks update -g MyResourceGroup -n MyManagedCLuster --tags "foo=bar" "baz=qux"
      - name: Update Windows password of a kubernetes cluster
        text: az aks update -g MyResourceGroup -n MyManagedCLuster --windows-admin-password "Repl@cePassw0rd12345678"
      - name: Update a managed AAD AKS cluster to use Azure RBAC
        text: az aks update -g MyResourceGroup -n MyManagedCluster --enable-azure-rbac
      - name: Disable Azure RBAC in a managed AAD AKS cluster
        text: az aks update -g MyResourceGroup -n MyManagedCluster --disable-azure-rbac
"""

helps['aks kollect'] = """
    type: command
    short-summary: Collecting diagnostic information for the Kubernetes cluster.
    long-summary: |-
        Collect diagnostic information for the Kubernetes cluster and store it in the specified storage account.
        You can provide the storage account in three ways:
          storage account name and a shared access signature with write permission.
          resource Id to a storage account you own.
          the storagea account in diagnostics settings for your managed cluster.
    parameters:
        - name: --storage-account
          type: string
          short-summary: Name or ID of the storage account to save the diagnostic information.
        - name: --sas-token
          type: string
          short-summary: The SAS token with writable permission for the storage account.
        - name: --container-logs
          type: string
          short-summary: The list of container logs to collect.
          long-summary: |-
            The list of container logs to collect. Its value can be either all containers
            in a namespace, for example, kube-system, or a specific container in a
            namespace, for example, kube-system/tunnelfront.
        - name: --kube-objects
          type: string
          short-summary: The list of kubernetes objects to describe.
          long-summary: |-
            The list of kubernetes objects to describe. Its value can be either all objects of a type
            in a namespace, for example, kube-system/pod, or a specific object of a type in a namespace,
            for example, kube-system/deployment/tunnelfront.
        - name: --node-logs
          type: string
          short-summary: The list of node logs to collect. For example, /var/log/cloud-init.log
    examples:
      - name: using storage account name and a shared access signature token with write permission
        text: az aks kollect -g MyResourceGroup -n MyManagedCluster --storage-account MyStorageAccount --sas-token "MySasToken"
      - name: using the resource id of a storagea account resource you own.
        text: az aks kollect -g MyResourceGroup -n MyManagedCluster --storage-account "MyStoreageAccountResourceId"
      - name: using the storagea account in diagnostics settings for your managed cluster.
        text: az aks kollect -g MyResourceGroup -n MyManagedCluster
      - name: customize the container logs to collect.
        text: az aks kollect -g MyResourceGroup -n MyManagedCluster --container-logs "mynamespace1/mypod1 myns2"
      - name: customize the kubernetes objects to collect.
        text: az aks kollect -g MyResourceGroup -n MyManagedCluster --kube-objects "mynamespace1/service myns2/deployment/deployment1"
      - name: customize the node log files to collect.
        text: az aks kollect -g MyResourceGroup -n MyManagedCluster --node-logs "/var/log/azure-vnet.log /var/log/azure-vnet-ipam.log"
"""

helps['aks kanalyze'] = """
    type: command
    short-summary: Display diagnostic results for the Kubernetes cluster after kollect is done.
"""

helps['aks command'] = """
    type: group
    short-summary: see detail usage in 'az aks command invoke', 'az aks command result'.
"""

helps['aks command invoke'] = """
    type: command
    short-summary: run a shell command (with kubectl, helm) on your aks cluster, support attaching files as well.
    parameters:
        - name: --command -c
          type: string
          short-summary: command or shell script you want run.
        - name: --file -f
          type: string
          short-summary: files will be used by the command, use '.' to attach the current folder.
"""

helps['aks command result'] = """
    type: command
    short-summary: fetch result from previously triggered 'aks command invoke'.
    parameters:
        - name: --command-id -i
          type: string
          short-summary: commandId returned from 'aks command invoke'.
"""

helps['aks maintenanceconfiguration'] = """
    type: group
    short-summary: Commands to manage maintenance configurations in managed Kubernetes cluster.
"""

helps['aks maintenanceconfiguration show'] = """
    type: command
    short-summary: show the details of a maintenance configuration in managed Kubernetes cluster.
"""

helps['aks maintenanceconfiguration delete'] = """
    type: command
    short-summary: Delete a maintenance configuration in managed Kubernetes cluster.
"""

helps['aks maintenanceconfiguration list'] = """
    type: command
    short-summary: List maintenance configurations in managed Kubernetes cluster.
"""

helps['aks maintenanceconfiguration add'] = """
    type: command
    short-summary: Add a maintenance configuration in managed Kubernetes cluster.
    parameters:
        - name: --weekday
          type: string
          short-summary: A day in week on which maintenance is allowed. E.g. Monday
        - name: --start-hour
          type: string
          short-summary: The start time of 1 hour window which maintenance is allowd. E.g. 1 means it's allowd between 1:00 am and 2:00 am
        - name: --config-file
          type: string
          short-summary: the maintenance configuration json file.
    examples:
        - name: Add a maintenance configuration with --weekday and --start-hour.
          text: |
            az aks maintenanceconfiguration add -g xiazhan-mtc-stg --cluster-name test1 -n default --weekday Monday  --start-hour 1
              The maintenance is allowed on Monday 1:00am to 2:00am
        - name: Add a maintenance configuration with --weekday.The maintenance is allowd on any time of that day.
          text: |
            az aks maintenanceconfiguration add -g xiazhan-mtc-stg --cluster-name test1 -n default --weekday Monday
              The maintenance is allowed on Monday.
        - name: Add a maintenance configuration with maintenance configuration json file
          text: |
            az aks maintenanceconfiguration add -g xiazhan-mtc-stg --cluster-name test1 -n default --config-file ./test.json
                The content of json file looks below. It means the maintenance is allowed on UTC time Tuesday 1:00am - 3:00 am and Wednesday 1:00am - 2:00am, 6:00am-7:00am
                No maintenance is allowed from 2020-11-26T03:00:00Z to 2020-11-30T12:00:00Z and from 2020-12-26T03:00:00Z to 2020-12-26T12:00:00Z even if they are allowed in the above weekly setting
                {
                      "timeInWeek": [
                        {
                          "day": "Tuesday",
                          "hour_slots": [
                            1,
                            2
                          ]
                        },
                        {
                          "day": "Wednesday",
                          "hour_slots": [
                            1,
                            6
                          ]
                        }
                      ],
                      "notAllowedTime": [
                        {
                          "start": "2021-11-26T03:00:00Z",
                          "end": "2021-11-30T12:00:00Z"
                        },
                        {
                          "start": "2021-12-26T03:00:00Z",
                          "end": "2021-12-26T12:00:00Z"
                        }
                      ]
              }
"""

helps['aks maintenanceconfiguration update'] = """
    type: command
    short-summary: Update a maintenance configuration of a managed Kubernetes cluster.
    parameters:
        - name: --weekday
          type: string
          short-summary: A day in week on which maintenance is allowed. E.g. Monday
        - name: --start-hour
          type: string
          short-summary: The start time of 1 hour window which maintenance is allowd. E.g. 1 means it's allowd between 1:00 am and 2:00 am
        - name: --config-file
          type: string
          short-summary: the maintenance configuration json file.
    examples:
        - name: Update a maintenance configuration with --weekday and --start-hour.
          text: |
            az aks maintenanceconfiguration update -g xiazhan-mtc-stg --cluster-name test1 -n default --weekday Monday  --start-hour 1
              The maintenance is allowed on Monday 1:00am to 2:00am
        - name: Update a maintenance configuration with --weekday.The maintenance is allowd on any time of that day.
          text: |
            az aks maintenanceconfiguration update -g xiazhan-mtc-stg --cluster-name test1 -n default --weekday Monday
              The maintenance is allowed on Monday.
        - name: Update a maintenance configuration with maintenance configuration json file
          text: |
            az aks maintenanceconfiguration update -g xiazhan-mtc-stg --cluster-name test1 -n default --config-file ./test.json
                The content of json file looks below. It means the maintenance is allowed on UTC time Tuesday 1:00am - 3:00 am and Wednesday 1:00am - 2:00am, 6:00am-7:00am
                No maintenance is allowed from 2020-11-26T03:00:00Z to 2020-11-30T12:00:00Z and from 2020-12-26T03:00:00Z to 2020-12-26T12:00:00Z even if they are allowed in the above weekly setting
                {
                      "timeInWeek": [
                        {
                          "day": "Tuesday",
                          "hour_slots": [
                            1,
                            2
                          ]
                        },
                        {
                          "day": "Wednesday",
                          "hour_slots": [
                            1,
                            6
                          ]
                        }
                      ],
                      "notAllowedTime": [
                        {
                          "start": "2021-11-26T03:00:00Z",
                          "end": "2021-11-30T12:00:00Z"
                        },
                        {
                          "start": "2021-12-26T03:00:00Z",
                          "end": "2021-12-26T12:00:00Z"
                        }
                      ]
              }
"""

helps['aks nodepool'] = """
    type: group
    short-summary: Commands to manage node pools in managed Kubernetes cluster.
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
        - name: --node-osdisk-type
          type: string
          short-summary: OS disk type to be used for machines in a given agent pool. Defaults to 'Managed'. May not be changed for this pool after creation.
        - name: --max-pods -m
          type: int
          short-summary: The maximum number of pods deployable to a node.
          long-summary: If not specified, defaults to 110, or 30 for advanced networking configurations.
        - name: --node-zones --zones -z
          type: string array
          short-summary: (will be deprecated, use --zones) Availability zones where agent nodes will be placed.
        - name: --vnet-subnet-id
          type: string
          short-summary: The ID of a subnet in an existing VNet into which to deploy the cluster.
        - name: --pod-subnet-id
          type: string
          short-summary: The ID of a subnet in an existing VNet into which to assign pods in the cluster (requires azure network-plugin)
        - name: --ppg
          type: string
          short-summary: The ID of a PPG.
        - name: --os-type
          type: string
          short-summary: The OS Type. Linux or Windows.
        - name: --os-sku
          type: string
          short-summary: The os-sku of the agent node pool. Ubuntu or CBLMariner.
        - name: --enable-fips-image
          type: bool
          short-summary: Use FIPS-enabled OS on agent nodes.
        - name: --enable-cluster-autoscaler -e
          type: bool
          short-summary: Enable cluster autoscaler.
        - name: --min-count
          type: int
          short-summary: Minimun nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specify the value in the range of [1, 100]
        - name: --max-count
          type: int
          short-summary: Maximum nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specify the value in the range of [1, 100]
        - name: --node-taints
          type: string
          short-summary: The node taints for the node pool. You can't change the node taints through CLI after the node pool is created.
        - name: --priority
          type: string
          short-summary: The priority of the node pool.
        - name: --eviction-policy
          type: string
          short-summary: The eviction policy of the Spot node pool. It can only be set when --priority is Spot.
        - name: --spot-max-price
          type: float
          short-summary: It can only be set when --priority is Spot. Specify the maximum price you are willing to pay in US Dollars. Possible values are any decimal value greater than zero or -1 which indicates default price to be up-to on-demand. It can only include up to 5 decimal places.
        - name: --enable-node-public-ip
          type: bool
          short-summary: Enable VMSS node public IP.
        - name: --node-public-ip-prefix-id
          type: string
          short-summary: Public IP prefix ID used to assign public IPs to VMSS nodes.
        - name: --labels
          type: string
          short-summary: The node labels for the node pool. You can't change the node labels through CLI after the node pool is created. See https://aka.ms/node-labels for syntax of labels.
        - name: --mode
          type: string
          short-summary: The mode for a node pool which defines a node pool's primary function. If set as "System", AKS prefers system pods scheduling to node pools with mode `System`. Learn more at https://aka.ms/aks/nodepool/mode.
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
        - name: --max-surge
          type: string
          short-summary: Extra nodes used to speed upgrade. When specified, it represents the number or percent used, eg. 5 or 33%
        - name: --kubelet-config
          type: string
          short-summary: Kubelet configurations for agent nodes.
        - name: --linux-os-config
          type: string
          short-summary: OS configurations for Linux agent nodes.
        - name: --enable-encryption-at-host
          type: bool
          short-summary: Enable EncryptionAtHost on agent node pool.
        - name: --enable-ultra-ssd
          type: bool
          short-summary: Enable UltraSSD on agent node pool.
    examples:
        - name: Create a nodepool in an existing AKS cluster with ephemeral os enabled.
          text: az aks nodepool add -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster --node-osdisk-type Ephemeral --node-osdisk-size 48
        - name: Create a nodepool with EncryptionAtHost enabled.
          text: az aks nodepool add -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster --enable-encryption-at-host
        - name: Create a nodepool cluster with a specific os-sku
          text: az aks nodepool add -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster  --os-sku Ubuntu
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
        - name: --node-image-only
          type: bool
          short-summary: Only upgrade agent pool's node image.
        - name: --max-surge
          type: string
          short-summary: Extra nodes used to speed upgrade. When specified, it represents the number or percent used, eg. 5 or 33%
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
          short-summary: Minimun nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specify the value in the range of [1, 100]
        - name: --max-count
          type: int
          short-summary: Maximum nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specify the value in the range of [1, 100]
        - name: --max-surge
          type: string
          short-summary: Extra nodes used to speed upgrade. When specified, it represents the number or percent used, eg. 5 or 33%
        - name: --mode
          type: string
          short-summary: The mode for a node pool which defines a node pool's primary function. If set as "System", AKS prefers system pods scheduling to node pools with mode `System`. Learn more at https://aka.ms/aks/nodepool/mode.
    examples:
      - name: Enable cluster-autoscaler within node count range [1,5]
        text: az aks nodepool update --enable-cluster-autoscaler --min-count 1 --max-count 5 -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster
      - name: Disable cluster-autoscaler for an existing cluster
        text: az aks nodepool update --disable-cluster-autoscaler -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster
      - name: Update min-count or max-count for cluster autoscaler.
        text: az aks nodepool update --update-cluster-autoscaler --min-count 1 --max-count 10 -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster
      - name: Change a node pool to system mode
        text: az aks nodepool update --mode System -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster
"""

helps['aks nodepool get-upgrades'] = """
type: command
short-summary: Get the available upgrade versions for an agent pool of the managed Kubernetes cluster.
examples:
  - name: Get the available upgrade versions for an agent pool of the managed Kubernetes cluster.
    text: az aks nodepool get-upgrades --resource-group MyResourceGroup --cluster-name MyManagedCluster --nodepool-name MyNodePool
    crafted: true
parameters:
  - name: --nodepool-name
    type: string
    short-summary: name of the node pool.
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
        http_application_routing        - configure ingress with automatic public DNS name creation.
        monitoring                      - turn on Log Analytics monitoring. Uses the Log Analytics Default Workspace if it exists, else creates one. Specify "--workspace-resource-id" to use an existing workspace.
                                          If monitoring addon is enabled --no-wait argument will have no effect
        virtual-node                    - enable AKS Virtual Node. Requires --subnet-name to provide the name of an existing subnet for the Virtual Node to use.
        azure-policy                    - enable Azure policy. The Azure Policy add-on for AKS enables at-scale enforcements and safeguards on your clusters in a centralized, consistent manner.
                                          Learn more at aka.ms/aks/policy.
        ingress-appgw                   - enable Application Gateway Ingress Controller addon (PREVIEW).
        open-service-mesh               - enable Open Service Mesh addon (PREVIEW).
        gitops                          - enable GitOps (PREVIEW).
        azure-keyvault-secrets-provider - enable Azure Keyvault Secrets Provider addon (PREVIEW).
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
  - name: --appgw-name
    type: string
    short-summary: Name of the application gateway to create/use in the node resource group. Use with ingress-azure addon.
  - name: --appgw-subnet-prefix
    type: string
    short-summary: Subnet Prefix to use for a new subnet created to deploy the Application Gateway. Use with ingress-azure addon.
  - name: --appgw-subnet-cidr
    type: string
    short-summary: Subnet CIDR to use for a new subnet created to deploy the Application Gateway. Use with ingress-azure addon.
  - name: --appgw-id
    type: string
    short-summary: Resource Id of an existing Application Gateway to use with AGIC. Use with ingress-azure addon.
  - name: --appgw-subnet-id
    type: string
    short-summary: Resource Id of an existing Subnet used to deploy the Application Gateway. Use with ingress-azure addon.
  - name: --appgw-watch-namespace
    type: string
    short-summary: Specify the namespace, which AGIC should watch. This could be a single string value, or a comma-separated list of namespaces. Use with ingress-azure addon.
  - name: --enable-sgxquotehelper
    type: bool
    short-summary: Enable SGX quote helper for confcom addon.
  - name: --enable-secret-rotation
    type: bool
    short-summary: Enable secret rotation. Use with azure-keyvault-secrets-provider addon.
examples:
  - name: Enable Kubernetes addons. (autogenerated)
    text: az aks enable-addons --addons virtual-node --name MyManagedCluster --resource-group MyResourceGroup --subnet-name VirtualNodeSubnet
    crafted: true
  - name: Enable ingress-appgw addon with subnet prefix.
    text: az aks enable-addons --name MyManagedCluster --resource-group MyResourceGroup --addons ingress-appgw --appgw-subnet-cidr 10.2.0.0/16 --appgw-name gateway
    crafted: true
  - name: Enable open-service-mesh addon.
    text: az aks enable-addons --name MyManagedCluster --resource-group MyResourceGroup --addons open-service-mesh
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

helps['aks get-os-options'] = """
type: command
short-summary: Get the OS options available for creating a managed Kubernetes cluster.
examples:
  - name: Get the OS options available for creating a managed Kubernetes cluster
    text: az aks get-os-options --location westus2
    crafted: true
"""

helps['aks get-credentials'] = """
type: command
short-summary: Get access credentials for a managed Kubernetes cluster.
parameters:
  - name: --admin -a
    type: bool
    short-summary: "Get cluster administrator credentials.  Default: cluster user credentials."
  - name: --user -u
    type: string
    short-summary: "Get credentials for the user. Only valid when --admin is False.  Default: cluster user credentials."
  - name: --file -f
    type: string
    short-summary: Kubernetes configuration file to update. Use "-" to print YAML to stdout instead.
  - name: --overwrite-existing
    type: bool
    short-summary: Overwrite any existing cluster entry with the same name.
  - name: --output -o
    type: string
    long-summary: Credentials are always in YAML format, so this argument is effectively ignored.
  - name: --public-fqdn
    type: bool
    short-summary: (Preview) Get private cluster credential with server address to be public fqdn.
examples:
  - name: Get access credentials for a managed Kubernetes cluster. (autogenerated)
    text: az aks get-credentials --name MyManagedCluster --resource-group MyResourceGroup
    crafted: true
"""

helps['aks rotate-certs'] = """
    type: command
    short-summary: Rotate certificates and keys on a managed Kubernetes cluster
    long-summary: Kubernetes will be unavailable during cluster certificate rotation.
"""

helps['aks pod-identity'] = """
    type: group
    short-summary: Commands to manage pod identities in managed Kubernetes cluster.
"""

helps['aks pod-identity add'] = """
    type: command
    short-summary: Add a pod identity to a managed Kubernetes cluster
    examples:
    - name: Add pod identity
      text: az aks pod-identity add --cluster-name MyManagedCluster --resource-group MyResourceGroup --namespace my-namespace --name my-identity --identity-resource-id <my-identity-resource-id>
"""

helps['aks pod-identity delete'] = """
    type: command
    short-summary: Remove a pod identity from a managed Kubernetes cluster
"""

helps['aks pod-identity list'] = """
    type: command
    short-summary: List pod identities in a managed Kubernetes cluster
"""

helps['aks pod-identity exception'] = """
    type: group
    short-summary: Commands to manage pod identity exceptions in managed Kubernetes cluster.
"""

helps['aks pod-identity exception add'] = """
    type: command
    short-summary: Add a pod identity exception to a managed Kubernetes cluster
"""

helps['aks pod-identity exception delete'] = """
    type: command
    short-summary: Remove a pod identity exception from a managed Kubernetes cluster
"""

helps['aks pod-identity exception update'] = """
    type: command
    short-summary: Update a pod identity exception in a managed Kubernetes cluster
"""

helps['aks pod-identity exception list'] = """
    type: command
    short-summary: List pod identity exceptions in a managed Kubernetes cluster
"""

helps['aks egress-endpoints'] = """
    type: group
    short-summary: Commands to manage egress endpoints in managed Kubernetes cluster.
"""

helps['aks egress-endpoints list'] = """
    type: command
    short-summary: List egress endpoints that are required or recommended to be whitelisted for a cluster.
"""
