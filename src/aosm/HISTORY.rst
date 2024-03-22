.. :changelog:

Release History
===============

Unreleased
++++++++
* Changed configurationType for NF Resources from Secret to Open

1.0.0b10
++++++++
* Removed imageName from deployParameters
* Removed image name parameter from input file
* Fixed camel casing of VHD Parameters
* Fixed blob sas url bug
* Edited comment in input file to reflect RGs are created if they do not exist
* Added creating RG if it does not exist
* Removed use of permanent temp file for helm package

1.0.0b9
++++++++
* Fixed: helm charts not uploading correctly
* Added creation of resource groups if does not exist
* Fixed: Manifest name built from ACR name, so clashes
* Fixed: Nexus image version must be semver
* Fixed: Sensible error when no type given in helm chart schema

1.0.0b8
++++++++
* No changes, building wheel from correct branch

1.0.0b7
++++++++
* Fixed: customLocation missing from Nexus
* Fixed: helm charts not uploading correctly

++++++++
1.0.0b6
++++++++
* Added Nexus support

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
