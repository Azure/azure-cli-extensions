# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=import-error,too-many-locals
import re
import uuid
from msrestazure.azure_exceptions import CloudError
from knack.log import get_logger
from azext_rdbms_up.vendored_sdks.azure_mgmt_rdbms import mysql
from azext_rdbms_up._client_factory import cf_mysql_firewall_rules, cf_mysql_config
from azext_rdbms_up.mysql_util import ClientType as MySqlClient
from azext_rdbms_up.util import update_kwargs, resolve_poller
import mysql.connector as mysql_connector

logger = get_logger(__name__)


def mysql_up(cmd, client, resource_group_name=None, server_name=None, sku_name=None,
             location=None, administrator_login=None, administrator_login_password=None,
             backup_retention=None, geo_redundant_backup=None, ssl_enforcement=None, storage_mb=None,
             database_name=None, tags=None, version=None):
    try:
        server_result = client.get(resource_group_name, server_name)
        logger.warning('Found existing MySQL Server \'%s\' ...', server_name)
        # update server if needed
        server_result = _update_mysql_server(
            cmd, client, server_result, resource_group_name, server_name, backup_retention, geo_redundant_backup,
            storage_mb, administrator_login_password, version, ssl_enforcement, tags)
    except CloudError:
        # Create mysql server
        logger.warning('Creating MySQL Server \'%s\' ...', server_name)
        if administrator_login_password is None:
            administrator_login_password = str(uuid.uuid4())
        parameters = mysql.models.ServerForCreate(
            sku=mysql.models.Sku(name=sku_name),
            properties=mysql.models.ServerPropertiesForDefaultCreate(
                administrator_login=administrator_login,
                administrator_login_password=administrator_login_password,
                version=version,
                ssl_enforcement=ssl_enforcement,
                storage_profile=mysql.models.StorageProfile(
                    backup_retention_days=backup_retention,
                    geo_redundant_backup=geo_redundant_backup,
                    storage_mb=storage_mb)),
            location=location,
            tags=tags)

        server_result = resolve_poller(
            client.create(resource_group_name, server_name, parameters), cmd.cli_ctx, 'MySQL Server Create')

        # Set timeout configuration
        logger.warning('Configuring wait timeout to 8 hours ...')
        config_client = cf_mysql_config(cmd.cli_ctx, None)
        resolve_poller(
            config_client.create_or_update(resource_group_name, server_name, 'wait_timeout', '28800'),
            cmd.cli_ctx, 'MySQL Configuration Update')

        # Create firewall rule to allow for Azure IPs
        logger.warning('Configuring firewall rule, \'azure-access\', to allow for Azure IPs ...')
        firewall_client = cf_mysql_firewall_rules(cmd.cli_ctx, None)
        resolve_poller(
            firewall_client.create_or_update(resource_group_name, server_name, 'azure-access', '0.0.0.0', '0.0.0.0'),
            cmd.cli_ctx, 'MySQL Firewall Rule Create/Update')

    # Check for user's ip address(es)
    user = '{}@{}'.format(administrator_login, server_name)
    host = server_result.fully_qualified_domain_name
    kwargs = {'user': user, 'host': host}
    if administrator_login_password is not None:
        kwargs['password'] = administrator_login_password

    addresses = set()
    for _ in range(50):
        try:
            connection = mysql_connector.connect(**kwargs)
            connection.close()
        except mysql_connector.errors.DatabaseError as ex:
            pattern = re.compile(r'.*\'(?P<ipAddress>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\'')
            try:
                addresses.add(pattern.match(str(ex)).groupdict().get('ipAddress'))
            except AttributeError:
                pass

    # Create firewall rules for devbox if needed
    firewall_client = cf_mysql_firewall_rules(cmd.cli_ctx, None)

    if addresses and len(addresses) == 1:
        ip_address = addresses.pop()
        logger.warning('Configuring firewall rule, \'devbox\', to allow for your ip address: %s', ip_address)
        resolve_poller(
            firewall_client.create_or_update(resource_group_name, server_name, 'devbox', ip_address, ip_address),
            cmd.cli_ctx, 'MySQL Firewall Rule Create/Update')
    elif addresses:
        logger.warning('Detected dynamic IP address, configuring firewall rules for IP addresses encountered ...')
        logger.warning('IP Addresses: %s', ', '.join(list(addresses)))
        firewall_results = []
        for i, ip_address in enumerate(addresses):
            firewall_results.append(firewall_client.create_or_update(
                resource_group_name, server_name, 'devbox' + str(i), ip_address, ip_address))
        for result in firewall_results:
            resolve_poller(result, cmd.cli_ctx, 'MySQL Firewall Rule Create/Update')
    logger.warning('If MySQL server declines your IP address, please create a new firewall rule using:')
    logger.warning('    `az mysql server firewall-rule create -g %s -s %s -n {rule_name} '
                   '--start-ip-address {ip_address} --end-ip-address {ip_address}`',
                   resource_group_name, server_name)

    # connect to mysql and run some commands
    if administrator_login_password is not None:
        _run_mysql_commands(host, user, administrator_login_password, database_name)

    return {
        'connectionStrings': _create_mysql_connection_string(
            host, user, administrator_login_password, database_name),
        'host': host,
        'username': user,
        'password': administrator_login_password if administrator_login_password is not None else '*****'
    }


def _create_mysql_connection_string(host, user, password, database):
    result = {
        MySqlClient.mysql_cmd: "mysql {database} --host {host} --user {user} --password={password}",
        MySqlClient.ado_net: "Server={host}; Port=3306; Database={database}; Uid={user}; Pwd={password}; "
                             "SslMode=Preferred;",
        MySqlClient.jdbc: "String url ='jdbc:mysql://{host}:3306/{database}?useSSL=true&requireSSL=false'; "
                          "myDbConn = DriverManager.getConnection(url, '{user}', {password});",
        MySqlClient.nodejs: "var conn = mysql.createConnection({{host: '{host}', user: '{user}', "
                            "password: {password}, database: {database}, port: 3306, "
                            "ssl:{{ca:fs.readFileSync({{ca-cert filename}})}}}});",
        MySqlClient.php: "$con=mysqli_init(); mysqli_ssl_set($con, NULL, NULL, {{ca-cert filename}}, NULL, NULL); "
                         "mysqli_real_connect($con, '{host}', '{user}', {password}, {database}, 3306);",
        MySqlClient.python: "cnx = mysql.connector.connect(user='{user}', password={password}, host='{host}', "
                            "port=3306, database={database}, ssl_ca={{ca-cert filename}}, ssl_verify_cert=true)",
        MySqlClient.ruby: "client = Mysql2::Client.new(username: '{user}', password: {password}, "
                          "database: {database}, host: '{host}', port: 3306, sslca:{{ca-cert filename}}, "
                          "sslverify:false, sslcipher:'AES256-SHA')"
    }

    connection_kwargs = {
        'host': host,
        'user': user,
        'password': password if password is not None else '{your_password}',
        'database': database
    }

    for k, v in result.items():
        result[k] = v.format(**connection_kwargs)
    return result


def _run_mysql_commands(host, user, password, database):
    # Connect to mysql and get cursor to run sql commands
    connection = mysql_connector.connect(user=user, host=host, password=password)
    logger.warning('Successfully Connected to MySQL.')
    cursor = connection.cursor()
    try:
        cursor.execute("CREATE DATABASE {}".format(database))
        logger.warning("Ran Database Query: `CREATE DATABASE %s`", database)
    except mysql_connector.errors.DatabaseError:
        pass
    try:
        cursor.execute("CREATE USER 'root' IDENTIFIED BY '{}'".format(database))
        logger.warning("Ran Database Query: `CREATE USER 'root' IDENTIFIED BY '%s'`", database)
    except mysql_connector.errors.DatabaseError:
        pass
    cursor.execute("GRANT ALL PRIVILEGES ON {}.* TO 'root'".format(database))
    logger.warning("Ran Database Query: `GRANT ALL PRIVILEGES ON %s.* TO 'root'`", database)


def _update_mysql_server(cmd, client, server_result, resource_group_name, server_name, backup_retention,
                         geo_redundant_backup, storage_mb, administrator_login_password, version, ssl_enforcement,
                         tags):
    # storage profile params
    storage_profile_kwargs = {}
    if backup_retention != server_result.storage_profile.backup_retention_days:
        update_kwargs(storage_profile_kwargs, 'backup_retention_days', backup_retention)
    if geo_redundant_backup != server_result.storage_profile.geo_redundant_backup:
        update_kwargs(storage_profile_kwargs, 'geo_redundant_backup', geo_redundant_backup)
    if storage_mb != server_result.storage_profile.storage_mb:
        update_kwargs(storage_profile_kwargs, 'storage_mb', storage_mb)

    # update params
    server_update_kwargs = {
        'storage_profile': mysql.models.StorageProfile(**storage_profile_kwargs)
    } if storage_profile_kwargs else {}
    update_kwargs(server_update_kwargs, 'administrator_login_password', administrator_login_password)
    if version != server_result.version:
        update_kwargs(server_update_kwargs, 'version', version)
    if ssl_enforcement != server_result.ssl_enforcement:
        update_kwargs(server_update_kwargs, 'ssl_enforcement', ssl_enforcement)
    update_kwargs(server_update_kwargs, 'tags', tags)

    if server_update_kwargs:
        logger.warning('Updating existing MySQL Server \'%s\' with given arguments', server_name)
        params = mysql.models.ServerUpdateParameters(**server_update_kwargs)
        return resolve_poller(client.update(
            resource_group_name, server_name, params), cmd.cli_ctx, 'MySQL Server Update')
    return server_result
