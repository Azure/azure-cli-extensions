.. :changelog:

Release History
===============
2.0.0b2
++++++++
* Remove msrestazure dependency

2.0.0b1
++++++++
* Renamed nfdvName to nfdv in CGVs
* Added useful comments to input files
* Added 1:1 mapping between NFVIsFromSite and NF RETs
* Added expose_all parameter in input file to expose all parameters in deployParameters and CGS
* Removed multiple_instances and depends_on from input file
* Added: mutating webhook for injectArtifactStoreDetails
* Added: Users can specify multiple image sources from all types of registries (not just ACRs). General improvements in how CNF image sources are handled. 
* Fixed: Namespace appeared twice in the `artifacts.json` file, leading to errors in the publish step of the CLI.
* Changed configurationType for NF Resources from Secret to Open
* Removed imageName from deployParameters
* Removed image name parameter from input file
* Fixed camel casing of VHD Parameters
* Fixed blob sas url bug
* Edited comment in input file to reflect RGs are created if they do not exist
* Added creating RG if it does not exist
* Removed use of permanent temp file for helm package
* Fixed: helm charts not uploading correctly
* Added creation of resource groups if does not exist
* Fixed: Manifest name built from ACR name, so clashes
* Fixed: Nexus image version must be semver
* Fixed: Sensible error when no type given in helm chart schema
* Fixed: customLocation missing from Nexus
* Fixed: helm charts not uploading correctly
* Added: Nexus support
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
