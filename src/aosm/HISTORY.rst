.. :changelog:

Release History
===============

0.0.2
++++++
Breaking change to commands - now use `nfd` instead of `definition`.
* `az aosm nfd generate-config` for vnf and cnf. This is for NFDVs
* `az aosm nfd build|publish|delete --definition-type vnf|cnf` for vnf and `build` only for cnf. This is for NFDVs

0.0.1
++++++
* Initial release - alpha quality
    * `az aosm definition generate-config` for vnf and cnf. This is for NFDVs
    * `az aosm definition build|publish|delete` for vnf and `build` only for cnf. This is for NFDVs
