.. :changelog:

Release History
===============
3.0.0
+++++	
**Breaking Changes**

* `az connectedmachine run-command create/update`: Script parameters restructured into `--source` object (backward-compatible aliases added):
  * `--command-id`, `--script`, `--script-uri`, `--script-uri-managed-identity` still work as top-level parameters
  * New structured syntax also supported: `--source command-id=<value> script=<value> ...`
* `az connectedmachine run-command create/update`: Blob identity parameters renamed (backward-compatible aliases added):
  * `--error-blob-id` → `--error-blob-identity` (both work)
  * `--output-blob-id` → `--output-blob-identity` (both work)
* `az connectedmachine update`: `--identity` parameter available for identity type management. For user-assigned identities, use dedicated commands:
  * `az connectedmachine identity assign`
  * `az connectedmachine identity remove`
* `az connectedmachine private-link-scope network-security-perimeter-configuration reconcile`: Removed `--no-wait` parameter (no corresponding wait command exists)
* `az connectedmachine private-link-scope network-security-perimeter-configuration wait`: Command removed (reconcile operation is synchronous)
* `az connectedmachine license validate`: Parameter `--license-details` flattened to individual parameters:
  * `--edition`
  * `--processors`
  * `--state`
  * `--target`
  * `--type`
  * `--volume-license-details`

**Features**

* Upgraded to stable API version 2026-07-15 (from preview 2026-06-16)
* Fixed AAZ paging bugs in 14 list commands
* Fixed reconcile output null-safety handling
* Added short parameter abbreviations for update command (`--parent-cluster-id`, `--private-link-scope-id`)

3.0.0b1
+++++	
* 2026/06/19-preview is used for aaz generation. Migrated to aaz.

2.0.0b2
+++++	
* Update connectedmachine extension image commands and set subscription id as optional.

2.0.0b1
+++++	
* 2024/11/10-preview is used for aaz generation. Migrated to aaz.

1.1.1b1
+++++	
* Fix connectedmachine list command and set resource group as optional.

1.1.0
+++++	
* Add Pay-as-you-go features. 2024/07/31-preview is used for aaz generation. Migrated to aaz.

1.0.0
+++++	
* 2024/07/10-stable is used for aaz generation. Migrated to aaz.

1.0.0b2
+++++	
* Add features. 2024/05/20-preview is used for aaz generation. Migrated to aaz.

1.0.0b1
+++++	
* Add ESU license and Network Security Perimeter API's. 2024/03/31-preview is used for aaz generation. Migrated to aaz.

0.7.0
+++++	
* Add run-commands API's. 2023/10/03-preview is used for aaz generation. Migrated to aaz.

0.6.0
+++++	
* Add install-patches/assess-patches/Extensionimage API's. 2022/12/27 is used for aaz generation. Migrated to aaz.

0.5.1
+++++	
* Add enable-auto-upgrade param back into the extension upgrade command

0.5.0
+++++	
* Upgrade the API version to stable/2022-03-10 

0.4.1	
+++++	
* Add the enable-auto-upgrade parameter in az connectedmachine extension create/update functions

0.4.0	
+++++	
* Add private link scope and private endpoint connection commands	

0.3.0	
+++++	
* Rename machine-extension subgroup to extension
* Move all commands under the machine subgroup to the extension level	

0.2.0	
+++++	
* machineextensions support	

0.1.1	
+++++	
* Remove the limitation of max compatible cli core version	

0.1.0
++++++
* Initial release.