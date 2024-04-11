# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
import os.path

from knack.help_files import helps

ACS_SERVICE_PRINCIPAL_CACHE = os.path.join(
    '$HOME', '.azure', 'acsServicePrincipal.json')
AKS_SERVICE_PRINCIPAL_CACHE = os.path.join(
    '$HOME', '.azure', 'aksServicePrincipal.json')

# AKS command help
helps['aks create'] = f"""
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
                         {AKS_SERVICE_PRINCIPAL_CACHE} to be used by subsequent `az aks` commands.
        - name: --skip-subnet-role-assignment
          type: bool
          short-summary: Skip role assignment for subnet (advanced networking).
          long-summary:  If specified, please make sure your service principal has the access to your subnet.
        - name: --zones -z
          type: string array
          short-summary: Space-separated list of availability zones where agent nodes will be placed.
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
          short-summary: Size in GiB of the OS disk for each node in the node pool. Minimum 30 GiB.
        - name: --node-osdisk-type
          type: string
          short-summary: OS disk type to be used for machines in a given agent pool. Defaults to 'Ephemeral' when possible in conjunction with VM size and OS disk size. May not be changed for this pool after creation. ('Ephemeral' or 'Managed')
        - name: --node-osdisk-diskencryptionset-id -d
          type: string
          short-summary: ResourceId of the disk encryption set to use for enabling encryption at rest on agent node os disk.
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
          short-summary: Comma-separated list of aad group object IDs that will be set as cluster admin.
        - name: --aad-client-app-id
          type: string
          short-summary: The ID of an Azure Active Directory client application of type "Native". This
                         application is for user login via kubectl.
          long-summary: --aad-client-app-id is deprecated. See https://aka.ms/aks/aad-legacy for details.
        - name: --aad-server-app-id
          type: string
          short-summary: The ID of an Azure Active Directory server application of type "Web app/API". This
                         application represents the managed cluster's apiserver (Server application).
          long-summary: --aad-server-app-id is deprecated. See https://aka.ms/aks/aad-legacy for details.
        - name: --aad-server-app-secret
          type: string
          short-summary: The secret of an Azure Active Directory server application.
          long-summary: --aad-server-app-secret is deprecated. See https://aka.ms/aks/aad-legacy for details.
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
        - name: --load-balancer-managed-outbound-ipv6-count
          type: int
          short-summary: Load balancer managed outbound IPv6 IP count.
          long-summary: Desired number of managed outbound IPv6 IPs for load balancer outbound connection. Valid for dual-stack (--ip-families IPv4,IPv6) only.
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
        - name: --load-balancer-backend-pool-type
          type: string
          short-summary: Load balancer backend pool type.
          long-summary: Load balancer backend pool type, supported values are nodeIP and nodeIPConfiguration.
        - name: --cluster-service-load-balancer-health-probe-mode
          type: string
          short-summary: Set the cluster service health probe mode.
          long-summary: Set the cluster service health probe mode. Default is "Servicenodeport".
        - name: --nat-gateway-managed-outbound-ip-count
          type: int
          short-summary: NAT gateway managed outbound IP count.
          long-summary: Desired number of managed outbound IPs for NAT gateway outbound connection. Please specify a value in the range of [1, 16]. Valid for Standard SKU load balancer cluster with managedNATGateway outbound type only.
        - name: --nat-gateway-idle-timeout
          type: int
          short-summary: NAT gateway idle timeout in minutes.
          long-summary: Desired idle timeout for NAT gateway outbound flows, default is 4 minutes. Please specify a value in the range of [4, 120]. Valid for Standard SKU load balancer cluster with managedNATGateway outbound type only.
        - name: --outbound-type
          type: string
          short-summary: How outbound traffic will be configured for a cluster.
          long-summary: Select between loadBalancer, userDefinedRouting, managedNATGateway and userAssignedNATGateway. If not set, defaults to type loadBalancer. Requires --vnet-subnet-id to be provided with a preconfigured route table and --load-balancer-sku to be Standard.
        - name: --enable-addons -a
          type: string
          short-summary: Enable the Kubernetes addons in a comma-separated list.
          long-summary: |-
            These addons are available:
            - http_application_routing        : configure ingress with automatic public DNS name creation.
            - monitoring                      :  turn on Log Analytics monitoring. Uses the Log Analytics Default Workspace if it exists, else creates one. Specify "--workspace-resource-id" to use an existing workspace. If monitoring addon is enabled --no-wait argument will have no effect
            - virtual-node                    : enable AKS Virtual Node. Requires --aci-subnet-name to provide the name of an existing subnet for the Virtual Node to use. aci-subnet-name must be in the same vnet which is specified by --vnet-subnet-id (required as well).
            - azure-policy                    : enable Azure policy. The Azure Policy add-on for AKS enables at-scale enforcements and safeguards on your clusters in a centralized, consistent manner. Required if enabling deployment safeguards. Learn more at aka.ms/aks/policy.
            - ingress-appgw                   : enable Application Gateway Ingress Controller addon (PREVIEW).
            - confcom                         : enable confcom addon, this will enable SGX device plugin by default(PREVIEW).
            - open-service-mesh               : enable Open Service Mesh addon (PREVIEW).
            - gitops                          : enable GitOps (PREVIEW).
            - azure-keyvault-secrets-provider : enable Azure Keyvault Secrets Provider addon.
            - web_application_routing         : enable Web Application Routing addon (PREVIEW). Specify "--dns-zone-resource-id" to configure DNS.
        - name: --disable-rbac
          type: bool
          short-summary: Disable Kubernetes Role-Based Access Control.
        - name: --max-pods -m
          type: int
          short-summary: The maximum number of pods deployable to a node.
          long-summary: If not specified, defaults based on network-plugin. 30 for "azure", 110 for "kubenet", or 250 for "none".
        - name: --network-plugin
          type: string
          short-summary: The Kubernetes network plugin to use.
          long-summary: Specify "azure" for routable pod IPs from VNET, "kubenet" for non-routable pod IPs with an overlay network, or "none" for no networking configured.
        - name: --network-plugin-mode
          type: string
          short-summary: The network plugin mode to use.
          long-summary: |
              Used to control the mode the network plugin should operate in. For example, "overlay" used with
              --network-plugin=azure will use an overlay network (non-VNET IPs) for pods in the cluster.
        - name: --network-policy
          type: string
          short-summary: (PREVIEW) The Kubernetes network policy to use.
          long-summary: |
              Using together with "azure" network plugin.
              Specify "azure" for Azure network policy manager, "calico" for calico network policy controller, "cilium" for Azure CNI Overlay powered by Cilium.
              Defaults to "" (network policy disabled).
        - name: --network-dataplane
          type: string
          short-summary: The network dataplane to use.
          long-summary: |
              Network dataplane used in the Kubernetes cluster.
              Specify "azure" to use the Azure dataplane (default) or "cilium" to enable Cilium dataplane.
        - name: --enable-cilium-dataplane
          type: bool
          short-summary: Use Cilium as the networking dataplane for the Kubernetes cluster.
          long-summary: |
              Used together with the "azure" network plugin.
              Requires either --pod-subnet-id or --network-plugin-mode=overlay.
              This flag is deprecated in favor of --network-dataplane=cilium.
        - name: --enable-network-observability
          type: bool
          short-summary: Enable network observability on a cluster.
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
        - name: --service-cidrs
          type: string
          short-summary: A comma separated list of CIDR notation IP ranges from which to assign service cluster IPs.
          long-summary: Each range must not overlap with any Subnet IP ranges. For example, 10.0.0.0/16.
        - name: --pod-cidrs
          type: string
          short-summary: A comma separated list of CIDR notation IP ranges from which to assign pod IPs when kubenet is used.
          long-summary: Each range must not overlap with any Subnet IP ranges. For example, 172.244.0.0/16.
        - name: --ip-families
          type: string
          short-summary: A comma separated list of IP versions to use for cluster networking.
          long-summary: Each IP version should be in the format IPvN. For example, IPv4.
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
        - name: --enable-msi-auth-for-monitoring
          type: bool
          short-summary: Send monitoring data to Log Analytics using the cluster's assigned identity (instead of the Log Analytics Workspace's shared key).
        - name: --enable-syslog
          type: bool
          short-summary: Enable syslog data collection for Monitoring addon
        - name: --data-collection-settings
          type: string
          short-summary: Path to JSON file containing data collection settings for Monitoring addon.
        - name: --enable-cluster-autoscaler
          type: bool
          short-summary: Enable cluster autoscaler, default value is false.
          long-summary: If specified, please make sure the kubernetes version is larger than 1.10.6.
        - name: --min-count
          type: int
          short-summary: Minimun nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specify the value in the range of [1, 1000].
        - name: --max-count
          type: int
          short-summary: Maximum nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specify the value in the range of [1, 1000].
        - name: --vm-set-type
          type: string
          short-summary: Agent pool vm set type. VirtualMachineScaleSets, AvailabilitySet or VirtualMachines(Preview).
        - name: --enable-pod-security-policy
          type: bool
          short-summary: Enable pod security policy.
          long-summary: --enable-pod-security-policy is deprecated. See https://aka.ms/aks/psp for details.
        - name: --node-resource-group
          type: string
          short-summary: The node resource group is the resource group where all customer's resources will be created in, such as virtual machines.
        - name: --k8s-support-plan
          type: string
          short-summary: Choose from "KubernetesOfficial" or "AKSLongTermSupport", with "AKSLongTermSupport" you get 1 extra year of CVE patchs.
        - name: --nrg-lockdown-restriction-level
          type: string
          short-summary: Restriction level on the managed node resource group.
          long-summary: The restriction level of permissions allowed on the cluster's managed node resource group, supported values are Unrestricted, and ReadOnly (recommended ReadOnly).
        - name: --uptime-sla
          type: bool
          short-summary: --uptime-sla is deprecated. Please use '--tier standard' instead.
        - name: --sku
          type: string
          short-summary: Specify SKU name for managed clusters. '--sku base' enables a base managed cluster. '--sku automatic' enables an automatic managed cluster.
        - name: --tier
          type: string
          short-summary: Specify SKU tier for managed clusters. '--tier standard' enables a standard managed cluster service with a financially backed SLA. '--tier free' does not have a financially backed SLA.
        - name: --attach-acr
          type: string
          short-summary: Grant the 'acrpull' role assignment to the ACR specified by name or resource ID.
        - name: --enable-apiserver-vnet-integration
          type: bool
          short-summary: Enable integration of user vnet with control plane apiserver pods.
        - name: --apiserver-subnet-id
          type: string
          short-summary: The ID of a subnet in an existing VNet into which to assign control plane apiserver pods(requires --enable-apiserver-vnet-integration)
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
        - name: --disable-public-fqdn
          type: bool
          short-summary: Disable public fqdn feature for private cluster.
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
          short-summary: Comma-separated list of authorized apiserver IP ranges. Set to 0.0.0.0/32 to restrict apiserver traffic to node pools.
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
        - name: --appgw-name
          type: string
          short-summary: Name of the application gateway to create/use in the node resource group. Use with ingress-azure addon.
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
        - name: --node-os-upgrade-channel
          type: string
          short-summary: Manner in which the OS on your nodes is updated. It could be NodeImage, None, SecurityPatch or Unmanaged.
        - name: --kubelet-config
          type: string
          short-summary: Kubelet configurations for agent nodes.
        - name: --linux-os-config
          type: string
          short-summary: OS configurations for Linux agent nodes.
        - name: --http-proxy-config
          type: string
          short-summary: Http Proxy configuration for this cluster.
        - name: --kube-proxy-config
          type: string
          short-summary: kube-proxy configuration for this cluster.
        - name: --enable-pod-identity
          type: bool
          short-summary: (PREVIEW) Enable pod identity addon.
        - name: --enable-pod-identity-with-kubenet
          type: bool
          short-summary: (PREVIEW) Enable pod identity addon for cluster using Kubnet network plugin.
        - name: --enable-workload-identity
          type: bool
          short-summary: (PREVIEW) Enable workload identity addon.
        - name: --disable-disk-driver
          type: bool
          short-summary: Disable AzureDisk CSI Driver.
        - name: --disk-driver-version
          type: string
          short-summary: Specify AzureDisk CSI Driver version.
        - name: --disable-file-driver
          type: bool
          short-summary: Disable AzureFile CSI Driver.
        - name: --disable-snapshot-controller
          type: bool
          short-summary: Disable CSI Snapshot Controller.
        - name: --enable-blob-driver
          type: bool
          short-summary: Enable AzureBlob CSI Driver.
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
        - name: --rotation-poll-interval
          type: string
          short-summary: Set interval of rotation poll. Use with azure-keyvault-secrets-provider addon.
        - name: --disable-local-accounts
          type: bool
          short-summary: (Preview) If set to true, getting static credential will be disabled for this cluster.
        - name: --workload-runtime
          type: string
          short-summary: Determines the type of workload a node can run. Defaults to OCIContainer.
        - name: --gpu-instance-profile
          type: string
          short-summary: GPU instance profile to partition multi-gpu Nvidia GPUs.
        - name: --enable-windows-gmsa
          type: bool
          short-summary: Enable Windows gmsa.
        - name: --gmsa-dns-server
          type: string
          short-summary: Specify DNS server for Windows gmsa for this cluster.
          long-summary: |-
             You do not need to set this if you have set DNS server in the VNET used by the cluster.
             You must set or not set --gmsa-dns-server and --gmsa-root-domain-name at the same time when setting --enable-windows-gmsa.
        - name: --gmsa-root-domain-name
          type: string
          short-summary: Specify root domain name for Windows gmsa for this cluster.
          long-summary: |-
             You do not need to set this if you have set DNS server in the VNET used by the cluster.
             You must set or not set --gmsa-dns-server and --gmsa-root-domain-name at the same time when setting --enable-windows-gmsa.
        - name: --snapshot-id
          type: string
          short-summary: The source nodepool snapshot id used to create this cluster.
        - name: --cluster-snapshot-id
          type: string
          short-summary: The source cluster snapshot id is used to create new cluster.
        - name: --enable-oidc-issuer
          type: bool
          short-summary: Enable OIDC issuer.
        - name: --crg-id
          type: string
          short-summary: The crg-id used to associate the new cluster with the existed Capacity Reservation Group resource.
        - name: --host-group-id
          type: string
          short-summary: (PREVIEW) The fully qualified dedicated host group id used to provision agent node pool.
        - name: --message-of-the-day
          type: string
          short-summary: Path to a file containing the desired message of the day. Only valid for linux nodes. Will be written to /etc/motd.
        - name: --enable-azure-keyvault-kms
          type: bool
          short-summary: Enable Azure KeyVault Key Management Service.
        - name: --azure-keyvault-kms-key-id
          type: string
          short-summary: Identifier of Azure Key Vault key.
        - name: --azure-keyvault-kms-key-vault-network-access
          type: string
          short-summary: Network Access of Azure Key Vault.
          long-summary: Allowed values are "Public", "Private". If not set, defaults to type "Public". Requires --azure-keyvault-kms-key-id to be used.
        - name: --azure-keyvault-kms-key-vault-resource-id
          type: string
          short-summary: Resource ID of Azure Key Vault.
        - name: --enable-image-cleaner
          type: bool
          short-summary: Enable ImageCleaner Service.
        - name: --image-cleaner-interval-hours
          type: int
          short-summary: ImageCleaner scanning interval.
        - name: --enable-image-integrity
          type: bool
          short-summary: Enable ImageIntegrity Service.
        - name: --dns-zone-resource-id
          type: string
          short-summary: The resource ID of the DNS zone resource to use with the web_application_routing addon.
        - name: --dns-zone-resource-ids
          type: string
          short-summary: A comma separated list of resource IDs of the DNS zone resource to use with the web_application_routing addon.
        - name: --enable-custom-ca-trust
          type: bool
          short-summary: Enable Custom CA Trust on agent node pool.
        - name: --ca-certs --custom-ca-trust-certificates
          type: string
          short-summary: Path to a file containing up to 10 blank line separated certificates. Only valid for linux nodes.
          long-summary: These certificates are used by Custom CA Trust features and will be added to trust stores of nodes. Requires Custom CA Trust to be enabled on the node.
        - name: --enable-keda
          type: bool
          short-summary: Enable KEDA workload auto-scaler.
        - name: --enable-defender
          type: bool
          short-summary: Enable Microsoft Defender security profile.
        - name: --defender-config
          type: string
          short-summary: Path to JSON file containing Microsoft Defender profile configurations.
        - name: --enable-vpa
          type: bool
          short-summary: Enable vertical pod autoscaler for cluster.
        - name: --enable-addon-autoscaling
          type: bool
          short-summary: Enable addon autoscaling for cluster.
        - name: --nodepool-allowed-host-ports
          type: string
          short-summary: Expose host ports on the node pool. When specified, format should be a comma-separated list of ranges with protocol, eg. 80/TCP,443/TCP,4000-5000/TCP.
        - name: --nodepool-asg-ids
          type: string
          short-summary: The IDs of the application security groups to which the node pool's network interface should belong. When specified, format should be a comma-separated list of IDs.
        - name: --node-public-ip-tags
          type: string
          short-summary: The ipTags of the node public IPs.
        - name: --safeguards-level
          type: string
          short-summary: The deployment safeguards Level. Accepted Values are [Off, Warning, Enforcement]. Requires azure policy addon to be enabled
        - name: --safeguards-version
          type: string
          short-summary: The version of deployment safeguards to use. Default "v1.0.0" Use the ListSafeguardsVersions API to discover available versions
        - name: --safeguards-excluded-ns
          type: string
          short-summary: Comma-separated list of Kubernetes namespaces to exclude from deployment safeguards
        - name: --enable-asm --enable-azure-service-mesh
          type: bool
          short-summary: Enable Azure Service Mesh.
        - name: --revision
          type: string
          short-summary: Azure Service Mesh revision to install.
        - name: --enable-azuremonitormetrics
          type: bool
          short-summary: Enable Azure Monitor Metrics Profile
        - name: --enable-azure-monitor-metrics
          type: bool
          short-summary: Enable Azure Monitor Metrics Profile
        - name: --azure-monitor-workspace-resource-id
          type: string
          short-summary: Resource ID of the Azure Monitor Workspace
        - name: --ksm-metric-labels-allow-list
          type: string
          short-summary: Comma-separated list of additional Kubernetes label keys that will be used in the resource' labels metric. By default the metric contains only name and namespace labels. To include additional labels provide a list of resource names in their plural form and Kubernetes label keys you would like to allow for them (e.g. '=namespaces=[k8s-label-1,k8s-label-n,...],pods=[app],...)'. A single '*' can be provided per resource instead to allow any labels, but that has severe performance implications (e.g. '=pods=[*]').
        - name: --ksm-metric-annotations-allow-list
          type: string
          short-summary: Comma-separated list of additional Kubernetes label keys that will be used in the resource' labels metric. By default the metric contains only name and namespace labels. To include additional labels provide a list of resource names in their plural form and Kubernetes label keys you would like to allow for them (e.g.'=namespaces=[k8s-label-1,k8s-label-n,...],pods=[app],...)'. A single '*' can be provided per resource instead to allow any labels, but that has severe performance implications (e.g. '=pods=[*]').
        - name: --grafana-resource-id
          type: string
          short-summary: Resource ID of the Azure Managed Grafana Workspace
        - name: --enable-windows-recording-rules
          type: bool
          short-summary: Enable Windows Recording Rules when enabling the Azure Monitor Metrics addon
        - name: --nodepool-labels
          type: string
          short-summary: The node labels for all node pools in this cluster. See https://aka.ms/node-labels for syntax of labels.
        - name: --nodepool-taints
          type: string
          short-summary: The node taints for all node pools in this cluster.
        - name: --node-init-taints --nodepool-initialization-taints
          type: string
          short-summary: The node initialization taints for node pools created with aks create operation.
        - name: --enable-cost-analysis
          type: bool
          short-summary: Enable exporting Kubernetes Namespace and Deployment details to the Cost Analysis views in the Azure portal. For more information see aka.ms/aks/docs/cost-analysis.
        - name: --node-provisioning-mode
          type: string
          short-summary: Set the node provisioning mode of the cluster. Valid values are "Auto" and "Manual". For more information on "Auto" mode see aka.ms/aks/nap.
        - name: --enable-app-routing
          type: bool
          short-summary: Enable Application Routing addon.
        - name: --enable-ai-toolchain-operator
          type: bool
          short-summary: Enable AI toolchain operator to the cluster.
        - name: --ssh-access
          type: string
          short-summary: Configure SSH setting for all node pools in this cluster. Use "disabled" to disable SSH access, "localuser" to enable SSH access using private key.
        - name: --pod-ip-allocation-mode
          type: string
          short-summary: Set the ip allocation mode for how Pod IPs from the Azure Pod Subnet are allocated to the nodes in the AKS cluster. The choice is between dynamic batches of individual IPs or static allocation of a set of CIDR blocks. Accepted Values are "DynamicIndividual" or "StaticBlock".
          long-summary: |
              Used together with the "azure" network plugin.
              Requires --pod-subnet-id.
        - name: --enable-secure-boot
          type: bool
          short-summary: Enable Secure Boot on all node pools in the cluster. Must use VMSS agent pool type.
        - name: --enable-vtpm
          type: bool
          short-summary: Enable vTPM on all node pools in the cluster. Must use VMSS agent pool type.
        - name: --bootstrap-artifact-source
          type: string
          short-summary: Configure artifact source when bootstraping the cluster.
          long-summary: |
              The artifacts include the addon image. Use "Direct" to download artifacts from MCR, "Cache" to downalod artifacts from Azure Container Registry.
        - name: --bootstrap-container-registry-resource-id
          type: string
          short-summary: Configure container registry resource ID. Must use "Cache" as bootstrap artifact source.
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
        - name: Create a kubernetes cluster with a AKS managed NAT gateway, with two outbound AKS managed IPs an idle flow timeout of 4 minutes
          text: az aks create -g MyResourceGroup -n MyManagedCluster --nat-gateway-managed-outbound-ip-count 2 --nat-gateway-idle-timeout 4
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
        - name: Create a kubernetes cluster with enabling Windows gmsa and with setting DNS server in the vnet used by the cluster.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --load-balancer-sku Standard --network-plugin azure --windows-admin-username azure --windows-admin-password 'replacePassword1234$' --enable-windows-gmsa
        - name: Create a kubernetes cluster with enabling Windows gmsa but without setting DNS server in the vnet used by the cluster.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --load-balancer-sku Standard --network-plugin azure --windows-admin-username azure --windows-admin-password 'replacePassword1234$' --enable-windows-gmsa --gmsa-dns-server "10.240.0.4" --gmsa-root-domain-name "contoso.com"
        - name: create a kubernetes cluster with a nodepool snapshot id.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --kubernetes-version 1.20.9 --snapshot-id "/subscriptions/00000/resourceGroups/AnotherResourceGroup/providers/Microsoft.ContainerService/snapshots/mysnapshot1"
        - name: create a kubernetes cluster with a cluster snapshot id.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --cluster-snapshot-id "/subscriptions/00000/resourceGroups/AnotherResourceGroup/providers/Microsoft.ContainerService/managedclustersnapshots/mysnapshot1"
        - name: create a kubernetes cluster with a Capacity Reservation Group(CRG) ID.
          text: az aks create -g MyResourceGroup -n MyMC --kubernetes-version 1.20.9 --node-vm-size VMSize --assign-identity CRG-RG-ID --enable-managed-identity --crg-id "subscriptions/SubID/resourceGroups/RGName/providers/Microsoft.ContainerService/CapacityReservationGroups/MyCRGID"
        - name: create a kubernetes cluster with support of hostgroup id.
          text: az aks create -g MyResourceGroup -n MyMC --kubernetes-version 1.20.13 --location westus2 --host-group-id /subscriptions/00000/resourceGroups/AnotherResourceGroup/providers/Microsoft.ContainerService/hostGroups/myHostGroup --node-vm-size VMSize --enable-managed-identity --assign-identity <user_assigned_identity_resource_id>
        - name: Create a kubernetes cluster with no CNI installed.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --network-plugin none
        - name: Create a kubernetes cluster with Custom CA Trust enabled.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --enable-custom-ca-trust
        - name: Create a kubernetes cluster with safeguards set to "Warning"
          text: az aks create -g MyResourceGroup -n MyManagedCluster --safeguards-level Warning --enable-addons azure-policy
        - name: Create a kubernetes cluster with safeguards set to "Warning" and some namespaces excluded
          text: az aks create -g MyResourceGroup -n MyManagedCluster --safeguards-level Warning --safeguards-excluded-ns ns1,ns2 --enable-addons azure-policy
        - name: Create a kubernetes cluster with Azure Service Mesh enabled.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --enable-azure-service-mesh
        - name: Create a kubernetes cluster with Azure Monitor Metrics enabled.
          text: az aks create -g MyResourceGroup -n MyManagedCluster --enable-azuremonitormetrics
        - name: Create a kubernetes cluster with a nodepool having ip allocation mode set to "StaticBlock"
          text: az aks create -g MyResourceGroup -n MyManagedCluster --os-sku Ubuntu --max-pods MaxPodsPerNode --network-plugin azure --vnet-subnet-id /subscriptions/00000/resourceGroups/AnotherResourceGroup/providers/Microsoft.Network/virtualNetworks/MyVnet/subnets/NodeSubnet --pod-subnet-id /subscriptions/00000/resourceGroups/AnotherResourceGroup/providers/Microsoft.Network/virtualNetworks/MyVnet/subnets/PodSubnet --pod-ip-allocation-mode StaticBlock

"""

helps['aks scale'] = """
    type: command
    short-summary: Scale the node pool in a managed Kubernetes cluster.
    parameters:
        - name: --node-count -c
          type: int
          short-summary: Number of nodes in the Kubernetes node pool.
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
"""

helps['aks stop'] = """
    type: command
    short-summary: Stop a managed cluster.
    long-summary: This can only be performed on Azure Virtual Machine Scale set backed clusters. Stopping a
        cluster stops the control plane and agent nodes entirely, while maintaining all object and
        cluster state. A cluster does not accrue charges while it is stopped. See `stopping a
        cluster <https://docs.microsoft.com/azure/aks/start-stop-cluster>`_ for more details about
        stopping a cluster.
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
        - name: --cluster-snapshot-id
          type: string
          short-summary: The source cluster snapshot id is used to upgrade existing cluster.
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
    examples:
      - name: Upgrade a existing managed cluster to a managed cluster snapshot.
        text: az aks upgrade -g MyResourceGroup -n MyManagedCluster --cluster-snapshot-id "/subscriptions/00000/resourceGroups/AnotherResourceGroup/providers/Microsoft.ContainerService/managedclustersnapshots/mysnapshot1"
"""

helps['aks update'] = """
    type: command
    short-summary: Update the properties of a managed Kubernetes cluster.
    long-summary: Update the properties of a managed Kubernetes cluster. Can be used for example to enable/disable cluster-autoscaler.  When called with no optional arguments this attempts to move the cluster to its goal state without changing the current cluster configuration. This can be used to move out of a non succeeded state.
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
          short-summary: Minimun nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specify the value in the range of [1, 1000]
        - name: --max-count
          type: int
          short-summary: Maximum nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specify the value in the range of [1, 1000]
        - name: --uptime-sla
          type: bool
          short-summary: Enable a standard managed cluster service with a financially backed SLA. --uptime-sla is deprecated. Please use '--tier standard' instead.
        - name: --no-uptime-sla
          type: bool
          short-summary: Change a standard managed cluster to a free one. --no-uptime-sla is deprecated. Please use '--tier free' instead.
        - name: --sku
          type: string
          short-summary: Specify SKU name for managed clusters. '--sku base' enables a base managed cluster. '--sku automatic' enables an automatic managed cluster.
        - name: --tier
          type: string
          short-summary: Specify SKU tier for managed clusters. '--tier standard' enables a standard managed cluster service with a financially backed SLA. '--tier free' changes a standard managed cluster to a free one.
        - name: --load-balancer-managed-outbound-ip-count
          type: int
          short-summary: Load balancer managed outbound IP count.
          long-summary: Desired number of managed outbound IPs for load balancer outbound connection. Valid for Standard SKU load balancer cluster only.
        - name: --load-balancer-managed-outbound-ipv6-count
          type: int
          short-summary: Load balancer managed outbound IPv6 IP count.
          long-summary: Desired number of managed outbound IPv6 IPs for load balancer outbound connection. Valid for dual-stack (--ip-families IPv4,IPv6) only.
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
        - name: --load-balancer-backend-pool-type
          type: string
          short-summary: Load balancer backend pool type.
          long-summary: Load balancer backend pool type, supported values are nodeIP and nodeIPConfiguration.
        - name: --cluster-service-load-balancer-health-probe-mode
          type: string
          short-summary: Set the cluster service health probe mode.
          long-summary: Set the cluster service health probe mode. Default is "Servicenodeport".
        - name: --nat-gateway-managed-outbound-ip-count
          type: int
          short-summary: NAT gateway managed outbound IP count.
          long-summary: Desired number of managed outbound IPs for NAT gateway outbound connection. Please specify a value in the range of [1, 16]. Valid for Standard SKU load balancer cluster with managedNATGateway outbound type only.
        - name: --nat-gateway-idle-timeout
          type: int
          short-summary: NAT gateway idle timeout in minutes.
          long-summary: Desired idle timeout for NAT gateway outbound flows, default is 4 minutes. Please specify a value in the range of [4, 120]. Valid for Standard SKU load balancer cluster with managedNATGateway outbound type only.
        - name: --outbound-type
          type: string
          short-summary: How outbound traffic will be configured for a cluster.
          long-summary: This option will change the way how the outbound connections are managed in the AKS cluster. Available options are loadbalancer, managedNATGateway, userAssignedNATGateway, userDefinedRouting. For custom vnet, loadbalancer, userAssignedNATGateway and userDefinedRouting are supported. For aks managed vnet, loadbalancer, managedNATGateway and userDefinedRouting are supported.
        - name: --enable-pod-security-policy
          type: bool
          short-summary: Enable pod security policy.
          long-summary: --enable-pod-security-policy is deprecated. See https://aka.ms/aks/psp for details.
        - name: --disable-pod-security-policy
          type: bool
          short-summary: Disable pod security policy
          long-summary: PodSecurityPolicy is deprecated. See https://aka.ms/aks/psp for details.
        - name: --nrg-lockdown-restriction-level
          type: string
          short-summary: Restriction level on the managed node resource.
          long-summary: The restriction level of permissions allowed on the cluster's managed node resource group, supported values are Unrestricted, and ReadOnly (recommended ReadOnly).
        - name: --attach-acr
          type: string
          short-summary: Grant the 'acrpull' role assignment to the ACR specified by name or resource ID.
        - name: --detach-acr
          type: string
          short-summary: Disable the 'acrpull' role assignment to the ACR specified by name or resource ID.
        - name: --api-server-authorized-ip-ranges
          type: string
          short-summary: Comma-separated list of authorized apiserver IP ranges. Set to "" to allow all traffic on a previously restricted cluster. Set to 0.0.0.0/32 to restrict apiserver traffic to node pools.
        - name: --enable-aad
          type: bool
          short-summary: Enable managed AAD feature for cluster.
        - name: --aad-admin-group-object-ids
          type: string
          short-summary: Comma-separated list of aad group object IDs that will be set as cluster admin.
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
        - name: --node-os-upgrade-channel
          type: string
          short-summary: Manner in which the OS on your nodes is updated. It could be NodeImage, None, SecurityPatch or Unmanaged.
        - name: --enable-force-upgrade
          type: bool
          short-summary: Enable forceUpgrade cluster upgrade settings override.
        - name: --disable-force-upgrade
          type: bool
          short-summary: Disable forceUpgrade cluster upgrade settings override.
        - name: --upgrade-override-until
          type: string
          short-summary: Until when the cluster upgradeSettings overrides are effective. It needs to be in a valid date-time format that's within the next 30 days. For example, 2023-04-01T13:00:00Z. Note that if --force-upgrade is set to true and --upgrade-override-until is not set, by default it will be set to 3 days from now.
        - name: --enable-managed-identity
          type: bool
          short-summary: Update current cluster to managed identity to manage cluster resource group.
        - name: --assign-identity
          type: string
          short-summary: Specify an existing user assigned identity to manage cluster resource group.
        - name: --assign-kubelet-identity
          type: string
          short-summary: Update cluster's kubelet identity to an existing user assigned identity. Note, this operation will recreate all agent node in the cluster.
        - name: --enable-pod-identity
          type: bool
          short-summary: (PREVIEW) Enable Pod Identity addon for cluster.
        - name: --enable-pod-identity-with-kubenet
          type: bool
          short-summary: (PREVIEW) Enable pod identity addon for cluster using Kubnet network plugin.
        - name: --disable-pod-identity
          type: bool
          short-summary: (PREVIEW) Disable Pod Identity addon for cluster.
        - name: --enable-workload-identity
          type: bool
          short-summary: (PREVIEW) Enable Workload Identity addon for cluster.
        - name: --disable-workload-identity
          type: bool
          short-summary: (PREVIEW) Disable Workload Identity addon for cluster.
        - name: --enable-secret-rotation
          type: bool
          short-summary: Enable secret rotation. Use with azure-keyvault-secrets-provider addon.
        - name: --disable-secret-rotation
          type: bool
          short-summary: Disable secret rotation. Use with azure-keyvault-secrets-provider addon.
        - name: --rotation-poll-interval
          type: string
          short-summary: Set interval of rotation poll. Use with azure-keyvault-secrets-provider addon.
        - name: --k8s-support-plan
          type: string
          short-summary: Choose from "KubernetesOfficial" or "AKSLongTermSupport", with "AKSLongTermSupport" you get 1 extra year of CVE patchs.
        - name: --enable-disk-driver
          type: bool
          short-summary: Enable AzureDisk CSI Driver.
        - name: --ip-families
          type: string
          short-summary: A comma separated list of IP versions to use for cluster networking.
          long-summary: Each IP version should be in the format IPvN. For example, IPv4.
        - name: --pod-cidr
          type: string
          short-summary: A CIDR notation IP range from which to assign pod IPs when kubenet is used.
          long-summary: This range must not overlap with any Subnet IP ranges. For example, 172.244.0.0/16.
        - name: --network-plugin
          type: string
          short-summary: The Kubernetes network plugin to use.
          long-summary: Specify "azure" for routable pod IPs from VNET, "kubenet" for non-routable pod IPs with an overlay network, or "none" for no networking configured.
        - name: --network-plugin-mode
          type: string
          short-summary: The network plugin mode to use.
          long-summary: |
              Used to control the mode the network plugin should operate in. For example, "overlay" used with
              --network-plugin=azure will use an overlay network (non-VNET IPs) for pods in the cluster.
        - name: --network-policy
          type: string
          short-summary: Update the mode of a network policy.
          long-summary: |
              Specify "azure" for Azure network policy manager, "cilium" for Azure CNI Overlay powered by Cilium.
              Defaults to "" (network policy disabled).
        - name: --network-dataplane
          type: string
          short-summary: The network dataplane to use.
          long-summary: |
              Network dataplane used in the Kubernetes cluster.
              Specify "azure" to use the Azure dataplane (default) or "cilium" to enable Cilium dataplane.
        - name: --disk-driver-version
          type: string
          short-summary: Specify AzureDisk CSI Driver version.
        - name: --disable-disk-driver
          type: bool
          short-summary: Disable AzureDisk CSI Driver.
        - name: --enable-file-driver
          type: bool
          short-summary: Enable AzureFile CSI Driver.
        - name: --disable-file-driver
          type: bool
          short-summary: Disable AzureFile CSI Driver.
        - name: --enable-snapshot-controller
          type: bool
          short-summary: Enable Snapshot Controller.
        - name: --disable-snapshot-controller
          type: bool
          short-summary: Disable CSI Snapshot Controller.
        - name: --enable-blob-driver
          type: bool
          short-summary: Enable AzureBlob CSI Driver.
        - name: --disable-blob-driver
          type: bool
          short-summary: Disable AzureBlob CSI Driver.
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
          short-summary: Enable public fqdn feature for private cluster.
        - name: --disable-public-fqdn
          type: bool
          short-summary: Disable public fqdn feature for private cluster.
        - name: --enable-windows-gmsa
          type: bool
          short-summary: Enable Windows gmsa on cluster.
        - name: --gmsa-dns-server
          type: string
          short-summary: Specify DNS server for Windows gmsa on cluster.
          long-summary: |-
             You do not need to set this if you have set DNS server in the VNET used by the cluster.
             You must set or not set --gmsa-dns-server and --gmsa-root-domain-name at the same time when setting --enable-windows-gmsa.
        - name: --gmsa-root-domain-name
          type: string
          short-summary: Specify root domain name for Windows gmsa on cluster.
          long-summary: |-
             You do not need to set this if you have set DNS server in the VNET used by the cluster.
             You must set or not set --gmsa-dns-server and --gmsa-root-domain-name at the same time when setting --enable-windows-gmsa.
        - name: --enable-oidc-issuer
          type: bool
          short-summary: Enable OIDC issuer.
        - name: --http-proxy-config
          type: string
          short-summary: HTTP Proxy configuration for this cluster.
        - name: --kube-proxy-config
          type: string
          short-summary: kube-proxy configuration for this cluster.
        - name: --enable-azure-keyvault-kms
          type: bool
          short-summary: Enable Azure KeyVault Key Management Service.
        - name: --disable-azure-keyvault-kms
          type: bool
          short-summary: Disable Azure KeyVault Key Management Service.
        - name: --azure-keyvault-kms-key-id
          type: string
          short-summary: Identifier of Azure Key Vault key.
        - name: --azure-keyvault-kms-key-vault-network-access
          type: string
          short-summary: Network Access of Azure Key Vault.
          long-summary: Allowed values are "Public", "Private". If not set, defaults to type "Public". Requires --azure-keyvault-kms-key-id to be used.
        - name: --azure-keyvault-kms-key-vault-resource-id
          type: string
          short-summary: Resource ID of Azure Key Vault.
        - name: --enable-image-cleaner
          type: bool
          short-summary: Enable ImageCleaner Service.
        - name: --disable-image-cleaner
          type: bool
          short-summary: Disable ImageCleaner Service.
        - name: --image-cleaner-interval-hours
          type: int
          short-summary: ImageCleaner scanning interval.
        - name: --enable-image-integrity
          type: bool
          short-summary: Enable ImageIntegrity Service.
        - name: --disable-image-integrity
          type: bool
          short-summary: Disable ImageIntegrity Service.
        - name: --enable-apiserver-vnet-integration
          type: bool
          short-summary: Enable integration of user vnet with control plane apiserver pods.
        - name: --apiserver-subnet-id
          type: string
          short-summary: The ID of a subnet in an existing VNet into which to assign control plane apiserver pods(requires --enable-apiserver-vnet-integration)
        - name: --enable-keda
          type: bool
          short-summary: Enable KEDA workload auto-scaler.
        - name: --disable-keda
          type: bool
          short-summary: Disable KEDA workload auto-scaler.
        - name: --enable-defender
          type: bool
          short-summary: Enable Microsoft Defender security profile.
        - name: --disable-defender
          type: bool
          short-summary: Disable defender profile.
        - name: --defender-config
          type: string
          short-summary: Path to JSON file containing Microsoft Defender profile configurations.
        - name: --enable-azuremonitormetrics
          type: bool
          short-summary: Enable Azure Monitor Metrics Profile
        - name: --enable-azure-monitor-metrics
          type: bool
          short-summary: Enable Azure Monitor Metrics Profile
        - name: --azure-monitor-workspace-resource-id
          type: string
          short-summary: Resource ID of the Azure Monitor Workspace
        - name: --ksm-metric-labels-allow-list
          type: string
          short-summary: Comma-separated list of additional Kubernetes label keys that will be used in the resource' labels metric. By default the metric contains only name and namespace labels. To include additional labels provide a list of resource names in their plural form and Kubernetes label keys you would like to allow for them (e.g. '=namespaces=[k8s-label-1,k8s-label-n,...],pods=[app],...)'. A single '*' can be provided per resource instead to allow any labels, but that has severe performance implications (e.g. '=pods=[*]').
        - name: --ksm-metric-annotations-allow-list
          type: string
          short-summary: Comma-separated list of additional Kubernetes label keys that will be used in the resource' labels metric. By default the metric contains only name and namespace labels. To include additional labels provide a list of resource names in their plural form and Kubernetes label keys you would like to allow for them (e.g.'=namespaces=[k8s-label-1,k8s-label-n,...],pods=[app],...)'. A single '*' can be provided per resource instead to allow any labels, but that has severe performance implications (e.g. '=pods=[*]').
        - name: --grafana-resource-id
          type: string
          short-summary: Resource ID of the Azure Managed Grafana Workspace
        - name: --enable-windows-recording-rules
          type: bool
          short-summary: Enable Windows Recording Rules when enabling the Azure Monitor Metrics addon
        - name: --disable-azuremonitormetrics
          type: bool
          short-summary: Disable Azure Monitor Metrics Profile. This will delete all DCRA's associated with the cluster, any linked DCRs with the data stream = prometheus-stream and the recording rule groups created by the addon for this AKS cluster.
        - name: --disable-azure-monitor-metrics
          type: bool
          short-summary: Disable Azure Monitor Metrics Profile. This will delete all DCRA's associated with the cluster, any linked DCRs with the data stream = prometheus-stream and the recording rule groups created by the addon for this AKS cluster.
        - name: --enable-node-restriction
          type: bool
          short-summary: Enable node restriction option on cluster.
        - name: --disable-node-restriction
          type: bool
          short-summary: Disable node restriction option on cluster.
        - name: --enable-private-cluster
          type: bool
          short-summary: Enable private cluster for apiserver vnet integration cluster.
        - name: --disable-private-cluster
          type: bool
          short-summary: Disable private cluster for apiserver vnet integration cluster.
        - name: --private-dns-zone
          type: string
          short-summary: The private dns zone mode for private cluster.
        - name: --enable-vpa
          type: bool
          short-summary: Enable vertical pod autoscaler for cluster.
        - name: --disable-vpa
          type: bool
          short-summary: Disable vertical pod autoscaler for cluster.
        - name: --enable-addon-autoscaling
          type: bool
          short-summary: Enable addon autoscaling for cluster.
        - name: --disable-addon-autoscaling
          type: bool
          short-summary: Disable addon autoscaling for cluster.
        - name: --cluster-snapshot-id
          type: string
          short-summary: The source cluster snapshot id is used to update existing cluster.
        - name: --ssh-key-value
          type: string
          short-summary: Public key path or key contents to install on node VMs for SSH access. For example,
                         'ssh-rsa AAAAB...snip...UcyupgH azureuser@linuxvm'.
        - name: --ca-certs --custom-ca-trust-certificates
          type: string
          short-summary: Path to a file containing up to 10 blank line separated certificates. Only valid for linux nodes.
          long-summary: These certificates are used by Custom CA Trust features and will be added to trust stores of nodes. Requires Custom CA Trust to be enabled on the node.
        - name: --safeguards-level
          type: string
          short-summary: The deployment safeguards Level. Accepted Values are [Off, Warning, Enforcement]. Requires azure policy addon to be enabled
        - name: --safeguards-version
          type: string
          short-summary: The version of deployment safeguards to use. Default "v1.0.0" Use the ListSafeguardsVersions API to discover available versions
        - name: --safeguards-excluded-ns
          type: string
          short-summary: Comma-separated list of Kubernetes namespaces to exclude from deployment safeguards. Use "" to clear a previously non-empty list
        - name: --nodepool-taints
          type: string
          short-summary: The node taints for all node pool.
        - name: --nodepool-labels
          type: string
          short-summary: The node labels for all node pool. See https://aka.ms/node-labels for syntax of labels.
        - name: --enable-network-observability
          type: bool
          short-summary: Enable network observability on a cluster.
        - name: --disable-network-observability
          type: bool
          short-summary: Disable network observability on a cluster
        - name: --enable-cost-analysis
          type: bool
          short-summary: Enable exporting Kubernetes Namespace and Deployment details to the Cost Analysis views in the Azure portal. For more information see aka.ms/aks/docs/cost-analysis.
        - name: --disable-cost-analysis
          type: bool
          short-summary: Disable exporting Kubernetes Namespace and Deployment details to the Cost Analysis views in the Azure portal.
        - name: --node-provisioning-mode
          type: string
          short-summary: Set the node provisioning mode of the cluster. Valid values are "Auto" and "Manual". For more information on "Auto" mode see aka.ms/aks/nap.
        - name: --enable-ai-toolchain-operator
          type: bool
          short-summary: Enable AI toolchain operator to the cluster
        - name: --disable-ai-toolchain-operator
          type: bool
          short-summary: Disable AI toolchain operator.
        - name: --ssh-access
          type: string
          short-summary: Update SSH setting for all node pools in this cluster. Use "disabled" to disable SSH access, "localuser" to enable SSH access using private key.
        - name: --node-init-taints --nodepool-initialization-taints
          type: string
          short-summary: The node initialization taints for all node pools in cluster.
    examples:
      - name: Reconcile the cluster back to its current state.
        text: az aks update -g MyResourceGroup -n MyManagedCluster
      - name: Enable cluster-autoscaler within node count range [1,5]
        text: az aks update --enable-cluster-autoscaler --min-count 1 --max-count 5 -g MyResourceGroup -n MyManagedCluster
      - name: Disable cluster-autoscaler for an existing cluster
        text: az aks update --disable-cluster-autoscaler -g MyResourceGroup -n MyManagedCluster
      - name: Update min-count or max-count for cluster autoscaler.
        text: az aks update --update-cluster-autoscaler --min-count 1 --max-count 10 -g MyResourceGroup -n MyManagedCluster
      - name: Disable pod security policy.
        text: az aks update --disable-pod-security-policy -g MyResourceGroup -n MyManagedCluster
      - name: Update a kubernetes cluster with standard SKU load balancer to use two AKS created IPs for the load balancer outbound connection usage.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --load-balancer-managed-outbound-ip-count 2
      - name: Update a kubernetes cluster with standard SKU load balancer to use the provided public IPs for the load balancer outbound connection usage.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --load-balancer-outbound-ips <ip-resource-id-1,ip-resource-id-2>
      - name: Update a kubernetes cluster with standard SKU load balancer to use the provided public IP prefixes for the load balancer outbound connection usage.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --load-balancer-outbound-ip-prefixes <ip-prefix-resource-id-1,ip-prefix-resource-id-2>
      - name: Update a kubernetes cluster with new outbound type
        text: az aks update -g MyResourceGroup -n MyManagedCluster --outbound-type managedNATGateway
      - name: Update a kubernetes cluster with two outbound AKS managed IPs an idle flow timeout of 5 minutes and 8000 allocated ports per machine
        text: az aks update -g MyResourceGroup -n MyManagedCluster --load-balancer-managed-outbound-ip-count 2 --load-balancer-idle-timeout 5 --load-balancer-outbound-ports 8000
      - name: Update a kubernetes cluster of managedNATGateway outbound type with two outbound AKS managed IPs an idle flow timeout of 4 minutes
        text: az aks update -g MyResourceGroup -n MyManagedCluster --nat-gateway-managed-outbound-ip-count 2 --nat-gateway-idle-timeout 4
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
      - name: Enable Windows gmsa for a kubernetes cluster with setting DNS server in the vnet used by the cluster.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --enable-windows-gmsa
      - name: Enable Windows gmsa for a kubernetes cluster without setting DNS server in the vnet used by the cluster.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --enable-windows-gmsa --gmsa-dns-server "10.240.0.4" --gmsa-root-domain-name "contoso.com"
      - name: Update a existing managed cluster to a managed cluster snapshot.
        text: az aks update -g MyResourceGroup -n MyManagedCluster --cluster-snapshot-id "/subscriptions/00000/resourceGroups/AnotherResourceGroup/providers/Microsoft.ContainerService/managedclustersnapshots/mysnapshot1"
      - name: Update a kubernetes cluster with safeguards set to "Warning". Assumes azure policy addon is already enabled
        text: az aks update -g MyResourceGroup -n MyManagedCluster --safeguards-level Warning
      - name: Update a kubernetes cluster with safeguards set to "Warning" and some namespaces excluded. Assumes azure policy addon is already enabled
        text: az aks update -g MyResourceGroup -n MyManagedCluster --safeguards-level Warning --safeguards-excluded-ns ns1,ns2
      - name: Update a kubernetes cluster to clear any namespaces excluded from safeguards. Assumes azure policy addon is already enabled
        text: az aks update -g MyResourceGroup -n MyManagedCluster --safeguards-excluded-ns ""
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
          short-summary: The list of node logs to collect for Linux nodes. For example, /var/log/cloud-init.log
        - name: --node-logs-windows
          type: string
          short-summary: The list of node logs to collect for Windows nodes. For example, C:\\AzureData\\CustomDataSetupScript.log
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
          short-summary: A day in week on which maintenance is allowed. E.g. Monday. Applicable to default maintenance configuration only.
        - name: --start-hour
          type: string
          short-summary: The start time of 1 hour window which maintenance is allowd. E.g. 1 means it's allowd between 1:00 am and 2:00 am. Applicable to default maintenance configuration only.
        - name: --schedule-type
          type: string
          short-summary: Choose either 'Daily', 'Weekly', 'AbsoluteMonthly' or 'RelativeMonthly' for your maintenance schedule. Only applicable to 'aksManagedAutoUpgradeSchedule' and 'aksManagedNodeOSUpgradeSchedule' maintenance configuration.
        - name: --start-date
          type: string
          short-summary: The date the maintenance configuration activates. If not specified, the maintenance window will be active right away."
        - name: --start-time
          type: string
          short-summary: The start time of the maintenance window. Accepted values are from '00:00' to '23:59'. '--utc-offset' applies to this field. For example, '02:00' with '--utc-offset +02:00' means UTC time '00:00'.
        - name: --duration
          type: int
          short-summary: The length of maintenance window range from 4 to 24 hours.
        - name: --utc-offset
          type: string
          short-summary: The UTC offset in format +/-HH:mm. For example, '+05:30' for IST and '-07:00' for PST. If not specified, the default is '+00:00'.
        - name: --interval-days
          type: int
          short-summary: The number of days between each set of occurrences for daily schedule type.
        - name: --interval-weeks
          type: int
          short-summary: The number of weeks between each set of occurrences. Applicable to weekly schedule types only.
        - name: --interval-months
          type: int
          short-summary: The number of months between each set of occurrences. Applicable to absolute and relative monthly schedule types.
        - name: --day-of-week
          type: string
          short-summary: Specify on which day of the week the maintenance occurs. E.g. "Monday". Applicable to weekly and relative monthly schedule types.
        - name: --day-of-month
          type: int
          short-summary: Specify on which day of the month the maintenance occurs. E.g. 1 indicates the 1st of the month. Applicable to absolute monthly schedule type only.
        - name: --week-index
          type: string
          short-summary: Specify on which instance of the allowed days specified in '--day-of-week' the maintenance occurs. Applicable to relative monthly schedule type only.
        - name: --config-file
          type: string
          short-summary: The maintenance configuration json file.
    examples:
        - name: Add default maintenance configuration with --weekday and --start-hour.
          text: |
            az aks maintenanceconfiguration add -g MyResourceGroup --cluster-name test1 -n default --weekday Monday  --start-hour 1
              The maintenance is allowed on Monday 1:00am to 2:00am
        - name: Add default maintenance configuration with --weekday. The maintenance is allowd on any time of that day.
          text: |
            az aks maintenanceconfiguration add -g MyResourceGroup --cluster-name test1 -n default --weekday Monday
              The maintenance is allowed on Monday.
        - name: Add default maintenance configuration with maintenance configuration json file
          text: |
            az aks maintenanceconfiguration add -g MyResourceGroup --cluster-name test1 -n default --config-file ./test.json
                The content of json file looks below. It means the maintenance is allowed on UTC time Tuesday 1:00am - 3:00 am and Wednesday 1:00am - 2:00am, 6:00am-7:00am
                No maintenance is allowed from 2020-11-26T03:00:00Z to 2020-11-30T12:00:00Z and from 2020-12-26T03:00:00Z to 2020-12-26T12:00:00Z even if they are allowed in the above weekly setting
                {
                      "timeInWeek": [
                        {
                          "day": "Tuesday",
                          "hourSlots": [
                            1,
                            2
                          ]
                        },
                        {
                          "day": "Wednesday",
                          "hourSlots": [
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
        - name: Add aksManagedNodeOSUpgradeSchedule maintenance configuration with daily schedule.
          text: |
            az aks maintenanceconfiguration add -g MyResourceGroup --cluster-name test1 -n aksManagedNodeOSUpgradeSchedule --schedule-type Daily --interval-days 2 --duration 12 --utc-offset=-08:00 --start-date 2023-01-16 --start-time 00:00
              The maintenance is allowed from 00:00 to 12:00 (adjusted with UTC offset: -08:00) every two days, and this configuration will be effective from 2023-01-16.
        - name: Add aksManagedNodeOSUpgradeSchedule maintenance configuration with weekly schedule.
          text: |
            az aks maintenanceconfiguration add -g MyResourceGroup --cluster-name test1 -n aksManagedNodeOSUpgradeSchedule --schedule-type Weekly --day-of-week Friday --interval-weeks 3 --duration 8 --utc-offset +05:30 --start-date 2023-01-16 --start-time 09:30
              The maintenance is allowed on Friday from 09:30 to 17:30 (adjusted with UTC offset: +05:30) every three weeks, and this configuration will be effective from 2023-01-16.
        - name: Add aksManagedAutoUpgradeSchedule maintenance configuration with absolute monthly schedule.
          text: |
            az aks maintenanceconfiguration add -g MyResourceGroup --cluster-name test1 -n aksManagedAutoUpgradeSchedule --schedule-type AbsoluteMonthly --day-of-month 15 --interval-months 1 --duration 6 --utc-offset +05:30 --start-date 2023-01-16 --start-time 09:30
              The maintenance is allowed on the 15th of the month from 09:30 to 15:30 (adjusted with UTC offset: +05:30) every month, and this configuration will be effective from 2023-01-16.
        - name: Add aksManagedAutoUpgradeSchedule maintenance configuration with relative monthly schedule.
          text: |
            az aks maintenanceconfiguration add -g MyResourceGroup --cluster-name test1 -n aksManagedAutoUpgradeSchedule --schedule-type RelativeMonthly --day-of-week Tuesday --week-index Last --interval-months 3 --duration 6 --start-date 2023-01-16 --start-time 09:30
              The maintenance is allowed on the last Tuesday from 09:30 to 15:30 in default UTC time every 3 months, and this configuration will be effective from 2023-01-16.
        - name: Add aksManagedAutoUpgradeSchedule maintenance configuration with json file.
          text: |
            az aks maintenanceconfiguration add -g MyResourceGroup --cluster-name test1 -n aksManagedAutoUpgradeSchedule --config-file ./test.json
                The content of json file looks below. It means the maintenance is allowed on the 1st of the month from 09:00 to 13:00 (adjusted with UTC offset: -08:00) every 3 months, and this configuration will be effective from 2023-01-16.
                No maintenance is allowed from 2022-12-23 to 2023-01-05 and from 2023-11-23 to 2023-11-26 even if they are allowed in the above monthly setting
                {
                    "maintenanceWindow": {
                        "schedule": {
                            "absoluteMonthly": {
                                "intervalMonths": 3,
                                "dayOfMonth": 1
                            }
                        },
                        "durationHours": 4,
                        "utcOffset": "-08:00",
                        "startTime": "09:00",
                        "notAllowedDates": [
                            {
                                "start": "2022-12-23",
                                "end": "2023-01-05"
                            },
                            {
                                "start": "2023-11-23",
                                "end": "2023-11-26"
                            }
                        ]
                    }
                }
"""

helps['aks maintenanceconfiguration update'] = """
    type: command
    short-summary: Update a maintenance configuration of a managed Kubernetes cluster.
    parameters:
        - name: --weekday
          type: string
          short-summary: A day in week on which maintenance is allowed. E.g. Monday. Applicable to default maintenance configuration only.
        - name: --start-hour
          type: string
          short-summary: The start time of 1 hour window which maintenance is allowd. E.g. 1 means it's allowd between 1:00 am and 2:00 am. Applicable to default maintenance configuration only.
        - name: --schedule-type
          type: string
          short-summary: Choose either 'Daily', 'Weekly', 'AbsoluteMonthly' or 'RelativeMonthly' for your maintenance schedule. Only applicable to 'aksManagedAutoUpgradeSchedule' and 'aksManagedNodeOSUpgradeSchedule' maintenance configuration.
        - name: --start-date
          type: string
          short-summary: The date the maintenance configuration activates. If not specified, the maintenance window will be active right away."
        - name: --start-time
          type: string
          short-summary: The start time of the maintenance window. Accepted values are from '00:00' to '23:59'. '--utc-offset' applies to this field. For example, '02:00' with '--utc-offset +02:00' means UTC time '00:00'.
        - name: --duration
          type: int
          short-summary: The length of maintenance window range from 4 to 24 hours.
        - name: --utc-offset
          type: string
          short-summary: The UTC offset in format +/-HH:mm. For example, '+05:30' for IST and '-07:00' for PST. If not specified, the default is '+00:00'.
        - name: --interval-days
          type: int
          short-summary: The number of days between each set of occurrences for daily schedule type.
        - name: --interval-weeks
          type: int
          short-summary: The number of weeks between each set of occurrences. Applicable to weekly schedule types only.
        - name: --interval-months
          type: int
          short-summary: The number of months between each set of occurrences. Applicable to absolute and relative monthly schedule types.
        - name: --day-of-week
          type: string
          short-summary: Specify on which day of the week the maintenance occurs. E.g. "Monday". Applicable to weekly and relative monthly schedule types.
        - name: --day-of-month
          type: int
          short-summary: Specify on which day of the month the maintenance occurs. E.g. 1 indicates the 1st of the month. Applicable to absolute monthly schedule type only.
        - name: --week-index
          type: string
          short-summary: Specify on which instance of the allowed days specified in '--day-of-week' the maintenance occurs. Applicable to relative monthly schedule type only.
        - name: --config-file
          type: string
          short-summary: The maintenance configuration json file.
    examples:
        - name: Update default maintenance configuration with --weekday and --start-hour.
          text: |
            az aks maintenanceconfiguration update -g MyResourceGroup --cluster-name test1 -n default --weekday Monday  --start-hour 1
              The maintenance is allowed on Monday 1:00am to 2:00am
        - name: Update default maintenance configuration with --weekday.The maintenance is allowd on any time of that day.
          text: |
            az aks maintenanceconfiguration update -g MyResourceGroup --cluster-name test1 -n default --weekday Monday
              The maintenance is allowed on Monday.
        - name: Update default maintenance configuration with maintenance configuration json file
          text: |
            az aks maintenanceconfiguration update -g MyResourceGroup --cluster-name test1 -n default --config-file ./test.json
                The content of json file looks below. It means the maintenance is allowed on UTC time Tuesday 1:00am - 3:00 am and Wednesday 1:00am - 2:00am, 6:00am-7:00am
                No maintenance is allowed from 2020-11-26T03:00:00Z to 2020-11-30T12:00:00Z and from 2020-12-26T03:00:00Z to 2020-12-26T12:00:00Z even if they are allowed in the above weekly setting
                {
                      "timeInWeek": [
                        {
                          "day": "Tuesday",
                          "hourSlots": [
                            1,
                            2
                          ]
                        },
                        {
                          "day": "Wednesday",
                          "hourSlots": [
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
        - name: Update aksManagedNodeOSUpgradeSchedule maintenance configuration with daily schedule.
          text: |
            az aks maintenanceconfiguration update -g MyResourceGroup --cluster-name test1 -n aksManagedNodeOSUpgradeSchedule --schedule-type Daily --interval-days 2 --duration 12 --utc-offset=-08:00 --start-date 2023-01-16 --start-time 00:00
              The maintenance is allowed from 00:00 to 12:00 (adjusted with UTC offset: -08:00) every two days. This configuration will be effective from 2023-01-16.
        - name: Update aksManagedNodeOSUpgradeSchedule maintenance configuration with weekly schedule.
          text: |
            az aks maintenanceconfiguration update -g MyResourceGroup --cluster-name test1 -n aksManagedNodeOSUpgradeSchedule --schedule-type Weekly --day-of-week Friday --interval-weeks 3 --duration 8 --utc-offset +05:30 --start-date 2023-01-16 --start-time 09:30
              The maintenance is allowed on Friday from 09:30 to 17:30 (adjusted with UTC offset: +05:30) every three weeks. This configuration will be effective from 2023-01-16.
        - name: Update aksManagedAutoUpgradeSchedule maintenance configuration with absolute monthly schedule.
          text: |
            az aks maintenanceconfiguration update -g MyResourceGroup --cluster-name test1 -n aksManagedAutoUpgradeSchedule --schedule-type AbsoluteMonthly --day-of-month 15 --interval-months 1 --duration 6 --utc-offset +05:30 --start-date 2023-01-16 --start-time 09:30
              The maintenance is allowed on the 15th of the month from 09:30 to 15:30 (adjusted with UTC offset: +05:30) every month. This configuration will be effective from 2023-01-16.
        - name: Update aksManagedAutoUpgradeSchedule maintenance configuration with relative monthly schedule.
          text: |
            az aks maintenanceconfiguration update -g MyResourceGroup --cluster-name test1 -n aksManagedAutoUpgradeSchedule --schedule-type RelativeMonthly --day-of-week Tuesday --week-index Last --interval-months 3 --duration 6 --start-date 2023-01-16 --start-time 09:30
              The maintenance is allowed on the last Tuesday from 09:30 to 15:30 in default UTC time every 3 months. This configuration will be effective from 2023-01-16.
        - name: Update aksManagedAutoUpgradeSchedule maintenance configuration with json file.
          text: |
            az aks maintenanceconfiguration update -g MyResourceGroup --cluster-name test1 -n aksManagedAutoUpgradeSchedule --config-file ./test.json
                The content of json file looks below. It means the maintenance is allowed on the 1st of the month from 09:00 to 13:00 (adjusted with UTC offset: -08:00) every 3 months, and this configuration will be effective from 2023-01-16.
                No maintenance is allowed from 2022-12-23 to 2023-01-05 and from 2023-11-23 to 2023-11-26 even if they are allowed in the above monthly setting
                {
                    "maintenanceWindow": {
                        "schedule": {
                            "absoluteMonthly": {
                                "intervalMonths": 3,
                                "dayOfMonth": 1
                            }
                        },
                        "durationHours": 4,
                        "utcOffset": "-08:00",
                        "startTime": "09:00",
                        "notAllowedDates": [
                            {
                                "start": "2022-12-23",
                                "end": "2023-01-05"
                            },
                            {
                                "start": "2023-11-23",
                                "end": "2023-11-26"
                            }
                        ]
                    }
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
          short-summary: Size in GiB of the OS disk for each node in the agent pool. Minimum 30 GiB.
        - name: --node-osdisk-type
          type: string
          short-summary: OS disk type to be used for machines in a given agent pool. Defaults to 'Ephemeral' when possible in conjunction with VM size and OS disk size. May not be changed for this pool after creation. ('Ephemeral' or 'Managed')
        - name: --max-pods -m
          type: int
          short-summary: The maximum number of pods deployable to a node.
          long-summary: If not specified, defaults based on network-plugin. 30 for "azure", 110 for "kubenet", or 250 for "none".
        - name: --zones -z
          type: string array
          short-summary: Space-separated list of availability zones where agent nodes will be placed. Must use VMSS agent pool type.
        - name: --vnet-subnet-id
          type: string
          short-summary: The ID of a subnet in an existing VNet into which to deploy the cluster.
        - name: --pod-subnet-id
          type: string
          short-summary: The ID of a subnet in an existing VNet into which to assign pods in the cluster (requires azure network-plugin)
        - name: --ppg
          type: string
          short-summary: The ID of a PPG. Must use VMSS agent pool type.
        - name: --os-type
          type: string
          short-summary: The OS Type. Linux or Windows. Windows not supported yet for "VirtualMachines" VM set type.
        - name: --os-sku
          type: string
          short-summary: The os-sku of the agent node pool. Ubuntu or CBLMariner when os-type is Linux, default is Ubuntu if not set; Windows2019 or Windows2022 when os-type is Windows, the current default is Windows2019 if not set, and the default will be changed to Windows2022 after Windows2019 is deprecated.
        - name: --enable-fips-image
          type: bool
          short-summary: Use FIPS-enabled OS on agent nodes.
        - name: --enable-cluster-autoscaler -e
          type: bool
          short-summary: Enable cluster autoscaler. Must use VMSS agent pool type.
        - name: --min-count
          type: int
          short-summary: Minimun nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specify the value in the range of [0, 1000] for user nodepool, and [1,1000] for system nodepool.
        - name: --max-count
          type: int
          short-summary: Maximum nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specify the value in the range of [0, 1000] for user nodepool, and [1,1000] for system nodepool.
        - name: --scale-down-mode
          type: string
          short-summary: "Describes how VMs are added to or removed from nodepools."
        - name: --node-taints
          type: string
          short-summary: The node taints for the node pool.
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
          short-summary: Enable VMSS node public IP. Must use VMSS agent pool type.
        - name: --node-public-ip-prefix-id
          type: string
          short-summary: Public IP prefix ID used to assign public IPs to VMSS nodes. Must use VMSS agent pool type.
        - name: --labels
          type: string
          short-summary: The node labels for the node pool. See https://aka.ms/node-labels for syntax of labels.
        - name: --mode
          type: string
          short-summary: The mode for a node pool which defines a node pool's primary function. If set as "System", AKS prefers system pods scheduling to node pools with mode `System`. Learn more at https://aka.ms/aks/nodepool/mode.
        - name: --vm-set-type
          type: string
          short-summary: Agent pool vm set type. VirtualMachineScaleSets, AvailabilitySet or VirtualMachines(Preview).
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
        - name: --max-surge
          type: string
          short-summary: Extra nodes used to speed upgrade. When specified, it represents the number or percent used, eg. 5 or 33%
        - name: --drain-timeout
          type: int
          short-summary: When nodes are drain how many minutes to wait for all pods to be evicted
        - name: --node-soak-duration
          type: int
          short-summary: The amount of time (in minutes) to wait after draining a node and before reimaging it and moving on to next node.
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
          short-summary: Enable UltraSSD on agent node pool. Must use VMSS agent pool type.
        - name: --workload-runtime
          type: string
          short-summary: Determines the type of workload a node can run. Defaults to OCIContainer.
        - name: --gpu-instance-profile
          type: string
          short-summary: GPU instance profile to partition multi-gpu Nvidia GPUs.
        - name: --snapshot-id
          type: string
          short-summary: The source snapshot id used to create this nodepool. Must use VMSS agent pool type.
        - name: --crg-id
          type: string
          short-summary: The crg-id used to associate the new nodepool with the existed Capacity Reservation Group resource. Must use VMSS agent pool type.
        - name: --host-group-id
          type: string
          short-summary: (PREVIEW) The fully qualified dedicated host group id used to provision agent node pool. Must use VMSS agent pool type.
        - name: --message-of-the-day
          type: string
          short-summary: Path to a file containing the desired message of the day. Only valid for linux nodes. Will be written to /etc/motd.
        - name: --enable-custom-ca-trust
          type: bool
          short-summary: Enable Custom CA Trust on agent node pool.
        - name: --disable-windows-outbound-nat
          type: bool
          short-summary: Disable Windows OutboundNAT on Windows agent node pool. Must use VMSS agent pool type.
        - name: --allowed-host-ports
          type: string
          short-summary: Expose host ports on the node pool. When specified, format should be a comma-separated list of ranges with protocol, eg. 80/TCP,443/TCP,4000-5000/TCP. Must use VMSS agent pool type.
        - name: --asg-ids
          type: string
          short-summary: The IDs of the application security groups to which the node pool's network interface should belong. When specified, format should be a comma-separated list of IDs. Must use VMSS agent pool type.
        - name: --node-public-ip-tags
          type: string
          short-summary: The ipTags of the node public IPs. Must use VMSS agent pool type.
        - name: --enable-artifact-streaming
          type: bool
          short-summary: Enable artifact streaming for VirtualMachineScaleSets managed by a node pool, to speed up the cold-start of containers on a node through on-demand image loading. To use this feature, container images must also enable artifact streaming on ACR. If not specified, the default is false.
        - name: --skip-gpu-driver-install
          type: bool
          short-summary: To skip GPU driver auto installation by AKS on a nodepool using GPU vm size if customers want to manage GPU driver installation by their own. If not specified, the default is false.
        - name: --ssh-access
          type: string
          short-summary: Configure SSH setting for the node pool. Use "disabled" to disable SSH access, "localuser" to enable SSH access using private key.
        - name: --pod-ip-allocation-mode
          type: string
          short-summary: Set the ip allocation mode for how Pod IPs from the Azure Pod Subnet are allocated to the nodes in the AKS cluster. The choice is between dynamic batches of individual IPs or static allocation of a set of CIDR blocks. Accepted Values are "DynamicIndividual" or "StaticBlock".
          long-summary: |
              Used together with the "azure" network plugin.
              Requires --pod-subnet-id.
        - name: --enable-secure-boot
          type: bool
          short-summary: Enable Secure Boot on agent node pool. Must use VMSS agent pool type.
        - name: --enable-vtpm
          type: bool
          short-summary: Enable vTPM on agent node pool. Must use VMSS agent pool type.
    examples:
        - name: Create a nodepool in an existing AKS cluster with ephemeral os enabled.
          text: az aks nodepool add -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster --node-osdisk-type Ephemeral --node-osdisk-size 48
        - name: Create a nodepool with EncryptionAtHost enabled.
          text: az aks nodepool add -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster --enable-encryption-at-host
        - name: Create a nodepool with a specific os-sku
          text: az aks nodepool add -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster  --os-sku Ubuntu
        - name: Create a nodepool which can run wasm workloads.
          text: az aks nodepool add -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster  --workload-runtime WasmWasi
        - name: create a kubernetes cluster with a snapshot id.
          text: az aks nodepool add -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster --kubernetes-version 1.20.9 --snapshot-id "/subscriptions/00000/resourceGroups/AnotherResourceGroup/providers/Microsoft.ContainerService/snapshots/mysnapshot1"
        - name: create a nodepool with a Capacity Reservation Group(CRG) ID.
          text: az aks nodepool add -g MyResourceGroup -n MyNodePool --cluster-name MyMC --node-vm-size VMSize --crg-id "/subscriptions/SubID/resourceGroups/ResourceGroupName/providers/Microsoft.ContainerService/CapacityReservationGroups/MyCRGID"
        - name: create a nodepool in an existing AKS cluster with host group id
          text: az aks nodepool add -g MyResourceGroup -n MyNodePool --cluster-name MyMC --host-group-id /subscriptions/00000/resourceGroups/AnotherResourceGroup/providers/Microsoft.ContainerService/hostGroups/myHostGroup --node-vm-size VMSize
        - name: Create a nodepool with ip allocation mode set to "StaticBlock" and using a pod subnet ID
          text: az aks nodepool add -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster  --os-sku Ubuntu --pod-subnet-id /subscriptions/00000/resourceGroups/AnotherResourceGroup/providers/Microsoft.Network/virtualNetworks/MyVnet/subnets/MySubnet --pod-ip-allocation-mode StaticBlock
"""

helps['aks nodepool scale'] = """
    type: command
    short-summary: Scale the node pool in a managed Kubernetes cluster.
    parameters:
        - name: --node-count -c
          type: int
          short-summary: Number of nodes in the Kubernetes node pool.
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
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
        - name: --drain-timeout
          type: int
          short-summary: When nodes are drain how many minutes to wait for all pods to be evicted
        - name: --node-soak-duration
          type: int
          short-summary: The amount of time (in minutes) to wait after draining a node and before reimaging it and moving on to next node.
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
        - name: --snapshot-id
          type: string
          short-summary: The source snapshot id used to upgrade this nodepool. Must use VMSS agent pool type.
"""

helps['aks nodepool update'] = """
    type: command
    short-summary: Update a node pool properties.
    long-summary: Update a node pool to enable/disable cluster-autoscaler or change min-count or max-count.  When called with no optional arguments this attempts to move the node pool to its goal state without changing the current node pool configuration. This can be used to move out of a non succeeded state.
    parameters:
        - name: --enable-cluster-autoscaler -e
          type: bool
          short-summary: Enable cluster autoscaler. Must use VMSS agent pool type.
        - name: --disable-cluster-autoscaler -d
          type: bool
          short-summary: Disable cluster autoscaler.
        - name: --update-cluster-autoscaler -u
          type: bool
          short-summary: Update min-count or max-count for cluster autoscaler.
        - name: --min-count
          type: int
          short-summary: Minimun nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specify the value in the range of [0, 1000] for user nodepool, and [1,1000] for system nodepool.
        - name: --max-count
          type: int
          short-summary: Maximum nodes count used for autoscaler, when "--enable-cluster-autoscaler" specified. Please specify the value in the range of [0, 1000] for user nodepool, and [1,1000] for system nodepool.
        - name: --scale-down-mode
          type: string
          short-summary: "Describes how VMs are added to or removed from nodepools."
        - name: --max-surge
          type: string
          short-summary: Extra nodes used to speed upgrade. When specified, it represents the number or percent used, eg. 5 or 33%
        - name: --drain-timeout
          type: int
          short-summary: When nodes are drain how many minutes to wait for all pods to be evicted
        - name: --node-soak-duration
          type: int
          short-summary: The amount of time (in minutes) to wait after draining a node and before reimaging it and moving on to next node.
        - name: --mode
          type: string
          short-summary: The mode for a node pool which defines a node pool's primary function. If set as "System", AKS prefers system pods scheduling to node pools with mode `System`. Learn more at https://aka.ms/aks/nodepool/mode.
        - name: --labels
          type: string
          short-summary: The node labels for the node pool. See https://aka.ms/node-labels for syntax of labels.
        - name: --node-taints
          type: string
          short-summary: The node taints for the node pool.
        - name: --enable-custom-ca-trust
          type: bool
          short-summary: Enable Custom CA Trust on agent node pool.
        - name: --dcat --disable-custom-ca-trust
          type: bool
          short-summary: Disable Custom CA Trust on agent node pool.
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
        - name: --allowed-host-ports
          type: string
          short-summary: Expose host ports on the node pool. When specified, format should be a comma-separated list of ranges with protocol, eg. 80/TCP,443/TCP,4000-5000/TCP. Must use VMSS agent pool type.
        - name: --asg-ids
          type: string
          short-summary: The IDs of the application security groups to which the node pool's network interface should belong. When specified, format should be a comma-separated list of IDs. Must use VMSS agent pool type.
        - name: --enable-artifact-streaming
          type: bool
          short-summary: Enable artifact streaming for VirtualMachineScaleSets managed by a node pool, to speed up the cold-start of containers on a node through on-demand image loading. To use this feature, container images must also enable artifact streaming on ACR. If not specified, the default is false.
        - name: --os-sku
          type: string
          short-summary: The os-sku of the agent node pool.
        - name: --ssh-access
          type: string
          short-summary: Update SSH setting for the node pool. Use "disabled" to disable SSH access, "localuser" to enable SSH access using private key.
        - name: --enable-secure-boot
          type: bool
          short-summary: Enable Secure Boot on an existing Trusted Launch enabled agent node pool. Must use VMSS agent pool type.
        - name: --disable-secure-boot
          type: bool
          short-summary: Disable Secure Boot on on an existing Trusted Launch enabled agent node pool.
        - name: --enable-vtpm
          type: bool
          short-summary: Enable vTPM on an existing Trusted Launch enabled agent node pool. Must use VMSS agent pool type.
        - name: --disable-vtpm
          type: bool
          short-summary: Disable vTPM on an existing Trusted Launch enabled agent node pool.
    examples:
      - name: Reconcile the nodepool back to its current state.
        text: az aks nodepool update -g MyResourceGroup -n nodepool1 --cluster-name MyManagedCluster
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
"""

helps['aks nodepool stop'] = """
    type: command
    short-summary: Stop running agent pool in the managed Kubernetes cluster.
    parameters:
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
    examples:
        - name: Stop agent pool in the managed cluster
          text: az aks nodepool stop --nodepool-name nodepool1 -g MyResourceGroup --cluster-name MyManagedCluster
"""

helps['aks nodepool start'] = """
    type: command
    short-summary: Start stopped agent pool in the managed Kubernetes cluster.
    parameters:
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
    examples:
        - name: Start agent pool in the managed cluster
          text: az aks nodepool start --nodepool-name nodepool1 -g MyResourceGroup --cluster-name MyManagedCluster
"""

helps['aks nodepool delete'] = """
    type: command
    short-summary: Delete the agent pool in the managed Kubernetes cluster.
    parameters:
        - name: --ignore-pod-disruption-budget -i
          type: bool
          short-summary: (PREVIEW) ignore-pod-disruption-budget deletes an existing nodepool without considering Pod Disruption Budget.
    examples:
        - name: Delete an agent pool with ignore-pod-disruption-budget
          text: az aks nodepool delete --resource-group MyResourceGroup --cluster-name MyManagedCluster --name nodepool1 --ignore-pod-disruption-budget=true
"""

helps['aks nodepool operation-abort'] = """
    type: command
    short-summary: Abort last running operation on nodepool.
    parameters:
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
    examples:
        - name: Abort operation on agent pool
          text: az aks nodepool operation-abort -g myResourceGroup --nodepool-name nodepool1 --cluster-name myAKSCluster
"""

helps['aks nodepool delete-machines'] = """
    type: command
    short-summary: Delete specific machines in an agentpool for a managed cluster.
    parameters:
        - name: --machine-names
          type: string array
          short-summary: Space-separated list of machine names from the agent pool to be deleted.
    examples:
        - name: Delete specific machines in an agent pool
          text: az aks nodepool delete-machines -g myResourceGroup --nodepool-name nodepool1 --cluster-name myAKSCluster --machine-names machine1
"""

helps['aks machine'] = """
   type: group
   short-summary: Get information about machines in a nodepool of a managed clusters
"""

helps['aks machine list'] = """
   type: command
   short-summary: Get information about IP Addresses, Hostname for all machines in an agentpool
   parameters:
       - name: --cluster-name
         type: string
         short-summary: Name of the managed cluster
       - name: --nodepool-name
         type: string
         short-summary: Name of the agentpool of a managed cluster
   exmaples:
       - name: Get information about IP Addresses, Hostname for all machines in an agentpool
         text: az aks machine list --cluster-name <clusterName> --nodepool-name <apName>
"""

helps['aks machine show'] = """
   type: command
   short-summary: Show IP Addresses, Hostname for a specific machine in an agentpool for a managedcluster.
   parameters:
       - name: --cluster-name
         type: string
         short-summary: Name of the managed cluster
       - name: --nodepool-name
         type: string
         short-summary: Name of the agentpool of a managed cluster
       - name: --machine-name
         type: string
         short-summary: Get IP Addresses, Hostname for a specific machine in an agentpool
   exmaples:
       - name: Get IP Addresses, Hostname for a specific machine in an agentpool
         text: az aks machine show --cluster-name <clusterName> --nodepool-name <apName> --machine-name <machineName>
"""

helps['aks operation-abort'] = """
    type: command
    short-summary: Abort last running operation on managed cluster.
    parameters:
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
    examples:
        - name: Abort operation on managed cluster
          text: az aks operation-abort -g myResourceGroup -n myAKSCluster
"""

helps['aks addon'] = """
    type: group
    short-summary: Commands to manage and view single addon conditions.
"""

helps['aks addon list-available'] = """
    type: command
    short-summary: List available Kubernetes addons.
"""

helps['aks addon list'] = """
    type: command
    short-summary: List status of all Kubernetes addons in given cluster.
"""

helps['aks addon show'] = """
    type: command
    short-summary: Show status and configuration for an enabled Kubernetes addon in a given cluster.
    parameters:
      - name: --addon -a
        type: string
        short-summary: Specify the Kubernetes addon.
    examples:
      - name: Show configuration for "monitoring" addon.
        text: az aks addon show -g myResourceGroup -n myAKSCluster -a monitoring
        crafted: true
"""

helps['aks addon disable'] = """
    type: command
    short-summary: Disable an enabled Kubernetes addon in a cluster.
    parameters:
      - name: --addon -a
        type: string
        short-summary: Specify the Kubernetes addon to disable.
    examples:
      - name: Disable the "monitoring" addon.
        text: az aks addon disable -g myResourceGroup -n myAKSCluster -a monitoring
        crafted: true
"""

helps['aks addon enable'] = """
type: command
short-summary: Enable a Kubernetes addon.
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
        azure-keyvault-secrets-provider - enable Azure Keyvault Secrets Provider addon.
        web_application_routing         - enable Web Application Routing addon (PREVIEW). Specify "--dns-zone-resource-id" to configure DNS.
parameters:
  - name: --addon -a
    type: string
    short-summary: Specify the Kubernetes addon to enable.
  - name: --workspace-resource-id
    type: string
    short-summary: The resource ID of an existing Log Analytics Workspace to use for storing monitoring data.
  - name: --enable-msi-auth-for-monitoring
    type: bool
    short-summary: Send monitoring data to Log Analytics using the cluster's assigned identity (instead of the Log Analytics Workspace's shared key).
  - name: --enable-syslog
    type: bool
    short-summary: Enable syslog data collection for Monitoring addon
  - name: --data-collection-settings
    type: string
    short-summary: Path to JSON file containing data collection settings for Monitoring addon.
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
  - name: --rotation-poll-interval
    type: string
    short-summary: Set interval of rotation poll. Use with azure-keyvault-secrets-provider addon.
  - name: --dns-zone-resource-id
    type: string
    short-summary: The resource ID of the DNS zone resource to use with the web_application_routing addon.
  - name: --dns-zone-resource-ids
    type: string
    short-summary: A comma separated list of resource IDs of the DNS zone resource to use with the web_application_routing addon.
examples:
  - name: Enable a Kubernetes addon. (autogenerated)
    text: az aks addon enable --addon virtual-node --name MyManagedCluster --resource-group MyResourceGroup --subnet-name VirtualNodeSubnet
    crafted: true
  - name: Enable ingress-appgw addon with subnet prefix.
    text: az aks addon enable --name MyManagedCluster --resource-group MyResourceGroup --addon ingress-appgw --appgw-subnet-cidr 10.2.0.0/16 --appgw-name gateway
    crafted: true
  - name: Enable open-service-mesh addon.
    text: az aks addon enable --name MyManagedCluster --resource-group MyResourceGroup -a open-service-mesh
    crafted: true
"""

helps['aks addon update'] = """
type: command
short-summary: Update an already enabled Kubernetes addon.
parameters:
  - name: --addon -a
    type: string
    short-summary: Specify the Kubernetes addon to update.
  - name: --workspace-resource-id
    type: string
    short-summary: The resource ID of an existing Log Analytics Workspace to use for storing monitoring data.
  - name: --enable-msi-auth-for-monitoring
    type: bool
    short-summary: Send monitoring data to Log Analytics using the cluster's assigned identity (instead of the Log Analytics Workspace's shared key).
  - name: --enable-syslog
    type: bool
    short-summary: Enable syslog data collection for Monitoring addon
  - name: --data-collection-settings
    type: string
    short-summary: Path to JSON file containing data collection settings for Monitoring addon.
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
  - name: --rotation-poll-interval
    type: string
    short-summary: Set interval of rotation poll. Use with azure-keyvault-secrets-provider addon.
  - name: --dns-zone-resource-id
    type: string
    short-summary: The resource ID of the DNS zone resource to use with the web_application_routing addon.
  - name: --dns-zone-resource-ids
    type: string
    short-summary: A comma separated list of resource IDs of the DNS zone resource to use with the web_application_routing addon.
examples:
  - name: Update a Kubernetes addon. (autogenerated)
    text: az aks addon update --addon virtual-node --name MyManagedCluster --resource-group MyResourceGroup --subnet-name VirtualNodeSubnet
    crafted: true
  - name: Update ingress-appgw addon with subnet prefix.
    text: az aks addon update --name MyManagedCluster --resource-group MyResourceGroup --addon ingress-appgw --appgw-subnet-cidr 10.2.0.0/16 --appgw-name gateway
    crafted: true
  - name: Update monitoring addon with workspace resource id.
    text: az aks addon update -g $rg -n $cn -a monitoring --workspace-resource-id=/subscriptions/0000000-00000000-00000-000-000/resourcegroups/myresourcegroup/providers/microsoft.operationalinsights/workspaces/defaultlaworkspace
    crafted: true
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
        azure-keyvault-secrets-provider - enable Azure Keyvault Secrets Provider addon.
        web_application_routing         - enable Web Application Routing addon (PREVIEW). Specify "--dns-zone-resource-id" to configure DNS.
parameters:
  - name: --addons -a
    type: string
    short-summary: Enable the Kubernetes addons in a comma-separated list.
  - name: --workspace-resource-id
    type: string
    short-summary: The resource ID of an existing Log Analytics Workspace to use for storing monitoring data.
  - name: --enable-msi-auth-for-monitoring
    type: bool
    short-summary: Send monitoring data to Log Analytics using the cluster's assigned identity (instead of the Log Analytics Workspace's shared key).
  - name: --enable-syslog
    type: bool
    short-summary: Enable syslog data collection for Monitoring addon
  - name: --data-collection-settings
    type: string
    short-summary: Path to JSON file containing data collection settings for Monitoring addon.
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
  - name: --rotation-poll-interval
    type: string
    short-summary: Set interval of rotation poll. Use with azure-keyvault-secrets-provider addon.
  - name: --dns-zone-resource-id
    type: string
    short-summary: The resource ID of the DNS zone resource to use with the web_application_routing addon.
  - name: --dns-zone-resource-ids
    type: string
    short-summary: A comma separated list of resource IDs of the DNS zone resource to use with the web_application_routing addon.
  - name: --aks-custom-headers
    type: string
    short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
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

helps['aks show'] = """
type: command
short-summary: Show the details for a managed Kubernetes cluster.
parameters:
  - name: --aks-custom-headers
    type: string
    short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
examples:
  - name: Show the details for a managed Kubernetes cluster
    text: az aks show -g MyResourceGroup -n MyManagedCluster
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
    short-summary: Get private cluster credential with server address to be public fqdn.
  - name: --format
    type: string
    short-summary: Specify the format of the returned credential. Available values are ["exec", "azure"].
                  Only take effect when requesting clusterUser credential of AAD clusters.
  - name: --aks-custom-headers
    type: string
    short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2
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

helps['aks snapshot'] = """
    type: group
    short-summary: Commands to manage cluster snapshots.
"""

helps['aks snapshot show'] = """
    type: command
    short-summary: Show the details of a cluster snapshot.
"""

helps['aks snapshot list'] = """
    type: command
    short-summary: List cluster snapshots.
"""

helps['aks snapshot create'] = """
    type: command
    short-summary: Create a snapshot of a cluster.
    parameters:
        - name: --cluster-id
          type: string
          short-summary: The source cluster id from which to create this snapshot.
        - name: --tags
          type: string
          short-summary: The tags of the snapshot.
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2

    examples:
        - name: Create a cluster snapshot.
          text: az aks snapshot create -g MyResourceGroup -n snapshot1 --cluster-id "/subscriptions/00000/resourceGroups/AnotherResourceGroup/providers/Microsoft.ContainerService/managedClusters/akscluster1"
        - name: Create a cluster snapshot with custom tags.
          text: az aks snapshot create -g MyResourceGroup -n snapshot1 --cluster-id "/subscriptions/00000/resourceGroups/AnotherResourceGroup/providers/Microsoft.ContainerService/managedClusters/akscluster1" --tags "foo=bar" "key1=val1"
"""

helps['aks snapshot delete'] = """
    type: command
    short-summary: Delete a cluster snapshot.
"""

helps['aks nodepool snapshot'] = """
    type: group
    short-summary: Commands to manage nodepool snapshots.
"""

helps['aks nodepool snapshot show'] = """
    type: command
    short-summary: Show the details of a nodepool snapshot.
"""

helps['aks nodepool snapshot list'] = """
    type: command
    short-summary: List nodepool snapshots.
"""

helps['aks nodepool snapshot update'] = """
    type: command
    short-summary: Update tags on a snapshot of a nodepool.

    examples:
        - name: Update tags on a nodepool snapshot.
          text: az aks nodepool snapshot update -g MyResourceGroup -n snapshot1 --tags "foo=bar" "key1=val1"
        - name: Clear tags on a nodepool snapshot.
          text: az aks nodepool snapshot update -g MyResourceGroup -n snapshot1 --tags ""
"""

helps['aks nodepool snapshot create'] = """
    type: command
    short-summary: Create a nodepool snapshot.
    parameters:
        - name: --nodepool-id
          type: string
          short-summary: The source nodepool id from which to create this snapshot.
        - name: --tags
          type: string
          short-summary: The tags of the snapshot.
        - name: --aks-custom-headers
          type: string
          short-summary: Send custom headers. When specified, format should be Key1=Value1,Key2=Value2

    examples:
        - name: Create a nodepool snapshot.
          text: az aks nodepool snapshot create -g MyResourceGroup -n snapshot1 --nodepool-id "/subscriptions/00000/resourceGroups/AnotherResourceGroup/providers/Microsoft.ContainerService/managedClusters/akscluster1/agentPools/nodepool1"
        - name: Create a nodepool snapshot with custom tags.
          text: az aks nodepool snapshot create -g MyResourceGroup -n snapshot1 --nodepool-id "/subscriptions/00000/resourceGroups/AnotherResourceGroup/providers/Microsoft.ContainerService/managedClusters/akscluster1/agentPools/nodepool1" --tags "foo=bar" "key1=val1"
"""

helps['aks nodepool snapshot delete'] = """
    type: command
    short-summary: Delete a nodepool snapshot.
"""

helps['aks trustedaccess'] = """
    type: group
    short-summary: Commands to manage trusted access security features.
"""

helps['aks trustedaccess role'] = """
    type: group
    short-summary: Commands to manage trusted access roles.
"""

helps['aks trustedaccess role list'] = """
    type: command
    short-summary: List trusted access roles.
"""

helps['aks trustedaccess rolebinding'] = """
    type: group
    short-summary: Commands to manage trusted access role bindings.
"""

helps['aks trustedaccess rolebinding list'] = """
    type: command
    short-summary: List all the trusted access role bindings.
"""

helps['aks trustedaccess rolebinding show'] = """
    type: command
    short-summary: Get the specific trusted access role binding according to binding name.
    parameters:
        - name: --name -n
          type: string
          short-summary: Specify the role binding name.
"""

helps['aks trustedaccess rolebinding create'] = """
    type: command
    short-summary: Create a new trusted access role binding.
    parameters:
        - name: --name -n
          type: string
          short-summary: Specify the role binding name.
        - name: --roles
          type: string
          short-summary: Specify the space-separated roles.
        - name: --source-resource-id
          type: string
          short-summary: Specify the source resource id of the binding.

    examples:
        - name: Create a new trusted access role binding
          text: az aks trustedaccess rolebinding create -g myResourceGroup --cluster-name myCluster -n bindingName --source-resource-id /subscriptions/0000/resourceGroups/myResourceGroup/providers/Microsoft.Demo/samples --roles Microsoft.Demo/samples/reader,Microsoft.Demo/samples/writer
"""

helps['aks trustedaccess rolebinding update'] = """
    type: command
    short-summary: Update a trusted access role binding.
    parameters:
        - name: --name -n
          type: string
          short-summary: Specify the role binding name.
        - name: --roles
          type: string
          short-summary: Specify the space-separated roles.
"""

helps['aks trustedaccess rolebinding delete'] = """
    type: command
    short-summary: Delete a trusted access role binding according to name.
    parameters:
        - name: --name -n
          type: string
          short-summary: Specify the role binding name.
"""

helps['aks draft'] = """
    type: group
    short-summary: Commands to build deployment files in a project directory and deploy to an AKS cluster.
"""

helps['aks draft create'] = """
    type: command
    short-summary: Generate a Dockerfile and the minimum required Kubernetes deployment files (helm, kustomize, manifests) for your project directory.
    parameters:
        - name: --destination
          type: string
          short-summary: Specify the path to the project directory (default is .).
        - name: --app
          type: string
          short-summary: Specify the name of the helm release.
        - name: --language
          type: string
          short-summary: Specify the language used to create the Kubernetes deployment.
        - name: --create-config
          type: string
          short-summary: Specify the path to the configuration file.
        - name: --dockerfile-only
          type: bool
          short-summary: Only generate Dockerfile for the Kubernetes deployment.
        - name: --deployment-only
          type: bool
          short-summary: Only generate deployment files (helm, kustomize, manifests) for the Kubernetes deployment.
        - name: --path
          type: string
          short-summary: Automatically download and use the Draft binary at the specified location.
    examples:
      - name: Prompt to generate a Dockerfile and deployment files in the current directory.
        text: az aks draft create
      - name: Generate only the Dockerfile in the current directory.
        text: az aks draft create --dockerfile-only=true
      - name: Generate only the deployment files in the current directory.
        text: az aks draft create --deployment-only=true
      - name: Generate a Dockerfile and an deployment file in a Java project with an app name at a specific project directory.
        text: az aks draft create --language=java --app=some_app --destination=/projects/some_project
"""

helps['aks draft setup-gh'] = """
    type: command
    short-summary: Set up GitHub OIDC for your application
    parameters:
        - name: --app
          type: string
          short-summary: Specify the Azure Active Directory applicaton name.
        - name: --subscription-id
          type: string
          short-summary: Specify the Azure subscription ID.
        - name: --resource-group
          type: string
          short-summary: Specify the name of the Azure resource group.
        - name: --provider
          type: string
          short-summary: Specify the cloud provider (default is azure).
        - name: --gh-repo
          type: string
          short-summary: Specify the the GitHub repository (organization/repo_name).
        - name: --path
          type: string
          short-summary: Automatically download and use the Draft binary at the specified location.
    examples:
      - name: Prompt to setup the GitHub OIDC for a repository.
        text: az aks draft setup-gh
      - name: Setup the GitHub OIDC on Azure for a specific repository.
        text: az aks draft setup-gh --provider=azure --gh-repo=some_organization/some_repo
      - name: Setup the GitHub OIDC on Azure with subscription ID and resource group.
        text: az aks draft setup-gh --provider=azure --subscription-id=some_subscription --resource-group=some_rg
      - name: Setup the GitHub OIDC with an application name on Azure with subscription ID and resource group for a specific repository.
        text: az aks draft setup-gh --app=some_app --provider=azure --subscription-id=some_subscription --resource-group=some_rg --gh-repo=some_organization/some_repo
"""

helps['aks draft generate-workflow'] = """
    type: command
    short-summary: Generate a GitHub workflow for automatic build and deploy to AKS
    long-summary: Before running this command, Make sure you have set up GitHub OIDC for your application.
                  You also need to create a resource group, a container registry and a Kubernetes cluster on Azure and
                  link the three resources using `az aks update -n <cluster-name> -g <resource-group-name> --attach-acr <acr-name>`.
    parameters:
        - name: --resource-group
          type: string
          short-summary: Specify the name of the Azure resource group.
        - name: --destination
          type: string
          short-summary: Specify the path to the project directory (default is .).
        - name: --cluster-name
          type: string
          short-summary: Specify the AKS cluster name.
        - name: --registry-name
          type: string
          short-summary: Specify the path to the project directory.
        - name: --container-name
          type: string
          short-summary: Specify the name of the container image.
        - name: --branch
          type: string
          short-summary: Specify the GitHub branch to automatically deploy from.
        - name: --path
          type: string
          short-summary: Automatically download and use the Draft binary at the specified location.
    examples:
      - name: Prompt to generate a GitHub workflow in the current directory.
        text: az aks draft generate-workflow
      - name: Prompt to generate a GitHub workflow in a specific project directory.
        text: az aks draft generate-workflow --destination=/projects/some_project
      - name: Generate a GitHub workflow with a resource group, an AKS cluster name, a container registry name in a specific project directory.
        text: az aks draft generate-workflow --resource-group=some_rg --cluster-name=some_cluster --registry-name=some_registry --destination=/projects/some_project
      - name: Generate a GitHub workflow that deploys from the main branch with a resource group, an AKS cluster name, a container registry name, and a container image name in a specific project directory.
        text: az aks draft generate-workflow --branch=main --resource-group=some_rg --cluster-name=some_cluster --registry-name=some_registry --container-name=some_image --destination=/projects/some_project
"""

helps['aks draft up'] = """
    type: command
    short-summary: Set up GitHub OIDC and generate a GitHub workflow for automatic build and deploy to AKS
    long-summary: This command combines `az aks draft setup-gh` and `az aks draft generate-workflow`.
                  Before running this command, create a resource group, a container registry and a Kubernetes cluster on Azure and
                  link the three resources using `az aks update -n <cluster-name> -g <resource-group-name> --attach-acr <acr-name>`.
    parameters:
        - name: --app
          type: string
          short-summary: Specify the name of the application.
        - name: --subscription-id
          type: string
          short-summary: Specify the Azure subscription ID.
        - name: --resource-group
          type: string
          short-summary: Specify the name of the Azure resource group.
        - name: --provider
          type: string
          short-summary: Specify the cloud provider (default is azure).
        - name: --gh-repo
          type: string
          short-summary: Specify the the GitHub repository (organization/repo_name).
        - name: --cluster-name
          type: string
          short-summary: Specify the AKS cluster name.
        - name: --registry-name
          type: string
          short-summary: Specify the path to the project directory.
        - name: --container-name
          type: string
          short-summary: Specify the name of the container image.
        - name: --destination
          type: string
          short-summary: Specify the path to the project directory (default is .).
        - name: --branch
          type: string
          short-summary: Specify the GitHub branch to automatically deploy from.
        - name: --path
          type: string
          short-summary: Automatically download and use the Draft binary at the specified location.
    examples:
      - name: Prompt to setup the GitHub OIDC then generate a GitHub workflow in the current directory.
        text: az aks draft up
      - name: Prompt to setup the GitHub OIDC then generate a GitHub workflow in a specific project directory.
        text: az aks draft up --destination=/projects/some_project
      - name: Prompt to setup the GitHub OIDC for a specific repository then generate a GitHub workflow in a specific project directory.
        text: az aks draft up --gh-repo=some_organization/some_repo --destination=/projects/some_project
"""

helps['aks draft update'] = """
    type: command
    short-summary: Update your application to be internet accessible.
    long-summary: This command automatically updates your yaml files as necessary so that your
                  application will be able to receive external requests.
    parameters:
        - name: --host
          type: string
          short-summary: Specify the host of the ingress resource.
        - name: --certificate
          type: string
          short-summary: Specify the URI of the Keyvault certificate to present.
        - name: --destination
          type: string
          short-summary: Specify the path to the project directory (default is .).
        - name: --path
          type: string
          short-summary: Automatically download and use the Draft binary at the specified location.
    examples:
      - name: Prompt to update the application to be internet accessible.
        text: az aks draft update
      - name: Prompt to update the application to be internet accessible in a specific project directory.
        text: az aks draft update --destination=/projects/some_project
      - name: Update the application to be internet accessible with a host of the ingress resource and a Keyvault certificate in a specific project directory.
        text: az aks draft update --host=some_host --certificate=some_certificate --destination=/projects/some_project
"""

helps['aks mesh'] = """
    type: group
    short-summary: Commands to manage Azure Service Mesh.
    long-summary: A group of commands to manage Azure Service Mesh in given cluster.
"""

helps['aks mesh enable'] = """
    type: command
    short-summary: Enable Azure Service Mesh.
    long-summary: This command enables Azure Service Mesh in given cluster.
    parameters:
      - name: --revision
        type: string
        short-summary: Azure Service Mesh revision to install.
      - name: --key-vault-id
        type: string
        short-summary: The Azure Keyvault id with plugin CA info.
      - name: --ca-cert-object-name
        type: string
        short-summary: Intermediate cert object name in the Azure Keyvault.
      - name: --ca-key-object-name
        type: string
        short-summary: Intermediate key object name in the Azure Keyvault.
      - name: --cert-chain-object-name
        type: string
        short-summary: Cert chain object name in the Azure Keyvault.
      - name: --root-cert-object-name
        type: string
        short-summary: Root cert object name in the Azure Keyvault.
    examples:
      - name: Enable Azure Service Mesh with selfsigned CA.
        text: az aks mesh enable --resource-group MyResourceGroup --name MyManagedCluster
      - name: Enable Azure Service Mesh with plugin CA.
        text: az aks mesh enable --resource-group MyResourceGroup --name MyManagedCluster --key-vault-id /subscriptions/8ecadfc9-d1a3-4ea4-b844-0d9f87e4d7c8/resourceGroups/foo/providers/Microsoft.KeyVault/vaults/foo --ca-cert-object-name my-ca-cert --ca-key-object-name my-ca-key --cert-chain-object-name my-cert-chain --root-cert-object-name my-root-cert

"""

helps['aks mesh disable'] = """
    type: command
    short-summary: Disable Azure Service Mesh.
    long-summary: This command disables Azure Service Mesh in given cluster.
"""

helps['aks mesh enable-ingress-gateway'] = """
    type: command
    short-summary: Enable an Azure Service Mesh ingress gateway.
    long-summary: This command enables an Azure Service Mesh ingress gateway in given cluster.
    parameters:
      - name: --ingress-gateway-type
        type: string
        short-summary: Specify the type of ingress gateway.
        long-summary: Allowed values are "External" which is backed by a load balancer with an external IP address; "Internal" which is backed by a load balancer with an internal IP address.
    examples:
      - name: Enable an internal ingress gateway.
        text: az aks mesh enable-ingress-gateway --resource-group MyResourceGroup --name MyManagedCluster --ingress-gateway-type Internal
"""

helps['aks mesh disable-ingress-gateway'] = """
    type: command
    short-summary: Disable an Azure Service Mesh ingress gateway.
    long-summary: This command disables an Azure Service Mesh ingress gateway in given cluster.
    parameters:
      - name: --ingress-gateway-type
        type: string
        short-summary: Specify the type of ingress gateway.
        long-summary: Allowed values are "External" which is backed by a load balancer with an external IP address, "Internal" which is backed by a load balancer with an internal IP address.
    examples:
      - name: Disable an internal ingress gateway.
        text: az aks mesh disable-ingress-gateway --resource-group MyResourceGroup --name MyManagedCluster --ingress-gateway-type Internal
"""

helps['aks mesh get-revisions'] = """
    type: command
    short-summary: Discover available Azure Service Mesh revisions and their compatibility.
    long-summary: This command discovers available Azure Service Mesh revisions and their compatibility information for the given location.
    examples:
      - name: Discover Azure Service Mesh revisions.
        text: az aks mesh get-revisions --location westus2
        crafted: true
"""

helps['aks mesh get-upgrades'] = """
    type: command
    short-summary: Discover available Azure Service Mesh upgrades.
    long-summary: This command discovers available Azure Service Mesh upgrades for the mesh revision installed on the cluster.
    examples:
      - name: Discover Azure Service Mesh upgrades.
        text: az aks mesh get-upgrades --resource-group MyResourceGroup --name MyManagedCluster
"""

helps['aks mesh upgrade start'] = """
    type: command
    short-summary: Initiate Azure Service Mesh upgrade.
    long-summary: This command initiates upgrade of Azure Service Mesh to the specified revision.
    parameters:
      - name: --revision
        type: string
        short-summary: Azure Service Mesh revision to upgrade to.
    examples:
      - name: Initiate Azure Service Mesh upgrade.
        text: az aks mesh upgrade start --resource-group MyResourceGroup --name MyManagedCluster --revision asm-1-18
"""

helps['aks mesh upgrade'] = """
    type: group
    short-summary: Commands to manage the upgrades for Azure Service Mesh.
    long-summary: A group of commands to manage the upgrades for Azure Service Mesh in given cluster.
"""

helps['aks mesh upgrade complete'] = """
    type: command
    short-summary: Complete Azure Service Mesh upgrade.
    long-summary: This command completes Azure Service Mesh canary upgrade by removing the previous revision.
    examples:
      - name: Complete Azure Service Mesh upgrade.
        text: az aks mesh upgrade complete --resource-group MyResourceGroup --name MyManagedCluster
"""

helps['aks mesh upgrade rollback'] = """
    type: command
    short-summary: Rollback Azure Service Mesh upgrade.
    long-summary: This command rolls back Azure Service Mesh upgrade to the previous stable revision.
    examples:
      - name: Rollback Azure Service Mesh upgrade.
        text: az aks mesh upgrade rollback --resource-group MyResourceGroup --name MyManagedCluster
"""

helps['aks mesh enable-egress-gateway'] = """
    type: command
    short-summary: Enable an Azure Service Mesh egress gateway.
    long-summary: This command enables an Azure Service Mesh egress gateway in given cluster.
    examples:
      - name: Enable an egress gateway.
        text: az aks mesh enable-egress-gateway --resource-group MyResourceGroup --name MyManagedCluster
"""

helps['aks mesh disable-egress-gateway'] = """
    type: command
    short-summary: Disable an Azure Service Mesh egress gateway.
    long-summary: This command disables an Azure Service Mesh egress gateway in given cluster.
    examples:
      - name: Disable an egress gateway.
        text: az aks mesh disable-egress-gateway --resource-group MyResourceGroup --name MyManagedCluster
"""

helps['aks approuting'] = """
    type: group
    short-summary: Commands to manage App Routing aadon.
    long-summary: A group of commands to manage App Routing in given cluster.
"""

helps['aks approuting enable'] = """
    type: command
    short-summary: Enable App Routing.
    long-summary: This command enables App Routing in given cluster.
    parameters:
      - name: --enable-kv
        type: bool
        short-summary: Enable the keyvault secrets provider.
        long-summary: This optional flag enables the keyvault-secrets-provider addon in given cluster. This is required for most App Routing use-cases.
      - name: --attach-kv
        type: string
        short-summary: Attach a keyvault id to access secrets and certificates.
        long-summary: This optional flag attaches a keyvault id to access secrets and certificates.
"""

helps['aks approuting disable'] = """
    type: command
    short-summary: Disable App Routing addon.
    long-summary: This command disables App Routing in given cluster.
"""

helps['aks approuting update'] = """
    type: command
    short-summary: Update App Routing addon.
    long-summary: This command is used to update keyvault id in App Routing addon.
    parameters:
      - name: --attach-kv
        type: string
        short-summary: Attach a keyvault id to access secrets and certificates.
        long-summary: This optional flag attaches a keyvault id to access secrets and certificates.
      - name: --enable-kv
        type: bool
        short-summary: Enable the keyvault secrets provider addon.
        long-summary: This optional flag enables the keyvault-secrets-provider addon in given cluster. This is required for most App Routing use-cases.
"""

helps['aks approuting zone'] = """
    type: group
    short-summary: Commands to manage App Routing DNS Zones.
    long-summary: A group of commands to manage App Routing DNS zones in given cluster.
"""

helps['aks approuting zone add'] = """
    type: command
    short-summary: Add DNS Zone(s) to App Routing.
    long-summary: This command adds multiple DNS zone resource IDs to App Routing.
    parameters:
      - name: --ids
        type: string
        short-summary: Comma-separated list of DNS zone resource IDs to add to App Routing.
      - name: --attach-zones
        type: bool
        short-summary: Grant DNS zone Contributor permissions on all zone IDs specified in --ids.
"""

helps['aks approuting zone delete'] = """
    type: command
    short-summary: Delete DNS Zone(s) from App Routing.
    long-summary: This command deletes DNS zone resource IDs from App Routing in given cluster.
    parameters:
      - name: --ids
        type: string
        short-summary: Comma-separated list of DNS zone resource IDs to delete from App Routing.
"""

helps['aks approuting zone update'] = """
    type: command
    short-summary: Replace DNS Zone(s) in App Routing.
    long-summary: This command replaces the DNS zone resource IDs used in App Routing.
    parameters:
      - name: --ids
        type: string
        short-summary: Comma-separated list of DNS zone resource IDs to replace in App Routing.
      - name: --attach-zones
        type: bool
        short-summary: Grant DNS zone Contributor permissions on all zone IDs specified in --ids.
"""

helps['aks approuting zone list'] = """
    type: command
    short-summary: List DNS Zone IDs in App Routing.
    long-summary: This command lists the DNS zone resources used in App Routing.
"""

helps['aks check-network'] = """
    type: group
    short-summary: Commands to troubleshoot network connectivity in managed Kubernetes cluster.
"""

helps['aks check-network outbound'] = """
    type: command
    short-summary: Perform outbound network connectivity check for a node in a managed Kubernetes cluster.
    long-summary: This command checks outbound network connectivity from a node to certain required AKS endpoints.
    parameters:
      - name: --name -n
        type: string
        short-summary: Name of the managed cluster.
      - name: --resource-group -g
        type: string
        short-summary: Name of the resource group.
      - name: --node-name
        type: string
        short-summary: Name of the node to perform the connectivity check. If not specified, a random node will be chosen.
      - name: --custom-endpoints
        type: string
        short-summary: Additional endpoint(s) to perform the connectivity check, separated by comma.
"""
