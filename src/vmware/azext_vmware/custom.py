# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import List, Tuple
from azext_vmware.vendored_sdks.avs_client import AVSClient

LEGAL_TERMS = '''
LEGAL TERMS

Azure VMware Solution ("AVS") is an Azure Service licensed to you as part of your Azure subscription and subject to the terms and conditions of the agreement under which you obtained your Azure subscription (https://azure.microsoft.com/support/legal/). The following additional terms also apply to your use of AVS:

DATA RETENTION. AVS does not currently support retention or extraction of data stored in AVS Clusters. Once an AVS Cluster is deleted, the data cannot be recovered as it terminates all running workloads, components, and destroys all Cluster data and configuration settings, including public IP addresses.

PROFESSIONAL SERVICES DATA TRANSFER TO VMWARE. In the event that you contact Microsoft for technical support relating to Azure VMware Solution and Microsoft must engage VMware for assistance with the issue, Microsoft will transfer the Professional Services Data and the Personal Data contained in the support case to VMware. The transfer is made subject to the terms of the Support Transfer Agreement between VMware and Microsoft, which establishes Microsoft and VMware as independent processors of the Professional Services Data. Before any transfer of Professional Services Data to VMware will occur, Microsoft will obtain and record consent from you for the transfer.

VMWARE DATA PROCESSING AGREEMENT. Once Professional Services Data is transferred to VMware (pursuant to the above section), the processing of Professional Services Data, including the Personal Data contained the support case, by VMware as an independent processor will be governed by the VMware Data Processing Agreement for Microsoft AVS Customers Transferred for L3 Support (the "VMware Data Processing Agreement") between you and VMware (located at https://www.vmware.com/content/dam/digitalmarketing/vmware/en/pdf/privacy/vmware-data-processing-agreement.pdf). You also give authorization to allow your representative(s) who request technical support for Azure VMware Solution to provide consent on your behalf to Microsoft for the transfer of the Professional Services Data to VMware.

ACCEPTANCE OF LEGAL TERMS. By continuing, you agree to the above additional Legal Terms for AVS. If you are an individual accepting these terms on behalf of an entity, you also represent that you have the legal authority to enter into these additional terms on that entity's behalf.
'''

ROTATE_VCENTER_PASSWORD_TERMS = '''
Any services connected using these credentials will stop working and may cause you to be locked out of your account.

Check if you're using your cloudadmin credentials for any connected services like backup and disaster recovery appliances, VMware HCX, or any vRealize suite products. Verify you're not using cloudadmin credentials for connected services before generating a new password.

If you are using cloudadmin for connected services, learn how you can setup a connection to an external identity source to create and manage new credentials for your connected services: https://docs.microsoft.com/en-us/azure/azure-vmware/configure-identity-source-vcenter

Press Y to confirm no services are using my cloudadmin credentials to connect to vCenter
'''

ROTATE_NSXT_PASSWORD_TERMS = '''
Currently, rotating your NSX-T managed admin credentials isn’t supported.  If you need to rotate your NSX-T manager admin credentials, please submit a support request in the Azure Portal: https://portal.azure.com/#create/Microsoft.Support

Press any key to continue
'''


def privatecloud_list(client: AVSClient, resource_group_name=None):
    if resource_group_name is None:
        return client.private_clouds.list_in_subscription()
    return client.private_clouds.list(resource_group_name)


def privatecloud_show(client: AVSClient, resource_group_name, name):
    return client.private_clouds.get(resource_group_name, name)


def privatecloud_addavailabilityzone(client: AVSClient, resource_group_name, private_cloud, strategy=None, zone=None, secondary_zone=None):
    from azext_vmware.vendored_sdks.avs_client.models import AvailabilityProperties
    pc = client.private_clouds.get(resource_group_name, private_cloud)
    pc.availability = AvailabilityProperties(strategy=strategy, zone=zone, secondary_zone=secondary_zone)
    return client.private_clouds.begin_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, private_cloud_update=pc)


# pylint: disable=too-many-locals
def privatecloud_create(client: AVSClient, resource_group_name, name, sku, cluster_size, network_block, location=None, internet=None, vcenter_password=None, nsxt_password=None, strategy=None, zone=None, secondary_zone=None, tags=None, accept_eula=False, mi_system_assigned=False, yes=False):
    from knack.prompting import prompt_y_n
    if not accept_eula:
        print(LEGAL_TERMS)
        msg = 'Do you agree to the above additional terms for AVS?'
        if not yes and not prompt_y_n(msg, default="n"):
            return None
    from azext_vmware.vendored_sdks.avs_client.models import PrivateCloud, Circuit, ManagementCluster, Sku, PrivateCloudIdentity, ResourceIdentityType, AvailabilityProperties, AvailabilityStrategy
    cloud = PrivateCloud(sku=Sku(name=sku), ciruit=Circuit(), management_cluster=ManagementCluster(cluster_size=cluster_size), network_block=network_block)
    if location is not None:
        cloud.location = location
    if tags is not None:
        cloud.tags = tags
    if mi_system_assigned:
        cloud.identity = PrivateCloudIdentity(type=ResourceIdentityType.SYSTEM_ASSIGNED)
    else:
        cloud.identity = PrivateCloudIdentity(type=ResourceIdentityType.NONE)
    if internet is not None:
        cloud.internet = internet
    if vcenter_password is not None:
        cloud.vcenter_password = vcenter_password
    if nsxt_password is not None:
        cloud.nsxt_password = nsxt_password
    if strategy == AvailabilityStrategy.SINGLE_ZONE:
        cloud.availability = AvailabilityProperties(strategy=AvailabilityStrategy.SINGLE_ZONE, zone=zone, secondary_zone=secondary_zone)
    if strategy == AvailabilityStrategy.DUAL_ZONE:
        cloud.availability = AvailabilityProperties(strategy=AvailabilityStrategy.DUAL_ZONE, zone=zone, secondary_zone=secondary_zone)
    return client.private_clouds.begin_create_or_update(resource_group_name, name, cloud)


def privatecloud_update(client: AVSClient, resource_group_name, name, cluster_size=None, internet=None, tags=None):
    from azext_vmware.vendored_sdks.avs_client.models import ManagementCluster
    private_cloud_update = client.private_clouds.get(resource_group_name, name)
    if tags is not None:
        private_cloud_update.tags = tags
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


def privatecloud_deleteidentitysource(client: AVSClient, resource_group_name, name, private_cloud, alias, domain, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the identity source. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    pc = client.private_clouds.get(resource_group_name, private_cloud)
    found = next((ids for ids in pc.identity_sources
                 if ids.name == name and ids.alias == alias and ids.domain == domain), None)
    if found:
        pc.identity_sources.remove(found)
        return client.private_clouds.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, private_cloud=pc)
    return pc


def privatecloud_addcmkencryption(client: AVSClient, resource_group_name, private_cloud, enc_kv_key_name=None, enc_kv_key_version=None, enc_kv_url=None):
    from azext_vmware.vendored_sdks.avs_client.models import Encryption, EncryptionKeyVaultProperties, EncryptionState
    pc = client.private_clouds.get(resource_group_name, private_cloud)
    pc.encryption = Encryption(status=EncryptionState.ENABLED, key_vault_properties=EncryptionKeyVaultProperties(key_name=enc_kv_key_name, key_version=enc_kv_key_version, key_vault_url=enc_kv_url))
    return client.private_clouds.begin_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, private_cloud_update=pc)


def privatecloud_deletecmkenryption(client: AVSClient, resource_group_name, private_cloud, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the managed keys encryption. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    from azext_vmware.vendored_sdks.avs_client.models import Encryption, EncryptionState
    pc = client.private_clouds.get(resource_group_name, private_cloud)
    pc.encryption = Encryption(status=EncryptionState.DISABLED)
    return client.private_clouds.begin_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, private_cloud_update=pc)


def privatecloud_identity_assign(client: AVSClient, resource_group_name, private_cloud, system_assigned=False):
    from azext_vmware.vendored_sdks.avs_client.models import PrivateCloudIdentity, ResourceIdentityType
    pc = client.private_clouds.get(resource_group_name, private_cloud)
    if system_assigned:
        pc.identity = PrivateCloudIdentity(type=ResourceIdentityType.SYSTEM_ASSIGNED)
    return client.private_clouds.begin_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, private_cloud_update=pc)


def privatecloud_identity_remove(client: AVSClient, resource_group_name, private_cloud, system_assigned=False):
    from azext_vmware.vendored_sdks.avs_client.models import PrivateCloudIdentity, ResourceIdentityType
    pc = client.private_clouds.get(resource_group_name, private_cloud)
    if system_assigned:
        pc.identity = PrivateCloudIdentity(type=ResourceIdentityType.NONE)
    return client.private_clouds.begin_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, private_cloud_update=pc)


def privatecloud_identity_get(client: AVSClient, resource_group_name, private_cloud):
    return client.private_clouds.get(resource_group_name, private_cloud).identity


def privatecloud_rotate_vcenter_password(client: AVSClient, resource_group_name, private_cloud, yes=False):
    from knack.prompting import prompt_y_n
    msg = ROTATE_VCENTER_PASSWORD_TERMS
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.private_clouds.begin_rotate_vcenter_password(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def privatecloud_rotate_nsxt_password():
    from knack.prompting import prompt
    msg = ROTATE_NSXT_PASSWORD_TERMS
    prompt(msg)
    # return client.private_clouds.begin_rotate_nsxt_password(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def cluster_create(client: AVSClient, resource_group_name, name, sku, private_cloud, size, hosts):
    from azext_vmware.vendored_sdks.avs_client.models import Sku, Cluster
    return client.clusters.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name, cluster=Cluster(sku=Sku(name=sku), cluster_size=size, hosts=hosts))


def cluster_update(client: AVSClient, resource_group_name, name, private_cloud, size=None, hosts=None):
    from azext_vmware.vendored_sdks.avs_client.models import ClusterUpdate
    return client.clusters.begin_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name, cluster_update=ClusterUpdate(cluster_size=size, hosts=hosts))


def cluster_list(client: AVSClient, resource_group_name, private_cloud):
    return client.clusters.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def cluster_show(client: AVSClient, resource_group_name, private_cloud, name):
    return client.clusters.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name)


def cluster_delete(client: AVSClient, resource_group_name, private_cloud, name, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the cluster. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.clusters.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name)


def cluster_list_zones(client: AVSClient, resource_group_name, private_cloud, name):
    return client.clusters.list_zones(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name)


def check_quota_availability(client: AVSClient, location):
    return client.locations.check_quota_availability(location)


def check_trial_availability(client: AVSClient, location, sku=None):
    from azext_vmware.vendored_sdks.avs_client.models import Sku
    return client.locations.check_trial_availability(location=location, sku=Sku(name=sku))


def authorization_create(client: AVSClient, resource_group_name, private_cloud, name, express_route_id=None):
    from azext_vmware.vendored_sdks.avs_client.models import ExpressRouteAuthorization
    return client.authorizations.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, authorization_name=name, authorization=ExpressRouteAuthorization(express_route_id=express_route_id))


def authorization_list(client: AVSClient, resource_group_name, private_cloud):
    return client.authorizations.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def authorization_show(client: AVSClient, resource_group_name, private_cloud, name):
    return client.authorizations.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, authorization_name=name)


def authorization_delete(client: AVSClient, resource_group_name, private_cloud, name, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the authorization. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.authorizations.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, authorization_name=name)


def hcxenterprisesite_create(client: AVSClient, resource_group_name, private_cloud, name):
    from azext_vmware.vendored_sdks.avs_client.models import HcxEnterpriseSite
    return client.hcx_enterprise_sites.create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, hcx_enterprise_site_name=name, hcx_enterprise_site=HcxEnterpriseSite())


def hcxenterprisesite_list(client: AVSClient, resource_group_name, private_cloud):
    return client.hcx_enterprise_sites.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def hcxenterprisesite_show(client: AVSClient, resource_group_name, private_cloud, name):
    return client.hcx_enterprise_sites.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, hcx_enterprise_site_name=name)


def hcxenterprisesite_delete(client: AVSClient, resource_group_name, private_cloud, name, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the HCX enterprise site. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.hcx_enterprise_sites.delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, hcx_enterprise_site_name=name)


def datastore_create():
    print('Please use "az vmware datastore netapp-volume create" or "az vmware datastore disk-pool-volume create" instead.')


def datastore_netappvolume_create(client: AVSClient, resource_group_name, private_cloud, cluster, name, volume_id):
    from azext_vmware.vendored_sdks.avs_client.models import NetAppVolume, Datastore
    net_app_volume = NetAppVolume(id=volume_id)
    return client.datastores.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster, datastore_name=name, datastore=Datastore(net_app_volume=net_app_volume))


def datastore_diskpoolvolume_create(client: AVSClient, resource_group_name, private_cloud, cluster, name, target_id, lun_name, mount_option="MOUNT"):
    from azext_vmware.vendored_sdks.avs_client.models import DiskPoolVolume, Datastore
    disk_pool_volume = DiskPoolVolume(target_id=target_id, lun_name=lun_name, mount_option=mount_option)
    return client.datastores.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster, datastore_name=name, datastore=Datastore(disk_pool_volume=disk_pool_volume))


def datastore_list(client: AVSClient, resource_group_name, private_cloud, cluster):
    return client.datastores.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster)


def datastore_show(client: AVSClient, resource_group_name, private_cloud, cluster, name):
    return client.datastores.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster, datastore_name=name)


def datastore_delete(client: AVSClient, resource_group_name, private_cloud, cluster, name, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the datastore. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.datastores.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster, datastore_name=name)


def addon_list(client: AVSClient, resource_group_name, private_cloud):
    return client.addons.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def addon_vr_create(client: AVSClient, resource_group_name, private_cloud, vrs_count: int):
    from azext_vmware.vendored_sdks.avs_client.models import AddonVrProperties, Addon
    properties = AddonVrProperties(vrs_count=vrs_count)
    return client.addons.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="vr", addon=Addon(properties=properties))


def addon_hcx_create(client: AVSClient, resource_group_name, private_cloud, offer: str):
    from azext_vmware.vendored_sdks.avs_client.models import AddonHcxProperties, Addon
    properties = AddonHcxProperties(offer=offer)
    return client.addons.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="hcx", addon=Addon(properties=properties))


def addon_srm_create(client: AVSClient, resource_group_name, private_cloud, license_key: str):
    from azext_vmware.vendored_sdks.avs_client.models import AddonSrmProperties, Addon
    properties = AddonSrmProperties(license_key=license_key)
    return client.addons.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="srm", addon=Addon(properties=properties))


def addon_arc_create(client: AVSClient, resource_group_name, private_cloud, vcenter: str):
    from azext_vmware.vendored_sdks.avs_client.models import AddonArcProperties, Addon
    properties = AddonArcProperties(v_center=vcenter)
    return client.addons.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="arc", addon=Addon(properties=properties))


def addon_vr_show(client: AVSClient, resource_group_name, private_cloud):
    return client.addons.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="vr")


def addon_hcx_show(client: AVSClient, resource_group_name, private_cloud):
    return client.addons.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="hcx")


def addon_srm_show(client: AVSClient, resource_group_name, private_cloud):
    return client.addons.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="srm")


def addon_arc_show(client: AVSClient, resource_group_name, private_cloud):
    return client.addons.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="arc")


def addon_vr_update(client: AVSClient, resource_group_name, private_cloud, vrs_count: int):
    from azext_vmware.vendored_sdks.avs_client.models import AddonVrProperties, Addon
    properties = AddonVrProperties(vrs_count=vrs_count)
    return client.addons.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="vr", addon=Addon(properties=properties))


def addon_hcx_update(client: AVSClient, resource_group_name, private_cloud, offer: str):
    from azext_vmware.vendored_sdks.avs_client.models import AddonHcxProperties, Addon
    properties = AddonHcxProperties(offer=offer)
    return client.addons.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="hcx", addon=Addon(properties=properties))


def addon_srm_update(client: AVSClient, resource_group_name, private_cloud, license_key: str):
    from azext_vmware.vendored_sdks.avs_client.models import AddonSrmProperties, Addon
    properties = AddonSrmProperties(license_key=license_key)
    return client.addons.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="srm", addon=Addon(properties=properties))


def addon_arc_update(client: AVSClient, resource_group_name, private_cloud, vcenter: str):
    from azext_vmware.vendored_sdks.avs_client.models import AddonArcProperties, Addon
    properties = AddonArcProperties(v_center=vcenter)
    return client.addons.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="arc", addon=Addon(properties=properties))


def addon_vr_delete(client: AVSClient, resource_group_name, private_cloud, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the VR addon. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.addons.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="vr")


def addon_hcx_delete(client: AVSClient, resource_group_name, private_cloud, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the HCX addon. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.addons.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="hcx")


def addon_srm_delete(client: AVSClient, resource_group_name, private_cloud, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the SRM addon. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.addons.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="srm")


def addon_arc_delete(client: AVSClient, resource_group_name, private_cloud, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the Arc addon. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.addons.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, addon_name="arc")


def globalreachconnection_create(client: AVSClient, resource_group_name, private_cloud, name, authorization_key=None, peer_express_route_circuit=None, express_route_id=None):
    from azext_vmware.vendored_sdks.avs_client.models import GlobalReachConnection
    return client.global_reach_connections.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, global_reach_connection_name=name, global_reach_connection=GlobalReachConnection(authorization_key=authorization_key, peer_express_route_circuit=peer_express_route_circuit, express_route_id=express_route_id))


def globalreachconnection_list(client: AVSClient, resource_group_name, private_cloud):
    return client.global_reach_connections.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def globalreachconnection_show(client: AVSClient, resource_group_name, private_cloud, name):
    return client.global_reach_connections.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, global_reach_connection_name=name)


def globalreachconnection_delete(client: AVSClient, resource_group_name, private_cloud, name, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the global reach connection. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.global_reach_connections.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, global_reach_connection_name=name)


def cloud_link_create(client: AVSClient, resource_group_name, name, private_cloud, linked_cloud):
    from azext_vmware.vendored_sdks.avs_client.models import CloudLink
    return client.cloud_links.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cloud_link_name=name, cloud_link=CloudLink(linked_cloud=linked_cloud))


def cloud_link_list(client: AVSClient, resource_group_name, private_cloud):
    return client.cloud_links.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def cloud_link_show(client: AVSClient, resource_group_name, private_cloud, name):
    return client.cloud_links.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cloud_link_name=name)


def cloud_link_delete(client: AVSClient, resource_group_name, private_cloud, name, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the cloud link. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.cloud_links.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cloud_link_name=name)


def script_cmdlet_list(client: AVSClient, resource_group_name, private_cloud, script_package):
    return client.script_cmdlets.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud, script_package_name=script_package)


def script_cmdlet_show(client: AVSClient, resource_group_name, private_cloud, script_package, name):
    return client.script_cmdlets.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, script_package_name=script_package, script_cmdlet_name=name)


def script_package_list(client: AVSClient, resource_group_name, private_cloud):
    return client.script_packages.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def script_package_show(client: AVSClient, resource_group_name, private_cloud, name):
    return client.script_packages.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, script_package_name=name)


def script_execution_create(client: AVSClient, resource_group_name, private_cloud, name, timeout, script_cmdlet_id=None, parameters=None, hidden_parameters=None, failure_reason=None, retention=None, out=None, named_outputs: List[Tuple[str, str]] = None):
    from azext_vmware.vendored_sdks.avs_client.models import ScriptExecution
    if named_outputs is not None:
        named_outputs = dict(named_outputs)
    script_execution = ScriptExecution(timeout=timeout, script_cmdlet_id=script_cmdlet_id, parameters=parameters, hidden_parameters=hidden_parameters, failure_reason=failure_reason, retention=retention, output=out, named_outputs=named_outputs)
    return client.script_executions.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, script_execution_name=name, script_execution=script_execution)


def script_execution_list(client: AVSClient, resource_group_name, private_cloud):
    return client.script_executions.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def script_execution_show(client: AVSClient, resource_group_name, private_cloud, name):
    return client.script_executions.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, script_execution_name=name)


def script_execution_delete(client: AVSClient, resource_group_name, private_cloud, name, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the script execution. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.script_executions.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, script_execution_name=name)


def script_execution_logs(client: AVSClient, resource_group_name, private_cloud, name):
    return client.script_executions.get_execution_logs(resource_group_name=resource_group_name, private_cloud_name=private_cloud, script_execution_name=name)


def workload_network_dhcp_server_create(client: AVSClient, resource_group_name, private_cloud, dhcp: str, display_name=None, revision=None, server_address=None, lease_time=None):
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkDhcpServer, WorkloadNetworkDhcp
    properties = WorkloadNetworkDhcp(properties=WorkloadNetworkDhcpServer(dhcp_type="SERVER", display_name=display_name, revision=revision, server_address=server_address, lease_time=lease_time))
    return client.workload_networks.begin_create_dhcp(resource_group_name=resource_group_name, private_cloud_name=private_cloud, dhcp_id=dhcp, workload_network_dhcp=properties)


def workload_network_dhcp_relay_create(client: AVSClient, resource_group_name, private_cloud, dhcp: str, display_name=None, revision=None, server_addresses=None):
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkDhcpRelay, WorkloadNetworkDhcp
    properties = WorkloadNetworkDhcp(properties=WorkloadNetworkDhcpRelay(dhcp_type="RELAY", display_name=display_name, revision=revision, server_addresses=server_addresses))
    return client.workload_networks.begin_create_dhcp(resource_group_name=resource_group_name, private_cloud_name=private_cloud, dhcp_id=dhcp, workload_network_dhcp=properties)


def workload_network_dhcp_server_update(client: AVSClient, resource_group_name, private_cloud, dhcp: str, display_name=None, revision=None, server_address=None, lease_time=None):
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkDhcpServer, WorkloadNetworkDhcp
    properties = WorkloadNetworkDhcp(properties=WorkloadNetworkDhcpServer(dhcp_type="SERVER", display_name=display_name, revision=revision, server_address=server_address, lease_time=lease_time))
    return client.workload_networks.begin_update_dhcp(resource_group_name=resource_group_name, private_cloud_name=private_cloud, dhcp_id=dhcp, workload_network_dhcp=properties)


def workload_network_dhcp_relay_update(client: AVSClient, resource_group_name, private_cloud, dhcp: str, display_name=None, revision=None, server_addresses=None):
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkDhcpRelay, WorkloadNetworkDhcp
    properties = WorkloadNetworkDhcp(properties=WorkloadNetworkDhcpRelay(dhcp_type="RELAY", display_name=display_name, revision=revision, server_addresses=server_addresses))
    return client.workload_networks.begin_update_dhcp(resource_group_name=resource_group_name, private_cloud_name=private_cloud, dhcp_id=dhcp, workload_network_dhcp=properties)


def workload_network_dhcp_delete(client: AVSClient, resource_group_name, private_cloud, dhcp: str, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the workload network DHCP. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.workload_networks.begin_delete_dhcp(resource_group_name=resource_group_name, private_cloud_name=private_cloud, dhcp_id=dhcp)


def workload_network_dhcp_list(client: AVSClient, resource_group_name, private_cloud):
    return client.workload_networks.list_dhcp(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def workload_network_dhcp_show(client: AVSClient, resource_group_name, private_cloud, dhcp: str):
    return client.workload_networks.get_dhcp(resource_group_name=resource_group_name, private_cloud_name=private_cloud, dhcp_id=dhcp)


def workload_network_dns_services_list(client: AVSClient, resource_group_name, private_cloud):
    return client.workload_networks.list_dns_services(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def workload_network_dns_services_get(client: AVSClient, resource_group_name, private_cloud, dns_service):
    return client.workload_networks.get_dns_service(resource_group_name=resource_group_name, private_cloud_name=private_cloud, dns_service_id=dns_service)


def workload_network_dns_services_create(client: AVSClient, resource_group_name, private_cloud, dns_service, display_name=None, dns_service_ip=None, default_dns_zone=None, fqdn_zones=None, log_level=None, revision=None):
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkDnsService
    prop = WorkloadNetworkDnsService(display_name=display_name, dns_service_ip=dns_service_ip, default_dns_zone=default_dns_zone, log_level=log_level, revision=revision, fqdn_zones=fqdn_zones)
    return client.workload_networks.begin_create_dns_service(resource_group_name=resource_group_name, private_cloud_name=private_cloud, dns_service_id=dns_service, workload_network_dns_service=prop)


def workload_network_dns_services_update(client: AVSClient, resource_group_name, private_cloud, dns_service, display_name=None, dns_service_ip=None, default_dns_zone=None, fqdn_zones=None, log_level=None, revision=None):
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkDnsService
    prop = WorkloadNetworkDnsService(display_name=display_name, dns_service_ip=dns_service_ip, default_dns_zone=default_dns_zone, fqdn_zones=fqdn_zones, log_level=log_level, revision=revision)
    return client.workload_networks.begin_update_dns_service(resource_group_name=resource_group_name, private_cloud_name=private_cloud, dns_service_id=dns_service, workload_network_dns_service=prop)


def workload_network_dns_services_delete(client: AVSClient, resource_group_name, private_cloud, dns_service, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the workload network DNS services. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.workload_networks.begin_delete_dns_service(resource_group_name=resource_group_name, private_cloud_name=private_cloud, dns_service_id=dns_service)


def workload_network_dns_zone_list(client: AVSClient, resource_group_name, private_cloud):
    return client.workload_networks.list_dns_zones(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def workload_network_dns_zone_get(client: AVSClient, resource_group_name, private_cloud, dns_zone):
    return client.workload_networks.get_dns_zone(resource_group_name=resource_group_name, private_cloud_name=private_cloud, dns_zone_id=dns_zone)


def workload_network_dns_zone_create(client: AVSClient, resource_group_name, private_cloud, dns_zone, display_name=None, domain=None, dns_server_ips=None, source_ip=None, dns_services=None, revision=None):
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkDnsZone
    prop = WorkloadNetworkDnsZone(display_name=display_name, domain=domain, dns_server_ips=dns_server_ips, source_ip=source_ip, dns_services=dns_services, revision=revision)
    return client.workload_networks.begin_create_dns_zone(resource_group_name=resource_group_name, private_cloud_name=private_cloud, dns_zone_id=dns_zone, workload_network_dns_zone=prop)


def workload_network_dns_zone_update(client: AVSClient, resource_group_name, private_cloud, dns_zone, display_name=None, domain=None, dns_server_ips=None, source_ip=None, dns_services=None, revision=None):
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkDnsZone
    prop = WorkloadNetworkDnsZone(display_name=display_name, domain=domain, dns_server_ips=dns_server_ips, source_ip=source_ip, dns_services=dns_services, revision=revision)
    return client.workload_networks.begin_update_dns_zone(resource_group_name=resource_group_name, private_cloud_name=private_cloud, dns_zone_id=dns_zone, workload_network_dns_zone=prop)


def workload_network_dns_zone_delete(client: AVSClient, resource_group_name, private_cloud, dns_zone, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the workload network DNS zone. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.workload_networks.begin_delete_dns_zone(resource_group_name=resource_group_name, private_cloud_name=private_cloud, dns_zone_id=dns_zone)


def workload_network_port_mirroring_list(client: AVSClient, resource_group_name, private_cloud):
    return client.workload_networks.list_port_mirroring(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def workload_network_port_mirroring_get(client: AVSClient, resource_group_name, private_cloud, port_mirroring):
    return client.workload_networks.get_port_mirroring(resource_group_name=resource_group_name, private_cloud_name=private_cloud, port_mirroring_id=port_mirroring)


def workload_network_port_mirroring_create(client: AVSClient, resource_group_name, private_cloud, port_mirroring, display_name=None, direction=None, source=None, destination=None, revision=None):
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkPortMirroring
    prop = WorkloadNetworkPortMirroring(display_name=display_name, direction=direction, source=source, destination=destination, revision=revision)
    return client.workload_networks.begin_create_port_mirroring(resource_group_name=resource_group_name, private_cloud_name=private_cloud, port_mirroring_id=port_mirroring, workload_network_port_mirroring=prop)


def workload_network_port_mirroring_update(client: AVSClient, resource_group_name, private_cloud, port_mirroring, display_name=None, direction=None, source=None, destination=None, revision=None):
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkPortMirroring
    prop = WorkloadNetworkPortMirroring(display_name=display_name, direction=direction, source=source, destination=destination, revision=revision)
    return client.workload_networks.begin_update_port_mirroring(resource_group_name=resource_group_name, private_cloud_name=private_cloud, port_mirroring_id=port_mirroring, workload_network_port_mirroring=prop)


def workload_network_port_mirroring_delete(client: AVSClient, resource_group_name, private_cloud, port_mirroring, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the workload network port mirroring. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.workload_networks.begin_delete_port_mirroring(resource_group_name=resource_group_name, private_cloud_name=private_cloud, port_mirroring_id=port_mirroring)


def workload_network_segment_list(client: AVSClient, resource_group_name, private_cloud):
    return client.workload_networks.list_segments(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def workload_network_segment_get(client: AVSClient, resource_group_name, private_cloud, segment):
    return client.workload_networks.get_segment(resource_group_name=resource_group_name, private_cloud_name=private_cloud, segment_id=segment)


def workload_network_segment_create(client: AVSClient, resource_group_name, private_cloud, segment, display_name=None, connected_gateway=None, revision=None, dhcp_ranges=None, gateway_address=None, port_name=None):
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkSegmentPortVif
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkSegmentSubnet
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkSegment
    portVif = WorkloadNetworkSegmentPortVif(port_name=port_name)
    subnet = WorkloadNetworkSegmentSubnet(dhcp_ranges=dhcp_ranges, gateway_address=gateway_address)
    segmentObj = WorkloadNetworkSegment(display_name=display_name, connected_gateway=connected_gateway, subnet=subnet, port_vif=portVif, revision=revision)
    return client.workload_networks.begin_create_segments(resource_group_name=resource_group_name, private_cloud_name=private_cloud, segment_id=segment, workload_network_segment=segmentObj)


def workload_network_segment_update(client: AVSClient, resource_group_name, private_cloud, segment, display_name=None, connected_gateway=None, revision=None, dhcp_ranges=None, gateway_address=None, port_name=None):
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkSegmentPortVif
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkSegmentSubnet
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkSegment
    portVif = WorkloadNetworkSegmentPortVif(port_name=port_name)
    subnet = WorkloadNetworkSegmentSubnet(dhcp_ranges=dhcp_ranges, gateway_address=gateway_address)
    segmentObj = WorkloadNetworkSegment(display_name=display_name, connected_gateway=connected_gateway, subnet=subnet, port_vif=portVif, revision=revision)
    return client.workload_networks.begin_update_segments(resource_group_name=resource_group_name, private_cloud_name=private_cloud, segment_id=segment, workload_network_segment=segmentObj)


def workload_network_segment_delete(client: AVSClient, resource_group_name, private_cloud, segment, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the workload network segment. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.workload_networks.begin_delete_segment(resource_group_name=resource_group_name, private_cloud_name=private_cloud, segment_id=segment)


def workload_network_public_ip_list(client: AVSClient, resource_group_name, private_cloud):
    return client.workload_networks.list_public_i_ps(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def workload_network_public_ip_get(client: AVSClient, resource_group_name, private_cloud, public_ip):
    return client.workload_networks.get_public_ip(resource_group_name=resource_group_name, private_cloud_name=private_cloud, public_ip_id=public_ip)


def workload_network_public_ip_create(client: AVSClient, resource_group_name, private_cloud, public_ip, display_name=None, number_of_public_ips=None):
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkPublicIP
    return client.workload_networks.begin_create_public_ip(resource_group_name=resource_group_name, private_cloud_name=private_cloud, public_ip_id=public_ip, workload_network_public_ip=WorkloadNetworkPublicIP(display_name=display_name, number_of_public_i_ps=number_of_public_ips))


def workload_network_public_ip_delete(client: AVSClient, resource_group_name, private_cloud, public_ip, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the workload network public IP. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.workload_networks.begin_delete_public_ip(resource_group_name=resource_group_name, private_cloud_name=private_cloud, public_ip_id=public_ip)


def workload_network_vm_group_list(client: AVSClient, resource_group_name, private_cloud):
    return client.workload_networks.list_vm_groups(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def workload_network_vm_group_get(client: AVSClient, resource_group_name, private_cloud, vm_group):
    return client.workload_networks.get_vm_group(resource_group_name=resource_group_name, private_cloud_name=private_cloud, vm_group_id=vm_group)


def workload_network_vm_group_create(client: AVSClient, resource_group_name, private_cloud, vm_group, display_name=None, members=None, revision=None):
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkVMGroup
    vmGroup = WorkloadNetworkVMGroup(display_name=display_name, members=members, revision=revision)
    return client.workload_networks.begin_create_vm_group(resource_group_name=resource_group_name, private_cloud_name=private_cloud, vm_group_id=vm_group, workload_network_vm_group=vmGroup)


def workload_network_vm_group_update(client: AVSClient, resource_group_name, private_cloud, vm_group, display_name=None, members=None, revision=None):
    from azext_vmware.vendored_sdks.avs_client.models import WorkloadNetworkVMGroup
    vmGroup = WorkloadNetworkVMGroup(display_name=display_name, members=members, revision=revision)
    return client.workload_networks.begin_update_vm_group(resource_group_name=resource_group_name, private_cloud_name=private_cloud, vm_group_id=vm_group, workload_network_vm_group=vmGroup)


def workload_network_vm_group_delete(client: AVSClient, resource_group_name, private_cloud, vm_group, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the workload network VM group. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.workload_networks.begin_delete_vm_group(resource_group_name=resource_group_name, private_cloud_name=private_cloud, vm_group_id=vm_group)


def workload_network_vm_list(client: AVSClient, resource_group_name, private_cloud):
    return client.workload_networks.list_virtual_machines(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def workload_network_vm_get(client: AVSClient, resource_group_name, private_cloud, virtual_machine):
    return client.workload_networks.get_virtual_machine(resource_group_name=resource_group_name, private_cloud_name=private_cloud, virtual_machine_id=virtual_machine)


def workload_network_gateway_list(client: AVSClient, resource_group_name, private_cloud):
    return client.workload_networks.list_gateways(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def workload_network_gateway_get(client: AVSClient, resource_group_name, private_cloud, gateway):
    return client.workload_networks.get_gateway(resource_group_name=resource_group_name, private_cloud_name=private_cloud, gateway_id=gateway)


def placement_policy_list(client: AVSClient, resource_group_name, private_cloud, cluster_name):
    return client.placement_policies.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster_name)


def placement_policy_get(client: AVSClient, resource_group_name, private_cloud, cluster_name, placement_policy_name):
    return client.placement_policies.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster_name, placement_policy_name=placement_policy_name)


def placement_policy_vm_create(client: AVSClient, resource_group_name, private_cloud, cluster_name, placement_policy_name, vm_members, affinity_type, state=None, display_name=None):
    from azext_vmware.vendored_sdks.avs_client.models import VmPlacementPolicyProperties, PlacementPolicy
    vmProperties = PlacementPolicy(properties=VmPlacementPolicyProperties(type="VmVm", state=state, display_name=display_name, vm_members=vm_members, affinity_type=affinity_type))
    return client.placement_policies.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster_name, placement_policy_name=placement_policy_name, placement_policy=vmProperties)


def placement_policy_vm_host_create(client: AVSClient, resource_group_name, private_cloud, cluster_name, placement_policy_name, vm_members, host_members, affinity_type, state=None, display_name=None, affinity_strength=None, azure_hybrid_benefit=None):
    from azext_vmware.vendored_sdks.avs_client.models import VmHostPlacementPolicyProperties, PlacementPolicy
    vmHostProperties = PlacementPolicy(properties=VmHostPlacementPolicyProperties(type="VmHost", state=state, display_name=display_name, vm_members=vm_members, host_members=host_members, affinity_type=affinity_type, affinity_strength=affinity_strength, azure_hybrid_benefit_type=azure_hybrid_benefit))
    return client.placement_policies.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster_name, placement_policy_name=placement_policy_name, placement_policy=vmHostProperties)


def placement_policy_update(client: AVSClient, resource_group_name, private_cloud, cluster_name, placement_policy_name, state=None, vm_members=None, host_members=None, affinity_strength=None, azure_hybrid_benefit=None):
    from azext_vmware.vendored_sdks.avs_client.models import PlacementPolicyUpdate
    props = PlacementPolicyUpdate(state=state, vm_members=vm_members, host_members=host_members, affinity_strength=affinity_strength, azure_hybrid_benefit_type=azure_hybrid_benefit)
    return client.placement_policies.begin_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster_name, placement_policy_name=placement_policy_name, placement_policy_update=props)


def placement_policy_delete(client: AVSClient, resource_group_name, private_cloud, cluster_name, placement_policy_name, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the placement policy. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return None
    return client.placement_policies.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster_name, placement_policy_name=placement_policy_name)


def virtual_machine_get(client: AVSClient, resource_group_name, private_cloud, cluster_name, virtual_machine):
    return client.virtual_machines.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster_name, virtual_machine_id=virtual_machine)


def virtual_machine_list(client: AVSClient, resource_group_name, private_cloud, cluster_name):
    return client.virtual_machines.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster_name)


def virtual_machine_restrict(client: AVSClient, resource_group_name, private_cloud, cluster_name, virtual_machine, restrict_movement):
    from azext_vmware.vendored_sdks.avs_client.models import VirtualMachineRestrictMovement
    return client.virtual_machines.begin_restrict_movement(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster_name, virtual_machine_id=virtual_machine, restrict_movement=VirtualMachineRestrictMovement(restrict_movement=restrict_movement))
