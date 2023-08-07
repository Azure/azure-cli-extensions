.. :changelog:

Release History
===============

1.0.0b1
++++++
* Migrate `az tsi access-policy/environment/reference-data-set` to CodeGen

0.2.1
++++++
* Command group ``az tsi`` GA

0.2.0
++++++
* [BREAKING CHANGE] ``az timeseriesinsights`` is changed to ``az tsi``
* [BREAKING CHANGE] ``az timeseriesinsights environment standard`` is changed to ``az tsi environment gen1``
* [BREAKING CHANGE] ``az timeseriesinsights environment longterm`` is changed to ``az tsi environment gen2``
* Add command group ``az tsi reference-data-set``

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
