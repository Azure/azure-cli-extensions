.. :changelog:

Release History
===============

1.0.0b9
+++++++
* New api version.
* Expose separate encryption key URI and managed identity arguments on cluster create and restore, requiring both to enable Azure Key Vault encryption.
* Expose the same encryption arguments and managed identity alias on cluster update, supporting independent sparse updates.
* Add `az horizondb cluster restore` with an optional restore time and source cluster settings inheritance.
* Inherit restore geo-redundancy from the source and allow location overrides only for geo-redundancy-enabled sources.
* Create clusters without a default pool or pool-related arguments.
* Wait for cluster provisioning to succeed and display provisioning progress messages.

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
