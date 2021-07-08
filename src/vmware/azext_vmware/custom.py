# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azext_vmware.vendored_sdks.avs_client import AVSClient

LEGAL_TERMS = '''
LEGAL TERMS

Azure VMware Solution ("AVS") is an Azure Service licensed to you as part of your Azure subscription and subject to the terms and conditions of the agreement under which you obtained your Azure subscription (https://azure.microsoft.com/support/legal/). The following additional terms also apply to your use of AVS:

DATA RETENTION. AVS does not currently support retention or extraction of data stored in AVS Clusters. Once an AVS Cluster is deleted, the data cannot be recovered as it terminates all running workloads, components, and destroys all Cluster data and configuration settings, including public IP addresses.

PROFESSIONAL SERVICES DATA TRANSFER TO VMWARE. In the event that you contact Microsoft for technical support relating to Azure VMware Solution and Microsoft must engage VMware for assistance with the issue, Microsoft will transfer the Professional Services Data and the Personal Data contained in the support case to VMware. The transfer is made subject to the terms of the Support Transfer Agreement between VMware and Microsoft, which establishes Microsoft and VMware as independent processors of the Professional Services Data. Before any transfer of Professional Services Data to VMware will occur, Microsoft will obtain and record consent from you for the transfer.

VMWARE DATA PROCESSING AGREEMENT. Once Professional Services Data is transferred to VMware (pursuant to the above section), the processing of Professional Services Data, including the Personal Data contained the support case, by VMware as an independent processor will be governed by the VMware Data Processing Agreement for Microsoft AVS Customers Transferred for L3 Support (the "VMware Data Processing Agreement") between you and VMware (located at https://www.vmware.com/content/dam/digitalmarketing/vmware/en/pdf/privacy/vmware-data-processing-agreement.pdf). You also give authorization to allow your representative(s) who request technical support for Azure VMware Solution to provide consent on your behalf to Microsoft for the transfer of the Professional Services Data to VMware.

ACCEPTANCE OF LEGAL TERMS. By continuing, you agree to the above additional Legal Terms for AVS. If you are an individual accepting these terms on behalf of an entity, you also represent that you have the legal authority to enter into these additional terms on that entity's behalf.
'''


def privatecloud_list(client: AVSClient, resource_group_name=None):
    if resource_group_name is None:
        return client.private_clouds.list_in_subscription()
    return client.private_clouds.list(resource_group_name)


def privatecloud_show(client: AVSClient, resource_group_name, name):
    return client.private_clouds.get(resource_group_name, name)


def privatecloud_create(client: AVSClient, resource_group_name, name, location, sku, cluster_size, network_block, circuit_primary_subnet=None, circuit_secondary_subnet=None, internet=None, vcenter_password=None, nsxt_password=None, tags=None, accept_eula=False):
    from knack.prompting import prompt_y_n
    if not accept_eula:
        print(LEGAL_TERMS)
        msg = 'Do you agree to the above additional terms for AVS?'
        if not prompt_y_n(msg, default="n"):
            return None

    from azext_vmware.vendored_sdks.avs_client.models import PrivateCloud, Circuit, ManagementCluster, Sku
    if circuit_primary_subnet is not None or circuit_secondary_subnet is not None:
        circuit = Circuit(primary_subnet=circuit_primary_subnet, secondary_subnet=circuit_secondary_subnet)
    else:
        circuit = None
    management_cluster = ManagementCluster(cluster_size=cluster_size)
    cloud = PrivateCloud(location=location, sku=Sku(name=sku), circuit=circuit, management_cluster=management_cluster, network_block=network_block, tags=tags)
    if internet is not None:
        cloud.internet = internet
    if vcenter_password is not None:
        cloud.vcenter_password = vcenter_password
    if nsxt_password is not None:
        cloud.nsxt_password = nsxt_password
    return client.private_clouds.begin_create_or_update(resource_group_name, name, cloud)


def privatecloud_update(client: AVSClient, resource_group_name, name, cluster_size=None, internet=None):
    from azext_vmware.vendored_sdks.avs_client.models import PrivateCloudUpdate, ManagementCluster
    private_cloud_update = PrivateCloudUpdate()
    if cluster_size is not None:
        private_cloud_update.management_cluster = ManagementCluster(cluster_size=cluster_size)
    if internet is not None:
        private_cloud_update.internet = internet
    return client.private_clouds.begin_update(resource_group_name, name, private_cloud_update)


def privatecloud_delete(client: AVSClient, resource_group_name, name, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the private cloud. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.private_clouds.begin_delete(resource_group_name, name)


def privatecloud_listadmincredentials(client: AVSClient, resource_group_name, private_cloud):
    return client.private_clouds.list_admin_credentials(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def privatecloud_addidentitysource(client: AVSClient, resource_group_name, name, private_cloud, alias, domain, base_user_dn, base_group_dn, primary_server, username, password, secondary_server=None, ssl="Disabled"):
    from azext_vmware.vendored_sdks.avs_client.models import IdentitySource
    pc = client.private_clouds.get(resource_group_name, private_cloud)
    identitysource = IdentitySource(name=name, alias=alias, domain=domain, base_user_dn=base_user_dn, base_group_dn=base_group_dn, primary_server=primary_server, ssl=ssl, username=username, password=password)
    if secondary_server is not None:
        identitysource.secondary_server = secondary_server
    pc.identity_sources.append(identitysource)
    return client.private_clouds.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, private_cloud=pc)


def privatecloud_deleteidentitysource(client: AVSClient, resource_group_name, name, private_cloud, alias, domain):
    pc = client.private_clouds.get(resource_group_name, private_cloud)
    found = next((ids for ids in pc.identity_sources
                 if ids.name == name and ids.alias == alias and ids.domain == domain), None)
    if found:
        pc.identity_sources.remove(found)
        return client.private_clouds.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, private_cloud=pc)
    return pc


def privatecloud_rotate_vcenter_password(client: AVSClient, resource_group_name, private_cloud):
    return client.private_clouds.begin_rotate_vcenter_password(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def privatecloud_rotate_nsxt_password(client: AVSClient, resource_group_name, private_cloud):
    return client.private_clouds.begin_rotate_nsxt_password(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def cluster_create(client: AVSClient, resource_group_name, name, sku, private_cloud, size):
    from azext_vmware.vendored_sdks.avs_client.models import Sku
    return client.clusters.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name, sku=Sku(name=sku), cluster_size=size)


def cluster_update(client: AVSClient, resource_group_name, name, private_cloud, size):
    return client.clusters.begin_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name, cluster_size=size)


def cluster_list(client: AVSClient, resource_group_name, private_cloud):
    return client.clusters.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def cluster_show(client: AVSClient, resource_group_name, private_cloud, name):
    return client.clusters.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name)


def cluster_delete(client: AVSClient, resource_group_name, private_cloud, name):
    return client.clusters.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name)


def check_quota_availability(client: AVSClient, location):
    return client.locations.check_quota_availability(location)


def check_trial_availability(client: AVSClient, location):
    return client.locations.check_trial_availability(location)


def authorization_create(client: AVSClient, resource_group_name, private_cloud, name):
    return client.authorizations.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, authorization_name=name)


def authorization_list(client: AVSClient, resource_group_name, private_cloud):
    return client.authorizations.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def authorization_show(client: AVSClient, resource_group_name, private_cloud, name):
    return client.authorizations.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, authorization_name=name)


def authorization_delete(client: AVSClient, resource_group_name, private_cloud, name):
    return client.authorizations.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, authorization_name=name)


def hcxenterprisesite_create(client: AVSClient, resource_group_name, private_cloud, name):
    return client.hcx_enterprise_sites.create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, hcx_enterprise_site_name=name)


def hcxenterprisesite_list(client: AVSClient, resource_group_name, private_cloud):
    return client.hcx_enterprise_sites.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def hcxenterprisesite_show(client: AVSClient, resource_group_name, private_cloud, name):
    return client.hcx_enterprise_sites.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, hcx_enterprise_site_name=name)


def hcxenterprisesite_delete(client: AVSClient, resource_group_name, private_cloud, name):
    return client.hcx_enterprise_sites.delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, hcx_enterprise_site_name=name)


def datastore_create():
    print('Please use "az vmware datastore netapp-volume create" or "az vmware datastore disk-pool-volume create" instead.')


def datastore_netappvolume_create(client: AVSClient, resource_group_name, private_cloud, cluster, name, volume_id):
    from azext_vmware.vendored_sdks.avs_client.models import NetAppVolume
    net_app_volume = NetAppVolume(id=volume_id)
    return client.datastores.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster, datastore_name=name, net_app_volume=net_app_volume, disk_pool_volume=None)


def datastore_diskpoolvolume_create(client: AVSClient, resource_group_name, private_cloud, cluster, name, target_id, lun_name, mount_option="MOUNT", path=None):
    from azext_vmware.vendored_sdks.avs_client.models import DiskPoolVolume
    disk_pool_volume = DiskPoolVolume(target_id=target_id, lun_name=lun_name, mount_option=mount_option, path=path)
    return client.datastores.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster, datastore_name=name, net_app_volume=None, disk_pool_volume=disk_pool_volume)


def datastore_list(client: AVSClient, resource_group_name, private_cloud, cluster):
    return client.datastores.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster)


def datastore_show(client: AVSClient, resource_group_name, private_cloud, cluster, name):
    return client.datastores.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster, datastore_name=name)


def datastore_delete(client: AVSClient, resource_group_name, private_cloud, cluster, name):
    return client.datastores.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster, datastore_name=name)


def addon_list(client: AVSClient, resource_group_name, private_cloud):
    return client.addons.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def addon_vr_create(client: AVSClient, resource_group_name, private_cloud, vrs_count: int):
    from azext_vmware.vendored_sdks.avs_client.models import AddonVrProperties
    properties = AddonVrProperties(vrs_count=vrs_count)
    return client.addons.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="vr", properties=properties)


def addon_hcx_create(client: AVSClient, resource_group_name, private_cloud, offer: str):
    from azext_vmware.vendored_sdks.avs_client.models import AddonHcxProperties
    properties = AddonHcxProperties(offer=offer)
    return client.addons.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="hcx", properties=properties)


def addon_srm_create(client: AVSClient, resource_group_name, private_cloud, license_key: str):
    from azext_vmware.vendored_sdks.avs_client.models import AddonSrmProperties
    properties = AddonSrmProperties(license_key=license_key)
    return client.addons.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="srm", properties=properties)


def addon_vr_show(client: AVSClient, resource_group_name, private_cloud):
    return client.addons.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="vr")


def addon_hcx_show(client: AVSClient, resource_group_name, private_cloud):
    return client.addons.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="hcx")


def addon_srm_show(client: AVSClient, resource_group_name, private_cloud):
    return client.addons.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="srm")


def addon_vr_update(client: AVSClient, resource_group_name, private_cloud, vrs_count: int):
    from azext_vmware.vendored_sdks.avs_client.models import AddonVrProperties
    properties = AddonVrProperties(vrs_count=vrs_count)
    return client.addons.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="vr", properties=properties)


def addon_hcx_update(client: AVSClient, resource_group_name, private_cloud, offer: str):
    from azext_vmware.vendored_sdks.avs_client.models import AddonHcxProperties
    properties = AddonHcxProperties(offer=offer)
    return client.addons.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="hcx", properties=properties)


def addon_srm_update(client: AVSClient, resource_group_name, private_cloud, license_key: str):
    from azext_vmware.vendored_sdks.avs_client.models import AddonSrmProperties
    properties = AddonSrmProperties(license_key=license_key)
    return client.addons.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="srm", properties=properties)


def addon_vr_delete(client: AVSClient, resource_group_name, private_cloud):
    return client.addons.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="vr")


def addon_hcx_delete(client: AVSClient, resource_group_name, private_cloud):
    return client.addons.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="hcx")


def addon_srm_delete(client: AVSClient, resource_group_name, private_cloud):
    return client.addons.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="srm")


def globalreachconnection_create(client: AVSClient, resource_group_name, private_cloud, name, authorization_key=None, peer_express_route_circuit=None):
    return client.global_reach_connections.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, global_reach_connection_name=name, authorization_key=authorization_key, peer_express_route_circuit=peer_express_route_circuit)


def globalreachconnection_list(client: AVSClient, resource_group_name, private_cloud):
    return client.global_reach_connections.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def globalreachconnection_show(client: AVSClient, resource_group_name, private_cloud, name):
    return client.global_reach_connections.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, global_reach_connection_name=name)


def globalreachconnection_delete(client: AVSClient, resource_group_name, private_cloud, name):
    return client.global_reach_connections.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, global_reach_connection_name=name)
