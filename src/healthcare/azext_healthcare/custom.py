# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument

import json


# module equivalent: azure_rm_healthcareapisservice
# URL: /subscriptions/{{ subscription_id }}/resourceGroups/{{ resource_group }}/providers/Microsoft.HealthcareApis/services/{{ service_name }}
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

    service_description={}
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


# module equivalent: azure_rm_healthcareapisservice
# URL: /subscriptions/{{ subscription_id }}/resourceGroups/{{ resource_group }}/providers/Microsoft.HealthcareApis/services/{{ service_name }}
def update_healthcare(cmd, client, body,
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
    return client.create_or_update(resource_group_name=resource_group, resource_name=name)


# module equivalent: azure_rm_healthcareapisservice
# URL: /subscriptions/{{ subscription_id }}/resourceGroups/{{ resource_group }}/providers/Microsoft.HealthcareApis/services/{{ service_name }}
def list_healthcare(cmd, client,
                    resource_group):
    if resource_group is not None:
        return client.list_by_resource_group(resource_group_name=resource_group)
    return client.list()
