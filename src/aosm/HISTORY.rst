.. :changelog:

Release History
===============

1.0.0b4
++++++++
* Fixed: Remove check for Allow-2023-09-01 feature flag that is no longer required (Bug #1063964)

1.0.0b3
++++++++
* Move azure-storage-blob dependency to vendored_sdks (on advice from Azure CLI team to avoid 'azure' namespace issues)

1.0.0b2
++++++++
* Fixed: Use default_factory when a dataclass default is hashable (Python 3.11 compatibility)

1.0.0b1
++++++++
* Initial release - beta quality
    * `az aosm nfd|nsd generate-config` to generate an example config file to fill in for an NFD or NSD
    * `az aosm nfd|nsd build|publish|delete` to prepare files for, publish or delete an NFD or NSD
