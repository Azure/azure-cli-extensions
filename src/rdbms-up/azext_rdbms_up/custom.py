# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
from msrestazure.azure_exceptions import CloudError
from azure.cli.core.commands import LongRunningOperation, _is_poller
from knack.log import get_logger
from azext_rdbms_up.vendored_sdks.azure_mgmt_rdbms import mysql
from azext_rdbms_up._client_factory import cf_mysql_firewall_rules, cf_mysql_config
from azext_rdbms_up.mysql_util import ClientType as MySqlClient
import mysql.connector as mysql_connector

logger = get_logger(__name__)


def mysql_up(cmd, client, resource_group_name=None, server_name=None, sku_name=None,
             location=None, administrator_login=None, administrator_login_password=None, backup_retention=None,
             geo_redundant_backup=None, ssl_enforcement=None, storage_mb=None, database_name=None, tags=None,
             version=None):
    try:
        server_result = client.get(resource_group_name, server_name)
        logger.warning('Found existing MySql Server \'%s\' ...', server_name)
    except CloudError as ex:
        # Create mysql server
        logger.warning('Creating MySql Server \'%s\' ...', server_name)
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

        server_result = client.create(resource_group_name, server_name, parameters)
        if _is_poller(server_result):
            server_result = LongRunningOperation(cmd.cli_ctx, 'Starting {}'.format(cmd.name))(server_result)

        # Set timeout configuration
        logger.warning('Configuring wait timeout to 8 hours ...')
        config_client = cf_mysql_config(cmd.cli_ctx, None)
        config_result = config_client.create_or_update(resource_group_name, server_name, 'wait_timeout', '28800')
        if _is_poller(config_result):
            config_result = LongRunningOperation(cmd.cli_ctx, 'Starting {}'.format(cmd.name))(config_result)

        # Create firewall rule to allow for Azure IPs
        logger.warning('Configuring firewall rule, \'azure-access\', to allow for Azure IPs ...')
        firewall_client = cf_mysql_firewall_rules(cmd.cli_ctx, None)
        firewall_result = firewall_client.create_or_update(
            resource_group_name, server_name, 'azure-access', '0.0.0.0', '0.0.0.0')
        if _is_poller(firewall_result):
            firewall_result = LongRunningOperation(cmd.cli_ctx, 'Starting {}'.format(cmd.name))(firewall_result)


    # Check for user's ip address
    ip_address = None
    # TODO get user, hostname
    user = '{}@{}'.format(administrator_login, server_name)
    host = server_result.fully_qualified_domain_name
    try:
        mysql_connector.connect(user=user, host=host, password=administrator_login_password)
    except mysql_connector.errors.DatabaseError as ex:
        pattern = re.compile(r'.*IP address \'(?P<ipAddress>.*)\' is not allowed.*')
        ip_address = pattern.match(str(ex)).groupdict().get('ipAddress')

    # Create firewall rules for devbox if needed
    if ip_address:
        logger.warning('Configuring firewall rule, \'devbox\', to allow for your ip address: %s', ip_address)
        firewall_client = cf_mysql_firewall_rules(cmd.cli_ctx, None)
        firewall_result = firewall_client.create_or_update(
            resource_group_name, server_name, 'devbox', ip_address, ip_address)
        if _is_poller(firewall_result):
            firewall_result = LongRunningOperation(cmd.cli_ctx, 'Starting {}'.format(cmd.name))(firewall_result)

    _run_mysql_commands(host, user, administrator_login_password, database_name)

    return {
        'serverInfo': server_result,
        'connectionDetails': {
            'connectionStrings': _create_mysql_connection_string(
                host, user, administrator_login_password, database_name),
            'host': host,
            'username': user,
            'password': administrator_login_password
        }
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
        'password': password,
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
