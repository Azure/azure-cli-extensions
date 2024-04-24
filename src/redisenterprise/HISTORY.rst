.. :changelog:

Release History
===============

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