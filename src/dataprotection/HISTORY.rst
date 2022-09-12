.. :changelog:

Release History
===============
0.6.0
++++++
* `az dataprotection backup-instance initialize`: Add optional `--tags` parameter

0.5.0
++++++
* `az dataprotection backup-instance update-msi-permissions`: New command to grant missing permissions to backup vault MSI
* `az dataprotection backup-instance initialize`: Added optional `--snapshot-resource-group-name` parameter

0.4.0
++++++
* `az dataprotection resource-guard`: Onboard ResourceGuard to dataprotection extension
* `az dataprotection backup-vault create/update`: Add support for Azure Monitor based alerts

0.3.0
++++++
* API version upgrade with bug fixes
* az dataprotection backup-instance: Support stop-protection/suspend-backup/resume-protection

0.2.0
++++++
* onboard OSS workload to dataprotection extension.
* [BREAKING CHANGE] `az dataprotection restorable-time-range find`: `--backup-instances` renamed to `--backup-instance-name`.

0.1.0
++++++
* Initial release.
