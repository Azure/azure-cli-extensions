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


def validate_table_role_definition_body(cmd, ns):
    """ Extracts role definition body """
    from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import RoleDefinitionType
    from azure.cli.core.util import get_file_json, shell_safe_json_parse
    import os

    if ns.table_role_definition_body is not None:
        if os.path.exists(ns.table_role_definition_body):
            table_role_definition = get_file_json(ns.table_role_definition_body)
        else:
            table_role_definition = shell_safe_json_parse(ns.table_role_definition_body)

        if not isinstance(table_role_definition, dict):
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid table role definition. A valid dictionary JSON representation is expected.')

        if 'RoleName' not in table_role_definition or not isinstance(table_role_definition['RoleName'], str) or len(table_role_definition['RoleName']) == 0:
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid table role name. A valid string role name is expected.')

        if 'AssignableScopes' not in table_role_definition or not isinstance(table_role_definition['AssignableScopes'], list) or len(table_role_definition['AssignableScopes']) == 0:
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid Table role definition for AssignableScopes. A valid list of strings is expected.')

        if 'Permissions' not in table_role_definition or not isinstance(table_role_definition['Permissions'], list) or len(table_role_definition['Permissions']) == 0:
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid Table role Permissions. A valid List JSON representation is expected.')

        if 'Type' not in table_role_definition:
            table_role_definition['Type'] = RoleDefinitionType.custom_role

        ns.table_role_definition_body = table_role_definition


def validate_table_role_definition_id(ns):
    """ Extracts Guid role definition Id """
    if ns.role_definition_id is not None:
        ns.role_definition_id = _parse_resource_path(ns.role_definition_id, False, "tableRoleDefinitions")


def validate_table_role_assignment_id(ns):
    """ Extracts Guid role assignment Id """
    if ns.role_assignment_id is not None:
        ns.role_assignment_id = _parse_resource_path(ns.role_assignment_id, False, "tableRoleAssignments")


def validate_gremlin_role_definition_body(cmd, ns):
    """ Extracts role definition body """
    from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import RoleDefinitionType
    from azure.cli.core.util import get_file_json, shell_safe_json_parse
    import os

    if ns.gremlin_role_definition_body is not None:
        if os.path.exists(ns.gremlin_role_definition_body):
            gremlin_role_definition = get_file_json(ns.gremlin_role_definition_body)
        else:
            gremlin_role_definition = shell_safe_json_parse(ns.gremlin_role_definition_body)

        if not isinstance(gremlin_role_definition, dict):
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid gremlin role definition. A valid dictionary JSON representation is expected.')

        if 'RoleName' not in gremlin_role_definition or not isinstance(gremlin_role_definition['RoleName'], str) or len(gremlin_role_definition['RoleName']) == 0:
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid gremlin role name. A valid string role name is expected.')

        if 'AssignableScopes' not in gremlin_role_definition or not isinstance(gremlin_role_definition['AssignableScopes'], list) or len(gremlin_role_definition['AssignableScopes']) == 0:
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid Gremlin role definition for AssignableScopes. A valid list of strings is expected.')

        if 'Permissions' not in gremlin_role_definition or not isinstance(gremlin_role_definition['Permissions'], list) or len(gremlin_role_definition['Permissions']) == 0:
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid Gremlin role Permissions. A valid List JSON representation is expected.')

        if 'Type' not in gremlin_role_definition:
            gremlin_role_definition['Type'] = RoleDefinitionType.custom_role

        ns.gremlin_role_definition_body = gremlin_role_definition


def validate_gremlin_role_definition_id(ns):
    """ Extracts Guid role definition Id """
    if ns.role_definition_id is not None:
        ns.role_definition_id = _parse_resource_path(ns.role_definition_id, False, "gremlinRoleDefinitions")


def validate_gremlin_role_assignment_id(ns):
    """ Extracts Guid role assignment Id """
    if ns.role_assignment_id is not None:
        ns.role_assignment_id = _parse_resource_path(ns.role_assignment_id, False, "gremlinRoleAssignments")


def validate_cassandra_role_definition_body(cmd, ns):
    """ Extracts role definition body """
    from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import RoleDefinitionType
    from azure.cli.core.util import get_file_json, shell_safe_json_parse
    import os

    if ns.cassandra_role_definition_body is not None:
        if os.path.exists(ns.cassandra_role_definition_body):
            cassandra_role_definition = get_file_json(ns.cassandra_role_definition_body)
        else:
            cassandra_role_definition = shell_safe_json_parse(ns.cassandra_role_definition_body)

        if not isinstance(cassandra_role_definition, dict):
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid cassandra role definition. A valid dictionary JSON representation is expected.')

        if 'RoleName' not in cassandra_role_definition or not isinstance(cassandra_role_definition['RoleName'], str) or len(cassandra_role_definition['RoleName']) == 0:
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid cassandra role name. A valid string role name is expected.')

        if 'AssignableScopes' not in cassandra_role_definition or not isinstance(cassandra_role_definition['AssignableScopes'], list) or len(cassandra_role_definition['AssignableScopes']) == 0:
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid Cassandra role definition for AssignableScopes. A valid list of strings is expected.')

        if 'Permissions' not in cassandra_role_definition or not isinstance(cassandra_role_definition['Permissions'], list) or len(cassandra_role_definition['Permissions']) == 0:
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid Cassandra role Permissions. A valid List JSON representation is expected.')

        if 'Type' not in cassandra_role_definition:
            cassandra_role_definition['Type'] = RoleDefinitionType.custom_role

        ns.cassandra_role_definition_body = cassandra_role_definition


def validate_cassandra_role_definition_id(ns):
    """ Extracts Guid role definition Id """
    if ns.role_definition_id is not None:
        ns.role_definition_id = _parse_resource_path(ns.role_definition_id, False, "cassandraRoleDefinitions")


def validate_cassandra_role_assignment_id(ns):
    """ Extracts Guid role assignment Id """
    if ns.role_assignment_id is not None:
        ns.role_assignment_id = _parse_resource_path(ns.role_assignment_id, False, "cassandraRoleAssignments")


def validate_mongoMI_role_definition_body(cmd, ns):
    """ Extracts role definition body """
    from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import RoleDefinitionType
    from azure.cli.core.util import get_file_json, shell_safe_json_parse
    import os

    if ns.mongoMI_role_definition_body is not None:
        if os.path.exists(ns.mongoMI_role_definition_body):
            mongoMI_role_definition = get_file_json(ns.mongoMI_role_definition_body)
        else:
            mongoMI_role_definition = shell_safe_json_parse(ns.mongoMI_role_definition_body)

        if not isinstance(mongoMI_role_definition, dict):
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid mongoMI role definition. A valid dictionary JSON representation is expected.')

        if 'RoleName' not in mongoMI_role_definition or not isinstance(mongoMI_role_definition['RoleName'], str) or len(mongoMI_role_definition['RoleName']) == 0:
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid mongoMI role name. A valid string role name is expected.')

        if 'AssignableScopes' not in mongoMI_role_definition or not isinstance(mongoMI_role_definition['AssignableScopes'], list) or len(mongoMI_role_definition['AssignableScopes']) == 0:
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid MongoMI role definition for AssignableScopes. A valid list of strings is expected.')

        if 'Permissions' not in mongoMI_role_definition or not isinstance(mongoMI_role_definition['Permissions'], list) or len(mongoMI_role_definition['Permissions']) == 0:
            raise InvalidArgumentValueError(
                'Role creation failed. Invalid MongoMI role Permissions. A valid List JSON representation is expected.')

        if 'Type' not in mongoMI_role_definition:
            mongoMI_role_definition['Type'] = RoleDefinitionType.custom_role

        ns.mongoMI_role_definition_body = mongoMI_role_definition


def validate_mongoMI_role_definition_id(ns):
    """ Extracts Guid role definition Id """
    if ns.role_definition_id is not None:
        ns.role_definition_id = _parse_resource_path(ns.role_definition_id, False, "mongoMIRoleDefinitions")


def validate_mongoMI_role_assignment_id(ns):
    """ Extracts Guid role assignment Id """
    if ns.role_assignment_id is not None:
        ns.role_assignment_id = _parse_resource_path(ns.role_assignment_id, False, "mongoMIRoleAssignments")


def validate_fleetspace_body(cmd, ns):
    from azure.cli.core.util import get_file_json, shell_safe_json_parse
    import os

    if ns.fleetspace_body is not None:
        if os.path.exists(ns.fleetspace_body):
            body = get_file_json(ns.fleetspace_body)
        else:
            body = shell_safe_json_parse(ns.fleetspace_body)

        if not isinstance(body, dict):
            raise InvalidArgumentValueError('Invalid fleetspace body. Must be a JSON object.')

        props = body.get('properties', {})
        if not isinstance(props, dict):
            raise InvalidArgumentValueError('Missing or invalid "properties" field in fleetspace body.')

        tp_config = props.get('throughputPoolConfiguration', {})
        if not isinstance(tp_config, dict):
            raise InvalidArgumentValueError('Missing or invalid "throughputPoolConfiguration" in properties.')

        for field in ['minThroughput', 'maxThroughput', 'serviceTier', 'dataRegions']:
            if field not in tp_config:
                raise InvalidArgumentValueError(f'Missing "{field}" in throughputPoolConfiguration.')

        if not isinstance(tp_config['minThroughput'], int) or tp_config['minThroughput'] <= 0:
            raise InvalidArgumentValueError('"minThroughput" must be a positive integer.')

        if not isinstance(tp_config['maxThroughput'], int) or tp_config['maxThroughput'] <= 0:
            raise InvalidArgumentValueError('"maxThroughput" must be a positive integer.')

        if not isinstance(tp_config['serviceTier'], str):
            raise InvalidArgumentValueError('"serviceTier" must be a string.')

        if not isinstance(tp_config['dataRegions'], list) or not all(isinstance(r, str) for r in tp_config['dataRegions']):
            raise InvalidArgumentValueError('"dataRegions" must be a list of strings.')

        ns.fleetspace_body = body


def validate_fleet_analytics_body(cmd, ns):
    from azure.cli.core.util import get_file_json, shell_safe_json_parse
    import os

    if ns.fleet_analytics_body is not None:
        if os.path.exists(ns.fleet_analytics_body):
            body = get_file_json(ns.fleet_analytics_body)
        else:
            body = shell_safe_json_parse(ns.fleet_analytics_body)

        if not isinstance(body, dict):
            raise InvalidArgumentValueError('Fleet Analytics body must be a valid JSON object.')

        props = body.get("properties")
        if not isinstance(props, dict):
            raise InvalidArgumentValueError('Missing or invalid "properties" field.')

        slt = props.get("storageLocationType")
        if slt not in ["StorageAccount", "FabricLakehouse"]:
            raise InvalidArgumentValueError('"storageLocationType" must be "StorageAccount" or "FabricLakehouse".')

        slu = props.get("storageLocationUri")
        if not isinstance(slu, str) or not slu.strip():
            raise InvalidArgumentValueError('"storageLocationUri" must be a non-empty string.')

        ns.fleet_analytics_body = body


def validate_fleetspaceAccount_body(cmd, ns):
    from azure.cli.core.util import get_file_json, shell_safe_json_parse
    import os

    if ns.fleetspace_account_body is not None:
        if os.path.exists(ns.fleetspace_account_body):
            body = get_file_json(ns.fleetspace_account_body)
        else:
            body = shell_safe_json_parse(ns.fleetspace_account_body)

        if not isinstance(body, dict):
            raise InvalidArgumentValueError("Fleetspace Account body must be a valid JSON object.")

        props = body.get("properties")
        if not isinstance(props, dict):
            raise InvalidArgumentValueError('Missing or invalid "properties" field.')

        gdp = props.get("globalDatabaseAccountProperties")
        if not isinstance(gdp, dict):
            raise InvalidArgumentValueError('Missing or invalid "globalDatabaseAccountProperties".')

        if "resourceId" not in gdp or not isinstance(gdp["resourceId"], str) or not gdp["resourceId"].startswith("/subscriptions/"):
            raise InvalidArgumentValueError('"resourceId" must be a valid ARM resource ID string.')

        if "armLocation" not in gdp or not isinstance(gdp["armLocation"], str):
            raise InvalidArgumentValueError('"armLocation" must be a valid string.')

        ns.fleetspace_account_body = body
