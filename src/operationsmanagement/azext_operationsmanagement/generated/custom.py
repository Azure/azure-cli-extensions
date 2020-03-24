# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-lines


def operationsmanagement_solution_list(cmd, client,
                                       resource_group_name=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def operationsmanagement_solution_show(cmd, client,
                                       resource_group_name,
                                       solution_name):
    return client.get(resource_group_name=resource_group_name,
                      solution_name=solution_name)


def operationsmanagement_solution_create(cmd, client,
                                         resource_group_name,
                                         solution_name,
                                         location=None,
                                         tags=None,
                                         plan=None,
                                         properties=None):
    return client.begin_create_or_update(resource_group_name=resource_group_name,
                                         solution_name=solution_name,
                                         location=location,
                                         tags=tags,
                                         plan=plan,
                                         properties=properties)


def operationsmanagement_solution_update(cmd, client,
                                         resource_group_name,
                                         solution_name,
                                         tags=None):
    return client.begin_update(resource_group_name=resource_group_name,
                               solution_name=solution_name,
                               tags=tags)


def operationsmanagement_solution_delete(cmd, client,
                                         resource_group_name,
                                         solution_name):
    return client.begin_delete(resource_group_name=resource_group_name,
                               solution_name=solution_name)


def operationsmanagement_management_association_list(cmd, client):
    return client.list_by_subscription()


def operationsmanagement_management_association_show(cmd, client,
                                                     resource_group_name,
                                                     provider_name,
                                                     resource_type,
                                                     resource_name,
                                                     management_association_name):
    return client.get(resource_group_name=resource_group_name,
                      provider_name=provider_name,
                      resource_type=resource_type,
                      resource_name=resource_name,
                      management_association_name=management_association_name)


def operationsmanagement_management_association_create(cmd, client,
                                                       resource_group_name,
                                                       provider_name,
                                                       resource_type,
                                                       resource_name,
                                                       management_association_name,
                                                       location=None,
                                                       properties=None):
    return client.create_or_update(resource_group_name=resource_group_name,
                                   provider_name=provider_name,
                                   resource_type=resource_type,
                                   resource_name=resource_name,
                                   management_association_name=management_association_name,
                                   location=location,
                                   properties=properties)


def operationsmanagement_management_association_update(cmd, client,
                                                       resource_group_name,
                                                       provider_name,
                                                       resource_type,
                                                       resource_name,
                                                       management_association_name,
                                                       location=None,
                                                       properties=None):
    return client.create_or_update(resource_group_name=resource_group_name,
                                   provider_name=provider_name,
                                   resource_type=resource_type,
                                   resource_name=resource_name,
                                   management_association_name=management_association_name,
                                   location=location,
                                   properties=properties)


def operationsmanagement_management_association_delete(cmd, client,
                                                       resource_group_name,
                                                       provider_name,
                                                       resource_type,
                                                       resource_name,
                                                       management_association_name):
    return client.delete(resource_group_name=resource_group_name,
                         provider_name=provider_name,
                         resource_type=resource_type,
                         resource_name=resource_name,
                         management_association_name=management_association_name)


def operationsmanagement_management_configuration_list(cmd, client):
    return client.list_by_subscription()


def operationsmanagement_management_configuration_show(cmd, client,
                                                       resource_group_name,
                                                       management_configuration_name):
    return client.get(resource_group_name=resource_group_name,
                      management_configuration_name=management_configuration_name)


def operationsmanagement_management_configuration_create(cmd, client,
                                                         resource_group_name,
                                                         management_configuration_name,
                                                         location=None,
                                                         properties=None):
    return client.create_or_update(resource_group_name=resource_group_name,
                                   management_configuration_name=management_configuration_name,
                                   location=location,
                                   properties=properties)


def operationsmanagement_management_configuration_update(cmd, client,
                                                         resource_group_name,
                                                         management_configuration_name,
                                                         location=None,
                                                         properties=None):
    return client.create_or_update(resource_group_name=resource_group_name,
                                   management_configuration_name=management_configuration_name,
                                   location=location,
                                   properties=properties)


def operationsmanagement_management_configuration_delete(cmd, client,
                                                         resource_group_name,
                                                         management_configuration_name):
    return client.delete(resource_group_name=resource_group_name,
                         management_configuration_name=management_configuration_name)
