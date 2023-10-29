.. :changelog:

Release History
===============
0.3.2
++++++
* Added null support for argument --certificate and --subnet in commands "az load update" and "az load create" to remove those properties from test.
* Added support to remove certificate, subnet from config file when provided in commands "az load update" and "az load create".
* Logical implementation changed when using config file using argument --load-test-config-file in commands "az load test update" and "az load test create".  
* Added test cases test_load_test_update_with_config to test the new fixes.

0.3.1
++++++
* Enhanced data plane test cases.
* Fix for failure criteria when 'az load test create' and 'az load test update' commands when using --load-test-config-file option.

0.3.0
++++++
* Initial release of Azure Load Testing data plane command groups.

0.2.0
++++++
* Stable version release.

0.1.0
++++++
* Initial release.