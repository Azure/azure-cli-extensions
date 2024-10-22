.. :changelog:

Release History
===============
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