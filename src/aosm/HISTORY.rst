.. :changelog:

Release History
===============

unreleased
++++++++++
* `az aosm nfd build` options `--order-params` and `--interactive` to help users choose which NF parameters to expose as deployParameters. Feature added that allows CNF value mappings file to be generated if none is supplied.

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
