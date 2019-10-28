# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def create_managednetwork(cmd, client,
                          resource_group,
                          name,
                          location=None,
                          tags=None,
                          scope_management_groups=None,
                          scope_subscriptions=None,
                          scope_virtual_networks=None,
                          scope_subnets=None,
                          connectivity_groups=None,
                          connectivity_peerings=None):
    body = {}
    body['location'] = location  # str
    body['tags'] = tags  # dictionary
    body.setdefault('scope', {})['management_groups'] = [{'id': i} for i in scope_management_groups]
    body.setdefault('scope', {})['subscriptions'] = [{'id': i} for i in scope_subscriptions]
    body.setdefault('scope', {})['virtual_networks'] = [{'id': i} for i in scope_virtual_networks]
    body.setdefault('scope', {})['subnets'] = [{'id': i} for i in scope_subnets]
    body.setdefault('connectivity', {})['groups'] = [{'id': i} for i in connectivity_groups]
    body.setdefault('connectivity', {})['peerings'] = [{'id': i} for i in connectivity_peerings]
    return client.create_or_update(resource_group_name=resource_group, managed_network_name=name, managed_network=body)


def update_managednetwork(cmd, client,
                          resource_group,
                          name,
                          location=None,
                          tags=None,
                          scope_management_groups=None,
                          scope_subscriptions=None,
                          scope_virtual_networks=None,
                          scope_subnets=None,
                          connectivity_groups=None,
                          connectivity_peerings=None):
    body = client.get(resource_group_name=resource_group, managed_network_name=name).as_dict()
    body.location = location  # str
    body.tags = tags  # dictionary
    body.scope.management_groups = [{'id': i} for i in scope_management_groups]
    body.scope.subscriptions = [{'id': i} for i in scope_subscriptions]
    body.scope.virtual_networks = [{'id': i} for i in scope_virtual_networks]
    body.scope.subnets = [{'id': i} for i in scope_subnets]
    body.connectivity.groups = [{'id': i} for i in connectivity_groups]
    body.connectivity.peerings = [{'id': i} for i in connectivity_peerings]
    return client.create_or_update(resource_group_name=resource_group, managed_network_name=name, managed_network=body)


def delete_managednetwork(cmd, client,
                          resource_group,
                          name):
    return client.delete(resource_group_name=resource_group, managed_network_name=name)


def list_managednetwork(cmd, client,
                        resource_group):
    if resource_group is not None:
        return client.list_by_resource_group(resource_group_name=resource_group)
    return client.list_by_subscription()


def create_managednetwork_scope_assignment(cmd, client,
                                           name,
                                           scope=None,
                                           location=None,
                                           assigned_managed_network=None):
    body = {}
    body['location'] = location  # str
    body['assigned_managed_network'] = assigned_managed_network  # str
    return client.create_or_update(scope=scope, scope_assignment_name=name, parameters=body)


def update_managednetwork_scope_assignment(cmd, client,
                                           name,
                                           scope=None,
                                           location=None,
                                           assigned_managed_network=None):
    body = client.get(scope=scope, scope_assignment_name=name).as_dict()
    body.location = location  # str
    body.assigned_managed_network = assigned_managed_network  # str
    return client.create_or_update(scope=scope, scope_assignment_name=name, parameters=body)


def delete_managednetwork_scope_assignment(cmd, client,
                                           name,
                                           scope=None):
    return client.delete(scope=scope, scope_assignment_name=name)


def list_managednetwork_scope_assignment(cmd, client,
                                         scope=None):
    return client.list(scope=scope)


def create_managednetwork_managed_network_group(cmd, client,
                                                resource_group,
                                                managed_network_name,
                                                name,
                                                location=None,
                                                management_groups=None,
                                                subscriptions=None,
                                                virtual_networks=None,
                                                subnets=None,
                                                kind=None):
    body = {}
    body['location'] = location  # str
    body['management_groups'] = [{'id': i} for i in management_groups]
    body['subscriptions'] = [{'id': i} for i in subscriptions]
    body['virtual_networks'] = [{'id': i} for i in virtual_networks]
    body['subnets'] = [{'id': i} for i in subnets]
    body['kind'] = kind  # str
    return client.create_or_update(resource_group_name=resource_group, managed_network_name=managed_network_name, managed_network_group_name=name, managed_network_group=body)


def update_managednetwork_managed_network_group(cmd, client,
                                                resource_group,
                                                managed_network_name,
                                                name,
                                                location=None,
                                                management_groups=None,
                                                subscriptions=None,
                                                virtual_networks=None,
                                                subnets=None,
                                                kind=None):
    body = client.get(resource_group_name=resource_group, managed_network_name=managed_network_name, managed_network_group_name=name).as_dict()
    body.location = location  # str
    body.management_groups = [{'id': i} for i in management_groups]
    body.subscriptions = [{'id': i} for i in subscriptions]
    body.virtual_networks = [{'id': i} for i in virtual_networks]
    body.subnets = [{'id': i} for i in subnets]
    body.kind = kind  # str
    return client.create_or_update(resource_group_name=resource_group, managed_network_name=managed_network_name, managed_network_group_name=name, managed_network_group=body)


def delete_managednetwork_managed_network_group(cmd, client,
                                                resource_group,
                                                managed_network_name,
                                                name):
    return client.delete(resource_group_name=resource_group, managed_network_name=managed_network_name, managed_network_group_name=name)


def list_managednetwork_managed_network_group(cmd, client,
                                              resource_group,
                                              managed_network_name):
    return client.list_by_managed_network(resource_group_name=resource_group, managed_network_name=managed_network_name)


def create_managednetwork_managed_network_peering_policy(cmd, client,
                                                         resource_group,
                                                         managed_network_name,
                                                         name,
                                                         _type,
                                                         location=None,
                                                         hub_id=None,
                                                         spokes=None,
                                                         mesh=None):
    body = {}
    body['location'] = location  # str
    body['type'] = _type  # str
    body.setdefault('hub', {})['id'] = hub_id  # str
    body['spokes'] = [{'id': i} for i in spokes]
    body['mesh'] = mesh
    return client.create_or_update(resource_group_name=resource_group, managed_network_name=managed_network_name, managed_network_peering_policy_name=name, managed_network_policy=body)


def update_managednetwork_managed_network_peering_policy(cmd, client,
                                                         resource_group,
                                                         managed_network_name,
                                                         name,
                                                         location=None,
                                                         _type=None,
                                                         hub_id=None,
                                                         spokes=None,
                                                         mesh=None):
    body = client.get(resource_group_name=resource_group, managed_network_name=managed_network_name, managed_network_peering_policy_name=name).as_dict()
    body.location = location  # str
    body.type = _type  # str
    body.hub.id = hub_id  # str
    body.spokes = [{'id': i} for i in spokes]
    body.mesh = mesh
    return client.create_or_update(resource_group_name=resource_group, managed_network_name=managed_network_name, managed_network_peering_policy_name=name, managed_network_policy=body)


def delete_managednetwork_managed_network_peering_policy(cmd, client,
                                                         resource_group,
                                                         managed_network_name,
                                                         name):
    return client.delete(resource_group_name=resource_group, managed_network_name=managed_network_name, managed_network_peering_policy_name=name)


def list_managednetwork_managed_network_peering_policy(cmd, client,
                                                       resource_group,
                                                       managed_network_name):
    return client.list_by_managed_network(resource_group_name=resource_group, managed_network_name=managed_network_name)
