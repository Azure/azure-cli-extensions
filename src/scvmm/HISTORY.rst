.. :changelog:

Release History
===============


0.1.7
++++++
* [Hotfix] Disabling pwinput till the issue here gets fixed: https://github.com/Azure/azure-cli/issues/24781 

0.1.6
++++++
* Displaying asterisks (*****) for password input.

0.1.5
+++
* Requesting VMMServer credentials from the user until they are non-empty.
* [BREAKING CHANGE] Removing default value for port. Asking for the input. If input is empty, setting port to 8100.

0.1.4
++++++
* Bug fixes
* Force and retain flags in VM delete
* Generated SDK now requires updated version of azure-cli
* Long running PATCH operations

0.1.3
++++++
* View Inventory, onboard inventory item to azure.
* CRUD for availablity sets.

0.1.2
++++++
* Interactive password.

0.1.1
++++++
* CRUD of VMMServer, Cloud, VMTemplate, VM. Tags Supported. azdev lint passing.

0.1.0
++++++
* Initial release.
