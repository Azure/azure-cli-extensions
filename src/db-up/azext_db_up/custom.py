# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=import-error,too-many-locals
import os
import re
import sys
import uuid
from msrestazure.azure_exceptions import CloudError
from knack.log import get_logger
from knack.util import CLIError
import mysql.connector as mysql_connector
import psycopg2
from azext_db_up.vendored_sdks.azure_mgmt_rdbms import mysql, postgresql
from azext_db_up.vendored_sdks.azure_mgmt_sql import sql
from azext_db_up._client_factory import (
    cf_mysql_firewall_rules, cf_mysql_config, cf_mysql_db,
    cf_postgres_firewall_rules, cf_postgres_config, cf_postgres_db,
    cf_sql_firewall_rules, cf_sql_db,
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
        logger.warning('Found existing MySQL Server \'%s\' in group \'%s\'',
                       server_name, resource_group_name)
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
    mysql_errors = (mysql_connector.errors.DatabaseError, mysql_connector.errors.InterfaceError)
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
        logger.warning('Found existing PostgreSQL Server \'%s\' in group \'%s\'',
                       server_name, resource_group_name)
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

        # # Set timeout configuration
        # logger.warning('Configuring wait timeout to 8 hours...')
        # config_client = cf_postgres_config(cmd.cli_ctx, None)
        # resolve_poller(
        #     config_client.create_or_update(
        #         resource_group_name, server_name, 'idle_in_transaction_session_timeout', '28800000'),
        #     cmd.cli_ctx, 'PostgreSQL Configuration Update')

    # Create postgresql database if it does not exist
    _create_database(db_context, cmd, resource_group_name, server_name, database_name)

    # check ip address(es) of the user and configure firewall rules
    postgres_errors = (psycopg2.OperationalError)
    host, user = _configure_firewall_rules(
        db_context, postgres_errors, cmd, server_result, resource_group_name, server_name, administrator_login,
        administrator_login_password, database_name)

    # Create firewall rule to allow for Azure IPs
    # - Moved here to run every time after other firewall rules are configured because
    #   bug on server disables this whenever other firewall rules are added.
    _create_azure_firewall_rule(db_context, cmd, resource_group_name, server_name)

    # connect to postgresql and run some commands
    if administrator_login_password is not None:
        _run_postgresql_commands(host, user, administrator_login_password, database_name)

    return _form_response(
        _create_postgresql_connection_string(host, user, administrator_login_password, database_name),
        host, user,
        administrator_login_password if administrator_login_password is not None else '*****'
    )


def sql_up(cmd, client, resource_group_name=None, server_name=None, location=None, administrator_login=None,
           administrator_login_password=None, version=None, database_name=None, tags=None):
    _ensure_pymssql()
    import pymssql
    db_context = DbContext(
        azure_sdk=sql, cf_firewall=cf_sql_firewall_rules, cf_db=cf_sql_db,
        logging_name='SQL', command_group='sql', server_client=client, connector=pymssql)

    try:
        server_result = client.get(resource_group_name, server_name)
        logger.warning('Found existing PostgreSQL Server \'%s\' in group \'%s\'',
                       server_name, resource_group_name)
        # update server if needed
        server_result = _update_sql_server(
            db_context, cmd, client, server_result, resource_group_name, server_name, administrator_login_password,
            version, tags)
    except CloudError:
        # Create sql server
        if administrator_login_password is None:
            administrator_login_password = str(uuid.uuid4())
        server_result = _create_sql_server(
            db_context, cmd, resource_group_name, server_name, location, administrator_login,
            administrator_login_password, version, tags)

        # Create firewall rule to allow for Azure IPs
        _create_azure_firewall_rule(db_context, cmd, resource_group_name, server_name)

    # Create sql database if it does not exist
    _create_sql_database(db_context, cmd, resource_group_name, server_name, database_name, location)

    # check ip address(es) of the user and configure firewall rules
    sql_errors = (pymssql.InterfaceError, pymssql.OperationalError)
    host, user = _configure_firewall_rules(
        db_context, sql_errors, cmd, server_result, resource_group_name, server_name, administrator_login,
        administrator_login_password, database_name, {'tds_version': '7.0'})

    user = '{}@{}'.format(administrator_login, server_name)
    host = server_result.fully_qualified_domain_name

    # connect to sql server and run some commands
    if administrator_login_password is not None:
        _run_sql_commands(host, user, administrator_login_password, database_name)

    return _form_response(
        _create_sql_connection_string(host, user, administrator_login_password, database_name),
        host, user,
        administrator_login_password if administrator_login_password is not None else '*****'
    )


def _ensure_pymssql():
    # we make sure "pymssql" get setup here, because on OSX, pymssql requires homebrew "FreeTDS",
    # which pip is not able to handle.
    try:
        import pymssql  # pylint: disable=unused-import,unused-variable
    except ImportError:
        import subprocess
        logger.warning("Installing dependencies required to configure Azure SQL server...")
        if sys.platform == 'darwin':
            try:
                subprocess.check_output(['brew', 'list', 'freetds'], stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError:
                logger.warning('  Installing "freetds" through brew...')
                subprocess.check_output(['brew', 'install', 'freetds'])
        from azure.cli.core.extension import EXTENSIONS_DIR
        db_up_ext_path = os.path.join(EXTENSIONS_DIR, 'db-up')
        python_path = os.environ.get('PYTHONPATH', '')
        os.environ['PYTHONPATH'] = python_path + ':' + db_up_ext_path if python_path else db_up_ext_path
        cmd = [sys.executable, '-m', 'pip', 'install', '--target', db_up_ext_path,
               'pymssql==2.1.4', '-vv', '--disable-pip-version-check', '--no-cache-dir']
        logger.warning('  Installing "pymssql" pip packages')
        with HomebrewPipPatch():
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        import pymssql  # reload


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


def create_mysql_connection_string(
        server_name='{server}', database_name='{database}', administrator_login='{login}',
        administrator_login_password='{password}'):
    user = '{}@{}'.format(administrator_login, server_name)
    host = '{}.mysql.database.azure.com'.format(server_name)
    return _form_response(
        _create_mysql_connection_string(host, user, administrator_login_password, database_name),
        host, user, administrator_login_password
    )


def create_postgresql_connection_string(
        server_name='{server}', database_name='{database}', administrator_login='{login}',
        administrator_login_password='{password}'):
    user = '{}@{}'.format(administrator_login, server_name)
    host = '{}.postgres.database.azure.com'.format(server_name)
    return _form_response(
        _create_postgresql_connection_string(host, user, administrator_login_password, database_name),
        host, user, administrator_login_password
    )


def create_sql_connection_string(
        server_name='{server}', database_name='{database}', administrator_login='{login}',
        administrator_login_password='{password}'):
    user = '{}@{}'.format(administrator_login, server_name)
    host = '{}.database.windows.net'.format(server_name)
    return _form_response(
        _create_sql_connection_string(host, user, administrator_login_password, database_name),
        host, user, administrator_login_password
    )


def _form_response(connection_strings, host, username, password):
    return {
        'connectionStrings': connection_strings,
        'host': host,
        'username': username,
        'password': password
    }


def _create_mysql_connection_string(host, user, password, database):
    result = {
        'mysql_cmd': "mysql {database} --host {host} --user {user} --password={password}",
        'ado.net': "Server={host}; Port=3306; Database={database}; Uid={user}; Pwd={password};",
        'jdbc': "jdbc:mysql://{host}:3306/{database}?user={user}&password={password}",
        'jdbc Spring': "spring.datasource.url=jdbc:mysql://{host}:3306/{database}  "
                       "spring.datasource.username={user}  "
                       "spring.datasource.password={password}",
        'node.js': "var conn = mysql.createConnection({{host: '{host}', user: '{user}', "
                   "password: {password}, database: {database}, port: 3306}});",
        'php': "host={host} port=5432 dbname={database} user={user} password={password}",
        'python': "cnx = mysql.connector.connect(user='{user}', password='{password}', host='{host}', "
                  "port=3306, database='{database}')",
        'ruby': "client = Mysql2::Client.new(username: '{user}', password: '{password}', "
                "database: '{database}', host: '{host}', port: 3306)",
        'webapp': "Database={database}; Data Source={host}; User Id={user}; Password={password}"
    }

    connection_kwargs = {
        'host': host,
        'user': user,
        'password': password if password is not None else '{password}',
        'database': database
    }

    for k, v in result.items():
        result[k] = v.format(**connection_kwargs)
    return result


def _create_postgresql_connection_string(host, user, password, database):
    result = {
        'psql_cmd': "psql --host={host} --port=5432 --username={user} --dbname={database}",
        'ado.net': "Server={host};Database={database};Port=5432;User Id={user};Password={password};",
        'jdbc': "jdbc:postgresql://{host}:5432/{database}?user={user}&password={password}",
        'jdbc Spring': "spring.datasource.url=jdbc:postgresql://{host}:5432/{database}  "
                       "spring.datasource.username={user}  "
                       "spring.datasource.password={password}",
        'node.js': "var client = new pg.Client('postgres://{user}:{password}@{host}:5432/{database}');",
        'php': "host={host} port=5432 dbname={database} user={user} password={password}",
        'python': "cnx = psycopg2.connect(database='{database}', user='{user}', host='{host}', password='{password}', "
                  "port='5432')",
        'ruby': "cnx = PG::Connection.new(:host => '{host}', :user => '{user}', :dbname => '{database}', "
                ":port => '5432', :password => '{password}')",
        'webapp': "Database={database}; Data Source={host}; User Id={user}; Password={password}"
    }

    connection_kwargs = {
        'host': host,
        'user': user,
        'password': password if password is not None else '{password}',
        'database': database
    }

    for k, v in result.items():
        result[k] = v.format(**connection_kwargs)
    return result


def _create_sql_connection_string(host, user, password, database):
    result = {
        # https://docs.microsoft.com/en-us/azure/sql-database/sql-database-connect-query-nodejs
        'ado.net': "Server={host},1433;Initial Catalog={database};User ID={user};Password={password};",
        'jdbc': "jdbc:sqlserver://{host}:1433;database={database};user={user};password={password};",
        'odbc': "Driver={{ODBC Driver 13 for SQL Server}};Server={host},1433;Database={database};Uid={user};"
                "Pwd={password};",
        'php': "$conn = new PDO('sqlsrv:server={host} ; Database = {database}', '{user}', '{password}');",
        'python': "pyodbc.connect('DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};DATABASE={database};"
                  "UID={admin_login};PWD={password}')",
        "node.js": "var conn = new require('tedious').Connection("
                   "{{authentication: {{ options: {{ userName: '{user}', password: '{password}' }}, type: 'default'}}, "
                   "server: '{host}', options:{{ database: '{database}', encrypt: true }}}});",
        'jdbc Spring': "spring.datasource.url=jdbc:sqlserver://{host}:1433/sampledb spring.datasource.username={user}  "
                       "spring.datasource.password={password}",
        "ruby": "client = TinyTds::Client.new(username: {user}, password: {password}, host: {host}, port: 1433, "
                "database: {database}, azure: true)",
    }

    admin_login, _ = user.split('@')
    connection_kwargs = {
        'host': host,
        'user': user,
        'password': password if password is not None else '{password}',
        'database': database,
        'admin_login': admin_login
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
        db_password = _create_db_password(database)
        cursor.execute("CREATE USER 'root' IDENTIFIED BY '{}'".format(db_password))
        logger.warning("Ran Database Query: `CREATE USER 'root' IDENTIFIED BY '%s'`", db_password)
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
        db_password = _create_db_password(database)
        cursor.execute("CREATE USER root WITH ENCRYPTED PASSWORD '{}'".format(db_password))
        logger.warning("Ran Database Query: `CREATE USER root WITH ENCRYPTED PASSWORD '%s'`", db_password)
    except psycopg2.ProgrammingError:
        pass
    cursor.execute("GRANT ALL PRIVILEGES ON DATABASE {} TO root".format(database))
    logger.warning("Ran Database Query: `GRANT ALL PRIVILEGES ON DATABASE %s TO root`", database)


def _run_sql_commands(host, user, password, database):
    # Connect to sql and get cursor to run sql commands
    _ensure_pymssql()
    import pymssql
    with pymssql.connect(host, user, password, database, tds_version='7.0') as connection:
        logger.warning('Successfully Connected to PostgreSQL.')
        with connection.cursor() as cursor:
            try:
                db_password = _create_db_password(database)
                cursor.execute("CREATE USER root WITH PASSWORD = '{}'".format(db_password))
                logger.warning("Ran Database Query: `CREATE USER root WITH PASSWORD = '%s'`", db_password)
            except pymssql.ProgrammingError:
                pass
            cursor.execute("Use {};".format(database))
            cursor.execute("GRANT ALL to root")
            logger.warning("Ran Database Query: `GRANT ALL TO root`")


def _configure_firewall_rules(
        db_context, connector_errors, cmd, server_result, resource_group_name, server_name, administrator_login,
        administrator_login_password, database_name, extra_connector_args=None):
    # unpack from context
    connector, cf_firewall, command_group, logging_name = (
        db_context.connector, db_context.cf_firewall, db_context.command_group, db_context.logging_name)

    # Check for user's ip address(es)
    user = '{}@{}'.format(administrator_login, server_name)
    host = server_result.fully_qualified_domain_name
    kwargs = {'user': user, 'host': host, 'database': database_name}
    if administrator_login_password is not None:
        kwargs['password'] = administrator_login_password
    kwargs.update(extra_connector_args or {})
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


def _create_sql_database(db_context, cmd, resource_group_name, server_name, database_name, location):
    cf_db, logging_name, azure_sdk = db_context.cf_db, db_context.logging_name, db_context.azure_sdk
    database_client = cf_db(cmd.cli_ctx, None)
    try:
        database_client.get(resource_group_name, server_name, database_name)
    except CloudError:
        logger.warning('Creating %s database \'%s\'...', logging_name, database_name)
        params = azure_sdk.models.Database(location=location)
        resolve_poller(
            database_client.create_or_update(resource_group_name, server_name, database_name, params), cmd.cli_ctx,
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
    logger.warning('Creating %s Server \'%s\' in group \'%s\'...', logging_name, server_name, resource_group_name)

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


def _create_sql_server(db_context, cmd, resource_group_name, server_name, location, administrator_login,
                       administrator_login_password, version, tags):
    logging_name, azure_sdk, server_client = db_context.logging_name, db_context.azure_sdk, db_context.server_client
    logger.warning('Creating %s Server \'%s\' in group \'%s\'...', logging_name, server_name, resource_group_name)

    parameters = azure_sdk.models.Server(
        administrator_login=administrator_login,
        administrator_login_password=administrator_login_password,
        version=version,
        location=location,
        tags=tags)

    return resolve_poller(
        server_client.create_or_update(resource_group_name, server_name, parameters), cmd.cli_ctx,
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


def _update_sql_server(db_context, cmd, client, server_result, resource_group_name, server_name,
                       administrator_login_password, version, tags):
    db_sdk, logging_name = db_context.azure_sdk, db_context.logging_name

    # update params
    server_update_kwargs = {}
    update_kwargs(server_update_kwargs, 'administrator_login_password', administrator_login_password)
    if version != server_result.version:
        update_kwargs(server_update_kwargs, 'version', version)
    update_kwargs(server_update_kwargs, 'tags', tags)

    if server_update_kwargs:
        logger.warning('Updating existing %s Server \'%s\' with given arguments', logging_name, server_name)
        params = db_sdk.models.ServerUpdate(**server_update_kwargs)
        return resolve_poller(client.update(
            resource_group_name, server_name, params), cmd.cli_ctx, '{} Server Update'.format(logging_name))
    return server_result


def _create_db_password(database_name):
    return '{}{}{}'.format(database_name[0].upper(), database_name[1:], '1')


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


def is_homebrew():
    HOMEBREW_CELLAR_PATH = '/usr/local/Cellar/azure-cli/'
    return any((p.startswith(HOMEBREW_CELLAR_PATH) for p in sys.path))


# port from azure.cli.core.extension
# A workaround for https://github.com/Azure/azure-cli/issues/4428
class HomebrewPipPatch(object):  # pylint: disable=too-few-public-methods

    CFG_FILE = os.path.expanduser(os.path.join('~', '.pydistutils.cfg'))

    def __init__(self):
        self.our_cfg_file = False

    def __enter__(self):
        if not is_homebrew():
            return
        if os.path.isfile(HomebrewPipPatch.CFG_FILE):
            logger.debug("Homebrew patch: The file %s already exists and we will not overwrite it. "
                         "If extension installation fails, temporarily rename this file and try again.",
                         HomebrewPipPatch.CFG_FILE)
            logger.warning("Unable to apply Homebrew patch for extension installation. "
                           "Attempting to continue anyway...")
            self.our_cfg_file = False
        else:
            logger.debug("Homebrew patch: Temporarily creating %s to support extension installation on Homebrew.",
                         HomebrewPipPatch.CFG_FILE)
            with open(HomebrewPipPatch.CFG_FILE, "w") as f:
                f.write("[install]\nprefix=")
            self.our_cfg_file = True

    def __exit__(self, exc_type, exc_value, tb):
        if not is_homebrew():
            return
        if self.our_cfg_file and os.path.isfile(HomebrewPipPatch.CFG_FILE):
            logger.debug("Homebrew patch: Deleting the temporarily created %s", HomebrewPipPatch.CFG_FILE)
            os.remove(HomebrewPipPatch.CFG_FILE)
