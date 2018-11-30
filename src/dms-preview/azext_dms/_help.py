# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['dms project create'] = """
    type: command
    short-summary: Create a migration Project which can contain multiple Tasks.
    long-summary: |
        The following project configurations are supported:
            -) source -> target
            1) SQL -> SQLDB
            2) MySQL -> AzureDbForMySql
            3) PostgreSQL -> AzureDbForPostgreSQL
            4) MongoDB -> MongoDB (for migrating to Cosmos DB via their MongoDB API)

    parameters:
        - name: --source-platform
          type: string
          short-summary: >
            The type of server for the source database. The supported types are: SQL, MySQL, PostgreSQL, MongoDB.
        - name: --target-platform
          type: string
          short-summary: >
            The type of service for the target database. The supported types are: SQLDB, AzureDbForMySql, AzureDbForPostgreSQL, MongoDB.
    examples:
        - name: Create a SQL Project for a DMS instance.
          text: >
            az dms project create -l westus -n myproject -g myresourcegroup --service-name mydms --source-platform SQL --target-platform SQLDB --tags tagName1=tagValue1 tagWithNoValue
"""

helps['dms project task create'] = """
    type: command
    short-summary: Create and start a migration Task.
    long-summary: |
        The following task configurations are supported:
            -) source -> target :: task type
            1) SQL -> SQLDB :: OfflineMigration
            2) MySQL -> AzureDbForMySql :: OnlineMigration
            3) PostgreSQL -> AzureDbForPostgreSQL :: OnlineMigration
            4) MongoDB -> MongoDB (for migrating to Cosmos DB via their MongoDB API) :: OfflineMigration

    parameters:
        - name: --task-type
          type: string
          short-summary: >
            The type of data movement the task will support. The supported types are: OnlineMigration, OfflineMigration.
        - name: --database-options-json
          type: string
          short-summary: >
            Database and table information. This can be either a JSON-formatted string or the location to a file containing the JSON object. See examples below for the format.
        - name: --source-connection-json
          type: string
          short-summary: >
            The connection information to the source server. This can be either a JSON-formatted string or the location to a file containing the JSON object. See examples below for the format.
        - name: --target-connection-json
          type: string
          short-summary: >
            The connection information to the target server. This can be either a JSON-formatted string or the location to a file containing the JSON object. See examples below for the format.
        - name: --enable-data-integrity-validation
          type: bool
          short-summary: >
            (For SQL only) Whether to perform a checksum based data integrity validation between source and target for the selected database and tables.
        - name: --enable-query-analysis-validation
          type: bool
          short-summary: >
            (For SQL only) Whether to perform a quick and intelligent query analysis by retrieving queries from the source database and executing them in the target. The result will have execution statistics for executions in source and target databases for the extracted queries.
        - name: --enable-schema-validation
          type: bool
          short-summary: >
            (For SQL only) Whether to compare the schema information between source and target.
        - name: --validate-only
          type: bool
          short-summary: >
            (For MongoDB to Cosmos DB only) Whether to run validation only and NOT run migration. This is useful for verifying connections, shard keys, RU settings, etc.
    examples:
        - name: Create and start a SQL Task which performs no validation checks.
          text: >
            az dms project task create --database-options-json C:\\CLI Files\\databaseOptions.json -n mytask --project-name myproject -g myresourcegroup --service-name mydms --source-connection-json '{'dataSource': 'myserver', 'authentication': 'SqlAuthentication', 'encryptConnection': 'true', 'trustServerCertificate': 'true'}' --target-connection-json C:\\CLI Files\\targetConnection.json --source-platform sql --target-platform sqldb --task-type offlinemigration
        - name: Create and start a SQL Task which performs all validation checks.
          text: >
            az dms project task create --database-options-json C:\\CLI Files\\databaseOptions.json -n mytask --project-name myproject -g myresourcegroup --service-name mydms --source-connection-json C:\\CLI Files\\sourceConnection.json --target-connection-json C:\\CLI Files\\targetConnection.json --enable-data-integrity-validation=True --enable-query-analysis-validation --enable-schema-validation --source-platform sql --target-platform sqldb --task-type offlinemigration
        - name: For SQL, the format of the database options JSON object.
          long-summary: |
            For SQL we support per table migrations. To use this, specify the tables names in the 'table_map' as below.
            You can also set the source as read only.
          text: >
            [
                {
                    "name": "source database",
                    "target_database_name": "target database",
                    "make_source_db_read_only": false|true,
                    "table_map": {
                        "schema.SourceTableName1": "schema.TargetTableName1",
                        "schema.SourceTableName2": "schema.TargetTableName2",
                        ...n
                    }
                },
                ...n
            ]
        - name: For MySQL and PostgreSQL, the format of the database options JSON object.
          text: >
            [
                {
                    "name": "source database",
                    "target_database_name": "target database"
                },
                ...n
            ]
        - name: For MongoDB, the format of the database options JSON object.
          long-summary: |
            For MongoDB we support per collection migrations. To use this, specify the collections inside the database object as below.
          text: >
            {
                // set to zero to get the default boost during migration (recommended)
                "boostRUs": 0,
                // "OneTime" or "Continuous", only "OneTime" is currently supported
                "replication": "OneTime",
                // Set to null to use maximum resources available.
                "throttling": {
                    // percentage of the CPU to try to avoid using
                    "minFreeCpu": 25,
                    // amount of RAM (in MBs) to try to avoid using
                    "minFreeMemoryMb": 1024,
                    // max number of collections to migrate at a time
                    "maxParallelism": 2
                },
                "databases": {
                    "database_name": {
                        // see https://docs.microsoft.com/th-th/azure/cosmos-db/request-units,     ||
                        // set to null to use default
                        // or 0 if throughput should not be provisioned at the database level
                        "targetRUs": 0,
                        "collections": {
                            "collection_name_1": {
                                // Whether the target database/collection will be deleted if exists
                                "canDelete": true,
                                // set to null if target should not be sharded
                                // or to copy the shard key from source (if exists)
                                "shardKey": null,
                                // set to null to use default (recommended)
                                "targetRUs": null
                            },
                            "collection_name_2": {
                                "canDelete": true,
                                "shardKey": {
                                    "fields": [
                                        {
                                            "name": "field_name",
                                            // accepts "Forward", "Reverse", or "Hashed"
                                            "order": "Forward"
                                        },
                                        ...n
                                    ],
                                    // whether shard key is unique
                                    // see https://docs.microsoft.com/en-us/azure/cosmos-db/partition-data
                                    "isUnique": false
                                },
                                "targetRUs": 10000
                            },
                            ...n
                        }
                    },
                    ...n
                }
            }
        - name: The format of the connection JSON object for SQL connections.
          text: >
            {
                "userName": "user name",    // if this is missing or null, you will be prompted
                "password": null,           // if this is missing or null (highly recommended) you will be prompted
                "dataSource": "server name[,port]",
                "authentication": "SqlAuthentication|WindowsAuthentication",
                "encryptConnection": true,      // highly recommended to leave as true
                "trustServerCertificate": true  // highly recommended to leave as true
            }
        - name: The format of the connection JSON object for MySql connections.
          text: >
            {
                "userName": "user name",    // if this is missing or null, you will be prompted
                "password": null,           // if this is missing or null (highly recommended) you will be prompted
                "serverName": "server name",
                "port": 3306                // if this is missing, it will default to 3306
            }
        - name: The format of the connection JSON object for PostgreSQL connections.
          text: >
            {
                "userName": "user name",    // if this is missing or null, you will be prompted
                "password": null,           // if this is missing or null (highly recommended) you will be prompted
                "serverName": "server name",
                "databaseName": "database name", // if this is missing, it will default to the 'postgres' database
                "port": 5432                // if this is missing, it will default to 5432
            }
        - name: The format of the connection JSON object for MongoDB connections.
          text: >
            {
                "userName": null,   // if this is missing or null, you will be prompted
                "password": null,   // if this is missing or null (highly recommended) you will be prompted
                "connectionString": "mongodb://hostOrIp:port"
            }
"""

helps['dms project task cancel'] = """
    type: command
    short-summary: This command is being deprecated. Use the stop command instead.
    long-summary: |
        To keep a more consistent experience with Azure's portal UI use:
            az dms project task stop

    parameters:
        - name: --task-type
          type: string
          short-summary: >
            The type of data movement the task was created for. The supported types are: OnlineMigration, OfflineMigration.
        - name: --object-name
          type: string
          short-summary: >
            Supported by MongoDB migrations only.
            The qualified name of the database or collection you wish to stop. Leave blank to stop the entire migration.
"""

helps['dms project task cutover'] = """
    type: command
    short-summary: For an online migration task, complete the migration by performing a cutover.
    long-summary: |
        To see the result of the request, please use the 'task show' command:
            az dms project task show ... --expand command

    parameters:
        - name: --object-name
          type: string
          short-summary: >
            For MongoDB migrations, the qualified name of the database or collection you wish to cutover.
            Leave blank to cutover the entire migration.
            For all other migration types, the name of the database on the source you wish to cutover.
        - name: --immediate
          type: bool
          short-summary: >
            For MongoDB migrations, whether to cutover immediately or to let the currently loaded events
            get migrated.
            For all other migration types, this has no effect.
"""

helps['dms project task restart'] = """
    type: command
    short-sumary: Restart either the entire migration or just a specified object. Currently only supported by MongoDB migrations.
    long-summary: |
        To see the result of the request, please use the 'task show' command:
            az dms project task show ... --expand command

    parameters:
        - name: --task-type
          type: string
          short-summary: >
            The type of data movement the task was created for. The supported types are: OnlineMigration, OfflineMigration.
        - name: --object-name
          type: string
          short-summary: >
            The qualified name of the database or collection you wish to restart. Leave blank to restart the entire migration.
"""

helps['dms project task stop'] = """
    type: command
    short-summary: Stops the task, or stops migration on the specified object (MongoDB migrations only).
    long-summary: |
        To see the result of the request, please use the 'task show' command:
            az dms project task show ... --expand command

    parameters:
        - name: --task-type
          type: string
          short-summary: >
            The type of data movement the task was created for. The supported types are: OnlineMigration, OfflineMigration.
        - name: --object-name
          type: string
          short-summary: >
            Supported by MongoDB migrations only.
            The qualified name of the database or collection you wish to stop. Leave blank to stop the entire migration.
"""
