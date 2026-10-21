.. :changelog:

Release History
===============

2.0.0b1
+++++++
* Update service group commands to use stable API version 2026-08-01.
* Add support for service group criticality attributes.
* BREAKING CHANGE: Remove the preview-only ``service-group list-ancestors`` command. Scripts using this command must be updated.
* BREAKING CHANGE: Remove ``--kind`` from ``service-group update`` because service group kind is create-time only. Use ``--kind`` with ``service-group create`` instead.

1.0.0b1
+++++++
* Initial release.
