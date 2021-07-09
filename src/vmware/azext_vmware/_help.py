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

helps['vmware private-cloud'] = """
    type: group
    short-summary: Commands to manage private clouds.
"""

helps['vmware cluster'] = """
    type: group
    short-summary: Commands to manage clusters in a private cloud.
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
    short-summary: Delete a cluster in a private cloud.
"""

helps['vmware cluster list'] = """
    type: command
    short-summary: List clusters in a private cloud.
"""

helps['vmware cluster show'] = """
    type: command
    short-summary: Show details of a cluster in a private cloud.
"""

helps['vmware cluster update'] = """
    type: command
    short-summary: Update a cluster in a private cloud.
"""

helps['vmware private-cloud addidentitysource'] = """
    type: command
    short-summary: Add a vCenter Single Sign On Identity Source to a private cloud.
"""

helps['vmware private-cloud create'] = """
    type: command
    short-summary: Create a private cloud.
"""

helps['vmware private-cloud delete'] = """
    type: command
    short-summary: Delete a private cloud.
"""

helps['vmware private-cloud deleteidentitysource'] = """
    type: command
    short-summary: Delete a vCenter Single Sign On Identity Source for a private cloud.
"""

helps['vmware private-cloud list'] = """
    type: command
    short-summary: List the private clouds.
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
      text: az vmware private-cloud rotate-nsxt-password --resource-group MyResourceGroup --private-cloud MyPrivateCloud
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

helps['vmware location checktrialavailability'] = """
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
