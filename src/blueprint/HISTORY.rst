.. :changelog:

Release History
===============
0.3.2
+++++
* Migrate to atomic commands

0.3.1
+++++
* Migrate blueprint to track2 SDK

0.3.0
+++++
* Allow user to export blueprint and artifacts to local directory

0.2.1
+++++
* Support removing depends_on relationships for artifacts in update command

0.2.0
+++++
* `az blueprint assignment create/update`: Support user assigned identity with `--user-assigned-identity`
* `az blueprint assignment create/update`: Remove `--principal-id`, `--tenant-id`, `--user-assigned-identities`

0.1.1
+++++
* `az blueprint assignment`: Fix resource group key error in Python 3.6 and 3.7
* `az blueprint publish`: Fix error when `--change-notes` is empty

0.1.0
++++++
* Initial release.
