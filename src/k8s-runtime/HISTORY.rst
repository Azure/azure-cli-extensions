.. :changelog:

Release History
===============

2.0.0
++++++
* Use stable ARM API version `2024-08-01` 
* [BREAKING CHANGE] Remove the deprecated `storage class` command set. It is only used internally, and thus should not affect customers.
* Add `update` command to the `load balancer` command set.

1.0.4
++++++
* Replace `azure-graphrbac` sdk with MS Graph sdk

1.0.3
++++++
* Vendor Azure SDKs and remove Azure SDKs from dependencies

1.0.2
++++++
* Use `preview` release train storage class extension when enabling storage class service

1.0.1
++++++
* Add RP registration check to networking resources

1.0.0
++++++
* Use stable API version `2024-03-01` for ARM API

1.0.0b2
++++++
* Fix `TypeError: 'NoneType' object is not callable` error when deleting storage class 

1.0.0b1
++++++
* Initial release.