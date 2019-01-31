# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=import-error,too-many-locals
import re
import uuid
from msrestazure.azure_exceptions import CloudError
from knack.log import get_logger
from knack.util import CLIError
import mysql.connector as mysql_connector
import psycopg2
from azext_db_up.vendored_sdks.azure_mgmt_rdbms import mysql, postgresql
from azext_db_up._client_factory import (
    cf_mysql_firewall_rules, cf_mysql_config, cf_mysql_db,
    cf_postgres_firewall_rules, cf_postgres_config, cf_postgres_db,
    resource_client_factory)
from azext_db_up.util import update_kwargs, resolve_poller

logger = get_logger(__name__)


def mysql_up(cmd, client, resource_group_name=None, server_name=None, location=None, backup_retention=None,
             sku_name=None, geo_redundant_backup=None, storage_mb=None, administrator_login=None,
             administrator_login_password=None, version=None, ssl_enforcement=None, database_name=None, tags=None):
    db_context = DbContext(
        azure_sdk=mysql, cf_firewall=cf_mysql_firewall_rules, cf_db=cf_mysql_db,
        cf_config=cf_mysql_config, logging_name='MySQL', connector=mysql_connector, command_group='mysql',
        server_client=client)

    try:
        server_result = client.get(resource_group_name, server_name)
        logger.warning('Found existing MySQL Server \'%s\'...', server_name)
        # update server if needed
        server_result = _update_server(
            db_context, cmd, client, server_result, resource_group_name, server_name, backup_retention,
            geo_redundant_backup, storage_mb, administrator_login_password, version, ssl_enforcement, tags)
    except CloudError:
        # Create mysql server
        if administrator_login_password is None:
            administrator_login_password = str(uuid.uuid4())
        server_result = _create_server(
            db_context, cmd, resource_group_name, server_name, location, backup_retention,
            sku_name, geo_redundant_backup, storage_mb, administrator_login, administrator_login_password, version,
            ssl_enforcement, tags)

        # Set timeout configuration
        logger.warning('Configuring wait timeout to 8 hours...')
        config_client = cf_mysql_config(cmd.cli_ctx, None)
        resolve_poller(
            config_client.create_or_update(resource_group_name, server_name, 'wait_timeout', '28800'),
            cmd.cli_ctx, 'MySQL Configuration Update')

        # Create firewall rule to allow for Azure IPs
        _create_azure_firewall_rule(db_context, cmd, resource_group_name, server_name)

    # Create mysql database if it does not exist
    _create_database(db_context, cmd, resource_group_name, server_name, database_name)

    # check ip address(es) of the user and configure firewall rules
    mysql_errors = (mysql_connector.errors.DatabaseError)
    host, user = _configure_firewall_rules(
        db_context, mysql_errors, cmd, server_result, resource_group_name, server_name, administrator_login,
        administrator_login_password, database_name)

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


def postgres_up(cmd, client, resource_group_name=None, server_name=None, location=None, backup_retention=None,
                sku_name=None, geo_redundant_backup=None, storage_mb=None, administrator_login=None,
                administrator_login_password=None, version=None, ssl_enforcement=None, database_name=None, tags=None):
    db_context = DbContext(
        azure_sdk=postgresql, cf_firewall=cf_postgres_firewall_rules, cf_db=cf_postgres_db,
        cf_config=cf_postgres_config, logging_name='PostgreSQL', connector=psycopg2, command_group='postgres',
        server_client=client)

    try:
        server_result = client.get(resource_group_name, server_name)
        logger.warning('Found existing PostgreSQL Server \'%s\'...', server_name)
        # update server if needed
        server_result = _update_server(
            db_context, cmd, client, server_result, resource_group_name, server_name, backup_retention,
            geo_redundant_backup, storage_mb, administrator_login_password, version, ssl_enforcement, tags)
    except CloudError:
        # Create postgresql server
        if administrator_login_password is None:
            administrator_login_password = str(uuid.uuid4())
        server_result = _create_server(
            db_context, cmd, resource_group_name, server_name, location, backup_retention,
            sku_name, geo_redundant_backup, storage_mb, administrator_login, administrator_login_password, version,
            ssl_enforcement, tags)

        # Set timeout configuration
        logger.warning('Configuring wait timeout to 8 hours...')
        config_client = cf_postgres_config(cmd.cli_ctx, None)
        resolve_poller(
            config_client.create_or_update(
                resource_group_name, server_name, 'idle_in_transaction_session_timeout', '28800000'),
            cmd.cli_ctx, 'PostgreSQL Configuration Update')

        # Create firewall rule to allow for Azure IPs
        _create_azure_firewall_rule(db_context, cmd, resource_group_name, server_name)

    # Create postgresql database if it does not exist
    _create_database(db_context, cmd, resource_group_name, server_name, database_name)

    # check ip address(es) of the user and configure firewall rules
    postgres_errors = (psycopg2.OperationalError)
    host, user = _configure_firewall_rules(
        db_context, postgres_errors, cmd, server_result, resource_group_name, server_name, administrator_login,
        administrator_login_password, database_name)

    # connect to postgresql and run some commands
    if administrator_login_password is not None:
        _run_postgresql_commands(host, user, administrator_login_password, database_name)

    return {
        'connectionStrings': _create_postgresql_connection_string(
            host, user, administrator_login_password, database_name),
        'host': host,
        'username': user,
        'password': administrator_login_password if administrator_login_password is not None else '*****'
    }


def server_down(cmd, client, resource_group_name=None, server_name=None, delete_group=None):
    if delete_group:
        resource_client = resource_client_factory(cmd.cli_ctx)
        if resource_group_name is None:
            raise CLIError("Expected a a resource group name saved in cache.")

        # delete resource group
        logger.warning('Deleting Resource Group \'%s\'...', resource_group_name)
        return resource_client.resource_groups.delete(resource_group_name)
    logger.warning('Deleting server \'%s\'...', server_name)
    return client.delete(resource_group_name, server_name)


def _create_mysql_connection_string(host, user, password, database):
    result = {
        'mysql_cmd': "mysql {database} --host {host} --user {user} --password={password}",
        'ado.net': "Server={host}; Port=3306; Database={database}; Uid={user}; Pwd={password}; SslMode=Preferred;",
        'jdbc': "String url ='jdbc:mysql://{host}:3306/{database}?useSSL=true&requireSSL=false'; "
                "Connection myDbConn = DriverManager.getConnection(url, '{user}', '{password}');",
        'node.js': "var conn = mysql.createConnection({{host: '{host}', user: '{user}', "
                   "password: {password}, database: {database}, port: 3306, "
                   "ssl:{{ca:fs.readFileSync({{ca-cert filename}})}}}});",
        'php': "$con=mysqli_init(); mysqli_ssl_set($con, NULL, NULL, {{ca-cert filename}}, NULL, NULL); "
               "mysqli_real_connect($con, '{host}', '{user}', {password}, {database}, 3306);",
        'python': "cnx = mysql.connector.connect(user='{user}', password='{password}', host='{host}', "
                  "port=3306, database='{database}', ssl_ca='{{ca-cert filename}}', ssl_verify_cert=True)",
        'ruby': "client = Mysql2::Client.new(username: '{user}', password: '{password}', "
                "database: '{database}', host: '{host}', port: 3306, sslca:'{{ca-cert filename}}', "
                "sslverify:false, sslcipher:'AES256-SHA')",
        'webapp': "Database={database}; Data Source={host}; User Id={user}; Password={password}"
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


def _create_postgresql_connection_string(host, user, password, database):
    result = {
        'psql_cmd': "psql --host={host} --port=5432 --username={user} --dbname={database}",
        'ado.net': "Server={host};Database={database};Port=5432;User Id={user};Password={password};SSL=true;"
                   "SslMode=Require;",
        'jdbc': "jdbc:postgresql://{host}:5432/{database}?user={user}&password={password}&sslmode=required",
        'node.js': "host={host} port=5432 dbname={database} user={user} password={password} sslmode=required",
        'php': "host={host} port=5432 dbname={database} user={user} password={password} sslmode=required",
        'python': "dbname='{database}' user='{user}' host='{host}' password='{password}' port='5432' sslmode=true'",
        'ruby': "host={host}; dbname={database} user={user} password={password} port=5432 sslmode=require",
        'webapp': "Database={database}; Data Source={host}; User Id={user}; Password={password}"
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
    connection = mysql_connector.connect(user=user, host=host, password=password, database=database)
    logger.warning('Successfully Connected to MySQL.')
    cursor = connection.cursor()
    try:
        cursor.execute("CREATE USER 'root' IDENTIFIED BY '{}'".format(database))
        logger.warning("Ran Database Query: `CREATE USER 'root' IDENTIFIED BY '%s'`", database)
    except mysql_connector.errors.DatabaseError:
        pass
    cursor.execute("GRANT ALL PRIVILEGES ON {}.* TO 'root'".format(database))
    logger.warning("Ran Database Query: `GRANT ALL PRIVILEGES ON %s.* TO 'root'`", database)


def _run_postgresql_commands(host, user, password, database):
    # Connect to postgresql and get cursor to run sql commands
    connection = psycopg2.connect(user=user, host=host, password=password, database=database)
    connection.set_session(autocommit=True)
    logger.warning('Successfully Connected to PostgreSQL.')
    cursor = connection.cursor()
    try:
        cursor.execute("CREATE USER root WITH ENCRYPTED PASSWORD '{}'".format(database))
        logger.warning("Ran Database Query: `CREATE USER root WITH ENCRYPTED PASSWORD '%s'`", database)
    except psycopg2.ProgrammingError:
        pass
    cursor.execute("GRANT ALL PRIVILEGES ON DATABASE {} TO root".format(database))
    logger.warning("Ran Database Query: `GRANT ALL PRIVILEGES ON DATABASE %s TO root`", database)


def _configure_firewall_rules(
        db_context, connector_errors, cmd, server_result, resource_group_name, server_name, administrator_login,
        administrator_login_password, database_name):
    # unpack from context
    connector, cf_firewall, command_group, logging_name = (
        db_context.connector, db_context.cf_firewall, db_context.command_group, db_context.logging_name)

    # Check for user's ip address(es)
    user = '{}@{}'.format(administrator_login, server_name)
    host = server_result.fully_qualified_domain_name
    kwargs = {'user': user, 'host': host, 'database': database_name}
    if administrator_login_password is not None:
        kwargs['password'] = administrator_login_password

    addresses = set()
    logger.warning('Checking your ip address...')
    for _ in range(20):
        try:
            connection = connector.connect(**kwargs)
            connection.close()
        except connector_errors as ex:
            pattern = re.compile(r'.*[\'"](?P<ipAddress>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)[\'"]')
            try:
                addresses.add(pattern.match(str(ex)).groupdict().get('ipAddress'))
            except AttributeError:
                pass

    # Create firewall rules for devbox if needed
    firewall_client = cf_firewall(cmd.cli_ctx, None)

    if addresses and len(addresses) == 1:
        ip_address = addresses.pop()
        logger.warning('Configuring server firewall rule, \'devbox\', to allow for your ip address: %s', ip_address)
        resolve_poller(
            firewall_client.create_or_update(resource_group_name, server_name, 'devbox', ip_address, ip_address),
            cmd.cli_ctx, '{} Firewall Rule Create/Update'.format(logging_name))
    elif addresses:
        logger.warning('Detected dynamic IP address, configuring firewall rules for IP addresses encountered...')
        logger.warning('IP Addresses: %s', ', '.join(list(addresses)))
        firewall_results = []
        for i, ip_address in enumerate(addresses):
            firewall_results.append(firewall_client.create_or_update(
                resource_group_name, server_name, 'devbox' + str(i), ip_address, ip_address))
        for result in firewall_results:
            resolve_poller(result, cmd.cli_ctx, '{} Firewall Rule Create/Update'.format(logging_name))
    logger.warning('If %s server declines your IP address, please create a new firewall rule using:', logging_name)
    logger.warning('    `az %s server firewall-rule create -g %s -s %s -n {rule_name} '
                   '--start-ip-address {ip_address} --end-ip-address {ip_address}`',
                   command_group, resource_group_name, server_name)

    return host, user


def _create_database(db_context, cmd, resource_group_name, server_name, database_name):
    # check for existing database, create if not
    cf_db, logging_name = db_context.cf_db, db_context.logging_name
    database_client = cf_db(cmd.cli_ctx, None)
    try:
        database_client.get(resource_group_name, server_name, database_name)
    except CloudError:
        logger.warning('Creating %s database \'%s\'...', logging_name, database_name)
        resolve_poller(
            database_client.create_or_update(resource_group_name, server_name, database_name), cmd.cli_ctx,
            '{} Database Create/Update'.format(logging_name))


def _create_azure_firewall_rule(db_context, cmd, resource_group_name, server_name):
    # allow access to azure ip addresses
    cf_firewall, logging_name = db_context.cf_firewall, db_context.logging_name
    logger.warning('Configuring server firewall rule, \'azure-access\', to accept connections from all '
                   'Azure resources...')
    firewall_client = cf_firewall(cmd.cli_ctx, None)
    resolve_poller(
        firewall_client.create_or_update(resource_group_name, server_name, 'azure-access', '0.0.0.0', '0.0.0.0'),
        cmd.cli_ctx, '{} Firewall Rule Create/Update'.format(logging_name))


def _create_server(db_context, cmd, resource_group_name, server_name, location, backup_retention, sku_name,
                   geo_redundant_backup, storage_mb, administrator_login, administrator_login_password, version,
                   ssl_enforcement, tags):
    logging_name, azure_sdk, server_client = db_context.logging_name, db_context.azure_sdk, db_context.server_client
    logger.warning('Creating %s Server \'%s\'...', logging_name, server_name)

    parameters = azure_sdk.models.ServerForCreate(
        sku=azure_sdk.models.Sku(name=sku_name),
        properties=azure_sdk.models.ServerPropertiesForDefaultCreate(
            administrator_login=administrator_login,
            administrator_login_password=administrator_login_password,
            version=version,
            ssl_enforcement=ssl_enforcement,
            storage_profile=azure_sdk.models.StorageProfile(
                backup_retention_days=backup_retention,
                geo_redundant_backup=geo_redundant_backup,
                storage_mb=storage_mb)),
        location=location,
        tags=tags)

    return resolve_poller(
        server_client.create(resource_group_name, server_name, parameters), cmd.cli_ctx,
        '{} Server Create'.format(logging_name))


def _update_server(db_context, cmd, client, server_result, resource_group_name, server_name, backup_retention,
                   geo_redundant_backup, storage_mb, administrator_login_password, version, ssl_enforcement, tags):
    # storage profile params
    storage_profile_kwargs = {}
    db_sdk, logging_name = db_context.azure_sdk, db_context.logging_name
    if backup_retention != server_result.storage_profile.backup_retention_days:
        update_kwargs(storage_profile_kwargs, 'backup_retention_days', backup_retention)
    if geo_redundant_backup != server_result.storage_profile.geo_redundant_backup:
        update_kwargs(storage_profile_kwargs, 'geo_redundant_backup', geo_redundant_backup)
    if storage_mb != server_result.storage_profile.storage_mb:
        update_kwargs(storage_profile_kwargs, 'storage_mb', storage_mb)

    # update params
    server_update_kwargs = {
        'storage_profile': db_sdk.models.StorageProfile(**storage_profile_kwargs)
    } if storage_profile_kwargs else {}
    update_kwargs(server_update_kwargs, 'administrator_login_password', administrator_login_password)
    if version != server_result.version:
        update_kwargs(server_update_kwargs, 'version', version)
    if ssl_enforcement != server_result.ssl_enforcement:
        update_kwargs(server_update_kwargs, 'ssl_enforcement', ssl_enforcement)
    update_kwargs(server_update_kwargs, 'tags', tags)

    if server_update_kwargs:
        logger.warning('Updating existing %s Server \'%s\' with given arguments', logging_name, server_name)
        params = db_sdk.models.ServerUpdateParameters(**server_update_kwargs)
        return resolve_poller(client.update(
            resource_group_name, server_name, params), cmd.cli_ctx, '{} Server Update'.format(logging_name))
    return server_result


# pylint: disable=too-many-instance-attributes,too-few-public-methods
class DbContext:
    def __init__(self, azure_sdk=None, cf_firewall=None, cf_db=None, cf_config=None, logging_name=None,
                 connector=None, command_group=None, server_client=None):
        self.azure_sdk = azure_sdk
        self.cf_firewall = cf_firewall
        self.cf_db = cf_db
        self.cf_config = cf_config
        self.logging_name = logging_name
        self.connector = connector
        self.command_group = command_group
        self.server_client = server_client
