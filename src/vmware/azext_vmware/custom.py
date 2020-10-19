# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azext_vmware.vendored_sdks.avs_client import AVSClient


def privatecloud_list(cmd, client: AVSClient, resource_group_name=None):
    if resource_group_name is None:
        return client.private_clouds.list_in_subscription()
    else:
        return client.private_clouds.list(resource_group_name)


def privatecloud_show(cmd, client: AVSClient, resource_group_name, name):
    return client.private_clouds.get(resource_group_name, name)


def privatecloud_create(cmd, client: AVSClient, resource_group_name, name, location, sku, cluster_size, network_block, circuit_primary_subnet=None, circuit_secondary_subnet=None, internet=None, vcenter_password=None, nsxt_password=None, tags=[]):
    from azext_vmware.vendored_sdks.models import PrivateCloud, Circuit, ManagementCluster, Sku
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
    return client.private_clouds.create_or_update(resource_group_name, name, cloud)


def privatecloud_update(cmd, client: AVSClient, resource_group_name, name, cluster_size=None, internet=None):
    from azext_vmware.vendored_sdks.models import PrivateCloudUpdate, ManagementCluster
    private_cloud_update = PrivateCloudUpdate()
    if cluster_size is not None:
        private_cloud_update.management_cluster = ManagementCluster(cluster_size=cluster_size)
    if internet is not None:
        private_cloud_update.internet = internet
    return client.private_clouds.update(resource_group_name, name, private_cloud_update)


def privatecloud_delete(cmd, client: AVSClient, resource_group_name, name):
    return client.private_clouds.delete(resource_group_name, name)


def privatecloud_listadmincredentials(cmd, client: AVSClient, resource_group_name, private_cloud):
    return client.private_clouds.list_admin_credentials(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def privatecloud_addidentitysource(cmd, client: AVSClient, resource_group_name, name, private_cloud, alias, domain, base_user_dn, base_group_dn, primary_server, username, password, secondary_server=None, ssl="Disabled"):
    from azext_vmware.vendored_sdks.models import IdentitySource
    pc = client.private_clouds.get(resource_group_name, private_cloud)
    identitysource = IdentitySource(name=name, alias=alias, domain=domain, base_user_dn=base_user_dn, base_group_dn=base_group_dn, primary_server=primary_server, ssl=ssl, username=username, password=password)
    if secondary_server is not None:
        identitysource.secondary_server = secondary_server
    pc.identity_sources.append(identitysource)
    return client.private_clouds.create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, private_cloud=pc)


def privatecloud_deleteidentitysource(cmd, client: AVSClient, resource_group_name, name, private_cloud, alias, domain):
    from azext_vmware.vendored_sdks.models import IdentitySource
    pc = client.private_clouds.get(resource_group_name, private_cloud)
    found = next((ids for ids in pc.identity_sources
                 if ids.name == name and ids.alias == alias and ids.domain == domain), None)
    if found:
        pc.identity_sources.remove(found)
        return client.private_clouds.create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, private_cloud=pc)
    else:
        return pc


def cluster_create(cmd, client: AVSClient, resource_group_name, name, sku, private_cloud, size, tags=[]):
    from azext_vmware.vendored_sdks.models import Cluster, Sku
    cluster = Cluster(sku=Sku(name=sku), cluster_size=size)
    return client.clusters.create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name, cluster=cluster)


def cluster_update(cmd, client: AVSClient, resource_group_name, name, private_cloud, size, tags=[]):
    from azext_vmware.vendored_sdks.models import ClusterUpdate
    cluster_update = ClusterUpdate(cluster_size=size)
    return client.clusters.update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name, cluster_update=cluster_update)


def cluster_list(cmd, client: AVSClient, resource_group_name, private_cloud):
    return client.clusters.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def cluster_show(cmd, client: AVSClient, resource_group_name, private_cloud, name):
    return client.clusters.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name)


def cluster_delete(cmd, client: AVSClient, resource_group_name, private_cloud, name):
    return client.clusters.delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, cluster_name=name)


def check_quota_availability(cmd, client: AVSClient, location):
    return client.locations.check_quota_availability(location)


def check_trial_availability(cmd, client: AVSClient, location):
    return client.locations.check_trial_availability(location)


def authorization_create(cmd, client: AVSClient, resource_group_name, private_cloud, name):
    from azext_vmware.vendored_sdks.models import ExpressRouteAuthorization
    authorization = ExpressRouteAuthorization()
    return client.authorizations.create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, authorization_name=name, authorization=authorization)


def authorization_list(cmd, client: AVSClient, resource_group_name, private_cloud):
    return client.authorizations.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def authorization_show(cmd, client: AVSClient, resource_group_name, private_cloud, name):
    return client.authorizations.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, authorization_name=name)


def authorization_delete(cmd, client: AVSClient, resource_group_name, private_cloud, name):
    return client.authorizations.delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, authorization_name=name)


def hcxenterprisesite_create(cmd, client: AVSClient, resource_group_name, private_cloud, name):
    from azext_vmware.vendored_sdks.models import HcxEnterpriseSite
    hcx_enterprise_site = HcxEnterpriseSite()
    return client.hcx_enterprise_sites.create_or_update(resource_group_name=resource_group_name, private_cloud_name=private_cloud, hcx_enterprise_site_name=name, hcx_enterprise_site=hcx_enterprise_site)


def hcxenterprisesite_list(cmd, client: AVSClient, resource_group_name, private_cloud):
    return client.hcx_enterprise_sites.list(resource_group_name=resource_group_name, private_cloud_name=private_cloud)


def hcxenterprisesite_show(cmd, client: AVSClient, resource_group_name, private_cloud, name):
    return client.hcx_enterprise_sites.get(resource_group_name=resource_group_name, private_cloud_name=private_cloud, hcx_enterprise_site_name=name)


def hcxenterprisesite_delete(cmd, client: AVSClient, resource_group_name, private_cloud, name):
    return client.hcx_enterprise_sites.delete(resource_group_name=resource_group_name, private_cloud_name=private_cloud, hcx_enterprise_site_name=name)
