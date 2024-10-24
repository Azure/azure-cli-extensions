.. :changelog:

Release History
===============
1.2.1b1
+++++++++
- Fix: Make latest version as peview as last 2 versions(1.2.0 abd 1.1.0) are mistakenly not marked as preview.

1.2.0
+++++++++
- Fixes for highAvailability and accessKeysAuthentication argument.

1.1.0
+++++++++
- Adds support for using Microsoft Entra token-based authentication.
- Cluster has new properties: highAvailability and redundancyMode.
- New product SKUs added.
- Database has new properties: accessKeysAuthentication.

1.0.0
+++++++++
- Added support for new enterprise SKU E1

0.1.4
+++++++++
- Added support for new enterprise SKU's E5, E200, E400

0.1.3
++++++
- Added support for flushing the data in case of geo replicated cache
- Added support for customer managed keys

0.1.2
++++++
- Added support for active georeplication
	- Creating a georeplicated database
	- Creating a cache with a georeplicated database
	- Force unlinking databases
- Added support for importing from multiple blobs

0.1.1
++++++
* Renamed remaining snake_case command output fields to camelCase to be consistent with the REST API.
* Listed the following cluster attribute as null in the command output when the cluster attribute is null: zones.

0.1.0
++++++
* Initial release.
