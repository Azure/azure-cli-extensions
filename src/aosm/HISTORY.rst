.. :changelog:

Release History
===============

Unreleased
++++++++

1.0.0b5
++++++++
* Add `publisher` command group for management of publisher resources.
* Changed the name of the `path_to_mappings` parameter in the CNF input file to `default_values`
* Added a `helm template` validation step to the `az aosm nfd build` command for the `cnf` definition type
* Added validation of the values file for helm charts when using the `az aosm nfd build` command for the `cnf` definition type
* Fixed helm chart image parsing in the `az aosm nfd build` command for the `cnf` definition type. This means that the images can now be extracted correctly from the helm chart.
* Fixed: infinite loop bug when retrying failed artifact uploads to the ACR

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
