.. :changelog:

Release History
===============

1.1.0
++++++
* Support Azure File Shares API version ``2026-09-01``.
* Add managed identity commands: ``az fileshare identity assign/remove/show``.
* Add redundancy conversion commands: ``az fileshare start-redundancy-conversion``, ``az fileshare get-redundancy-conversion-status``.
* Update ``az fileshare create`` with managed identity, encryption (customer-managed key, infrastructure encryption), scale mode, and HDD media tier options; ``az fileshare update`` with encryption options. Change identities on an existing share with ``az fileshare identity assign/remove``.
* Add offer options (``--protocol``, ``--media-tier``, ``--scale-mode``) to ``az fileshare limits-show`` and ``az fileshare get-provisioning-recommendation``.
* Surface file share migration state on ``az fileshare show``.
* Fix ``az fileshare snapshot create`` sending the create request twice.
* ``az fileshare identity remove`` rejects user-assigned identities that are not assigned to the file share, instead of removing the assigned one.

1.0.2
++++++
* Fix release

1.0.1
++++++
* Fix version

1.0.0
++++++
* GA release.
* Support for managing Azure File Shares resources using API version ``2026-06-01``.
* Commands for file share CRUD operations: ``az fileshare create/show/list/update/delete``.
* Check file share name availability: ``az fileshare check-name-availability``.
* View file share limits and provisioning recommendations: ``az fileshare limits-show``, ``az fileshare get-provisioning-recommendation``.
* View file share usage data: ``az fileshare usage-show``.
* Manage file share snapshots: ``az fileshare snapshot create/show/list/update/delete``.
* Manage private endpoint connections: ``az fileshare private-endpoint-connection create/show/list/update/delete``.
* View private link resources: ``az fileshare private-link-resource show/list``.