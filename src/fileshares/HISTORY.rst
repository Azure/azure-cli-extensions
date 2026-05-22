.. :changelog:

Release History
===============

1.0.0b1
++++++
* Initial release.
* Support for managing Azure File Shares resources using API version ``2025-09-01-preview``.
* Commands for file share CRUD operations: ``az fileshare create/show/list/update/delete``.
* Check file share name availability: ``az fileshare check-name-availability``.
* View file share limits and provisioning recommendations: ``az fileshare limits-show``, ``az fileshare get-provisioning-recommendation``.
* View file share usage data: ``az fileshare usage-show``.
* Manage file share snapshots: ``az fileshare snapshot create/show/list/update/delete``.
* Manage private endpoint connections: ``az fileshare private-endpoint-connection create/show/list/update/delete``.
* View private link resources: ``az fileshare private-link-resource show/list``.