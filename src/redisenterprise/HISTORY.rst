.. :changelog:

Release History
===============
1.5.0b1
- Preview release. Adds support for the 2025-08-01-preview, 2026-02-01-preview, and 2026-05-01-preview API versions.
- Added a new command group `az redisenterprise migration` to migrate an existing Azure Cache for Redis instance into an Azure Managed Redis (Redis Enterprise) cluster:
  - `start`: start a migration from a source Azure Cache for Redis resource. The source properties are exposed as flat arguments: `--source-resource-id`, `--skip-data-migration`, `--switch-dns`, and `--force-migrate`.
  - `validate`: validate whether a source Azure Cache for Redis resource can be migrated to the target cluster.
  - `undo`: cancel or roll back an in-progress migration.
  - `list` / `show`: view migration attempts on a cluster.
- Added `--maintenance-config`/`--maintenance-configuration` to `az redisenterprise create` and `az redisenterprise update` to configure cluster-level maintenance, including custom maintenance windows that control when maintenance is applied to the cluster.
- Added `--notify-keyspace-events` to `az redisenterprise database create` and `az redisenterprise database update` to configure Redis keyspace notifications. Defaults to disabled (empty string); when set, the value must include at least 'K' (keyspace events) or 'E' (keyevent events), for example 'AKE' to enable all standard events.
- Added `--access-string` to `az redisenterprise database access-policy-assignment create` and `update` to set a custom Redis ACL permissions string for the assignment (for example, `+@read ~cache:*`); defaults to `+@all ~*` when not specified.

1.4.0
- add a new command `az redisenterprise test-connection` to test the connection to a cluster.

1.3.1
- Fixed an issue where updating sku from Azure Cache for Enterprise to Azure Managed Redis SKU was not working as expected.

1.3.0
- Added a new required property: PublicNetworkAccess for Cluster.
- Updated the default value of AccessKeysAuthentication property for Database to 'Disabled'.

1.2.3
- Added breaking change warning for upcoming release

1.2.2
- Added breaking change warning for upcoming release

1.2.1
- Added support for listing all SKUs a cluster can scale to.
- Added a new enum: NoCluster for Clustering policy.

1.2.1b2
+++++++++
- Update module documentation.

1.2.1b1
+++++++++
- Fix: Make latest version as peview as last 2 versions(1.2.0 abd 1.1.0) are mistakenly not marked as preview.

1.2.0
+++++++++
- Fixes for highAvailability and accessKeysAuthentication argument.

1.1.0
+++++++++
- Adds support for using Microsoft Entra token-based authentication.
- Cluster has new properties: highAvailability and redundancyMode.
- New product SKUs added.
- Database has new properties: accessKeysAuthentication.

1.0.0
+++++++++
- Added support for new enterprise SKU E1

0.1.4
+++++++++
- Added support for new enterprise SKU's E5, E200, E400

0.1.3
++++++
- Added support for flushing the data in case of geo replicated cache
- Added support for customer managed keys

0.1.2
++++++
- Added support for active georeplication
	- Creating a georeplicated database
	- Creating a cache with a georeplicated database
	- Force unlinking databases
- Added support for importing from multiple blobs

0.1.1
++++++
* Renamed remaining snake_case command output fields to camelCase to be consistent with the REST API.
* Listed the following cluster attribute as null in the command output when the cluster attribute is null: zones.

0.1.0
++++++
* Initial release.
