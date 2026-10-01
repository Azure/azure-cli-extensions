.. :changelog:

Release History
===============

0.1.2
++++++
* Fix: ``az functionapp scale config always-ready delete`` now correctly removes always-ready
  instances whose names contain a colon (e.g. ``function:Function1``). The deletion logic
  uses case-insensitive name comparison to handle ARM API name normalization.

0.1.1
++++++
* Fix bug when running `az functionapp devops-pipeline create`

0.1.0
++++++
* Initial release.
