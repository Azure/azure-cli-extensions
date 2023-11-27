.. :changelog:

Release History
===============

Unreleased
++++++++
* Add `publisher` command group for management of publisher resources.

1.0.0b2
++++++++
* Fixed: Use default_factory when a dataclass default is hashable (Python 3.11 compatibility)

1.0.0b1
++++++++
* Initial release - beta quality
    * `az aosm nfd|nsd generate-config` to generate an example config file to fill in for an NFD or NSD
    * `az aosm nfd|nsd build|publish|delete` to prepare files for, publish or delete an NFD or NSD
