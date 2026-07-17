.. :changelog:

Release History
===============

1.0.0b1
+++++++
* Initial release of the DocumentDB (Azure Cosmos DB for MongoDB vCore) extension.
* Add ``az documentdb mongocluster`` commands to create, update, show, list, and delete
  mongo clusters, list connection strings, and check name availability.
* Add ``az documentdb mongocluster firewall-rule`` commands to manage IP firewall rules.
* Add ``az documentdb mongocluster entra-user`` commands to manage Microsoft Entra ID
  database users.
* Add ``az documentdb mongocluster identity`` commands to manage the cluster's
  user-assigned managed identity.
* Add ``az documentdb mongocluster replica`` commands to list and promote read replicas,
  and ``replica create`` to create a cross-region GeoReplica.
* Add ``az documentdb mongocluster restore`` for point-in-time restore into a new cluster.
* Add ``az documentdb mongocluster reset-password`` to reset the administrator password.