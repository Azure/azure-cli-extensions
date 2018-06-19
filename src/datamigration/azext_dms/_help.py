# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['dms project create'] = """
    type: command
    short-summary: Create a migration Project which can contain multiple Tasks.
    long-summary: |
        This extension currently supports the following project configurations.
            -) source -> target :: data movement type
            1) SQL -> SQLDB :: One time
            2) PostgreSQL -> AzureDbForPostgreSql :: Continuous
            3) MySQL -> AzureDbForMySql :: Continuous

    parameters:
        - name: --source-platform
          type: string
          short-summary: >
            The type of server for the source database. The supported types are: SQL, PostgreSQL, MySQL
        - name: --target-platform
          type: string
          short-summary: >
            The type of service for the target database. The supported types are: SQLDB, AzureDbForPostgreSql, AzureDbForMySql.
    examples:
        - name: Create a SQL Project for a DMS instance.
          text: >
            az dms project create -l westus -n myproject -g myresourcegroup --service-name mydms --source-platform SQL--target-platform SQLDB --tags tagName1=tagValue1 tagWithNoValue
"""

helps['dms project task create'] = """
    type: command
    short-summary: Create a migration Project which can contain multiple Tasks.
    parameters:
        - name: --source-platform
          type: string
          short-summary: >
            The type of server for the source database. The supported types are: SQL, PostgreSQL, MySQL
        - name: --target-platform
          type: string
          short-summary: >
            The type of service for the target database. The supported types are: SQLDB, AzureDbForPostgreSql, AzureDbForMySql.
        - name: --database-options-json
          type: string
          short-summary: >
            Database and table information. This can be either a JSON-formatted string or the location to a file containing the JSON object. See example below for the format.
        - name: --source-connection-json
          type: string
          short-summary: >
            The connection information to the source server. This can be either a JSON-formatted string or the location to a file containing the JSON object. See example below for the format.
        - name: --target-connection-json
          type: string
          short-summary: >
            The connection information to the target server. This can be either a JSON-formatted string or the location to a file containing the JSON object. See example below for the format.
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
    examples:
        - name: Create and start a SQL Task which performs no validation checks.
          text: >
            az dms project task create --database-options-json C:\\CLI Files\\databaseOptions.json -n mytask --project-name myproject -g myresourcegroup --service-name mydms --source-connection-json '{'dataSource': 'myserver', 'authentication': 'SqlAuthentication', 'encryptConnection': 'true', 'trustServerCertificate': 'true'}' --target-connection-json C:\\CLI Files\\targetConnection.json
        - name: Create and start a SQL Task which performs all validation checks.
          text: >
            az dms project task create --database-options-json C:\\CLI Files\\databaseOptions.json -n mytask --project-name myproject -g myresourcegroup --service-name mydms --source-connection-json C:\\CLI Files\\sourceConnection.json --target-connection-json C:\\CLI Files\\targetConnection.json --enable-data-integrity-validation=True --enable-query-analysis-validation --enable-schema-validation
        - name: For SQL, the format of the database options JSON object.
          long-summary: |
            For SQL we support per table migrations. To use this, specify the tables names in the 'table_map' as below.
            YOu can aslo set the source as read only.
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
        - name: For PostgreSQL and MySQL, the format of the database options JSON object.
          text: >
            [
                {
                    "name": "source database",
                    "target_database_name": "target database",
                },
                ...n
            ]
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
        - name: The format of the connection JSON object for PostgreSql connections.
          text: >
            {
                "userName": "user name",    // if this is missing or null, you will be prompted
                "password": null,           // if this is missing or null (highly recommended) you will be prompted
                "serverName": "server name",
                "databaseName": "database name", // if this is missing, it will default to the 'postgres' database
                "port": 5432                // if this is missing, it will default to 5432
            }
"""

helps['dms project task cutover'] = """
    type: command
    short-summary: For a continuous task, complete the migration by performing a cutover.
    parameters:
        - name: --database-name
          type: string
          short-summary: >
            The name of the database on the source you wish to cutover.
"""
