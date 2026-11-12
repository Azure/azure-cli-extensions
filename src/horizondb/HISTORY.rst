.. :changelog:

Release History
===============

1.0.0b9
+++++++
* Update the management API to ``2026-10-01-preview`` with PostgreSQL 17 and 18 support.
* Breaking change: Move cluster and private connectivity commands under
  ``az horizondb cluster``. Manage pool firewall rules under
  ``az horizondb cluster pool firewall-rule``.
* Manage compute and high availability through ``az horizondb cluster pool``.
  Cluster creation no longer creates a default pool or accepts pool settings.
* Add ``az horizondb cluster restore`` with source settings inheritance and an
  optional ``--point-in-time-utc`` defaulting to five minutes before the current UTC time.
  Restore inherits the source's PostgreSQL version and geo-redundancy; location
  overrides require a geo-redundancy-enabled source.
* Support customer-managed encryption through ``--primary-key-uri`` and
  ``--primary-user-assigned-identity-id`` (alias ``--primary-user-id``).
  Create and restore require both arguments when overriding encryption, assign
  the selected identity to the cluster, and preserve existing identities on restore.
* Allow independent encryption key or identity updates on cluster update,
  sending only the supplied encryption fields.
* Wait for cluster create and restore provisioning to complete and return the
  resulting cluster; support ``--no-wait`` to submit without waiting.
* Add parameter-group updates and subscription-scoped listing. Associate custom
  parameter groups with existing pools using ``--param-group-id`` and
  ``--param-group-apply`` on pool update.
* Approve or reject private endpoint connections with
  ``az horizondb cluster private-endpoint-connection update --status Approved``
  or ``--status Rejected``. Use ``--resource-name`` for private-link-resource show.
* Standardize backup retention on ``--backup-retention-days``, retaining
  ``--retention-days`` as an alias on cluster create.

1.0.0b8
+++++++
* Add support for restoring HorizonDB clusters through `az horizondb restore`.

1.0.0b7
+++++++
* Add `az horizondb parameter-group` commands to create, delete, list, show, and list connections for HorizonDB parameter groups.

1.0.0b6
+++++++
* Add private endpoint connection commands: `az horizondb private-endpoint-connection list/show/approve/reject/delete`.
* Add private link resource commands: `az horizondb private-link-resource list/show`.

1.0.0b5
+++++++
* Add support for configuring public access on HorizonDB clusters through `az horizondb create --public-access` and `az horizondb update --public-access`. Supplying an IP address or range automatically creates a firewall rule.
* Add the `az horizondb firewall-rule` command group (`create`, `show`, `list`, `update`, `delete`) to manage cluster firewall rules.

1.0.0b4
+++++++
* Update validation checks for commands. Add short form arguments for user convenience.

1.0.0b3
+++++++
* Add support for assigning a parameter group to HorizonDB clusters through `az horizondb update --parameter-group`.

1.0.0b2
+++++++
* Add support for updating HorizonDB clusters through `az horizondb update`.

1.0.0b1
+++++++
* Add create, list, and delete commands for HorizonDB clusters.

0.1.0
++++++
* Initial release.
