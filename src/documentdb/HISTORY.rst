.. :changelog:

Release History
===============

1.0.0b2
+++++++
* Rename ``az documentdb mongocluster user`` to ``entra-user``; the group only supports
  Microsoft Entra ID principals, so the name makes that explicit.
* The user identifier is now ``--object-id`` (the Entra object/client ID GUID), keeping the
  ``-n``/``--name`` aliases.
* Rename ``entra-user create``/``delete`` to ``assign``/``remove``: the Entra principal already
  exists, so the command grants or revokes its data-plane access, matching
  ``mongocluster identity assign/remove``.
* Add ``--password``/``-p`` aliases to the administrator password across create, update,
  reset-password, and restore.
* Mark all commands and groups as Preview so the reference docs reflect the preview status.
* Rebrand the extension name to Azure DocumentDB.

1.0.0b1
+++++++
* Initial release of the Azure DocumentDB extension.
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