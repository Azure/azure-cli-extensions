.. :changelog:

Release History
===============

=======
1.0.0b1
++++++
* Added support for version update in command `az datamigration login-migration`.

0.6.1
++++++
* Added parameter to help gather telemetry in command `az datamigration tde-migration`.

0.6.0
++++++
* [NEW COMMAND] `az datamigration sql-server-schema` : Migrate database schema objects to the target Azure Sql Servers.

0.5.0
++++++
* [NEW COMMAND] `az datamigration tde-migration` : Migrate TDE certificate from source SQL Server to the target Azure SQL Server.

0.4.1
++++++
* Bug fix for list-logins parameter in command "az datamigration login-migration".

0.4.0
++++++
* [NEW COMMAND] `az datamigration login-migration` : Migrate logins from the source Sql Servers to the target Azure Sql Servers.

0.3.1
++++++
* [NEW PARAMETER] `az datamigration register-integration-runtime`: Added parameter `--installed-ir-path` to read the installed location of Microsoft Integration Runtime (SHIR) and use it for registering the Database Migration Service if command is unable to find the installed SHIR path. 
* [NEW PARAMETER] `az datamigration performance-data-collection`: Added parameter `--time` to specify the amount of time(in seconds) performance data collection is to be done. After the timeout the process is terminated automatically.

0.3.0
++++++
* [BREAKING CHANGE] `az datamigration sql-managed-instance/sql-vm create`: Remove `--provisioing-error` and `--migration-operation-id` as they are unnecessary parameters. 
* [BREAKING CHANGE] `az datamigration sql-managed-instance/sql-vm cancel/cutover`: Making `--migration-operation-id` as a required parameter.
* [BREAKING CHANGE] `az datamigration performance-data-collection`: Rename `--number-of-interation` to `--number-of-iteration` for typo correction
* [NEW COMMAND GROUP] `az datamigration sql-db`: Manage database migrations to SQL DB instance.

0.2.0
++++++
* Bug fix for Multiple connection strings in az datamigration get-assessment command.
* [NEW COMMAND] `az datamigration performance-data-collection` - Collect performance data for given SQL Server instance(s).
* [NEW COMMAND] `az datamigration get-sku-recommendation` - Give SKU recommendations for Azure SQL offerings.

0.1.0
++++++
* Initial release.
