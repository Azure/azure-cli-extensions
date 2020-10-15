.. :changelog:

Release History
===============
0.5.0
++++++
* Apply v2020-02-10 api version for blob operations
* Add `az storage blob download-batch/upload-batch/delete-batch/copy start-batch` commands

0.4.0
++++++
* Support blob url for blob related commands
* az storage blob delete: Support --delete-snapshots with only and include values
* az storage blob upload: Support data directly uploading with --data

0.3.0
++++++
* az storage container list: Add --include-deleted to list soft-deleted containers and --show-next-marker to show marker
* az storage container restore: Restore soft-deleted container.

0.2.0
++++++
* az storage account blob-service-properties update: Support last access time tracking policy
* az storage account management-policy create/update: Support DaysAfterLastAccessTimeGreaterThan
* az storage blob show: Add lastAccessOn property

0.1.0
++++++
* Initial release.