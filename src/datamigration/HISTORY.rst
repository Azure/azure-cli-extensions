.. :changelog:

Release History
===============

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
