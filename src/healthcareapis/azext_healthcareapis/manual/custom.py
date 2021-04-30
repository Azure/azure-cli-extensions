# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines
# pylint: disable=bare-except

from azure.cli.core.util import sdk_no_wait

def healthcareapis_service_show(client,
                                resource_group_name,
                                resource_name):
    return client.get(resource_group_name=resource_group_name,
                      resource_name=resource_name)

# we use this as a create or update
def healthcareapis_service_create(client,
                                  resource_group_name,
                                  resource_name,
                                  kind,
                                  location,
                                  tags=None,
                                  etag=None,
                                  identity_type=None,
                                  access_policies=None,
                                  cosmos_db_configuration=None,
                                  authentication_configuration=None,
                                  cors_configuration=None,
                                  private_endpoint_connections=None,
                                  public_network_access=None,
                                  export_configuration_storage_account_name=None,
                                  no_wait=False):


    currentResource = None

    try:
        currentResource = healthcareapis_service_show(client, resource_group_name, resource_name)
    except:
        pass

    properties = {}
    currentProperties = None

    if currentResource is not None:
        currentProperties = currentResource.properties

    if export_configuration_storage_account_name is not None:
        properties['export_configuration'] = {
            'storage_account_name': export_configuration_storage_account_name
        }
    elif currentProperties is not None:
        properties['export_configuration'] = currentProperties.export_configuration

    service_identity_type = None
    if identity_type is not None:
        service_identity_type = {
            'principal_id': None,
            'tenant_id': None,
            'type': identity_type,
        }
    elif currentResource is not None:
        service_identity_type = currentResource.identity
    else:
        service_identity_type = {
            'principal_id': None,
            'tenant_id': None,
            'type': "None",
        }

    if access_policies is not None:
        if access_policies.get('authority') is None and currentProperties is not None:
            access_policies['authority'] = currentProperties.acces_policies.authority
        if access_policies.get('audience') is None and currentProperties is not None:
            access_policies['audience'] = currentProperties.acces_policies.audience
        if access_policies['smart_proxy_enabled'] is None and currentProperties is not None:
            access_policies['smart_proxy_enabled'] = currentProperties.acces_policies.smart_proxy_enabled
        properties['access_policies'] = access_policies
    elif currentProperties is not None:
        properties['access_policies'] = currentProperties.access_policies

    if cosmos_db_configuration is not None:
        if cosmos_db_configuration['offer_throughput'] is None and currentProperties is not None:
            cosmos_db_configuration['offer_throughput'] = currentProperties.cosmos_db_configuration.offer_throughput
        if cosmos_db_configuration.get('key_vault_key_uri') is None and currentProperties is not None:
            cosmos_db_configuration['key_vault_key_uri'] = currentProperties.cosmos_db_configuration.key_vault_key_uri
        properties['cosmos_db_configuration'] = cosmos_db_configuration
    elif currentProperties is not None:
        properties['cosmos_db_configuration'] = currentProperties.cosmos_db_configuration

    if authentication_configuration is not None:
        properties['authentication_configuration'] = authentication_configuration

    if cors_configuration is not None:
        if cors_configuration.get('origins') is None and currentProperties is not None:
            cors_configuration['origins'] = currentProperties.cors_configuration.origins
        if cors_configuration.get('headers') is None and currentProperties is not None:
            cors_configuration['headers'] = currentProperties.cors_configuration.headers
        if cors_configuration.get('methods') is None and currentProperties is not None:
            cors_configuration['methods'] = currentProperties.cors_configuration.methods
        if cors_configuration['max_age'] is None and currentProperties is not None:
            cors_configuration['max_age'] = currentProperties.cors_configuration.max_age
        properties['cors_configuration'] = cors_configuration
    elif currentProperties is not None:
        properties['cors_configuration'] = currentProperties.cors_configuration

    if private_endpoint_connections is not None:
        if private_endpoint_connections.get('name') is None and currentProperties is not None:
            private_endpoint_connections['name'] = currentProperties.private_endpoint_connections.name
        if private_endpoint_connections.get('id') is None and currentProperties is not None:
            private_endpoint_connections['id'] = currentProperties.private_endpoint_connections.id
        properties['private_endpoint_connections'] = private_endpoint_connections
    elif currentProperties is not None:
        properties['private_endpoint_connections'] = currentProperties.private_endpoint_connections

    if public_network_access is not None:
        properties['public_network_access'] = public_network_access
    elif currentProperties is not None:
        properties['public_network_access'] = currentProperties.public_network_access

    service_description = {
        'name': resource_name,
        'kind': kind,
        'location': location,
        'etag': etag,
        'properties': properties,
        'identity': service_identity_type
    }

    if tags is not None:
        service_description['tags'] = tags
    elif currentResource is not None:
        service_description['tags'] = currentResource.tags

    return sdk_no_wait(no_wait,
                       client.create_or_update,
                       resource_group_name=resource_group_name,
                       resource_name=resource_name,
                       service_description=service_description)
