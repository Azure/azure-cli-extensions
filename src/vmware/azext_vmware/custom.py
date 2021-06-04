# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azext_vmware.vendored_sdks.avs_client import AVSClient

LEGAL_TERMS = '''
LEGAL TERMS

Azure VMware Solution ("AVS") is an Azure Service licensed to you as part of your Azure subscription and subject to the terms and conditions of the agreement under which you obtained your Azure subscription (https://azure.microsoft.com/support/legal/). The following additional terms also apply to your use of AVS:

DATA RETENTION. AVS does not currently support retention or extraction of data stored in AVS Clusters. Once an AVS Cluster is deleted, the data cannot be recovered as it terminates all running workloads, components, and destroys all Cluster data and configuration settings, including public IP addresses.

PROFESSIONAL SERVICES DATA TRANSFER TO VMWARE. In the event that you contact Microsoft for technical support relating to Azure VMware Solution and Microsoft must engage VMware for assistance with the issue, Microsoft will transfer the Professional Services Data and the Personal Data contained in the support case to VMware. The transfer is made subject to the terms of the Support Transfer Agreement between VMware and Microsoft, which establishes Microsoft and VMware as independent processors of the Professional Services Data. Before any transfer of Professional Services Data to VMware will occur, Microsoft will obtain and record consent from you for the transfer.

VMWARE DATA PROCESSING AGREEMENT. Once Professional Services Data is transferred to VMware (pursuant to the above section), the processing of Professional Services Data, including the Personal Data contained the support case, by VMware as an independent processor will be governed by the VMware Data Processing Agreement for Microsoft AVS Customers Transferred for L3 Support (the "VMware Data Processing Agreement") between you and VMware (located at https://www.vmware.com/content/dam/digitalmarketing/vmware/en/pdf/privacy/vmware-data-processing-agreement.pdf). You also give authorization to allow your representative(s) who request technical support for Azure VMware Solution to provide consent on your behalf to Microsoft for the transfer of the Professional Services Data to VMware.

ACCEPTANCE OF LEGAL TERMS. By continuing, you agree to the above additional Legal Terms for AVS. If you are an individual accepting these terms on behalf of an entity, you also represent that you have the legal authority to enter into these additional terms on that entity's behalf.
'''


def privatecloud_list(cmd, client: AVSClient, resource_group_name=None):
    if resource_group_name is None:
        return client.private_clouds.list_in_subscription()
    else:
        return client.private_clouds.list(resource_group_name)


def privatecloud_show(cmd, client: AVSClient, resource_group_name, name):
    return client.private_clouds.get(resource_group_name, name)


def privatecloud_create(cmd, client: AVSClient, resource_group_name, name, location, sku, cluster_size, network_block, circuit_primary_subnet=None, circuit_secondary_subnet=None, internet=None, vcenter_password=None, nsxt_password=None, tags=[], accept_eula=False):
    from knack.prompting import prompt_y_n
    if not accept_eula:
        print(LEGAL_TERMS)
        msg = 'Do you agree to the above additional terms for AVS?'
        if not prompt_y_n(msg, default="n"):
            return

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


def privatecloud_update(cmd, client: AVSClient, resource_group_name, name, cluster_size=None, internet=None):
    from azext_vmware.vendored_sdks.avs_client.models import PrivateCloudUpdate, ManagementCluster
    private_cloud_update = PrivateCloudUpdate()
    if cluster_size is not None:
        private_cloud_update.management_cluster = ManagementCluster(cluster_size=cluster_size)
    if internet is not None:
        private_cloud_update.internet = internet
    return client.private_clouds.begin_update(resource_group_name, name, private_cloud_update)


def privatecloud_delete(cmd, client: AVSClient, resource_group_name, name, yes=False):
    from knack.prompting import prompt_y_n
    msg = 'This will delete the private cloud. Are you sure?'
    if not yes and not prompt_y_n(msg, default="n"):
        return
    return client.private_clouds.begin_delete(resource_group_name, name)


def privatecloud_listadmincredentials(cmd, client: AVSClient, resource_group_name, private_cloud):
    return client.private_clouds.list_admin_credentials(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def privatecloud_addidentitysource(cmd, client: AVSClient, resource_group_name, name, private_cloud, alias, domain, base_user_dn, base_group_dn, primary_server, username, password, secondary_server=None, ssl="Disabled"):
    from azext_vmware.vendored_sdks.avs_client.models import IdentitySource
    pc = client.private_clouds.get(resource_group_name, private_cloud)
    identitysource = IdentitySource(name=name, alias=alias, domain=domain, base_user_dn=base_user_dn, base_group_dn=base_group_dn, primary_server=primary_server, ssl=ssl, username=username, password=password)
    if secondary_server is not None:
        identitysource.secondary_server = secondary_server
    pc.identity_sources.append(identitysource)
    return client.private_clouds.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, private_cloud=pc)


def privatecloud_deleteidentitysource(cmd, client: AVSClient, resource_group_name, name, private_cloud, alias, domain):
    from azext_vmware.vendored_sdks.avs_client.models import IdentitySource
    pc = client.private_clouds.get(resource_group_name, private_cloud)
    found = next((ids for ids in pc.identity_sources
                 if ids.name == name and ids.alias == alias and ids.domain == domain), None)
    if found:
        pc.identity_sources.remove(found)
        return client.private_clouds.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, private_cloud=pc)
    else:
        return pc


def privatecloud_rotate_vcenter_password(cmd, client: AVSClient, resource_group_name, private_cloud):
    return client.private_clouds.begin_rotate_vcenter_password(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def privatecloud_rotate_nsxt_password(cmd, client: AVSClient, resource_group_name, private_cloud):
    return client.private_clouds.begin_rotate_nsxt_password(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def cluster_create(cmd, client: AVSClient, resource_group_name, name, sku, private_cloud, size, tags=[]):
    from azext_vmware.vendored_sdks.avs_client.models import Cluster, Sku
    cluster = Cluster(sku=Sku(name=sku), cluster_size=size)
    return client.clusters.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name, cluster=cluster)


def cluster_update(cmd, client: AVSClient, resource_group_name, name, private_cloud, size, tags=[]):
    from azext_vmware.vendored_sdks.avs_client.models import ClusterUpdate
    cluster_update = ClusterUpdate(cluster_size=size)
    return client.clusters.begin_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name, cluster_update=cluster_update)


def cluster_list(cmd, client: AVSClient, resource_group_name, private_cloud):
    return client.clusters.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def cluster_show(cmd, client: AVSClient, resource_group_name, private_cloud, name):
    return client.clusters.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name)


def cluster_delete(cmd, client: AVSClient, resource_group_name, private_cloud, name):
    return client.clusters.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name)


def check_quota_availability(cmd, client: AVSClient, location):
    return client.locations.check_quota_availability(location)


def check_trial_availability(cmd, client: AVSClient, location):
    return client.locations.check_trial_availability(location)


def authorization_create(cmd, client: AVSClient, resource_group_name, private_cloud, name):
    from azext_vmware.vendored_sdks.avs_client.models import ExpressRouteAuthorization
    authorization = ExpressRouteAuthorization()
    return client.authorizations.begin_create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, authorization_name=name, authorization=authorization)


def authorization_list(cmd, client: AVSClient, resource_group_name, private_cloud):
    return client.authorizations.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def authorization_show(cmd, client: AVSClient, resource_group_name, private_cloud, name):
    return client.authorizations.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, authorization_name=name)


def authorization_delete(cmd, client: AVSClient, resource_group_name, private_cloud, name):
    return client.authorizations.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, authorization_name=name)


def hcxenterprisesite_create(cmd, client: AVSClient, resource_group_name, private_cloud, name):
    from azext_vmware.vendored_sdks.avs_client.models import HcxEnterpriseSite
    hcx_enterprise_site = HcxEnterpriseSite()
    return client.hcx_enterprise_sites.create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, hcx_enterprise_site_name=name, hcx_enterprise_site=hcx_enterprise_site)


def hcxenterprisesite_list(cmd, client: AVSClient, resource_group_name, private_cloud):
    return client.hcx_enterprise_sites.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def hcxenterprisesite_show(cmd, client: AVSClient, resource_group_name, private_cloud, name):
    return client.hcx_enterprise_sites.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, hcx_enterprise_site_name=name)


def hcxenterprisesite_delete(cmd, client: AVSClient, resource_group_name, private_cloud, name):
    return client.hcx_enterprise_sites.delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, hcx_enterprise_site_name=name)


def datastore_create(cmd, client: AVSClient, resource_group_name, private_cloud, cluster, name, nfs_provider_ip=None, nfs_file_path=None, endpoints=[], lun_name=None):
    from azext_vmware.vendored_sdks.avs_client.models import Datastore, NetAppVolume, DiskPoolVolume
    datastore = Datastore()
    if nfs_provider_ip is not None or nfs_file_path is not None:
        datastore.net_app_volume = NetAppVolume(nfs_provider_ip=nfs_provider_ip, nfs_file_path=nfs_file_path)
    if len(endpoints) > 0 or lun_name is not None:
        datastore.disk_pool_volume = DiskPoolVolume(endpoints=endpoints, lun_name=lun_name)
    return client.datastores.begin_create(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster, datastore_name=name, datastore=datastore)


def datastore_list(cmd, client: AVSClient, resource_group_name, private_cloud, cluster):
    return client.datastores.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster)


def datastore_show(cmd, client: AVSClient, resource_group_name, private_cloud, cluster, name):
    return client.datastores.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster, datastore_name=name)


def datastore_delete(cmd, client: AVSClient, resource_group_name, private_cloud, cluster, name):
    return client.datastores.begin_delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=cluster, datastore_name=name)
