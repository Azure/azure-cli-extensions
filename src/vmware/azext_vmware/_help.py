# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['vmware'] = """
    type: group
    short-summary: Commands to manage Azure VMware Solution.
"""

helps['vmware addon'] = """
    type: group
    short-summary: Commands to manage addons for a private cloud.
"""

helps['vmware addon hcx'] = """
    type: group
    short-summary: Commands to manage a HCX addon.
"""

helps['vmware addon srm'] = """
    type: group
    short-summary: Commands to manage a Site Recovery Manager (SRM) addon.
"""

helps['vmware addon vr'] = """
    type: group
    short-summary: Commands to manage a vSphere Replication (VR) addon.
"""

helps['vmware addon arc'] = """
    type: group
    short-summary: Commands to manage a Arc addon.
"""

helps['vmware private-cloud'] = """
    type: group
    short-summary: Commands to manage private clouds.
"""

helps['vmware cluster'] = """
    type: group
    short-summary: Commands to manage all the clusters in a private cloud, excluding the first cluster which is the default management cluster. The default management cluster is created and managed as part of the private cloud. For management cluster commands, use az vmware private-cloud.
"""

helps['vmware authorization'] = """
    type: group
    short-summary: Commands to manage the authorizations of an ExpressRoute Circuit for a private cloud.
"""

helps['vmware hcx-enterprise-site'] = """
    type: group
    short-summary: Commands to manage HCX Enterprise Sites in a private cloud.
"""

helps['vmware location'] = """
    type: group
    short-summary: Commands to check availability by location.
"""

helps['vmware datastore'] = """
    type: group
    short-summary: Commands to manage a datastore in a private cloud cluster.
"""

helps['vmware cluster create'] = """
    type: command
    short-summary: Create a cluster in a private cloud. The maximum number of clusters is 4.
"""

helps['vmware cluster delete'] = """
    type: command
    short-summary: Delete a cluster in a private cloud, excluding the first cluster which is the default management cluster. The default management cluster is created and managed as part of the private cloud. To delete the management cluster, use az vmware private-cloud delete.
"""

helps['vmware cluster list'] = """
    type: command
    short-summary: List clusters in a private cloud, excluding the first cluster which is the default management cluster. The default management cluster is created and managed as part of the private cloud. To view details of the management cluster, use az vmware private-cloud show.
"""

helps['vmware cluster show'] = """
    type: command
    short-summary: Show details of a cluster in a private cloud, excluding the first cluster which is the default management cluster. The default management cluster is created and managed as part of the private cloud. To view details of the management cluster, use az vmware private-cloud show.
"""

helps['vmware cluster update'] = """
    type: command
    short-summary: Update a cluster in a private cloud, excluding the first cluster which is the default management cluster. The default management cluster is created and managed as part of the private cloud. To update details of the management cluster, use az vmware private-cloud update.
"""

helps['vmware cluster list-zones'] = """
    type: command
    short-summary: List hosts by zone in a cluster in a private cloud, including the first cluster which is the default management cluster. The default management cluster is created and managed as part of the private cloud.
"""

helps['vmware private-cloud add-identity-source'] = """
    type: command
    short-summary: Add a vCenter Single Sign On Identity Source to a private cloud.
"""

helps['vmware private-cloud addidentitysource'] = """
    type: command
    short-summary: Add a vCenter Single Sign On Identity Source to a private cloud.
"""

helps['vmware private-cloud add-cmk-encryption'] = """
    type: command
    short-summary: Add a Customer Managed Keys Encryption to a private cloud.
"""

helps['vmware private-cloud delete-cmk-encryption'] = """
    type: command
    short-summary: Delete a Customer Managed Keys Encryption from a private cloud.
"""

helps['vmware private-cloud enable-cmk-encryption'] = """
    type: command
    short-summary: Enable a Customer Managed Keys Encryption to a private cloud.
"""

helps['vmware private-cloud disable-cmk-encryption'] = """
    type: command
    short-summary: Disable a Customer Managed Keys Encryption from a private cloud.
"""

helps['vmware private-cloud identity'] = """
    type: group
    short-summary: Commands for Managed Identity in a private cloud.
"""

helps['vmware private-cloud identity assign'] = """
    type: command
    short-summary: Assign a Managed Identity in a private cloud.
"""

helps['vmware private-cloud identity remove'] = """
    type: command
    short-summary: Remove a Managed Identity in a private cloud.
"""

helps['vmware private-cloud identity show'] = """
    type: command
    short-summary: Show Managed Identities in a private cloud.
"""

helps['vmware private-cloud create'] = """
    type: command
    short-summary: Create a private cloud.
"""

helps['vmware private-cloud delete'] = """
    type: command
    short-summary: Delete a private cloud.
"""

helps['vmware private-cloud delete-identity-source'] = """
    type: command
    short-summary: Delete a vCenter Single Sign On Identity Source for a private cloud.
"""

helps['vmware private-cloud deleteidentitysource'] = """
    type: command
    short-summary: Delete a vCenter Single Sign On Identity Source for a private cloud.
"""

helps['vmware private-cloud list'] = """
    type: command
    short-summary: List the private clouds.
"""

helps['vmware private-cloud list-admin-credentials'] = """
    type: command
    short-summary: List the admin credentials for the private cloud.
"""

helps['vmware private-cloud listadmincredentials'] = """
    type: command
    short-summary: List the admin credentials for the private cloud.
"""

helps['vmware private-cloud show'] = """
    type: command
    short-summary: Show details of a private cloud.
"""

helps['vmware private-cloud update'] = """
    type: command
    short-summary: Update a private cloud.
"""

helps['vmware private-cloud rotate-vcenter-password'] = """
    type: command
    short-summary: Rotate the vCenter password.
    examples:
    - name: Rotate the vCenter password.
      text: az vmware private-cloud rotate-vcenter-password --resource-group MyResourceGroup --private-cloud MyPrivateCloud
"""

helps['vmware private-cloud rotate-nsxt-password'] = """
    type: command
    short-summary: Rotate the NSX-T Manager password.
    examples:
    - name: Rotate the NSX-T Manager password.
      text: az vmware private-cloud rotate-nsxt-password
"""

helps['vmware authorization create'] = """
    type: command
    short-summary: Create an authorization for an ExpressRoute Circuit in a private cloud.
"""

helps['vmware authorization list'] = """
    type: command
    short-summary: List authorizations for an ExpressRoute Circuit in a private cloud.
"""

helps['vmware authorization show'] = """
    type: command
    short-summary: Show details of an authorization for an ExpressRoute Circuit in a private cloud.
"""

helps['vmware authorization delete'] = """
    type: command
    short-summary: Delete an authorization for an ExpressRoute Circuit in a private cloud.
"""

helps['vmware hcx-enterprise-site create'] = """
    type: command
    short-summary: Create an HCX Enterprise Site in a private cloud.
"""

helps['vmware hcx-enterprise-site list'] = """
    type: command
    short-summary: List HCX Enterprise Sites in a private cloud.
"""

helps['vmware hcx-enterprise-site show'] = """
    type: command
    short-summary: Show details of an HCX Enterprise Site in a private cloud.
"""

helps['vmware hcx-enterprise-site delete'] = """
    type: command
    short-summary: Delete an HCX Enterprise Site in a private cloud.
"""

helps['vmware location checkquotaavailability'] = """
    type: command
    short-summary: Return quota for subscription by region.
"""
helps['vmware location check-quota-availability'] = """
    type: command
    short-summary: Return quota for subscription by region.
"""

helps['vmware location checktrialavailability'] = """
    type: command
    short-summary: Return trial status for subscription by region.
"""

helps['vmware location check-trial-availability'] = """
    type: command
    short-summary: Return trial status for subscription by region.
"""

helps['vmware datastore create'] = """
    type: command
    short-summary: Please use "netapp-volume create" or "disk-pool-volume create" instead.
"""

helps['vmware datastore netapp-volume'] = """
    type: group
    short-summary: Create a new Microsoft.NetApp provided NetApp volume in a private cloud cluster.
"""

helps['vmware datastore netapp-volume create'] = """
    type: command
    short-summary: Create a new Microsoft.NetApp provided NetApp volume in a private cloud cluster.
    examples:
    - name: Create a new Microsoft.NetApp provided NetApp volume based NFSv3 datastore.
      text: az vmware datastore netapp-volume create --name ANFDatastore1 --resource-group MyResourceGroup --cluster Cluster-1 --private-cloud MyPrivateCloud --volume-id /subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/ResourceGroup1/providers/Microsoft.NetApp/netAppAccounts/NetAppAccount1/capacityPools/CapacityPool1/volumes/NFSVol1
"""

helps['vmware datastore disk-pool-volume'] = """
    type: group
    short-summary: Create a VMFS datastore in a private cloud cluster using Microsoft.StoragePool provided iSCSI target.
"""

helps['vmware datastore disk-pool-volume create'] = """
    type: command
    short-summary: Create a VMFS datastore in a private cloud cluster using Microsoft.StoragePool provided iSCSI target.
    examples:
    - name: Create a new Microsoft.StoragePool provided disk pool based iSCSI datastore.
      text: az vmware datastore disk-pool-volume create --name iSCSIDatastore1 --resource-group MyResourceGroup --cluster Cluster-1 --private-cloud MyPrivateCloud --target-id /subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/ResourceGroup1/providers/Microsoft.StoragePool/diskPools/mpio-diskpool/iscsiTargets/mpio-iscsi-target --lun-name lun0
"""

helps['vmware datastore show'] = """
    type: command
    short-summary: Show details of a datastore in a private cloud cluster.
    examples:
    - name: Show the details of an iSCSI or NFS based datastore.
      text: az vmware datastore show --name MyCloudSANDatastore1 --resource-group MyResourceGroup --cluster Cluster-1 --private-cloud MyPrivateCloud
"""

helps['vmware datastore list'] = """
    type: command
    short-summary: List datastores in a private cloud cluster.
    examples:
    - name: List all iSCSI or NFS based datastores under Cluster-1.
      text: az vmware datastore list --resource-group MyResourceGroup --cluster Cluster-1 --private-cloud MyPrivateCloud
"""

helps['vmware datastore delete'] = """
    type: command
    short-summary: Delete a datastore in a private cloud cluster.
    examples:
    - name: Delete an iSCSI or NFS based datastore.
      text: az vmware datastore delete --name MyCloudSANDatastore1 --resource-group MyResourceGroup --cluster Cluster-1 --private-cloud MyPrivateCloud
"""

helps['vmware addon list'] = """
    type: command
    short-summary: List addons in a private cloud.
    examples:
    - name: List addons in a private cloud.
      text: az vmware addon list --resource-group MyResourceGroup --private-cloud MyPrivateCloud
"""

helps['vmware addon vr create'] = """
    type: command
    short-summary: Create a vSphere Replication (VR) addon for a private cloud.
    examples:
    - name: Create a vSphere Replication (VR) addon.
      text: az vmware addon vr create --resource-group MyResourceGroup --private-cloud MyPrivateCloud --vrs-count 1
"""

helps['vmware addon hcx create'] = """
    type: command
    short-summary: Create a HCX addon for a private cloud.
    examples:
    - name: Create a HCX addon.
      text: az vmware addon hcx create --resource-group MyResourceGroup --private-cloud MyPrivateCloud --offer "VMware MaaS Cloud Provider (Enterprise)"
"""

helps['vmware addon srm create'] = """
    type: command
    short-summary: Create a Site Recovery Manager (SRM) addon for a private cloud.
    examples:
    - name: Create a Site Recovery Manager (SRM) addon.
      text: az vmware addon srm create --resource-group MyResourceGroup --private-cloud MyPrivateCloud --license-key "41915-178A8-FF4A4-DB683-6D735"
"""

helps['vmware addon arc create'] = """
    type: command
    short-summary: Create an Arc addon for a private cloud.
    examples:
    - name: Create an Arc addon.
      text: az vmware addon arc create --resource-group MyResourceGroup --private-cloud MyPrivateCloud --vcenter "00000000-0000-0000-0000-000000000000"
"""

helps['vmware addon vr show'] = """
    type: command
    short-summary: Show details of a vSphere Replication (VR) addon for a private cloud.
    examples:
    - name: Show details of a vSphere Replication (VR) addon.
      text: az vmware addon vr show --resource-group MyResourceGroup --private-cloud MyPrivateCloud
"""

helps['vmware addon hcx show'] = """
    type: command
    short-summary: Show details of a HCX addon for a private cloud.
    examples:
    - name: Show details of a HCX addon.
      text: az vmware addon hcx show --resource-group MyResourceGroup --private-cloud MyPrivateCloud
"""

helps['vmware addon srm show'] = """
    type: command
    short-summary: Show details of a Site Recovery Manager (SRM) addon for a private cloud.
    examples:
    - name: Show details of a Site Recovery Manager (SRM) addon.
      text: az vmware addon srm show --resource-group MyResourceGroup --private-cloud MyPrivateCloud
"""

helps['vmware addon arc show'] = """
    type: command
    short-summary: Show details of an Arc addon for a private cloud.
    examples:
    - name: Show details of an Arc addon.
      text: az vmware addon arc show --resource-group MyResourceGroup --private-cloud MyPrivateCloud
"""

helps['vmware addon vr update'] = """
    type: command
    short-summary: Update a vSphere Replication (VR) addon for a private cloud.
    examples:
    - name: Update a vSphere Replication (VR) addon.
      text: az vmware addon vr update --resource-group MyResourceGroup --private-cloud MyPrivateCloud --vrs-count 1
"""

helps['vmware addon hcx update'] = """
    type: command
    short-summary: Update a HCX addon for a private cloud.
    examples:
    - name: Update a HCX addon.
      text: az vmware addon hcx update --resource-group MyResourceGroup --private-cloud MyPrivateCloud --offer "VMware MaaS Cloud Provider (Enterprise)"
"""

helps['vmware addon srm update'] = """
    type: command
    short-summary: Update a Site Recovery Manager (SRM) addon for a private cloud.
    examples:
    - name: Update a Site Recovery Manager (SRM) addon.
      text: az vmware addon srm update --resource-group MyResourceGroup --private-cloud MyPrivateCloud --license-key "41915-178A8-FF4A4-DB683-6D735"
"""

helps['vmware addon arc update'] = """
    type: command
    short-summary: Update an Arc addon for a private cloud.
    examples:
    - name: Update an Arc addon.
      text: az vmware addon arc update --resource-group MyResourceGroup --private-cloud MyPrivateCloud --vcenter "00000000-0000-0000-0000-000000000000"
"""

helps['vmware addon vr delete'] = """
    type: command
    short-summary: Delete a vSphere Replication (VR) addon for a private cloud.
    examples:
    - name: Delete a vSphere Replication (VR) addon.
      text: az vmware addon vr delete --resource-group MyResourceGroup --private-cloud MyPrivateCloud
"""

helps['vmware addon hcx delete'] = """
    type: command
    short-summary: Delete a HCX addon for a private cloud.
    examples:
    - name: Delete a HCX addon.
      text: az vmware addon hcx delete --resource-group MyResourceGroup --private-cloud MyPrivateCloud
"""

helps['vmware addon srm delete'] = """
    type: command
    short-summary: Delete a Site Recovery Manager (SRM) addon for a private cloud.
    examples:
    - name: Delete a Site Recovery Manager (SRM) addon.
      text: az vmware addon srm delete --resource-group MyResourceGroup --private-cloud MyPrivateCloud
"""

helps['vmware addon arc delete'] = """
    type: command
    short-summary: Delete an Arc addon for a private cloud.
    examples:
    - name: Delete an Arc addon.
      text: az vmware addon arc delete --resource-group MyResourceGroup --private-cloud MyPrivateCloud
"""

helps['vmware global-reach-connection'] = """
    type: group
    short-summary: Commands to manage global reach connections in a private cloud.
"""

helps['vmware global-reach-connection create'] = """
    type: command
    short-summary: Create a global reach connection in a private cloud.
"""

helps['vmware global-reach-connection list'] = """
    type: command
    short-summary: List global reach connections in a private cloud.
"""

helps['vmware global-reach-connection show'] = """
    type: command
    short-summary: Show details of a global reach connection in a private cloud.
"""

helps['vmware global-reach-connection delete'] = """
    type: command
    short-summary: Delete a global reach connection in a private cloud.
"""

helps['vmware cloud-link'] = """
    type: group
    short-summary: Commands to manage cloud links in a private cloud.
"""

helps['vmware cloud-link create'] = """
    type: command
    short-summary: Create or update a cloud link in a private cloud.
    examples:
    - name: Create a cloud link.
      text: az vmware cloud-link create --resource-group group1 --private-cloud cloud1 --name cloudLink1 --linked-cloud "/subscriptions/12341234-1234-1234-1234-123412341234/resourceGroups/mygroup/providers/Microsoft.AVS/privateClouds/cloud2"
"""

helps['vmware cloud-link list'] = """
    type: command
    short-summary: List cloud links in a private cloud.
    examples:
    - name: List cloud links.
      text: az vmware cloud-link list --resource-group group1 --private-cloud cloud1
"""

helps['vmware cloud-link show'] = """
    type: command
    short-summary: Show details of a cloud link in a private cloud.
    examples:
    - name: Show a cloud link.
      text: az vmware cloud-link show --resource-group group1 --private-cloud cloud1 --name cloudLink1
"""

helps['vmware cloud-link delete'] = """
    type: command
    short-summary: Delete a cloud link in a private cloud.
    examples:
    - name: Delete a cloud link.
      text: az vmware cloud-link delete --resource-group group1 --private-cloud cloud1 --name cloudLink1
"""

helps['vmware script-cmdlet'] = """
    type: group
    short-summary: Commands to list and show script cmdlet resources.
"""

helps['vmware script-cmdlet list'] = """
    type: command
    short-summary: List script cmdlet resources available for a private cloud to create a script execution resource on a private cloud.
    examples:
    - name: List script cmdlet resources.
      text: az vmware script-cmdlet list --resource-group group1 --private-cloud cloud1 --script-package package1
"""

helps['vmware script-cmdlet show'] = """
    type: command
    short-summary: Get information about a script cmdlet resource in a specific package on a private cloud.
    examples:
    - name: Show a script cmdlet.
      text: az vmware script-cmdlet show --resource-group group1 --private-cloud cloud1 --script-package package1 --name cmdlet1
"""

helps['vmware script-package'] = """
    type: group
    short-summary: Commands to list and show script packages available to run on the private cloud.
"""

helps['vmware script-package list'] = """
    type: command
    short-summary: List script packages available to run on the private cloud.
    examples:
    - name: List script packages.
      text: az vmware script-package list --resource-group group1 --private-cloud cloud1
"""

helps['vmware script-package show'] = """
    type: command
    short-summary: Get a script package available to run on a private cloud.
    examples:
    - name: Show a script package.
      text: az vmware script-package show --resource-group group1 --private-cloud cloud1 --name package1
"""

helps['vmware script-execution'] = """
    type: group
    short-summary: Commands to manage script executions in a private cloud.
"""

helps['vmware script-execution create'] = """
    type: command
    short-summary: Create or update a script execution in a private cloud.
    examples:
    - name: Create a script execution.
      text: az vmware script-execution create --resource-group group1 --private-cloud cloud1 --name addSsoServer --script-cmdlet-id "/subscriptions/{subscription-id}/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/scriptPackages/AVS.PowerCommands@1.0.0/scriptCmdlets/New-SsoExternalIdentitySource" --timeout P0Y0M0DT0H60M60S --retention P0Y0M60DT0H60M60S --parameter name=DomainName type=Value value=placeholderDomain.local --parameter name=BaseUserDN type=Value "value=DC=placeholder, DC=placeholder" --hidden-parameter name=Password type=SecureValue secureValue=PlaceholderPassword
"""

helps['vmware script-execution list'] = """
    type: command
    short-summary: List script executions in a private cloud.
    examples:
    - name: List script executions.
      text: az vmware script-execution list --resource-group group1 --private-cloud cloud1
"""

helps['vmware script-execution show'] = """
    type: command
    short-summary: Get an script execution by name in a private cloud.
    examples:
    - name: Show a script execution.
      text: az vmware script-execution show --resource-group group1 --private-cloud cloud1 --name addSsoServer
"""

helps['vmware script-execution delete'] = """
    type: command
    short-summary: Delete a script execution in a private cloud.
    examples:
    - name: Delete a script execution.
      text: az vmware script-execution delete --resource-group group1 --private-cloud cloud1 --name addSsoServer
"""

helps['vmware workload-network'] = """
    type: group
    short-summary: Commands to manage workload-networks in a private cloud.
"""

helps['vmware workload-network dhcp'] = """
    type: group
    short-summary: Commands to manage a DHCP (Data Host Configuration Protocol) workload network.
"""

helps['vmware workload-network dhcp list'] = """
    type: command
    short-summary: List DHCP in a private cloud workload network.
    examples:
    - name: List DHCP in a workload network.
      text: az vmware workload-network dhcp list --resource-group group1 --private-cloud cloud1
"""

helps['vmware workload-network dhcp show'] = """
    type: command
    short-summary: Get DHCP by ID in a private cloud workload network.
    examples:
    - name: Get DHCP by ID in a workload network.
      text: az vmware workload-network dhcp show --resource-group group1 --private-cloud cloud1 --dhcp dhcp1
"""

helps['vmware workload-network dhcp relay'] = """
    type: group
    short-summary: Commands to manage a DHCP (Data Host Configuration Protocol) workload network.
"""

helps['vmware workload-network dhcp relay create'] = """
    type: command
    short-summary: Create DHCP by ID in a private cloud workload network.
    examples:
    - name: Create DHCP by ID in a workload network.
      text: az vmware workload-network dhcp relay create --resource-group group1 --private-cloud cloud1 --dhcp dhcp1 --display-name dhcpConfigurations1 --revision 1 --server-addresses 40.1.5.1/24
"""

helps['vmware workload-network dhcp relay delete'] = """
    type: command
    short-summary: Delete DHCP by ID in a private cloud workload network.
    examples:
    - name: Delete DHCP by ID in a workload network.
      text: az vmware workload-network dhcp relay delete --resource-group group1 --private-cloud cloud1 --dhcp dhcp1
"""

helps['vmware workload-network dhcp relay update'] = """
    type: command
    short-summary: Update DHCP by ID in a private cloud workload network.
    examples:
    - name: Update DHCP by ID in a workload network.
      text: az vmware workload-network dhcp relay update --resource-group group1 --private-cloud cloud1 --dhcp dhcp1 --display-name dhcpConfigurations1 --revision 1 --server-addresses 40.1.5.1/24
"""

helps['vmware workload-network dhcp server'] = """
    type: group
    short-summary: Commands to manage a DHCP (Data Host Configuration Protocol) workload network.
"""

helps['vmware workload-network dhcp server create'] = """
    type: command
    short-summary: Create DHCP by ID in a private cloud workload network.
    examples:
    - name: Create DHCP by ID in a workload network.
      text: az vmware workload-network dhcp server create --resource-group group1 --private-cloud cloud1 --dhcp dhcp1 --display-name dhcpConfigurations1 --revision 1 --server-address 40.1.5.1/24 --lease-time 86400
"""

helps['vmware workload-network dhcp server delete'] = """
    type: command
    short-summary: Delete DHCP by ID in a private cloud workload network.
    examples:
    - name: Delete DHCP by ID in a workload network.
      text: az vmware workload-network dhcp server delete --resource-group group1 --private-cloud cloud1 --dhcp dhcp1
"""

helps['vmware workload-network dhcp server update'] = """
    type: command
    short-summary: Update DHCP by ID in a private cloud workload network.
    examples:
    - name: Update DHCP by ID in a workload network.
      text: az vmware workload-network dhcp server update --resource-group group1 --private-cloud cloud1 --dhcp dhcp1 --display-name dhcpConfigurations1 --revision 1 --server-address 40.1.5.1/24 --lease-time 86400
"""


helps['vmware workload-network dns-service'] = """
    type: group
    short-summary: Commands to manage a DNS Service workload network.
"""


helps['vmware workload-network dns-service list'] = """
    type: command
    short-summary: List of DNS services in a private cloud workload network.
    examples:
    - name: List of DNS services in a workload network.
      text: az vmware workload-network dns-service list --resource-group group1 --private-cloud cloud1
"""

helps['vmware workload-network dns-service show'] = """
    type: command
    short-summary: Get a DNS service by ID in a private cloud workload network.
    examples:
    - name: Get a DNS service by ID in a workload network.
      text: az vmware workload-network dns-service show --resource-group group1 --private-cloud cloud1 --dns-service dnsService1
"""

helps['vmware workload-network dns-service create'] = """
    type: command
    short-summary: Create a DNS service by ID in a private cloud workload network.
    examples:
    - name: Create a DNS service by ID in a workload network.
      text: az vmware workload-network dns-service create --resource-group group1 --private-cloud cloud1 --dns-service dnsService1 --display-name dnsService1 --dns-service-ip 5.5.5.5 --default-dns-zone defaultDnsZone1 --fqdn-zones fqdnZone1 --log-level INFO --revision 1
"""

helps['vmware workload-network dns-service update'] = """
    type: command
    short-summary: Update a DNS service by ID in a private cloud workload network.
    examples:
    - name: Update a DNS service by ID in a workload network.
      text: az vmware workload-network dns-service update --resource-group group1 --private-cloud cloud1 --dns-service dnsService1 --display-name dnsService1 --dns-service-ip 5.5.5.5 --default-dns-zone defaultDnsZone1 --fqdn-zones fqdnZone1 --log-level INFO --revision 1
"""

helps['vmware workload-network dns-service delete'] = """
    type: command
    short-summary: Delete a DNS service by ID in a private cloud workload network.
    examples:
    - name: Delete a DNS service by ID in a workload network.
      text: az vmware workload-network dns-service delete --resource-group group1 --private-cloud cloud1 --dns-service dnsService1
"""

helps['vmware workload-network dns-zone'] = """
    type: group
    short-summary: Commands to manage a DNS Zone workload network.
"""

helps['vmware workload-network dns-zone list'] = """
    type: command
    short-summary: List of DNS zones in a private cloud workload network.
    examples:
    - name: List of DNS zones in a workload network.
      text: az vmware workload-network dns-zone list --resource-group group1 --private-cloud cloud1
"""

helps['vmware workload-network dns-zone show'] = """
    type: command
    short-summary: Get a DNS zone by ID in a private cloud workload network.
    examples:
    - name: Get a DNS zone by ID in a workload network.
      text: az vmware workload-network dns-zone show --resource-group group1 --private-cloud cloud1 --dns-zone dnsZone1
"""

helps['vmware workload-network dns-zone create'] = """
    type: command
    short-summary: Create a DNS zone by ID in a private cloud workload network.
    examples:
    - name: Create a DNS zone by ID in a workload network.
      text: az vmware workload-network dns-zone create --resource-group group1 --private-cloud cloud1 --dns-zone dnsZone1 --display-name dnsZone1 --domain domain1 --dns-server-ips 1.1.1.1 --source-ip 8.8.8.8 --dns-services 1 --revision 1
"""

helps['vmware workload-network dns-zone update'] = """
    type: command
    short-summary: Update a DNS zone by ID in a private cloud workload network.
    examples:
    - name: Update a DNS zone by ID in a workload network.
      text: az vmware workload-network dns-zone update --resource-group group1 --private-cloud cloud1 --dns-zone dnsZone1 --display-name dnsZone1 --domain domain1 --dns-server-ips 1.1.1.1 --source-ip 8.8.8.8 --dns-services 1 --revision 1
"""

helps['vmware workload-network dns-zone delete'] = """
    type: command
    short-summary: Delete a DNS zone by ID in a private cloud workload network.
    examples:
    - name: Delete a DNS zone by ID in a workload network.
      text: az vmware workload-network dns-zone delete --resource-group group1 --private-cloud cloud1 --dns-zone dnsZone1
"""

helps['vmware workload-network port-mirroring'] = """
    type: group
    short-summary: Commands to manage a Port Mirroring workload network.
"""

helps['vmware workload-network port-mirroring list'] = """
    type: command
    short-summary: List of port mirroring profiles in a private cloud workload network.
    examples:
    - name: List of port mirroring profiles in a workload network.
      text: az vmware workload-network port-mirroring list --resource-group group1 --private-cloud cloud1
"""

helps['vmware workload-network port-mirroring show'] = """
    type: command
    short-summary: Get a port mirroring profile by ID in a private cloud workload network.
    examples:
    - name: Get a port mirroring profile by ID in a workload network.
      text: az vmware workload-network port-mirroring show --resource-group group1 --private-cloud cloud1 --port-mirroring portMirroring1
"""

helps['vmware workload-network port-mirroring create'] = """
    type: command
    short-summary: Create a port mirroring profile by ID in a private cloud workload network.
    examples:
    - name: Create a port mirroring profile by ID in a workload network.
      text: az vmware workload-network port-mirroring create --resource-group group1 --private-cloud cloud1 --port-mirroring portMirroring1 --display-name portMirroring1 --direction BIDIRECTIONAL --source vmGroup1 --destination vmGroup2 --revision 1
"""

helps['vmware workload-network port-mirroring update'] = """
    type: command
    short-summary: Update a port mirroring profile by ID in a private cloud workload network.
    examples:
    - name: Update a port mirroring profile by ID in a workload network.
      text: az vmware workload-network port-mirroring update --resource-group group1 --private-cloud cloud1 --port-mirroring portMirroring1 --display-name portMirroring1 --direction BIDIRECTIONAL --source vmGroup1 --destination vmGroup2 --revision 1
"""

helps['vmware workload-network port-mirroring delete'] = """
    type: command
    short-summary: Delete a port mirroring profile by ID in a private cloud workload network.
    examples:
    - name: Delete a port mirroring profile by ID in a workload network.
      text: az vmware workload-network port-mirroring delete --resource-group group1 --private-cloud cloud1 --port-mirroring portMirroring1
"""

helps['vmware workload-network segment'] = """
    type: group
    short-summary: Commands to manage a Segment workload network.
"""

helps['vmware workload-network segment list'] = """
    type: command
    short-summary: List of segments in a private cloud workload network.
    examples:
    - name: List of segments in a workload network.
      text: az vmware workload-network segment list --resource-group group1 --private-cloud cloud1
"""

helps['vmware workload-network segment show'] = """
    type: command
    short-summary: Get a segment by ID in a private cloud workload network.
    examples:
    - name: Get a segment by ID in a workload network.
      text: az vmware workload-network segment show --resource-group group1 --private-cloud cloud1 --segment segment1
"""

helps['vmware workload-network segment create'] = """
    type: command
    short-summary: Create a segment by ID in a private cloud workload network.
    examples:
    - name: Create a segment by ID in a workload network.
      text: az vmware workload-network segment create --resource-group group1 --private-cloud cloud1 --segment segment1 --display-name segment1 --connected-gateway /infra/tier-1s/gateway --revision 1 --dhcp-ranges 40.20.0.0 40.20.0.1 --gateway-address 40.20.20.20/16
"""

helps['vmware workload-network segment update'] = """
    type: command
    short-summary: Update a segment by ID in a private cloud workload network.
    examples:
    - name: Update a segment by ID in a workload network.
      text: az vmware workload-network segment update --resource-group group1 --private-cloud cloud1 --segment segment1 --display-name segment1 --connected-gateway /infra/tier-1s/gateway --revision 1 --dhcp-ranges 40.20.0.0 40.20.0.1 --gateway-address 40.20.20.20/16
"""

helps['vmware workload-network segment delete'] = """
    type: command
    short-summary: Delete a segment by ID in a private cloud workload network.
    examples:
    - name: Delete a segment by ID in a workload network.
      text: az vmware workload-network segment delete --resource-group group1 --private-cloud cloud1 --segment segment1
"""

helps['vmware workload-network public-ip'] = """
    type: group
    short-summary: Commands to manage a Public-IP workload network.
"""

helps['vmware workload-network public-ip list'] = """
    type: command
    short-summary: List of Public IP Blocks in a private cloud workload network.
    examples:
    - name: List of Public IP Blocks in a workload network.
      text: az vmware workload-network public-ip list --resource-group group1 --private-cloud cloud1
"""

helps['vmware workload-network public-ip show'] = """
    type: command
    short-summary: Get a Public IP Block by ID in a private cloud workload network.
    examples:
    - name: Get a Public IP Block by ID in a workload network.
      text: az vmware workload-network public-ip show --resource-group group1 --private-cloud cloud1 --public-ip publicIP1
"""

helps['vmware workload-network public-ip create'] = """
    type: command
    short-summary: Create a Public IP Block by ID in a private cloud workload network.
    examples:
    - name: Create a Public IP Block by ID in a workload network.
      text: az vmware workload-network public-ip create --resource-group group1 --private-cloud cloud1 --public-ip publicIP1 --display-name publicIP1 --number-of-public-ips 32
"""

helps['vmware workload-network public-ip delete'] = """
    type: command
    short-summary: Delete a Public IP Block by ID in a private cloud workload network.
    examples:
    - name: Delete a Public IP Block by ID in a workload network.
      text: az vmware workload-network public-ip delete --resource-group group1 --private-cloud cloud1 --public-ip publicIP1
"""

helps['vmware workload-network vm-group'] = """
    type: group
    short-summary: Commands to manage a VM Group workload network.
"""

helps['vmware workload-network vm-group list'] = """
    type: command
    short-summary: List of VM Groups in a private cloud workload network.
    examples:
    - name: List of VM Groups in a workload network.
      text: az vmware workload-network vm-group list --resource-group group1 --private-cloud cloud1
"""

helps['vmware workload-network vm-group show'] = """
    type: command
    short-summary: Get a VM Group by ID in a private cloud workload network.
    examples:
    - name: Get a VM Group by ID in a workload network.
      text: az vmware workload-network vm-group show --resource-group group1 --private-cloud cloud1 --vm-group vmGroup1
"""

helps['vmware workload-network vm-group create'] = """
    type: command
    short-summary: Create a VM Group by ID in a private cloud workload network.
    examples:
    - name: Create a VM Group by ID in a workload network.
      text: az vmware workload-network vm-group create --resource-group group1 --private-cloud cloud1 --vm-group vmGroup1 --display-name vmGroup1 --members 564d43da-fefc-2a3b-1d92-42855622fa50 --revision 1
"""

helps['vmware workload-network vm-group update'] = """
    type: command
    short-summary: Update a VM Group by ID in a private cloud workload network.
    examples:
    - name: Update a VM Group by ID in a workload network.
      text: az vmware workload-network vm-group update --resource-group group1 --private-cloud cloud1 --vm-group vmGroup1 --display-name vmGroup1 --members 564d43da-fefc-2a3b-1d92-42855622fa50 --revision 1
"""

helps['vmware workload-network vm-group delete'] = """
    type: command
    short-summary: Delete a VM Group by ID in a private cloud workload network.
    examples:
    - name: Delete a VM Group by ID in a private cloud workload network.
      text: az vmware workload-network vm-group delete --resource-group group1 --private-cloud cloud1 --vm-group vmGroup1
"""

helps['vmware workload-network vm'] = """
    type: group
    short-summary: Commands to manage a Virtual Machine workload network.
"""

helps['vmware workload-network vm list'] = """
    type: command
    short-summary: List of Virtual Machines in a private cloud workload network.
    examples:
    - name: List of Virtual Machines in a workload network.
      text: az vmware workload-network vm list --resource-group group1 --private-cloud cloud1
"""

helps['vmware workload-network vm show'] = """
    type: command
    short-summary: Get a Virtual Machines by ID in a private cloud workload network.
    examples:
    - name: Get a Virtual Machines by ID in a workload network.
      text: az vmware workload-network vm show --resource-group group1 --private-cloud cloud1 --virtual-machine vm1
"""

helps['vmware workload-network gateway'] = """
    type: group
    short-summary: Commands to manage a Gateway workload network.
"""

helps['vmware workload-network gateway list'] = """
    type: command
    short-summary: List of Gateways in a private cloud workload network.
    examples:
    - name: List of Gateways in a workload network.
      text: az vmware workload-network gateway list --resource-group group1 --private-cloud cloud1
"""

helps['vmware workload-network gateway show'] = """
    type: command
    short-summary: Get a Gateway by ID in a private cloud workload network.
    examples:
    - name: Get a Gateway by ID in a workload network.
      text: az vmware workload-network gateway show --resource-group group1 --private-cloud cloud1 --gateway gateway1
"""

helps['vmware placement-policy'] = """
    type: group
    short-summary: Commands to manage placement policies.
"""

helps['vmware placement-policy list'] = """
    type: command
    short-summary: List placement policies in a private cloud cluster.
    examples:
    - name: List placement policies.
      text: az vmware placement-policy list --resource-group group1 --private-cloud cloud1 --cluster-name cluster1
"""

helps['vmware placement-policy show'] = """
    type: command
    short-summary: Get a placement policy by name in a private cloud cluster.
    examples:
    - name: Get a placement policy by name.
      text: az vmware placement-policy show --resource-group group1 --private-cloud cloud1 --cluster-name cluster1 --placement-policy-name policy1
"""

helps['vmware placement-policy vm-host'] = """
    type: group
    short-summary: Commands to manage VM Host placement policies.
"""

helps['vmware placement-policy vm-host create'] = """
    type: command
    short-summary: Create a VM Host placement policy in a private cloud cluster.
    examples:
    - name: Create a VM Host placement policy.
      text: az vmware placement-policy vm-host create --resource-group group1 --private-cloud cloud1 --cluster-name cluster1 --placement-policy-name policy1 --state Enabled --display-name policy1 --vm-members /subscriptions/subId/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/clusters/cluster1/virtualMachines/vm-128 /subscriptions/subId/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/clusters/cluster1/virtualMachines/vm-256 --host-members fakehost22.nyc1.kubernetes.center fakehost23.nyc1.kubernetes.center --affinity-type AntiAffinity
"""

helps['vmware placement-policy vm-host update'] = """
    type: command
    short-summary: Update a VM Host placement policy in a private cloud cluster.
    examples:
    - name: Update a VM Host placement policy.
      text: az vmware placement-policy vm-host update --resource-group group1 --private-cloud cloud1 --cluster-name cluster1 --placement-policy-name policy1 --state Enabled --vm-members /subscriptions/subId/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/clusters/cluster1/virtualMachines/vm-128 /subscriptions/subId/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/clusters/cluster1/virtualMachines/vm-256 --host-members fakehost22.nyc1.kubernetes.center fakehost23.nyc1.kubernetes.center
"""

helps['vmware placement-policy vm-host delete'] = """
    type: command
    short-summary: Delete a VM Host placement policy in a private cloud cluster.
    examples:
    - name: Delete a VM Host placement policy.
      text: az vmware placement-policy vm-host delete --resource-group group1 --private-cloud cloud1 --cluster-name cluster1 --placement-policy-name policy1
"""

helps['vmware placement-policy vm'] = """
    type: group
    short-summary: Commands to manage VM placement policies.
"""

helps['vmware placement-policy vm create'] = """
    type: command
    short-summary: Create a VM placement policy in a private cloud cluster.
    examples:
    - name: Create a VM placement policy.
      text: az vmware placement-policy vm create --resource-group group1 --private-cloud cloud1 --cluster-name cluster1 --placement-policy-name policy1 --state Enabled --display-name policy1 --vm-members /subscriptions/subId/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/clusters/cluster1/virtualMachines/vm-128 /subscriptions/subId/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/clusters/cluster1/virtualMachines/vm-256 --affinity-type AntiAffinity
"""

helps['vmware placement-policy vm update'] = """
    type: command
    short-summary: Update a VM placement policy in a private cloud cluster.
    examples:
    - name: Update a VM placement policy.
      text: az vmware placement-policy vm update --resource-group group1 --private-cloud cloud1 --cluster-name cluster1 --placement-policy-name policy1 --state Enabled --vm-members /subscriptions/subId/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/clusters/cluster1/virtualMachines/vm-128 /subscriptions/subId/resourceGroups/group1/providers/Microsoft.AVS/privateClouds/cloud1/clusters/cluster1/virtualMachines/vm-256
"""

helps['vmware placement-policy vm delete'] = """
    type: command
    short-summary: Delete a VM placement policy in a private cloud cluster.
    examples:
    - name: Delete a VM placement policy.
      text: az vmware placement-policy vm delete --resource-group group1 --private-cloud cloud1 --cluster-name cluster1 --placement-policy-name policy1
"""

helps['vmware vm'] = """
    type: group
    short-summary: Commands to manage Virtual Machines.
"""

helps['vmware vm show'] = """
    type: command
    short-summary: Get a virtual machine by ID in a private cloud cluster.
    examples:
    - name: Get a virtual machine by ID.
      text: az vmware vm show --resource-group group1 --private-cloud cloud1 --cluster-name cluster1 --virtual-machine vm-209
"""

helps['vmware vm list'] = """
    type: command
    short-summary: List of virtual machines in a private cloud cluster.
    examples:
    - name: List of virtual machines.
      text: az vmware vm list --resource-group group1 --private-cloud cloud1 --cluster-name cluster1
"""

helps['vmware vm restrict-movement'] = """
    type: command
    short-summary: Enable or disable DRS-driven VM movement restriction.
    examples:
    - name: Enable or disable DRS-driven VM movement restriction.
      text: az vmware vm restrict-movement --resource-group group1 --private-cloud cloud1 --cluster-name cluster1 --virtual-machine vm-209 --restrict-movement Enabled
"""
