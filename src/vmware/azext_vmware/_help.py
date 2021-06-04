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
    short-summary: Create a datastore in a private cloud cluster.
    examples:
    - name: Create a new Microsoft.StoragePool provided disk pool based iSCSI datastore.
      text: az vmware datastore create --name iSCSIDatastore1 --resource-group MyResourceGroup --cluster Cluster-1 --private-cloud MyPrivateCloud --endpoints 10.10.0.1:3260 --lun-name lun0
    - name: Create a new Microsoft.StoragePool provided disk pool based iSCSI datastore with multiple endpoints.
      text: az vmware datastore create --name iSCSIDatastore1 --resource-group MyResourceGroup --cluster Cluster-1 --private-cloud MyPrivateCloud --endpoints 10.10.0.1:3260 10.10.0.2:3260 --lun-name lun0
    - name: Create a new Microsoft.NetApp provided NetApp volume based NFSv3 datastore.
      text: az vmware datastore create --name ANFDatastore1 --resource-group MyResourceGroup --cluster Cluster-1 --private-cloud MyPrivateCloud --nfs-file-path ANFVol1FilePath --nfs-provider-ip 10.10.0.1
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
