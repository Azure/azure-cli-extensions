.. :changelog:

Release History
===============

0.2.0
++++++
* [BREAKING CHANGE] Deprecate ``az timeseriesinsights`` command group, add a command group ``az tsi``
* ``az tsi environment`` support ``gen1 environment`` and ``gen2 environment``
* Add command group `az tsi reference-data-set`

0.1.3
++++++

* Fix #2003: ``az timeseriesinsights environment standard create``: ``--partition-key-properties`` should be optional

0.1.2
++++++

* Fix #1712: ``az timeseriesinsights event-source eventhub/iothub create``: ``--timestamp-property-name`` should be optional

0.1.1
++++++
* Fix #1657: ``timeSeriesIdPropertyName`` is not parsed properly
* Fix #1658: When creating a new Standard Environment, ``--data-retention-time`` is not properly documented

0.1.0
++++++
* Initial release.
