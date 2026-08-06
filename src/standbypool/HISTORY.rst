.. :changelog:

Release History
===============

2.1.0
++++++
* Upgrade api-version to 2025-10-01
* `az standby-vm-pool create/update`: Add new properties `--dynamic-sizing-enabled` and `--post-provisioning-delay`.
* `az standby-container-group-pool create/update`: Add new property `--dynamic-sizing-enabled`.
* `az standby-vm-pool create/update`: Remove max=2000 constraint on `--max-ready-capacity` and `--min-ready-capacity`.

2.0.0
++++++
* Upgrade api-version to 2025-03-01
* `az standby-vm-pool status`: Add new StandbyPool Prediction and StandbyPool Health Status in the response.
* `az standby-container-group-pool status`:Add new StandbyPool Prediction and StandbyPool Health Status in the response.
* `az standby-container-group-pool create/update`: Add new properties `--zones` to support zonal StandbyPools.

1.0.0
++++++
* Upgrade api-version to 2024-03-01
* `az standby-vm-pool status`: Add new command
* `az standby-container-group-pool status`: Add new command
* `az standby-vm-pool create/update`: Add new properties `--min-ready-capacity` to support min ready capacity.
* `az standby-vm-pool vm show/list`: Removed command

1.0.0b1
++++++
* Initial release.