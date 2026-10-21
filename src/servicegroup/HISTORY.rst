.. :changelog:

Release History
===============

2.0.0b1
+++++++
* Update service group commands to use stable API version 2026-08-01.
* Add support for service group criticality attributes.
* Update create and update polling to retrieve the final service group from the original resource URI.
* BREAKING CHANGE: Remove the preview-only ``service-group list-ancestors`` command. Scripts using this command must be updated.
* BREAKING CHANGE: Remove ``--kind`` from ``service-group update`` because service group kind is create-time only. Use ``--kind`` with ``service-group create`` instead.
* BREAKING CHANGE: ``service-group update`` no longer supports clearing ``--display-name``, ``--parent``, or ``--tags`` by passing an explicit null because these properties are not nullable in the service contract. Omit an argument to retain its current value, or provide a replacement value.

1.0.0b1
+++++++
* Initial release.
