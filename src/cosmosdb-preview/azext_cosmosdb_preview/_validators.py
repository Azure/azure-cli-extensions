# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, too-many-statements, no-else-raise, unused-argument, too-many-branches

import ipaddress
from azure.cli.core.azclierror import InvalidArgumentValueError


def validate_gossip_certificates(ns):
    """ Extracts multiple comma-separated certificates """
    if ns.external_gossip_certificates is not None:
        ns.external_gossip_certificates = get_certificates(ns.external_gossip_certificates)


def validate_client_certificates(ns):
    """ Extracts multiple comma-separated certificates """
    if ns.client_certificates is not None:
        ns.client_certificates = get_certificates(ns.client_certificates)


def validate_server_certificates(ns):
    """ Extracts multiple comma-separated certificates """
    if ns.server_certificates is not None:
        ns.server_certificates = get_certificates(ns.server_certificates)


def get_certificates(input_certificates):
    from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import Certificate
    certificates = []
    for item in input_certificates:
        certificate = get_certificate(item)
        certificates.append(Certificate(pem=certificate))
    return certificates


def get_certificate(cert):
    """ Extract certificate from file or from string """
    from azure.cli.core.util import read_file_content
    import os
    certificate = ''
    if cert is not None:
        if os.path.exists(cert):
            certificate = read_file_content(cert)
        else:
            certificate = cert
    else:
        raise InvalidArgumentValueError("""One of the value provided for the certificates is empty.
    Please verify there aren't any spaces.""")
    return certificate


def validate_seednodes(ns):
    """ Extracts multiple comma-separated ipaddresses """
    from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import SeedNode
    if ns.external_seed_nodes is not None:
        seed_nodes = []
        for item in ns.external_seed_nodes:
            try:
                ipaddress.ip_address(item)
            except ValueError as e:
                raise InvalidArgumentValueError("""IP address provided is invalid.
            Please verify if there are any spaces or other invalid characters.""") from e
            seed_nodes.append(SeedNode(ip_address=item))
        ns.external_seed_nodes = seed_nodes


def validate_node_count(ns):
    """ Validate node count is greater than 3"""
    if ns.node_count is not None:
        if int(ns.node_count) < 3:
            raise InvalidArgumentValueError("""Node count cannot be less than 3.""")


def _gen_guid():
    import uuid
    return uuid.uuid4()


def _parse_resource_path(resource,
                         to_fully_qualified,
                         resource_type=None,
                         subscription_id=None,
                         resource_group_name=None,
                         account_name=None):
    """Returns a properly formatted mongo role definition or user definition id."""
    import re
    regex = "/subscriptions/(?P<subscription>.*)/resourceGroups/(?P<resource_group>.*)/providers/" \
            "Microsoft.DocumentDB/databaseAccounts/(?P<database_account>.*)"
    formatted = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.DocumentDB/databaseAccounts/{2}"

    if resource_type is not None:
        regex += "/" + resource_type + "/(?P<resource_id>.*)"
        formatted += "/" + resource_type + "/"

    formatted += "{3}"

    if to_fully_qualified:
        result = re.match(regex, resource)
        if result is not None:
            return resource

        return formatted.format(subscription_id, resource_group_name, account_name, resource)

    result = re.match(regex, resource)
    if result is None:
        return resource

    return result['resource_id']


def validate_mongo_role_definition_body(cmd, ns):
    """ Extracts role definition body """
    from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import RoleDefinitionType
    from azure.cli.core.util import get_file_json, shell_safe_json_parse
    import os

    if ns.mongo_role_definition_body is not None:
        if os.path.exists(ns.mongo_role_definition_body):
            mongo_role_definition = get_file_json(ns.mongo_role_definition_body)
        else:
            mongo_role_definition = shell_safe_json_parse(ns.mongo_role_definition_body)

        if not isinstance(mongo_role_definition, dict):
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid Mongo role definition. A valid dictionary JSON representation is expected.')

        if 'Id' not in mongo_role_definition or not isinstance(mongo_role_definition['Id'], str) or len(mongo_role_definition['Id']) == 0:
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid Mongo role id. A valid string <DatabaseName>.<RoleName> is expected.')

        mongo_role_definition['Id'] = _parse_resource_path(mongo_role_definition['Id'], False, "mongodbRoleDefinitions")

        if 'RoleName' not in mongo_role_definition or not isinstance(mongo_role_definition['RoleName'], str) or len(mongo_role_definition['RoleName']) == 0:
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid Mongo role name. A valid string role name is expected.')

        if 'DatabaseName' not in mongo_role_definition or not isinstance(mongo_role_definition['DatabaseName'], str) or len(mongo_role_definition['DatabaseName']) == 0:
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid Mongo database name. A valid string database name is expected.')

        if 'Privileges' not in mongo_role_definition or not isinstance(mongo_role_definition['Privileges'], list) or len(mongo_role_definition['Privileges']) == 0:
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid Mongo role Privileges. A valid List JSON representation is expected.')
        else:

            for privilege in mongo_role_definition['Privileges']:
                if 'Resource' not in privilege or not isinstance(privilege['Resource'], dict):
                    raise InvalidArgumentValueError(
                        'Role creation failed. Invalid Mongo role Resources for Privileges. A valid dictionary JSON representation is expected.')
                else:
                    if 'Db' not in privilege['Resource'] or not isinstance(privilege['Resource']['Db'], str):
                        raise InvalidArgumentValueError(
                            'Role creation failed. Invalid Mongo database name under Privileges->Resoures. A valid string database name is expected.')

                    if 'Collection' in privilege['Resource'] and not isinstance(privilege['Resource']['Collection'], str):
                        raise InvalidArgumentValueError(
                            'Role creation failed. Invalid Mongo database Collection name under Privileges->Resoures. A valid string database name is expected.')

                if 'Actions' not in privilege or not isinstance(privilege['Actions'], list) or len(privilege['Actions']) == 0:
                    raise InvalidArgumentValueError(
                        'Role creation failed. Invalid Mongo role Actions for Privileges. A valid list of strings is expected.')

        if 'Roles' in mongo_role_definition:
            if not isinstance(mongo_role_definition['Roles'], list):
                raise InvalidArgumentValueError(
                    'Role creation failed. Invalid Mongo Roles. A valid dictionary JSON representation is expected')
            else:
                for Role in mongo_role_definition['Roles']:
                    if 'Role' not in Role or not isinstance(Role['Role'], str) or len(Role['Role']) == 0:
                        raise InvalidArgumentValueError(
                            'Role creation failed. Invalid Mongo Role. A valid string Role is expected.')

        if 'Type' not in mongo_role_definition:
            mongo_role_definition['Type'] = RoleDefinitionType.custom_role

        ns.mongo_role_definition_body = mongo_role_definition


def validate_mongo_role_definition_id(ns):
    """ Extracts Guid role definition Id """
    if ns.mongo_role_definition_id is not None:
        ns.mongo_role_definition_id = _parse_resource_path(ns.mongo_role_definition_id, False, "mongodbRoleDefinitions")


def validate_mongo_user_definition_body(cmd, ns):
    """ Extracts user definition body """
    from azure.cli.core.util import get_file_json, shell_safe_json_parse
    import os

    if ns.mongo_user_definition_body is not None:
        if os.path.exists(ns.mongo_user_definition_body):
            mongo_user_definition = get_file_json(ns.mongo_user_definition_body)
        else:
            mongo_user_definition = shell_safe_json_parse(ns.mongo_user_definition_body)

        if not isinstance(mongo_user_definition, dict):
            raise InvalidArgumentValueError(
                'User creation failed. Invalid Mongo user definition. A valid dictionary JSON representation is expected.')

        if 'Id' not in mongo_user_definition or not isinstance(mongo_user_definition['Id'], str) or len(mongo_user_definition['Id']) == 0:
            raise InvalidArgumentValueError(
                'User creation failed. Invalid Mongo User ID. A valid string of <DatabaseName>.<Username> is expected.')

        mongo_user_definition['Id'] = _parse_resource_path(mongo_user_definition['Id'], False, "mongodbUserDefinitions")

        if 'UserName' not in mongo_user_definition or not isinstance(mongo_user_definition['UserName'], str) or len(mongo_user_definition['UserName']) == 0:
            raise InvalidArgumentValueError(
                'User creation failed. Invalid Mongo User definition user name. A valid string user name is expected.')

        if 'Password' not in mongo_user_definition or not isinstance(mongo_user_definition['Password'], str) or len(mongo_user_definition['Password']) == 0:
            raise InvalidArgumentValueError(
                'User creation failed. Invalid Mongo User definition password. A valid string password is expected.')

        if 'DatabaseName' not in mongo_user_definition or not isinstance(mongo_user_definition['DatabaseName'], str) or len(mongo_user_definition['DatabaseName']) == 0:
            raise InvalidArgumentValueError(
                'User creation failed. User creation failed. Invalid Mongo database name. A valid string database name is expected.')

        if 'CustomData' in mongo_user_definition and not isinstance(mongo_user_definition['CustomData'], str):
            raise InvalidArgumentValueError(
                'User creation failed. Invalid Mongo Custom Data parameter. A valid string custom data is expected.')

        if 'Mechanisms' in mongo_user_definition and not isinstance(mongo_user_definition['Mechanisms'], str) or len(mongo_user_definition['Mechanisms']) == 0:
            raise InvalidArgumentValueError(
                'User creation failed. Invalid Mongo Mechanisms parameter. A valid string Mechanisms is expected.')

        if 'Roles' in mongo_user_definition:
            if not isinstance(mongo_user_definition['Roles'], list) or len(mongo_user_definition['Roles']) == 0:
                raise InvalidArgumentValueError(
                    'User creation failed. Invalid Mongo Roles. A valid dictionary JSON representation is expected')
            else:
                for Role in mongo_user_definition['Roles']:
                    if 'Role' not in Role or not isinstance(Role['Role'], str) or len(Role['Role']) == 0:
                        raise InvalidArgumentValueError(
                            'User creation failed. Invalid Mongo Role. A valid string Role is expected.')
                    if 'Db' in Role and not isinstance(Role['Db'], str):
                        raise InvalidArgumentValueError(
                            'User creation failed. Invalid Mongo Db. A valid string database name is expected.')

        ns.mongo_user_definition_body = mongo_user_definition


def validate_mongo_user_definition_id(ns):
    """ Extracts Guid user definition Id """
    if ns.mongo_user_definition_id is not None:
        ns.mongo_user_definition_id = _parse_resource_path(ns.mongo_user_definition_id, False, "mongodbUserDefinitions")
