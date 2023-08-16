.. :changelog:

Release History
===============

unreleased
++++++++++
* Added a `--clean` flag to the NSD `delete` command. This flag will delete the NSDG on top of the other resources deleted by the `delete` command.
* Added integration tests for `publish` and `delete` commands.
* Added a `--force` flag to the aosm `build` and `delete` commands. This command will force the `build` or `delete` commands to proceed without waiting on user input to confirm.
* `az aosm nfd build` options `--order-params` and `--interactive` to help users choose which NF parameters to expose as deployParameters. Feature added that allows CNF value mappings file to be generated if none is supplied.
* NFDV version exposed as a CGV on an SNS.
* `az aosm nfd publish` option added for `--definition-type cnf` to publish the CNF bicep templates, upload helm charts from disk to the ACR and copy the images from a source ACR to the target ACR.
* Managed Identity added to VNF NF templates - requires subscription to be registered for the feature flag.
* Various fixes to NFD build of deployParameters schema and interactive mode create of deployParameters mappings file.
* Fix CNF NFD publish so that it doesn't render the ACR unuseable for future Artifact publishing.
* Allow CNF NFD image copy from a source ACR using a namespace.
* Fix - Add new CGSchema parameters not from the NFD to the `required` section of the schema.
* Add the ability to skip bicep publish or artifact upload during publish commands.
* Fix Manifest name for NSDs so it isn't the same as that for NFDs
* Add validation of source_registry_id format for CNF configuration
* Workaround Oras client bug (#90) on Windows for Artifact upload to ACR
* Take Oras 0.1.18 so above Workaround could be removed
* Take Oras 0.1.19 to fix NSD Artifact upload on Windows
* Support deploying multiple instances of the same NF in an SNS
* Fix CNF publish on Windows by using Linux style paths in rendered NFD bicep templates (bicep always requires Linux style paths).

0.2.0
++++++
Breaking change to commands - now use `nfd` instead of `definition`. Publish option removed from build.
* `az aosm nfd generate-config` for vnf and cnf. This is for NFDVs
* `az aosm nfd build|publish|delete --definition-type vnf|cnf` for vnf and `build` only for cnf. This is for NFDVs

0.1.0
++++++
* Initial release - alpha quality
    * `az aosm definition generate-config` for vnf and cnf. This is for NFDVs
    * `az aosm definition build|publish|delete` for vnf and `build` only for cnf. This is for NFDVs
