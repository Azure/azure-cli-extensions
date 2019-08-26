# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def create_healthcare(cmd, client,
                      resource_group,
                      name,
                      kind,
                      location,
                      access_policies_object_id,
                      tags=None,
                      etag=None,
                      cosmos_db_offer_throughput=None,
                      authentication_authority=None,
                      authentication_audience=None,
                      authentication_smart_proxy_enabled=None,
                      cors_origins=None,
                      cors_headers=None,
                      cors_methods=None,
                      cors_max_age=None,
                      cors_allow_credentials=None):

    service_description = {}
    service_description['location'] = location
    service_description['kind'] = kind
    service_description['properties'] = {}
    service_description['properties']['access_policies'] = []
    for policy in access_policies_object_id.split(','):
        service_description['properties']['access_policies'].append({'object_id': policy})
    service_description['properties']['cors_configuration'] = {}
    service_description['properties']['cors_configuration']['origins'] = None if cors_origins is None else cors_origins.split(',')
    service_description['properties']['cors_configuration']['headers'] = None if cors_headers is None else cors_headers.split(',')
    service_description['properties']['cors_configuration']['methods'] = None if cors_methods is None else cors_methods.split(',')
    service_description['properties']['cors_configuration']['max_age'] = cors_max_age
    service_description['properties']['cors_configuration']['allow_credentials'] = cors_allow_credentials
    service_description['properties']['cosmos_db_configuration'] = {}
    service_description['properties']['cosmos_db_configuration']['offer_throughput'] = cosmos_db_offer_throughput
    service_description['authentication_configuration'] = {}
    service_description['authentication_configuration']['authority'] = authentication_authority
    service_description['authentication_configuration']['audience'] = authentication_audience
    service_description['authentication_configuration']['smart_proxy_enabled'] = authentication_smart_proxy_enabled

    return client.create_or_update(resource_group_name=resource_group, resource_name=name, service_description=service_description)


def update_healthcare(cmd, client,
                      resource_group,
                      name,
                      kind=None,
                      location=None,
                      access_policies_object_id=None,
                      tags=None,
                      etag=None,
                      cosmos_db_offer_throughput=None,
                      authentication_authority=None,
                      authentication_audience=None,
                      authentication_smart_proxy_enabled=None,
                      cors_origins=None,
                      cors_headers=None,
                      cors_methods=None,
                      cors_max_age=None,
                      cors_allow_credentials=None):
    service_description = client.get(resource_group_name=resource_group, resource_name=name).as_dict()
    if location is not None:
        service_description['location'] = location
    if kind is not None:
        service_description['kind'] = kind
    if access_policies_object_id is not None:
        service_description['properties']['access_policies'] = []
        for policy in access_policies_object_id.split(','):
            service_description['properties']['access_policies'].append({'object_id': policy})
    if service_description['properties'].get('cors_configuration') is None:
        service_description['properties']['cors_configuration'] = {}
    if cors_origins is not None:
        service_description['properties']['cors_configuration']['origins'] = None if cors_origins is None else cors_origins.split(',')
    if cors_headers is not None:
        service_description['properties']['cors_configuration']['headers'] = None if cors_headers is None else cors_headers.split(',')
    if cors_methods is not None:
        service_description['properties']['cors_configuration']['methods'] = None if cors_methods is None else cors_methods.split(',')
    if cors_max_age is not None:
        service_description['properties']['cors_configuration']['max_age'] = cors_max_age
    if cors_allow_credentials is not None:
        service_description['properties']['cors_configuration']['allow_credentials'] = cors_allow_credentials
    if service_description['properties'].get('cosmos_db_configuration') is None:
        service_description['properties']['cosmos_db_configuration'] = {}
    if cosmos_db_offer_throughput is not None:
        service_description['properties']['cosmos_db_configuration']['offer_throughput'] = cosmos_db_offer_throughput
    if service_description['properties'].get('authentication_configuration') is None:
        service_description['authentication_configuration'] = {}
    if authentication_authority is not None:
        service_description['authentication_configuration']['authority'] = authentication_authority
    if authentication_audience is not None:
        service_description['authentication_configuration']['audience'] = authentication_audience
    if authentication_smart_proxy_enabled is not None:
        service_description['authentication_configuration']['smart_proxy_enabled'] = authentication_smart_proxy_enabled
    return client.create_or_update(resource_group_name=resource_group, resource_name=name, service_description=service_description)


def list_healthcare(cmd, client,
                    resource_group=None):
    if resource_group is not None:
        return client.list_by_resource_group(resource_group_name=resource_group)
    return client.list()


def show_healthcare(cmd, client,
                    resource_group,
                    name):
    return client.get(resource_group_name=resource_group, resource_name=name)


def delete_healthcare(cmd, client,
                      resource_group,
                      name):
    return client.delete(resource_group_name=resource_group, resource_name=name)
