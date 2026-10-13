.. :changelog:

Release History
===============
1.4.0b1
++++++
* `az elastic-san`: Support the 2026-05-01-preview API version and Elastic SAN V2 capacity and performance settings.
* `az elastic-san volume`: Support managed-by resource IDs and permanent deletion of soft-deleted volumes.
* `az elastic-san volume-group`: Support PATCH updates, delete retention, encryption in transit, and QoS reservations.
* `az elastic-san volume snapshot update`: Add snapshot update support.
* BREAKING CHANGE: `az elastic-san update` no longer accepts `--sku` or `--availability-zones`. Use `az elastic-san create --sku` and/or `--availability-zones` instead.

1.3.2
++++++
* `az elastic-san`: Support autoscale, prerestore, and prebackup

1.3.1b1
++++++
* `az elastic-san volume-group create/update`: Add warning for CRC data integration check

1.3.0
++++++
* `az elastic-san create`: Make `--base-size-tib` and `--extended-capacity-size-tib` optional with default value of 20 and 0

1.2.0b3
++++++
* `az elastic-san volume restore`: Support restoring soft-deleted volume
* `az elastic-san volume-group/volume list`: Support listing soft-deleted volume-group/volume
* `az elastic-san volume delete`: Support permanent delete soft-deleted volume
* `az elastic-san volume-group test-backup/test-restore`: Support testing backup volume or restore from disk snapshot

1.2.0b2
++++++
* Update module documentation.

1.2.0b1
++++++
* `az elastic-san create/update`: Support AutoScale, Add `--auto-scale-policy-enforcement`, `--capacity-unit-scale-up-limit-tib`, `--increase-capacity-unit-by-tib`, `--unused-size-tib`

1.1.0
++++++
* `az elastic-san volume-group create/update`: Add `--enforce-data-integrity-check-for-iscsi`

1.0.0
++++++
* GA with 2023-01-01 api-version
* Add connect/disconnect scripts

1.0.0b2
++++++
* Support 2023-01-01 api-version as preview
* Add `az elastic-san volume-group snapshot` command group
* Support CMK for volume-group

1.0.0b1
++++++
* Support private endpoint
* Support 2022-12-01-preview api-version
* BREAKING CHANGE: `--tags` has been removed from `az elastic-san volume-group/volume`
* BREAKING CHANGE: `--size-gib` is required for `az elastic-san volume create`

0.1.0
++++++
* Initial release.