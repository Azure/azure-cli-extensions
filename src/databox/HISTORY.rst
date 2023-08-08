.. :changelog:

Release History
===============

1.1.0
++++++
* `az databox job create`: Add new parameters `--transfer-all-blobs` and `--transfer-all-files` to support setting transfer all details

1.0.0
++++++
* `az databox job create`: Add new parameter `--transfer-type` `--transfer-configuration-type` `--transfer-filter-details` `--data-box-customer-disk` to support managing import or export` jobs
* `az databox job create/update`: Add new parameter `--kek-type` `--kek-identity` `--kek-url` `--kek-vault-resource-id` to support managing customer managed key
* `az databox job`: Add new subcommand `mark-devices-shipped` to support marking devices shipped

0.1.2
++++++
* Migrate to track2 SDK

0.1.1
++++++
* GA databox module.

0.1.0
++++++
* Initial release.
