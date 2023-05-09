.. :changelog:

Release History
===============
0.7.2
++++++
* Remove commands supported in azure cli

0.7.1
++++++
* `az storage blob copy start`: Fix auth issue

0.7.0
++++++
* `az storage blob upload/set-tier/copy start`: Support `Cold` for `--tier`

0.6.2
++++++
* `az storage blob filter`: Add `--container-name` to support filter blobs in specific container

0.6.1
++++++
* `az storage blob immutability-policy set/delete`: Extend/Lock/Unlock/Delete blob's immutability policy
* `az storage blob set-legal-hold`: Configure/Clear blob legal hold

0.6.0
++++++
* Remove `az storage account blob-service-properties` since all the preview arguments are supported in main azure cli
* Add `parquet` option to `az storage blob query --input-format`

0.5.2
++++++
* Apply v2020-06-12 api version for blob operations
* Add `az storage blob download-batch/upload-batch/delete-batch/copy start-batch` commands

0.5.1
++++++
* Fix issue #3460
* Remove commands supported in azure cli

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