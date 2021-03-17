.. :changelog:

Release History
===============
0.5.0
++++++
* `az storage blob upload`: Refine help message
* Remove `az storage account management-policy` because it is supported in main azure cli
* Upgrade api version to 2021-01-01 for `az storage account blob-service-properties`
* az storage blob upload: Support larger size of block blob, increasing from 4.75 TiB to 190.7 TiB (50,000 blocks, each block from 100MB to 4000MB)

0.4.1
++++++
* `az storage blob service-properties`: Adopt new api version with track2 SDK

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