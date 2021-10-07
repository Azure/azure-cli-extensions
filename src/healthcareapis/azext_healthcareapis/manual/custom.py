# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines

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

    properties = {
        'access_policies': access_policies,
        'authentication_configuration': authentication_configuration,
        'cors_configuration': cors_configuration,
        'cosmos_db_configuration': cosmos_db_configuration,
        'private_endpoint_connections': private_endpoint_connections,
        'public_network_access': public_network_access
    }

    if export_configuration_storage_account_name is not None:
        properties['export_configuration'] = {
            'storage_account_name': export_configuration_storage_account_name
        }

    service_description = {
        'name': resource_name,
        'kind': kind,
        'location': location,
        'etag': etag,
        'properties': properties,
        'tags': tags
    }

    if identity_type is not None:
        service_description['identity'] = {
            'principal_id': None,
            'tenant_id': None,
            'type': identity_type,
        }
    else:
        service_description['identity'] = {
            'principal_id': None,
            'tenant_id': None,
            'type': "None",
        }

    return sdk_no_wait(no_wait,
                       client.create_or_update,
                       resource_group_name=resource_group_name,
                       resource_name=resource_name,
                       service_description=service_description)
