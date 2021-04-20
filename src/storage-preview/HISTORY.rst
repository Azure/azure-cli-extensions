.. :changelog:

Release History
===============
0.7.2(2021-04-09)
++++++++++++++++++
* Remove `az storage blob service-properties` as it is supported in storage-blob-preview extension and Azure CLI

0.7.1(2021-04-06)
++++++++++++++++++
* `az storage account file-service-properties`: Add support for secured SMB

0.7.0 (2020-12-28)
++++++++++++++++++
* Add support for `az storage file upload`, `az storage file upload-batch` (Track 2)

0.6.1 (2020-12-15)
++++++++++++++++++
* `az storage account file-service-properties`: Support SMB multichannel in file service properties

0.6.0 (2020-11-04)
++++++++++++++++++
* Support Blob Inventory Policy in storage account

0.5.0 (2020-11-02)
++++++++++++++++++
* Support resource access rules in storage account

0.4.0 (2020-10-15)
++++++++++++++++++
* Add deprecate info for `az storage blob access`, `az storage blob directory`, `az storage blob move`
* [BREAKING CHANGE] Remove `az storage account` related commands because they are supported in main azure cli

0.3.0 (2020-09-15)
++++++++++++++++++
* Remove `az storage blob list`

0.2.12 (2020-07-29)
++++++++++++++++++
* Upgrade azcopy version to 10.5.0

0.2.11 (2020-07-27)
++++++++++++++++++
* Fix the storage account name in examples
* Fix the bug of `--num-results` for command `az storage blob directory list`
* Fix the bug for command `az storage blob directory move`
* Fix azcopy issue

0.2.10 (2019-11-25)
++++++++++++++++++
* Fix bugs for ADLS Gen2

0.2.9 (2019-10-31)
++++++++++++++++++
* Integrate Azcopy v10.3.1
* Add `az storage blob directory` command group
* Add blob move command and blob access command group

0.2.8 (2019-7-5)
++++++++++++++++++
* Remove file-add command argument

0.2.7 (2019-6-14)
++++++++++++++++++
* Remove min_profile

0.2.6 (2019-5-28)
++++++++++++++++++
* Update the max CLI core version as 2.0.66

0.2.5 (2019-5-1)
++++++++++++++++++
* Release management policy

0.2.4 (2019-4-11)
++++++++++++++++++
* Release azcopy commands: `az storage azcopy blob sync`

0.2.3 (2019-3-21)
++++++++++++++++++
* Release initial azcopy commands: `az storage azcopy blob delete/upload/download`

0.2.2 (2019-1-18)
++++++++++++++++++
* set minCliCoreVersion metadata to v2.0.52

0.2.1 (2019-1-4)
++++++++++++++++++
* fixed missing `--auth-mode` from data-plane commands
* add validation for StorageV2 account when using static website

0.2.0 (2018-12-14)
++++++++++++++++++
* created HISTORY.rst
* added customer-controlled failover feature
